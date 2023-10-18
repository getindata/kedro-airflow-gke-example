"""Project pipelines."""
from collections import defaultdict
import logging
from typing import Dict, Optional, Tuple

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from .airflow_utils import group_nodes_with_tags, update_node_tags, get_tasks_from_dependencies 

## this should sourced from and be the same as in airflow.yml, FIXME
GROUPING_PREFIX = "airflow:"
MACHINE_PREFIX = "machine:"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def validate_tag_grouping(pipeline) -> Tuple[Optional[str], set]:
    # Returns name of the node that caused validation error and all nodes in path that has lead to cycle if error occured
    node_tags = {}
    node_dependencies = defaultdict(set)
    for node, parent_nodes in pipeline.node_dependencies.items():
        for parent in parent_nodes:
            node_dependencies[parent.name].add(node.name)

    for node in pipeline.nodes:
        node_tags[node.name] = node.tags

    group_translator, tag_groups = group_nodes_with_tags(node_tags, GROUPING_PREFIX)
    task_names, group_dependencies = get_tasks_from_dependencies(node_dependencies, group_translator)
    update_node_tags(node_tags, tag_groups)

    # Validation of machine tags
    for group, tags in node_tags.items():
        if len([x for x in filter(lambda x: 1 if x.startswith(MACHINE_PREFIX) else 0, tags)]) > 1:
            logger.warning(f"Group {group} has multiple machine tags, this may cause unexpected behavior in which machine is used for the group, please use only one machine tag per group")

    visited_nodes = set()

    # This representation is not optimal, but does not need to be as these DAGs are small graphs
    def find_cycle(node : str, dfs_visit_history : set) -> Optional[str]:
        visited_nodes.add(node)
        dfs_visit_history.add(node)
        if node in group_dependencies:
            for child in group_dependencies[node]:
                if child == node:
                    return node
                if child not in dfs_visit_history:
                    ret = find_cycle(child, dfs_visit_history)
                    if ret is not None:
                        return ret
                else:
                    return child
        dfs_visit_history.remove(node)
        return None
    history = set()

    start_node = "__start__"
    while start_node in group_dependencies:
        start_node = "_" + start_node + "_"
    # Adding artificial node that points to all non terminating nodes
    group_dependencies[start_node] = { node for node in group_dependencies.keys() }
    
    # Alternative solution - try to build a new superficial graph and use kedro to validate it
    return find_cycle(start_node, history), history


def validate_pipelines(pipelines):
    logger.info("Validating pipelines tagging...")
    # Tag grouping validation
    for name, pipeline in pipelines.items():
        try:
            result, cycle = validate_tag_grouping(pipeline)
        except ValueError as verr:
            logger.error(f"Pipeline {name} has invalid grouping in some nodes: {verr}")
        if result:
            logger.error(f"Pipeline {name} has invalid grouping that creates a cycle in its grouping tags regarding nodes: {str(cycle)}")


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    pipelines = find_pipelines()
    pipelines["__default__"] = sum([p for k, p in pipelines.items() if k != "airflow_xcom"])

    validate_pipelines(pipelines)
    return pipelines
