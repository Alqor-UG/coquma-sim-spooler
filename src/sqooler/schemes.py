"""
The module that contains common logic for schemes, validation etc.
There is no obvious need, why this code should be touch in a new back-end.
"""

from collections.abc import Callable
from typing import Optional, Type, Any
from pydantic import ValidationError, BaseModel, Field

from icecream import ic


class ExperimentDict(BaseModel):
    """
    A class that defines the structure of the experiments.
    """

    header: dict = Field(description="Contains centralized information about the job.")
    shots: int = Field(description="number of shots in the experiment.")
    success: bool = Field(description="True if experiment ran successfully.")
    data: dict = Field(description="dictionary of results for the experiment.")


class StatusMsgDict(BaseModel):
    """
    A class that defines the structure of the status messages.
    """

    job_id: str = Field(description="unique execution id from the backend.")
    status: str = Field(description="status of job execution.")
    detail: str = Field(description="detailed status of job execution.")
    error_message: str = Field(description="error message of job execution.")


class ResultDict(BaseModel):
    """
    A class that defines the structure of results. It is closely related to the
    qiskit class qiskit.result.Result.
    """

    backend_name: Optional[str] = Field(
        default=None, description="The name of the backend"
    )
    display_name: str = Field(description="alternate name field for the backend")
    backend_version: str = Field(description="backend version, in the form X.Y.Z.")
    job_id: str = Field(description="unique execution id from the backend.")
    qobj_id: Optional[str] = Field(default=None, description="user-generated Qobj id.")
    success: bool = Field(description="True if complete input qobj executed correctly.")
    status: str = Field(description="status of job execution.")
    header: dict = Field(description="Contains centralized information about the job.")
    results: list[ExperimentDict] = Field(
        description="corresponding results for array of experiments of the input qobj"
    )


class DropboxLoginInformation(BaseModel):
    """
    The login information for the dropbox
    """

    app_key: str
    app_secret: str
    refresh_token: str


class MongodbLoginInformation(BaseModel):
    """
    The login information for MongoDB
    """

    mongodb_username: str
    mongodb_password: str
    mongodb_database_url: str


class LocalLoginInformation(BaseModel):
    """
    The login information for a local storage provider.
    """

    base_path: str = Field(
        description="The base path of the storage provider on your local file system."
    )


class BackendStatusSchemaOut(BaseModel):
    """
    The schema for the status of a backend. Follows the conventions of the
    `qiskit.providers.models.BackendStatus`.
    """

    backend_name: str = Field(description="The name of the backend")
    backend_version: str = Field(
        description="The version of the backend. Of the form X.Y.Z"
    )
    operational: bool = Field(description="True if the backend is operational")
    pending_jobs: int = Field(description="The number of pending jobs on the backend")
    status_msg: str = Field(description="The status message for the backend")


class BackendConfigSchemaIn(BaseModel):
    """
    The schema send in to detail the configuration of the backend.
    This is uploaded to the storage provider.
    """

    description: str = Field(description="A description for the backend")
    version: str = Field(description="The backend version in the form X.Y.Z")
    display_name: Optional[str] = Field(
        description=" Alternate name field for the backend"
    )
    cold_atom_type: str = Field(
        description="The type of cold atom system that is simulated. Non standard qiskit field."
    )
    gates: list = Field(
        description="The list of GateConfig objects for the basis gates of the backend"
    )
    max_experiments: int = Field(
        description="The maximum number of experiments per job"
    )
    max_shots: int = Field(
        description="The maximum number of shots allowed on the backend"
    )
    simulator: bool = Field(description="True if the backend is a simulator")
    supported_instructions: list[str] = Field(
        description="Instructions supported by the backend."
    )
    num_wires: int = Field(description="The number of qubits / wires for the backend")
    wire_order: str = Field(
        description="The wire order of the backend. Either linear or interleaved."
    )
    num_species: int = Field(description="The number of species in the system.")
    operational: bool = Field(description="True if the backend is operational")
    pending_jobs: Optional[int] = Field(
        default=None, description="The number of pending jobs on the backend"
    )
    status_msg: Optional[str] = Field(
        default=None, description="The status message for the backend"
    )


