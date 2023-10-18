import mlflow
from typing import List

def register_mlflow_run_id() -> List[dict]:
    run = mlflow.active_run()
    if run is None:
        # TODO: add run name and experiment name from params if kedro-mlflow is not enabled
        run_id = mlflow.start_run().info.run_id
    else:
        run_id = run.info.run_id  
    return f"{run_id}"