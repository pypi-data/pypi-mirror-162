import io
import json
import math
import time

import control
import numpy as np
import pandas as pd

from pycollimator.api import Api
from pycollimator.diagrams import Block
from pycollimator.error import NotFoundError
from pycollimator.i18n import N
from pycollimator.log import Log
from pycollimator.models import Model, ModelParameters, load_model
from pycollimator.simulation_hashed_file import SimulationHashedFile
from pycollimator.utils import is_uuid


class LinearizationResult:
    def __init__(self, A, B, C, D):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def to_state_space(self):
        """
        convert the linearization result to a python control object
        """
        return control.StateSpace(self.A, self.B, self.C, self.D)

    def __repr__(self):
        def tostring(x):
            return np.array2string(x, separator=",").replace("\n", "").replace(" ", "")

        return (
            f"<{self.__class__.__name__} A={tostring(self.A)} B={tostring(self.B)} "
            + f"C={tostring(self.C)} D={tostring(self.D)}>"
        )

    @classmethod
    def _from_csv(cls, csv_text):
        a_mat, b_mat, c_mat, d_mat = cls.__reshape_results_linearization(csv_text)
        return cls(a_mat, b_mat, c_mat, d_mat)

    # FIXME this format is not very robust
    @classmethod
    def __reshape_results_linearization(csv, results_text):
        read_st = -1
        lines = results_text.splitlines()
        for each in lines:
            if read_st == -1:
                if each[:3] == "dim":
                    # do the processing common for all matrices to get their dimensions
                    line_data = each.split(",")
                    mat_name = line_data[1]
                    tmp_dim = np.fromiter((float(x) for x in line_data[2:4]), dtype=int)
                    read_st = 0
                    if mat_name == "A":
                        a_dims = tmp_dim.copy()
                    elif mat_name == "B":
                        b_dims = tmp_dim.copy()
                    elif mat_name == "C":
                        c_dims = tmp_dim.copy()
                    elif mat_name == "D":
                        d_dims = tmp_dim.copy()
                    else:
                        print("unrecognized matrix name")
            else:
                # do the processing common for all matrices tobget their data
                line_data = each.split(",")
                line_data = line_data[:-1]
                # print(line_data)
                tmp = np.fromiter((float(x) for x in line_data), dtype=float)
                read_st = -1
                if mat_name == "A":
                    a_mat = np.reshape(tmp, a_dims)
                elif mat_name == "B":
                    b_mat = np.reshape(tmp, b_dims)
                elif mat_name == "C":
                    c_mat = np.reshape(tmp, c_dims)
                elif mat_name == "D":
                    d_mat = np.reshape(tmp, d_dims)
                else:
                    print("unrecognized matrix name")
        # get column names instead of uuids.
        return a_mat, b_mat, c_mat, d_mat


class SimulationResults:
    def __init__(self, stream, model: Model):
        if isinstance(stream, str):
            stream = io.StringIO(stream)
        self._raw_df = pd.read_csv(stream)
        self._model = model

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} {len(self.to_pandas().index)} rows x {len(self.to_pandas().columns)} columns>"
        )

    def __getitem__(self, item):
        if item == "time":
            return self._raw_df["time"]  # pylint: disable=unsubscriptable-object
        if is_uuid(item):
            blk = self._model.find_block(uuid=item)
        elif isinstance(item, Block):
            blk = self._model.find_block(uuid=item.uuid)
        else:
            try:
                blk = self._model.find_block(name=item, case=True)
            except NotFoundError:
                try:
                    blk = self._model.find_block(name=item, case=False)
                except NotFoundError:
                    blk = self._model.find_block(item)
        df = self.to_pandas(uuid=blk.uuid)
        return df

    def to_pandas(self, pattern=None, name=None, uuid=None, type=None, case=False) -> pd.DataFrame:
        if is_uuid(pattern):
            uuid = pattern
            pattern = None

        blocks = self._model.find_blocks(pattern=pattern, name=name, uuid=uuid, type=type, case=case)

        cols_by_uuid = []
        for block in blocks:
            for col in self._raw_df.columns:  # type: str
                if col.startswith(block.uuid):
                    cols_by_uuid.append(col)

        cols_by_path = []
        for col in cols_by_uuid:
            path = self._model.get_block_path(col.split("[")[0])
            idx = col.split("[")[1].split("]")[0]
            if path is not None:
                if idx == "0":
                    cols_by_path.append(path)
                else:
                    cols_by_path.append(f"{path}[{idx}]")

        df = self._raw_df[cols_by_uuid]  # pylint: disable=unsubscriptable-object
        df.columns = cols_by_path
        df.index = self._raw_df["time"]  # pylint: disable=unsubscriptable-object
        df.index.name = "time"
        return df

    @property
    def columns(self) -> list:
        pd_columns = self.to_pandas().columns.tolist()
        cols = []
        for col in pd_columns:
            uuid = col.split("[")[0]
            block = is_uuid(uuid) and self._model.find_block(uuid=uuid) or None
            if block is not None:
                cols.append(block.path)
            else:
                cols.append(col)
        return cols