class BackendConfigSchemaOut(BaseModel):
    """
    The schema send out to detail the configuration of the backend. We follow the
    conventions of the qiskit configuration dictionary here.

    Will becomes compatible with qiskit.providers.models.BackendConfiguration
    """

    description: str = Field(description="A description for the backend")
    display_name: str = Field(description=" Alternate name field for the backend")
    conditional: bool = Field(
        default=False, description="True if the backend supports conditional operations"
    )
    coupling_map: str = Field(
        default="linear", description="The coupling map for the device"
    )
    dynamic_reprate_enabled: bool = Field(
        default=False,
        description="whether delay between programs can be set dynamically ",
    )
    local: bool = Field(
        default=False, description="True if the backend is local or False if remote"
    )
    memory: bool = Field(default=False, description="True if backend supports memory")
    open_pulse: bool = Field(default=False, description="True if backend is OpenPulse")
    backend_version: str = Field(description="The backend version in the form X.Y.Z")
    n_qubits: int = Field(description="The number of qubits / wires for the backend")
    backend_name: str = Field(description="The backend name")
    basis_gates: list[str] = Field(
        description="The list of strings for the basis gates of the backends"
    )
    max_experiments: int = Field(
        description="The maximum number of experiments per job"
    )
    max_shots: int = Field(
        description="The maximum number of shots allowed on the backend"
    )
    simulator: bool = Field(description="True if the backend is a simulator")
    gates: list = Field(
        description="The list of GateConfig objects for the basis gates of the backend"
    )
    supported_instructions: list[str] = Field(
        description="Instructions supported by the backend."
    )
    cold_atom_type: str = Field(
        description="The type of cold atom system that is simulated. Non standard qiskit field."
    )
    wire_order: str = Field(
        description=(
            "The wire order of the backend. Either linear or interleaved."
            " Non standard qiskit field."
        )
    )
    num_species: int = Field(
        description="The number of species in the system. Non standard qiskit field."
    )
    url: Optional[str] = Field(default=None, description="The url of the backend")


class GateDict(BaseModel):
    """
    The most basic class for a gate as it is communicated in
    the json API.
    """

    name: str = Field(description="The name of the gate")
    wires: list[int] = Field(description="The wires on which the gate acts")
    params: list[float] = Field(description="The parameters of the gate")


class GateInstruction(BaseModel):
    """
    The basic class for all the gate intructions of a backend.
    Any gate has to have the following attributes.
    """

    name: str
    parameters: str
    description: str
    coupling_map: list
    qasm_def: str = "{}"
    is_gate: bool = True

    @classmethod
    def config_dict(cls) -> dict:
        """
        Give back the properties of the instruction such as needed for the server.
        """
        return {
            "coupling_map": cls.model_fields["coupling_map"].default,
            "description": cls.model_fields["description"].default,
            "name": cls.model_fields["name"].default,
            "parameters": [cls.model_fields["parameters"].default],
            "qasm_def": cls.model_fields["qasm_def"].default,
        }


