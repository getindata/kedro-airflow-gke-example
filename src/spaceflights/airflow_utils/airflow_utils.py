from typing import Tuple

def group_nodes_with_tags(node_tags:dict, grouping_prefix:str = "airflow:") -> Tuple[dict, dict]:
    # Helper dictionary that says to which group/node each node is part of
    group_translator = { k:k for k in node_tags.keys() }
    # Dict of groups and nodes they consist of
    tag_groups = dict()
    for node, tags in node_tags.items():
        for tag in tags:
            if tag.startswith(grouping_prefix):
                if tag not in tag_groups:
                    tag_groups[tag] = set()
                tag_groups[tag].add(node)
                group_translator[node] = tag
    return group_translator, tag_groups


def get_tasks_from_dependencies(node_dependencies: dict, group_translator: dict) -> Tuple[set, dict]:
    # Calculating graph structure after grouping nodes by grouping tags
    group_dependencies = {}
    task_names = set()
    for parent, children in node_dependencies.items():
        if group_translator[parent] not in group_dependencies:
            group_dependencies[group_translator[parent]] = set()
        this_group_deps = group_dependencies[group_translator[parent]]
        task_names.add(group_translator[parent])
        for child in children:
            if group_translator[child] != group_translator[parent]:
                this_group_deps.add(group_translator[child])
            task_names.add(group_translator[child])
    return task_names, group_dependencies
        

def update_node_tags(node_tags: dict, tag_groups: dict) -> dict:
    # Grouping tags of new group nodes as sum of nodes' tags
    node_tags.update({ group : set([tag for node in tag_groups[group] for tag in node_tags[node]]) for group in tag_groups})
    return node_tags


# {# # data from the database about who triggered the run and log it.
# # This does not work in gke composer, but works on local airflow, for some reason
# def fetch_and_log_trigger_info(**kwargs):
#     from airflow.models.log import Log
#     from airflow.utils.db import create_session

#     try:
#         with create_session() as session:
#             results = session.query(Log.dttm, Log.dag_id, Log.execution_date, Log.owner, Log.extra).filter(Log.dag_id == "{{ dag_name | safe }}", Log.event == 'trigger').all()

#         manually_triggered_by = results[1][3] # first result, 4rd argument is the triggerer
#     except Exception:
#         manually_triggered_by = "unknown"
#     # Log the information.
    
#     # logging.info(f"DAG manually triggered by: {manually_triggered_by}")
#     return slugify(manually_triggered_by) #}
