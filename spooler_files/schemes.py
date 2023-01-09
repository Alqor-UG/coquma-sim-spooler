"""
The module that contains common logic for schemes, validation etc.
There is no obvious need, why this code should be touch in a new back-end.
"""

from typing import Tuple, TypedDict, List

from pydantic import BaseModel

from jsonschema import validate
from jsonschema.exceptions import ValidationError


class ExperimentScheme(BaseModel):
    """
    The schema for the experiments, which is used for validation.
    TODO: Make the difference with ExperimentDict clear.
    """

    required: List[str]
    properties: dict
    type: str = "object"
    additionalProperties: bool = False


class InstructionScheme(BaseModel):
    """
    The schema for the instructions
    """

    items: list
    type: str = "array"
    minItems: int = 3
    maxItems: int = 3


class ExperimentDict(TypedDict):
    """
    A class that defines the structure of the experiments.
    """

    header: dict
    shots: int
    success: bool
    data: dict


class Spooler:
    """
    The class for the spooler. So it is not just a scheme, but it also contains some common logic.
    So it should most likely live in another file at some point.

    Attributes:
        exper_schema: The schema of allowed experimental inputs.
        ins_schema_dict : A dictionary the contains all the allowed instructions for this spooler.

    Args:
        exper_schema: Sets the `exper_schema` attribute of the class
        ins_schema_dict : Sets the `ins_schema_dict` attribute of the class
    """

    def __init__(self, exper_schema: ExperimentScheme, ins_schema_dict: dict):
        """
        The constructor of the class.
        """
        self.exper_schema = exper_schema
        self.ins_schema_dict = ins_schema_dict

    def check_json_dict(self, json_dict: dict) -> Tuple[str, bool]:
        """
        Check if the json file has the appropiate syntax.

        Args:
            json_dict (dict): the dictonary that we will test.

        Returns:
            bool: is the expression having the appropiate syntax ?
        """

        max_exps = 50
        for expr in json_dict:
            err_code = "Wrong experiment name or too many experiments"
            # Fix this pylint issue whenever you have time, but be careful !
            # pylint: disable=W0702
            try:
                exp_ok = (
                    expr.startswith("experiment_")
                    and expr[11:].isdigit()
                    and (int(expr[11:]) <= max_exps)
                )
            except:
                exp_ok = False
                break
            if not exp_ok:
                break
            # TODO: get rid of this weird type cast as this should be really already handled
            # through pydantic by now
            err_code, exp_ok = check_with_schema(
                json_dict[expr], dict(self.exper_schema)
            )
            if not exp_ok:
                break
            ins_list = json_dict[expr]["instructions"]
            for ins in ins_list:
                # Fix this pylint issue whenever you have time, but be careful !
                # pylint: disable=W0703
                try:
                    err_code, exp_ok = check_with_schema(
                        ins, self.ins_schema_dict[ins[0]]
                    )
                except Exception as err:
                    err_code = "Error in instruction " + str(err)
                    exp_ok = False
                if not exp_ok:
                    break
            if not exp_ok:
                break
        return err_code.replace("\n", ".."), exp_ok


def check_with_schema(obj: dict, schm: dict) -> Tuple[str, bool]:
    """
    Caller for the validate function of jsonschema

    Args:
        obj (dict): the object that should be checked.
        schm (dict): the schema that defines the object properties.

    Returns:
        boolean flag tellings if dictionary matches schema syntax.

    """
    # Fix this pylint issue whenever you have time, but be careful !
    # pylint: disable=W0703
    try:
        validate(instance=obj, schema=schm)
        return "", True
    except ValidationError as err:
        return str(err), False


def create_memory_data(
    shots_array: list, exp_name: str, n_shots: int
) -> ExperimentDict:
    """
    The function to create memory key in results dictionary
    with proprer formatting.
    """
    exp_sub_dict: ExperimentDict = {
        "header": {"name": "experiment_0", "extra metadata": "text"},
        "shots": 3,
        "success": True,
        "data": {"memory": None},
    }

    exp_sub_dict["header"]["name"] = exp_name
    exp_sub_dict["shots"] = n_shots
    memory_list = [
        str(shot).replace("[", "").replace("]", "").replace(",", "")
        for shot in shots_array
    ]
    exp_sub_dict["data"]["memory"] = memory_list
    return exp_sub_dict