class Spooler:
    """
    The class for the spooler. So it is not just a scheme, but it also contains some common logic.
    So it should most likely live in another file at some point.

    Attributes:
        ins_schema_dict : A dictionary the contains all the allowed instructions for this spooler.
        device_config: A dictionary that some main config params for the experiment.
        n_wires: maximum number of wires for the spooler
        n_max_shots: the maximum number of shots for the spooler

    """

    def __init__(
        self,
        ins_schema_dict: dict,
        device_config: Type[BaseModel],
        n_wires: int,
        description: str = "",
        n_max_shots: int = 1000,
        version: str = "0.0.1",
        cold_atom_type: str = "spin",
        n_max_experiments: int = 15,
        wire_order: str = "interleaved",
        num_species: int = 1,
        operational: bool = True,
    ):
        """
        The constructor of the class.
        """
        self.ins_schema_dict = ins_schema_dict
        self.device_config = device_config
        self.n_max_shots = n_max_shots
        self.n_wires = n_wires
        self.description = description
        self.version = version
        self.cold_atom_type = cold_atom_type
        self.n_max_experiments = n_max_experiments
        self.wire_order = wire_order
        self.num_species = num_species
        self._display_name: str = ""
        self.operational = operational

    def check_experiment(self, exper_dict: dict) -> tuple[str, bool]:
        """
        Check the validity of the experiment.
        This has to be implement in each subclass extra.

        Args:
            exper_dict: The dictionary that contains the logic and should
                be verified.

        Returns:
            str: The error message
            bool: Is the experiment ok ?
        """
        try:
            self.device_config(**exper_dict)
            return "", True
        except ValidationError as err:
            return str(err), False

    def get_configuration(self) -> BackendConfigSchemaIn:
        """
        Sends back the configuration dictionary of the spooler.
        """
        gate_list = []
        for _, ins_obj in self.ins_schema_dict.items():
            if "is_gate" in ins_obj.model_fields:
                gate_list.append(ins_obj.config_dict())
        backend_config_dict = {
            "description": self.description,
            "version": self.version,
            "cold_atom_type": self.cold_atom_type,
            "gates": gate_list,
            "max_experiments": self.n_max_experiments,
            "max_shots": self.n_max_shots,
            "simulator": True,
            "supported_instructions": list(self.ins_schema_dict.keys()),
            "num_wires": self.n_wires,
            "wire_order": self.wire_order,
            "num_species": self.num_species,
            "operational": self.operational,
            "display_name": self.display_name,
        }
        return BackendConfigSchemaIn(**backend_config_dict)

    def check_instructions(self, ins_list: list) -> tuple[str, bool]:
        """
        Check all the instruction to make sure that they are valid and part
        of the allowed instructions.
        """
        err_code = ""
        exp_ok = False
        ic("start checking instructions")
        for ins in ins_list:
            ic(ins)
            try:
                gate_instr = gate_dict_from_list(ins)
                # see if the instruction is part of the allowed instructions
                if gate_instr.name not in self.ins_schema_dict.keys():
                    err_code = "Instruction not allowed."
                    exp_ok = False
                    return err_code, exp_ok

                # now verify that the parameters are ok
                gate_dict = gate_instr.model_dump()
                self.ins_schema_dict[gate_instr.name](**gate_dict)
                exp_ok = True
            except ValidationError as err:
                err_code = "Error in instruction " + str(err)
                exp_ok = False
            if not exp_ok:
                break
        ic(err_code, exp_ok)
        return err_code, exp_ok

    def check_dimension(self, json_dict: dict) -> tuple[str, bool]:
        """
        Make sure that the Hilbert space dimension is not too large.

        It can be implemented in the class that inherits, but it is not necessary.
        So this is only a placeholder.

        Args:
            json_dict: the dictonary with the instructions

        Returns:
            str: the error message
            bool: is the dimension ok ?
        """
        # pylint: disable=W0613
        return "", True

    def check_json_dict(self, json_dict: dict) -> tuple[str, bool]:
        """
        Check if the json file has the appropiate syntax.

        Args:
            json_dict (dict): the dictonary that we will test.

        Returns:
            bool: is the expression having the appropiate syntax ?
        """
        err_code = "No instructions received."
        exp_ok = False
        for expr in json_dict:
            ic(expr)
            err_code = "Wrong experiment name or too many experiments"
            # Fix this pylint issue whenever you have time, but be careful !
            # pylint: disable=W0702
            try:
                exp_ok = (
                    expr.startswith("experiment_")
                    and expr[11:].isdigit()
                    and (int(expr[11:]) <= self.n_max_experiments)
                )
            except:
                exp_ok = False
                break
            if not exp_ok:
                break
            # test the structure of the experiment
            ic("start checking experiment")
            err_code, exp_ok = self.check_experiment(json_dict[expr])
            ic(err_code)
            if not exp_ok:
                break
            ic("Check instructions")
            # time to check the structure of the instructions
            ins_list = json_dict[expr]["instructions"]
            err_code, exp_ok = self.check_instructions(ins_list)
            ic(err_code)
            ic(err_code, exp_ok)
            if not exp_ok:
                break
        return err_code.replace("\n", ".."), exp_ok

    @property
    def display_name(self) -> str:
        """
        The name of the spooler.
        """
        return self._display_name

    @display_name.setter
    def display_name(self, value: str) -> None:
        if isinstance(value, str):  # Check if the provided value is a string
            self._display_name = value
        else:
            raise ValueError("display_name must be a string")

    @property
    def gen_circuit(self) -> Callable[[dict], ExperimentDict]:
        """
        The function that generates the circuit.
        It can be basically anything that allows the execution of the circuit.
        """
        return self._gen_circuit

    @gen_circuit.setter
    def gen_circuit(self, value: Callable[[dict], ExperimentDict]) -> None:
        if callable(value):  # Check if the provided value is a callable (function)
            self._gen_circuit = value
        else:
            raise ValueError("gen_circuit must be a callable function")

    def add_job(
        self, json_dict: dict, status_msg_dict: StatusMsgDict
    ) -> tuple[ResultDict, StatusMsgDict]:
        """
        The function that translates the json with the instructions into some circuit and executes it.
        It performs several checks for the job to see if it is properly working.
        If things are fine the job gets added the list of things that should be executed.

        Args:
            json_dict: The job dictonary of all the instructions.
            status_msg_dict: the status dictionary of the job we are treating.

        Returns:
            result_dict: The dictionary with the results of the job.
            status_msg_dict: The status dictionary of the job.
        """
        job_id = status_msg_dict.job_id

        result_draft: dict = {
            "display_name": self.display_name,
            "backend_version": self.version,
            "job_id": job_id,
            "qobj_id": None,
            "success": True,
            "status": "finished",
            "header": {},
            "results": [],
        }
        err_msg, json_is_fine = self.check_json_dict(json_dict)
        ic(err_msg)
        if json_is_fine:
            # check_hilbert_space_dimension
            dim_err_msg, dim_ok = self.check_dimension(json_dict)
            if dim_ok:
                for exp in json_dict:
                    exp_dict = {exp: json_dict[exp]}
                    # Here we
                    result_draft["results"].append(self.gen_circuit(exp_dict))

                status_msg_dict.detail += "; Passed json sanity check; Compilation done. \
                    Shots sent to solver."
                status_msg_dict.status = "DONE"
                result_dict = ResultDict(**result_draft)
                return result_dict, status_msg_dict

            status_msg_dict.detail += (
                "; Failed dimensionality test. Too many atoms. File will be deleted. Error message : "
                + dim_err_msg
            )
            status_msg_dict.error_message += (
                "; Failed dimensionality test. Too many atoms. File will be deleted. Error message :  "
                + dim_err_msg
            )
            status_msg_dict.status = "ERROR"
            result_dict = ResultDict(**result_draft)
            return result_dict, status_msg_dict
        else:
            status_msg_dict.detail += (
                "; Failed json sanity check. File will be deleted. Error message : "
                + err_msg
            )
            status_msg_dict.error_message += (
                "; Failed json sanity check. File will be deleted. Error message : "
                + err_msg
            )
            status_msg_dict.status = "ERROR"

        result_dict = ResultDict(**result_draft)
        return result_dict, status_msg_dict