class SimulationLogLine:
    def __init__(self, data):
        self._data = data
        self._str: str = ""
        self._parse(data)

    def __str__(self) -> str:
        return self._str

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._data}>"

    def _parse(self, data):
        try:
            js_data = data
            if isinstance(data, str):
                js_data = json.loads(data)
            ts = ""
            if js_data.get("timestamp") is not None:
                ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(js_data["timestamp"])) + " "
            parsed_line = f"{ts}{js_data.get('level')} {js_data.get('message')}"
            for k, v in js_data.items():
                if k not in ["timestamp", "level", "message"]:
                    parsed_line += f" {k}={v}"
            self._str = parsed_line
        except Exception as e:
            Log.trace(f"Failed to parse log line: {e}")
            self._str = str(data)


class Simulation:
    def __init__(self, data: dict, model: Model):
        self.model = model
        self._data = data
        self._logs: list[SimulationLogLine] = None
        self._results: pd.DataFrame = None

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self) -> str:
        if Log.is_level_above("DEBUG"):
            return f"<{self.__class__.__name__} status='{self.status}' uuid='{self.uuid}'>"
        return f"<{self.__class__.__name__} status='{self.status}'>"

    @property
    def uuid(self) -> str:
        return self._data["uuid"]

    @property
    def status(self) -> str:
        return self._data["status"]

    @property
    def model_uuid(self) -> str:
        return self._data["model_uuid"]

    @property
    def results_available(self) -> bool:
        return self._data.get("results_available") is True

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"

    @property
    def is_running(self) -> bool:
        return self.status != "created" and not self.is_failed and not self.is_completed

    @property
    def is_started(self) -> bool:
        return self.status != "created"

    @property
    def logs(self) -> list[SimulationLogLine]:
        if self._logs is None:
            logs = Api.simulation_logs(self.model_uuid, self.uuid)
            self._logs = [SimulationLogLine(s) for s in str(logs).splitlines()]
        return self._logs

    @property
    def compilation_logs(self) -> SimulationLogLine:
        logs = self._data.get("compilation_logs")
        if logs is None:
            return None
        if isinstance(logs, list):
            return SimulationLogLine(logs[0])
        return SimulationLogLine(logs)

    def show_logs(self) -> None:
        # It would be awesome to use markdown to pretty-print these logs
        if self.is_failed:
            print(self.compilation_logs)
            return
        for log_line in self.logs:
            print(log_line)

    @property
    def results(self) -> SimulationResults:
        if not self.results_available:
            Log.warning("Simulation results may not be available yet:", self)
            # But we will try downloading them anyway since that's what the user asked for
        results = Api.simulation_results(self.model_uuid, self.uuid)
        return SimulationResults(results, self.model)

    def get_results(self, wait=True) -> SimulationResults:
        if wait:
            self.wait()
        return self.results

    def update(self):
        Log.trace("Updating simulation:", self)
        self._data = Api.simulation_get(self.model_uuid, self.uuid)
        return self

    def start(self):
        Log.debug("Starting simulation:", self)
        self._data = Api.simulation_start(self.model_uuid, self.uuid)

    def wait(self):
        if self.is_completed:
            return

        if not self.is_started:
            Log.debug("Simulation not started:", self)
            self.start()

        start_ts = time.time()
        while self.is_running:
            Log.debug(f"Waiting for simulation {math.trunc(time.time() - start_ts)}s:", self)
            self.update()
            if self.status == "completed":
                break
            time.sleep(1)
        Log.debug("Simulation completed:", self)

    def to_pandas(self, wait=True):
        return self.get_results(wait=wait).to_pandas()

    def _upload_hashed_files(self, model, simulation):
        parameter_overrides = []
        blocks = model._get_blocks_with_data()
        for block_uuid in blocks:
            input_data = blocks[block_uuid]
            sdf = SimulationHashedFile(input_data)
            resp = sdf.upload(model.uuid, simulation.uuid)
            Log.trace(f"Uploaded hashed file for block '{block_uuid}':", resp)
            parameter_overrides.append(
                {
                    "expression": f'__hashed_file("{sdf.hash}", "{sdf.content_type}")',
                    "block_uuid": block_uuid,
                    "parameter_name": "file_name",
                }
            )
        Log.trace("Parameter overrides:", parameter_overrides)
        return parameter_overrides


