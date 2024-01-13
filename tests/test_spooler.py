"""
Here we test the spooler class and its functions.
"""

from typing import Literal, Optional
from pydantic import ValidationError, BaseModel, Field

from typing_extensions import Annotated
import pytest

from sqooler.schemes import Spooler, StatusMsgDict, gate_dict_from_list


class TestExperiment(BaseModel):
    """
    The class that defines some basic properties for a test experiment
    """

    wire_order: Literal["interleaved", "sequential"] = "sequential"

    # mypy keeps throwing errors here because it does not understand the type.
    # not sure how to fix it, so we leave it as is for the moment
    # HINT: Annotated does not work
    shots: Annotated[int, Field(gt=0, le=5)]
    num_wires: Annotated[int, Field(ge=1, le=5)]
    instructions: list[list]
    seed: Optional[int] = None


def test_spooler_config() -> None:
    """
    Test that it is possible to get the config of the spooler.
    """
    test_spooler = Spooler(ins_schema_dict={}, device_config=TestExperiment, n_wires=2)

    spooler_config = test_spooler.get_configuration()
    assert spooler_config.num_wires == 2
    assert spooler_config.operational


def test_spooler_operational() -> None:
    """
    Test that it is possible to set the operational status of the spooler.
    """
    test_spooler = Spooler(
        ins_schema_dict={}, device_config=TestExperiment, n_wires=2, operational=False
    )

    spooler_config = test_spooler.get_configuration()
    assert spooler_config.num_wires == 2
    assert not spooler_config.operational


def test_spooler_add_job() -> None:
    """
    Test that it is possible to add a job to the spooler.
    """

    test_spooler = Spooler(
        ins_schema_dict={}, device_config=TestExperiment, n_wires=2, operational=False
    )
    status_msg_draft = {
        "job_id": "Test_ID",
        "status": "None",
        "detail": "None",
        "error_message": "None",
    }

    job_payload = {
        "experiment_0": {
            "instructions": [],
            "num_wires": 2,
            "shots": 4,
            "wire_order": "interleaved",
        },
    }
    status_msg_dict = StatusMsgDict(**status_msg_draft)
    result_dict, status_msg_dict = test_spooler.add_job(job_payload, status_msg_dict)
    assert result_dict is not None


def test_gate_dict() -> None:
    """
    Test that it is possible to create the a nice instruction.
    """
    inst_list = ["test", [1, 2], [0.1, 0.2]]
    gate_dict = gate_dict_from_list(inst_list)
    assert gate_dict.name == "test"

    # test that it fails if the list is too short
    inst_list = ["test", [1, 2]]
    with pytest.raises(IndexError):
        gate_dict_from_list(inst_list)

    # test that it fails if the types doe not work out
    inst_list = ["test", [1, 2], "test"]
    with pytest.raises(ValidationError):
        gate_dict_from_list(inst_list)


def test_spooler_instructions() -> None:
    """
    Test that it is possible to verify the validity of the instructions.
    """
    test_spooler = Spooler(
        ins_schema_dict={}, device_config=TestExperiment, n_wires=2, operational=False
    )

    # test that it works if the instructions are not valid as the key is not known
    inst_list = [["test", [1, 2], [0.1, 0.2]]]
    err_code, exp_ok = test_spooler.check_instructions(inst_list)
    assert exp_ok is not True
    assert err_code == "Instruction not allowed."

    # test that it works if the instructions are not valid