class LabscriptSpooler(Spooler):
    """
    A specialized spooler class that allows us to execute jobs in labscript directly.
    The main changes are that we need to add the job in a different way and connect it to a
     `runmanager.remoeClient`
    """

    def __init__(
        self,
        ins_schema_dict: dict,
        device_config: Type[BaseModel],
        n_wires: int,
        remote_client: Any,  # it would be really nice to fix this type
        description: str = "",
        n_max_shots: int = 1000,
        version: str = "0.0.1",
        cold_atom_type: str = "spin",
        n_max_experiments: int = 15,
        wire_order: str = "interleaved",
        num_species: int = 1,
        operational: bool = True,
    ):
        """
        The constructor of the class.
        """
        self.ins_schema_dict = ins_schema_dict
        self.device_config = device_config
        self.n_max_shots = n_max_shots
        self.remote_client = remote_client
        self.n_wires = n_wires
        self.description = description
        self.version = version
        self.cold_atom_type = cold_atom_type
        self.n_max_experiments = n_max_experiments
        self.wire_order = wire_order
        self.num_species = num_species
        self._display_name: str = ""
        self.operational = operational

    def add_job(
        self, json_dict: dict, status_msg_dict: StatusMsgDict
    ) -> tuple[ResultDict, StatusMsgDict]:
        """
        The function that translates the json with the instructions into some circuit
        and executes it. It performs several checks for the job to see if it is properly
        working. If things are fine the job gets added the list of things that should be
        executed.

        Args:
            json_dict: The job dictonary of all the instructions.
            status_msg_dict: the status dictionary of the job we are treating.
        """
        job_id = status_msg_dict.job_id

        result_draft: dict = {
            "display_name": self.display_name,
            "backend_version": self.version,
            "job_id": job_id,
            "qobj_id": None,
            "success": True,
            "status": "finished",
            "header": {},
            "results": [],
        }
        err_msg, json_is_fine = self.check_json_dict(json_dict)
        if json_is_fine:
            # check_hilbert_space_dimension
            dim_err_msg, dim_ok = self.check_dimension(json_dict)
            if dim_ok:
                ic("Passed dimensionality test")
                for exp in json_dict:
                    exp_dict = {exp: json_dict[exp]}
                    # prepare the shots folder
                    self.remote_client.reset_shot_output_folder()
                    self._modify_shot_output_folder(job_id + "/" + str(exp))

                    # Here we generate the ciruit
                    result_draft["results"].append(self.gen_circuit(exp_dict, job_id))

                status_msg_dict.detail += "; Passed json sanity check; Compilation done. \
                    Shots sent to solver."
                status_msg_dict.status = "DONE"
                result_dict = ResultDict(**result_draft)
                return result_dict, status_msg_dict

            status_msg_dict.detail += (
                ";Failed dimensionality test. Too many atoms. File will be deleted. Error message: "
                + dim_err_msg
            )
            status_msg_dict.error_message += (
                ";Failed dimensionality test. Too many atoms. File will be deleted. Error message: "
                + dim_err_msg
            )
            status_msg_dict.status = "ERROR"

            result_dict = ResultDict(**result_draft)
            return result_dict, status_msg_dict

        status_msg_dict.detail += (
            "; Failed json sanity check. File will be deleted. Error message : "
            + err_msg
        )
        status_msg_dict.error_message += (
            "; Failed json sanity check. File will be deleted. Error message : "
            + err_msg
        )
        status_msg_dict.status = "ERROR"

        result_dict = ResultDict(**result_draft)
        return result_dict, status_msg_dict

    def _modify_shot_output_folder(self, new_dir: str) -> None:
        """
        I am not sure what this function does.

        Args:
            new_dir: The new directory under which we save the shots.
        """
        defaut_shot_folder = str(self.remote_client.get_shot_output_folder())
        print(f"Default shot folder: {defaut_shot_folder}")
        modified_shot_folder = (defaut_shot_folder.rsplit("\\", 1)[0]) + "/" + new_dir
        print(f"Modified shot folder: {modified_shot_folder}")
        self.remote_client.set_shot_output_folder(modified_shot_folder)


def gate_dict_from_list(inst_list: list) -> GateDict:
    """
    Transforms a list into an appropiate dictionnary for instructions. The list
    is assumed to be in the format [name, wires, params].

    Args:
        inst_list: The list that should be transformed.

    Returns:
        A GateDict object.
    """
    gate_draft = {"name": inst_list[0], "wires": inst_list[1], "params": inst_list[2]}
    return GateDict(**gate_draft)