def _run_simulation_common(model, linearization, parameters, wait, no_sync, ignore_cache) -> Simulation:
    Log.trace("run_simulation:", model.__repr__())
    if not isinstance(model, Model):
        model = load_model(model)

    if not no_sync:
        model.sync()

    if linearization is not None:
        if is_uuid(linearization):
            linearization = {"submodel_uuid": linearization}
        elif isinstance(linearization, Block):
            linearization = {"submodel_uuid": linearization.uuid}
        else:
            raise ValueError(N("Invalid argument 'linearization'"))

    # Prepare DataSource files
    hashed_files = model._get_hashed_files()
    overrides = [
        {
            "expression": f'__hashed_file("{hashed_file.hash}", "{hashed_file.content_type}")',
            "block_uuid": block_uuid,
            "parameter_name": "file_name",
        }
        for block_uuid, hashed_file in hashed_files.items()
    ]

    # Send simulation specific parameters
    parameters = {
        **model.parameters.to_api_data(),
        **(ModelParameters(parameters or {}).to_api_data()),
    }

    sim_request = {
        "version": model.version,
        "no_start": True,
        "overrides": overrides,
        "parameters": parameters,
        "ignore_cache": ignore_cache,
    }

    if linearization is not None:
        sim_request["linearization"] = linearization

    sim = Simulation(Api.simulation_create(model.uuid, sim_request), model)

    if sim.status == "created":
        # Upload DataSource files
        parameter_overrides = sim._upload_hashed_files(model, sim)
        if len(parameter_overrides) > 0:
            body = {"overrides": parameter_overrides}
            sim._data = Api.simulation_parameters_set(model.uuid, sim.uuid, body)
        sim.start()

    if wait:
        sim.wait()

    if sim.is_failed:
        Log.error(N("Simulation failed! Use .show_logs() to see the logs."))

    return sim


def run_simulation(model, parameters: dict = None, wait=True, no_sync=False, ignore_cache=False) -> Simulation:
    """
    Run a simulation on the given model.
    """
    return _run_simulation_common(model, None, parameters, wait, no_sync, ignore_cache)


def linearize(model, submodel, parameters: dict = None, no_sync=False, ignore_cache=False):
    """
    Linearize the submodel within a model.
    """
    if not isinstance(model, Model):
        model = load_model(model)

    if not isinstance(submodel, Block):
        submodel = model.find_block(submodel)

    sim = _run_simulation_common(model, submodel, parameters, True, no_sync, ignore_cache)

    if not sim.is_completed:
        Log.error(N("Simulation could not complete!"))
        sim.show_logs()
        return sim

    lin_results_csv = Api.linearization_results_csv(model.uuid, sim.uuid)
    res = LinearizationResult._from_csv(lin_results_csv)
    return res
