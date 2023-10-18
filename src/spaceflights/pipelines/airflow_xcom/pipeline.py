from kedro.pipeline import Pipeline, node, pipeline

from .nodes import register_mlflow_run_id


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=register_mlflow_run_id,
                inputs=None,
                outputs="airflow_xcom_push",
                name="export_mlflow_run_id",
                tags=[]
            ),
        ]
    )