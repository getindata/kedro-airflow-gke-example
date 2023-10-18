"""Project settings. There is no need to edit this file unless you want to change values
from the Kedro defaults. For further information, including these default values, see
https://kedro.readthedocs.io/en/stable/kedro_project_setup/settings.html."""

# Instantiated project hooks.
# For example, after creating a hooks.py and defining a ProjectHooks class there, do
# from spaceflights.hooks import MLFlowRunIdHook

# DISABLE_HOOKS_FOR_PLUGINS = ("kedro-mlflow",)
# HOOKS = (MLFlowRunIdHook(),)#, MlflowHook()) 

# Installed plugins for which to disable hook auto-registration.

# Class that manages storing KedroSession data.
# from kedro.framework.session.store import BaseSessionStore
# SESSION_STORE_CLASS = BaseSessionStore
# Keyword arguments to pass to the `SESSION_STORE_CLASS` constructor.
# SESSION_STORE_ARGS = {
#     "path": "./sessions"
# }

# Directory that holds configuration.
# CONF_SOURCE = "conf"

# Class that manages how configuration is loaded.
from kedro.config import OmegaConfigLoader
from omegaconf.resolvers import oc
CONFIG_LOADER_CLASS = OmegaConfigLoader
# Keyword arguments to pass to the `CONFIG_LOADER_CLASS` constructor.
CONFIG_LOADER_ARGS = {
    "custom_resolvers": {
        "oc.env": oc.env
    }
}

# Class that manages Kedro's library components.
# from kedro.framework.context import KedroContext
# CONTEXT_CLASS = KedroContext

# Class that manages the Data Catalog.
# from kedro.io import DataCatalog
# DATA_CATALOG_CLASS = DataCatalog
