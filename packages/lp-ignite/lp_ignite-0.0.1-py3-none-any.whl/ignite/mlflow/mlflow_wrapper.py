from typing import Any, Dict, Mapping, Sequence, Union

try:
    import mlflow
    from mlflow.entities import Param
    from mlflow.exceptions import MlflowException
    from mlflow.tracking import MlflowClient
except ImportError:
    mlflow = None


class MLFlowLogger():
     """
     
     MLflow <https://mlflow.org>_ tracking client handler to log parameters and metrics during the training
     and validation.

     Args:
          experiment_name (str): MLflow experiment name
          tracking_uri (str): MLflow tracking uri. See MLflow docs for more details

     """
     def __init__(
          self, experiment_name: str, tracking_uri: Union[str, None] = None
     ) -> None:
          super().__init__()

          try:
               import mlflow
          except ImportError:
               raise RuntimeError(
                    "This contrib module requires mlflow to be installed. "
                    "Please install it with command: \n pip install mlflow"
               )

          self.tracking = tracking_uri
          self.ml_flow_client = MlflowClient(tracking_uri=self.tracking)
          self.experiment_name = experiment_name
          self._handle_experiment_id(experiment_name)
          self.run_id = self.ml_flow_client.create_run(experiment_id=self.experiment_id).info.run_id

          self._status = "FAILED"  # Base case is a failure.

     def log_params(self, params: Dict[str, Any]) -> None:
          """
          Log a batch of params for the current run. If no run is active, this method will create a
          new active run.
          Args:
               Dictionary of param_name: String -> value: (String, but will be string-ified if
                    not)
          Returns:
               None
          """
          params_arr = [Param(key, str(value)) for key, value in params.items()]
          self.ml_flow_client.log_batch(run_id=self.run_id, metrics=[], params=params_arr, tags=[])

     def log_param(self, param_name: str, value: Union[str, float]) -> None:
          """
          Log the value of a parameter into the experiment.
          Args:
               param_name (str): The name of the parameter.
               value (Union[str, float]): The value of the parameter.
          """
          self.ml_flow_client.log_param(run_id=self.run_id, key=param_name, value=value)

     def log_config_params(self, config_params: Mapping) -> None:
          """
          Args:
               config_params (Mapping):
               The config parameters of the training to log, 
               such as number of epoch, loss function, optimizer etc.
          """
          for param_name, element in config_params.items():
               self._log_config_write(param_name, element)

     def artifact_location(self) -> str:
          """Create the experiment if it does not exist to get the artifact location.
          Returns:
               The artifact location.
          """
          expt = self.ml_flow_client.get_experiment_by_name(self.experiment_name)
          return expt.artifact_location

     def set_tag(self, key: str, value: Any) -> None:
          """
          Set a tag on the run with the specified ID
          Args:
               key: Tag name (string).
               value: Tag value (string, but will be string-ified if not).
          """
          return self.ml_flow_client.set_tag(self.run_id, key, value)

     def log_artifact(self, src_file_path: str) -> None:
          """
          Log the artifact into the experiment.
          Args:
               src_file_path (str): The name of the path.
          """
          return self.ml_flow_client.log_artifact(src_file_path)

     def log_metric(self, metric_name: str, value: float, step: Union[int, None] = None) -> None:
          """
          Log the value of a metric into the experiment.
          Args:
               metric_name (str): The name of the metric.
               value (float): The value of the metric.
               step (Union[int, None]): The step when the metric was computed (Default = None).
          """
          self.ml_flow_client.log_metric(run_id=self.run_id, key=metric_name, value=value, step=step)

     def _log_config_write(self, parent_name: str, element: Union[int, float, str, Mapping, Sequence]) -> None:
          """
          Log the config parameters when it's a mapping or a sequence of elements.
          """
          if isinstance(element, Mapping):
               for key, value in element.items():
                    # We recursively open the element (Dict format type).
                    self._log_config_write(f"{parent_name}.{key}", value)
          elif isinstance(element, Sequence) and not isinstance(element, str):
               # Since str are sequence we negate it to be logged in the else.
               for idx, value in enumerate(element):
                    self._log_config_write(f"{parent_name}.{idx}", value)
          else:
               self.log_param(parent_name, element)

     def _status_handling(self):
          # We set_terminated the run to get the finishing status (FINISHED or FAILED)
          self.ml_flow_client.set_terminated(self.run_id, status=self._status)

     def _handle_experiment_id(self, experiment_name):
          """
          Handle the existing experiment name to grab the id and append a new experiment to it.
          """
          try:
               self.experiment_id = self.ml_flow_client.create_experiment(experiment_name, self.tracking)
          except MlflowException:
               self.experiment_id = self.ml_flow_client.get_experiment_by_name(experiment_name).experiment_id

     def get_best_score(self, metric_name):
          """
          Get the best score for a given metric
          """
          active_run_id = mlflow.active_run().info.run_id
          return self.ml_flow_client.best_score(active_run_id, metric_name)
