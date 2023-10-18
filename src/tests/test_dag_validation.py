"""
This module contains an example test.

Tests should be placed in ``src/tests``, in modules that mirror your
project's structure, and in files named test_*.py. They are simply functions
named ``test_*`` which test a unit of logic.

To run the tests, run ``kedro test`` from the project root directory.
"""
from pathlib import Path

import pytest
from kedro.config import ConfigLoader
from kedro.framework.context import KedroContext
from kedro.framework.hooks import _create_hook_manager
from spaceflights.pipeline_registry import validate_tag_grouping
from kedro.pipeline import Pipeline, node, pipeline


@pytest.fixture
def config_loader():
    return ConfigLoader(conf_source=str(Path.cwd()))


@pytest.fixture
def project_context(config_loader):
    return KedroContext(
        package_name="spaceflights",
        project_path=Path.cwd(),
        config_loader=config_loader,
        hook_manager=_create_hook_manager(),
    )

def dummy_node(*args, **kwargs):
    pass

# The tests below are here for the demonstration purpose
# and should be replaced with the ones testing the project
# functionality
class TestTagValidation:
    def test_dummy_tagging(self):
        test_pipe = pipeline(
            [
                node(
                    func=dummy_node,
                    inputs=["model_input_table", "params:model_options"],
                    outputs=["X_train", "X_test", "y_train", "y_test"],
                    name="split_data_node",
                    tags=["airflow:split", "machine:medium"]
                ),
                node(
                    func=dummy_node,
                    inputs=["X_train", "y_train"],
                    outputs="regressor",
                    name="train_model_node",
                    tags=["machine:medium"]
                ),
                node(
                    func=dummy_node,
                    inputs=["regressor", "X_test", "y_test"],
                    outputs=None,
                    name="evaluate_model_node",
                    tags=["machine:medium"]
                ),
            ]
        )
        cycle, history = validate_tag_grouping(test_pipe)
        assert cycle == None

    def test_correct_tagging(self):
        test_pipe = pipeline(
            [
                node(
                    func=dummy_node,
                    inputs=["model_input_table", "params:model_options"],
                    outputs=["X_train", "X_test", "y_train", "y_test"],
                    name="split_data_node",
                    tags=["airflow:split", "machine:medium"]
                ),
                node(
                    func=dummy_node,
                    inputs=["X_train", "y_train"],
                    outputs="regressor",
                    name="train_model_node",
                    tags=["airflow:split", "machine:medium"]
                ),
                node(
                    func=dummy_node,
                    inputs=["regressor", "X_test", "y_test"],
                    outputs=None,
                    name="evaluate_model_node",
                    tags=["machine:medium"]
                ),
            ]
        )
        cycle, history = validate_tag_grouping(test_pipe)
        assert cycle == None

    def test_incorrect_tagging(self):
        test_pipe = pipeline(
            [
                node(
                    func=dummy_node,
                    inputs=["model_input_table", "params:model_options"],
                    outputs=["X_train", "X_test", "y_train", "y_test"],
                    name="split_data_node",
                    tags=["airflow:split", "machine:medium"]
                ),
                node(
                    func=dummy_node,
                    inputs=["X_train", "y_train"],
                    outputs="regressor",
                    name="train_model_node",
                    tags=["machine:medium"]
                ),
                node(
                    func=dummy_node,
                    inputs=["regressor", "X_test", "y_test"],
                    outputs=None,
                    name="evaluate_model_node",
                    tags=["airflow:split", "machine:medium"]
                ),
            ]
        )
        # with pytest.raises(ValueError):
        cycle, history = validate_tag_grouping(test_pipe)
        assert cycle != None


    def test_incorrect_tagging_warning(self, caplog):
        test_pipe = pipeline(
            [
                node(
                    func=dummy_node,
                    inputs=["model_input_table", "params:model_options"],
                    outputs=["X_train", "X_test", "y_train", "y_test"],
                    name="split_data_node",
                    tags=["airflow:split", "machine:medium"]
                ),
                node(
                    func=dummy_node,
                    inputs=["X_train", "y_train"],
                    outputs="regressor",
                    name="train_model_node",
                    tags=["airflow:split", "machine:small"]
                ),
                node(
                    func=dummy_node,
                    inputs=["regressor", "X_test", "y_test"],
                    outputs=None,
                    name="evaluate_model_node",
                    tags=["machine:medium"]
                ),
            ]
        )
        cycle, history = validate_tag_grouping(test_pipe)
        assert any([record for record in caplog.records if record.levelname == "WARNING"])

