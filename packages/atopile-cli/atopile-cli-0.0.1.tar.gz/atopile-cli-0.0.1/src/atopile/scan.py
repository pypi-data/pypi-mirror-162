import logging
from enum import Enum, auto
from typing import Dict, Set
from pathlib import Path

import networkx as nx
from attrs import define

from .stages import File, Handle, Stage, StageIO
from .utils import SubLog

log = logging.getLogger(__name__)

class NodeType(Enum):
    Stage = auto()
    IO = auto()

@define
class BuildGraph(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.name: str = None
        self.log: SubLog = None
        self.logger: logging.Logger = None
        self.project_dir: Path = None

    def get_nodes_by_type(self, node_type: NodeType) -> Dict[str, dict]:
        nodes = {}
        for n in self.nodes:
            node = self.nodes[n]
            if node['type'] == node_type:
                nodes[n] = self.nodes[n]
        return nodes

    @property
    def ios(self) -> Dict[str, StageIO]:
        return {k: n['io'] for k, n in self.get_nodes_by_type(NodeType.IO).items()}

    @property
    def stages(self) -> Dict[str, Stage]:
        return {k: n['stage'] for k, n in self.get_nodes_by_type(NodeType.Stage).items()}

    @property
    def roots(self) -> Set[str]:
        """
        The base inputs which have no dependencies
        """
        leaves = [n for n in self.nodes() if self.in_degree(n) == 0]
        return leaves

    @property
    def leaves(self) -> Set[str]:
        """
        The final outputs which are used by nothing more
        """
        graph = nx.reverse_view(self)
        leaves = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        return leaves

    def direct_upstream_nodes(self, reference: str) -> Set[str]:
        reversed_graph = nx.reverse_view(self)
        upstream = set(reversed_graph.neighbors(reference))
        return upstream

    def direct_downstream_nodes(self, reference: str) -> Set[str]:
        downstream = set(self.neighbors(reference))
        return downstream

    def all_upstream_nodes(self, reference: str) -> Set[str]:
        dependants = nx.dfs_tree(self, reference)
        return set(dependants.nodes())

    def all_downstream_nodes(self, reference: str) -> Set[str]:
        dependants = nx.dfs_tree(nx.reverse_view(self), reference)
        return set(dependants.nodes())

    def get_inputs(self, stage_ref: str) -> Dict[str, StageIO]:
        inputs = {}
        for n in self.direct_upstream_nodes(stage_ref):
            if self.nodes[n]['type'] == NodeType.IO:
                edge = self.get_edge_data(n, stage_ref)
                hook = edge['hook']
                inputs[hook] = self.nodes[n]['io']
        return inputs

    def get_outputs(self, stage_ref: str) -> Dict[str, StageIO]:
        outputs = {}
        for n in self.direct_downstream_nodes(stage_ref):
            if self.nodes[n]['type'] == NodeType.IO:
                outputs[n] = self.nodes[n]['io']
        return outputs
   
    def handle_source_stage(self, reference: str) -> Stage:
        """
        Return the source of a handle
        """
        node = self.nodes[reference]
        if node.get('type') != NodeType.IO:
            self.logger.fatal(f'{reference} is a {node.get("type")} not an {NodeType.IO}')
            raise ValueError

        upstream = self.direct_upstream_nodes(reference)
        if len(upstream) != 1:
            self.logger.fatal(f'multiple sources for {reference}')
            raise ValueError

        return self.nodes[list(upstream)[0]]['stage']

    def validate_handle_degree(self, reference: str):
        """
        Validate a hendle node has a unique source
        """
        if self.in_degree(reference) < 1:
            self.logger.error(f'no source for handle {reference}')
            return True
        elif self.in_degree(reference) > 1:
            self.logger.error(f'multiple sources for handle {reference}')

    def validate_handle_types(self, reference: str):
        """
        Validate a hendle node has a unique source
        """
        source = self.handle_source_stage(reference)
        source_output = self.get_edge_data(source.name, reference)['hook']
        consumer_nodes = self.direct_downstream_nodes(reference)

        for consumer_node in consumer_nodes:
            consumer = self.nodes[consumer_node]['stage']
            consumer_hook = self.get_edge_data(reference, consumer_node)['hook']
            source_type = source.outputs[source_output].typename
            consumer_type = consumer.inputs[consumer_hook].typename
            if source_type != consumer_type:
                self.logger.error(f'{source.name} and {consumer.name} disagree on {reference} type')

    def validate_handle(self, reference: str, handle: Handle):
        """
        Validate a handle
        """
        self.validate_handle_degree(reference)
        self.validate_handle_types(reference)

    def validate_file(self, reference: str, file: File):
        """
        Validate a file
        """
        if not (self.project_dir / file.path).exists():
            self.logger.error(f'{reference} doens\'t exist')

    def validate_ios(self):
        for reference, io in self.ios.items():
            if isinstance(io, File):
                self.validate_file(reference, io)
            elif isinstance(io, Handle):
                self.validate_handle(reference, io)

    def validate_cyclical_deps(self) -> bool:
        if not nx.is_directed_acyclic_graph(self):
            cycle = nx.find_cycle(self._graph)
            cycle_steps = [edge[0] for edge in cycle]
            cycle_steps += [cycle_steps[0]]
            friendly_cycle = ' -> '.join(cycle_steps)
            self.logger.error(friendly_cycle)

    def validate(self):
        self.validate_ios()
        self.validate_cyclical_deps()

    @classmethod
    def from_stages(cls, name, stages: Dict[str, Stage], project_dir: Path):
        self = cls()
        self.name = name
        self.log = SubLog(name)
        self.logger = self.log.logger
        self.project_dir = project_dir

        # make stages first
        for stage_name, stage in stages.items():
            self.add_node(stage_name, type=NodeType.Stage, stage=stage, log=log, logger=self.log.get_logger(stage_name))

        # link them up
        # this is currently a little odd, because it just chooses one of the StageIO object instances, multiple of which will point to the same thing
        for stage_name, stage in stages.items():
            for input_name, input in stage.inputs.items():
                if not self.has_node(input.reference):
                    self.add_node(input.reference, type=NodeType.IO, io=input, log=log, logger=self.log.get_logger(stage_name))
                self.add_edge(input.reference, stage_name, hook=input_name)

            for output_name, output in stage.outputs.items():
                if not self.has_node(output.reference):
                    self.add_node(output.reference, type=NodeType.IO, io=output, log=log, logger=self.log.get_logger(stage_name))
                self.add_edge(stage_name, output.reference, hook=output_name)

            for after_stage_name in stage.after:
                self.add_edge(after_stage_name, stage_name, hook=None)

        # check this build is legitimate
        self.validate()

        # fail of there's anything worse than a warning with this build
        if self.log.max_levelno > logging.WARNING:
            print(str(self.log))
            raise ValueError(f'{self.name} validation failed')

        return self
