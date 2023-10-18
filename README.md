# Spaceflights

## Overview

This is your new Kedro project for the [spaceflights tutorial](https://kedro.readthedocs.io/en/stable/tutorial/spaceflights_tutorial.html), which was generated using `Kedro 0.18.13`.

Take a look at the [Kedro documentation](https://kedro.readthedocs.io) to get started.

This is an example of using `kedro` and `kedro-airflow` plugins together to generate dags out of pipelines that can run on GCP Composer. 

## Main additions/changes relative to spaceflights starter 

The main artifacts/changes here are:

- `templates/gke_operator.py` - this is the template for the `kedro-airflow` to generate a DAG using `GKEStartPodOperator`. All the magic of this example is defined there.
- `conf/base/airlow.yml` - this is the configuration file for the `kedro-airflow` plugin. It defines the `airflow` specific configuration and provides the key values for jinja to fill in the dag template. It is loaded by ConfigLoader, so templating works there as well.
- `conf/base/catalog.yml` - this is the catalog configuration file. It required to define all inputs and outputs for the node 1-1 mapping scenario, as all node are executed on separate nodes then. There's also MLflow integration and registering the model as an artifact. I also added `airflow_xcom` export to GKE specific path of mount point to communicate MLflow run id to other nodes.
- `conf/cloud/mlflow.yml` - the setup of MLflow tracking server. It is used by `kedro-mlflow` plugin to connect to our MLflow server.
- `src/spaceflights/pipelines/airflow_xcom` - simple pipeline to retrieve or start MLflow run id and then export it using Airflow xcom mechanism. This node is treated specially in the template to exclude it from the pipeline and 
- `src/spaceflights/auth.py` - special class that uses `kedro-mlflow` class template as request header provider to authenticate with GCP. Its service account should be the same as the one bound to workload identity k8s service account (in `airflow.yml`).
- `airflow_dags` - where dags get generated.
- `src/spaceflights/pipeline_registry.py` - addition of tags verification code
- `src/spaceflights/airflow_utils` - utility module for the DAG template

Additional features:
- grouping nodes for execution within the same process/pod using tags with special prefix (here: `airflow:`)
- assigning k8s machine specification (memory/cpu requests/limits) for nodes based on special tags (starting with `machine:`)

## Quickstart

To comment shortly about required environment setup for Airflow Composer and describe usage of the plugin.

### Setup

I am skipping setup here and requirements install. You can find that below in "how to install dependencies" section. On the GCP side you need to create Composer environment and configure it to use GKE cluster. You can find the details here: https://cloud.google.com/composer/docs/how-to/managing/creating#composer_create_cluster-python. In our setup you also need to configure workload identity for the cluster to be able to access MLflow server. Workload identity by default is already enabled so follow from there: https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#authenticating_to 

In this example I added k8s service account `airflow-ml-jobs` and the same namespace and bound it to gke compute default service account. I've made a separate service account for composer and made sure that it can access MLflow by adding it to `data-scientists` group within our platform's terraform: https://gitlab.com/getindata/ml-ops/ml-ops-infrastructure/-/merge_requests/4

Additionally you might want to add more dependencies for Airflow Composer environment, like `mlflow`. You can do it [on many ways](https://cloud.google.com/composer/docs/how-to/using/installing-python-dependencies). For example like this from `requirements.txt`:

```bash
gcloud composer environments update ENVIRONMENT_NAME --location LOCATION --update-pypi-packages-from-file requirements.txt
```

This is different `requirements.txt` than the one in the Kedro project. They are dependencies that our jinja template uses. For reference, we could use the following dependencies here:

```
apache-airflow[google,kubernetes]
kubernetes
mlflow
```

All but `mlflow` should be already present there.

### Quickstart

Update `conf/cloud/catalog_globals.yml` with bucket name to store intermediate data. For demo purpose we re-use the same bucket as was created for dags storage. You can find the bucket name with commands below. **Disclaimer**: here we keep all catalog entries for all intermediate steps, however should we want to only upkeep nodes in grouped versions, we can delete entries that would be necessary to communicate between them, as MemoryDataSet can be used in this scenario. 

First, you need to build & upload docker image of this, for example (you need to point to your own docker image registry):
```bash
kedro docker build && docker tag spaceflights-airflow europe-west1-docker.pkg.dev/gid-labs-mlops-sandbox/images/spaceflights-airflow:latest && docker push europe-west1-docker.pkg.dev/gid-labs-mlops-sandbox/images/spaceflights-airflow
```

Then generate the DAG:
```bash
kedro airflow create -j ./templates/gke_operator.pytpl --env cloud
```

Then we need to upload the DAG to Composer's bucket. You can do that either through UI or CLI. When using CLI you can use the steps below. List composer environments in given location:
```bash
LOCATION=europe-west1; gcloud composer environments list --locations $LOCATION
```

Figure out which bucket is your dag bucket, fill `COMPOSER_ENV` from last step:
```bash
COMPOSER_ENV="test-environment"; export DAGS_PATH=$(gcloud composer environments describe $COMPOSER_ENV --location $LOCATION --format "value(config.dagGcsPrefix)")
```
Then copy the DAG from `airflow_dags` to your dag bucket. Also include DAG's local dependencies which is utils module.

```bash
gcloud storage cp airflow_dags/spaceflights_dag.py $DAGS_PATH
gcloud storage cp -r src/spaceflights/airflow_utils $DAGS_PATH/airflow_utils
```

Lastly, you can trigger the DAG from Airflow UI. You can find the DAG name in the file name of the dag file. You can also trigger it from CLI or define triggering schedule in params.


## Rules and guidelines - continuation of Spaceflights Readme

In order to get the best out of the template:

* Don't remove any lines from the `.gitignore` file we provide
* Make sure your results can be reproduced by following a [data engineering convention](https://kedro.readthedocs.io/en/stable/faq/faq.html#what-is-data-engineering-convention)
* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to install dependencies

Declare any dependencies in `src/requirements.txt` for `pip` installation and `src/environment.yml` for `conda` installation.

To install them, run:

```
pip install -r src/requirements.txt
```

## How to run your Kedro pipeline

You can run your Kedro project with:

```
kedro run
```

## How to test your Kedro project

Have a look at the file `src/tests/test_run.py` for instructions on how to write your tests. You can run your tests as follows:

```
kedro test
```

To configure the coverage threshold, go to the `.coveragerc` file.

## Project dependencies

To generate or update the dependency requirements for your project:

```
kedro build-reqs
```

This will `pip-compile` the contents of `src/requirements.txt` into a new file `src/requirements.lock`. You can see the output of the resolution by opening `src/requirements.lock`.

After this, if you'd like to update your project requirements, please update `src/requirements.txt` and re-run `kedro build-reqs`.


## How to work with Kedro and notebooks

> Note: Using `kedro jupyter` or `kedro ipython` to run your notebook provides these variables in scope: `catalog`, `context`, `pipelines` and `session`.
>
> Jupyter, JupyterLab, and IPython are already included in the project requirements by default, so once you have run `pip install -r src/requirements.txt` you will not need to take any extra steps before you use them.

### Jupyter
To use Jupyter notebooks in your Kedro project, you need to install Jupyter:

```
pip install jupyter
```

After installing Jupyter, you can start a local notebook server:

```
kedro jupyter notebook
```

### JupyterLab
To use JupyterLab, you need to install it:

```
pip install jupyterlab
```

You can also start JupyterLab:

```
kedro jupyter lab
```

### IPython
And if you want to run an IPython session:

```
kedro ipython
```

### How to convert notebook cells to nodes in a Kedro project
You can move notebook code over into a Kedro project structure using a mixture of [cell tagging](https://jupyter-notebook.readthedocs.io/en/stable/changelog.html#cell-tags) and Kedro CLI commands.

By adding the `node` tag to a cell and running the command below, the cell's source code will be copied over to a Python file within `src/<package_name>/nodes/`:

```
kedro jupyter convert <filepath_to_my_notebook>
```
> *Note:* The name of the Python file matches the name of the original notebook.

Alternatively, you may want to transform all your notebooks in one go. Run the following command to convert all notebook files found in the project root directory and under any of its sub-folders:

```
kedro jupyter convert --all
```

### How to ignore notebook output cells in `git`
To automatically strip out all output cell contents before committing to `git`, you can run `kedro activate-nbstripout`. This will add a hook in `.git/config` which will run `nbstripout` before anything is committed to `git`.

> *Note:* Your output cells will be retained locally.


