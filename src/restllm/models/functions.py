from typing import Optional, Any
from enum import StrEnum

from pydantic import BaseModel, Field


class NotAFunctionCall(ValueError):
    pass


class FunctionNameMismatch(ValueError):
    pass


class MissingFunctionDescription(ValueError):
    pass


class FunctionCall(BaseModel):
    name: str = Field(
        description="Name of the function to call"
    )
    args: dict[str, Any]


class Function(BaseModel):
    name: str = Field(
        max_length=64,
        pattern="^[a-zA-Z0-9_-]*$",
        description="The name of the function to be called. It should contain a-z, A-Z, 0-9, underscores and dashes, with a maximum length of 64 characters.",
        examples=["get_weather_status", None],
    )
    description: Optional[str] = Field(
        description="A description explaining what the function does. It helps the model to decide when and how to call the function.",
        examples=["Function to get current weather status"],
    )
    parameters: dict[str, Any] = Field(
        description="The parameters that the function accepts, described as a JSON Schema object.",
        examples=[
            {
                "type": "object",
                "properties": {
                    "name": "location",
                    "description": "Location for the weather status",
                },
            },
            None,
        ],
    )


# MIT License
#
# Copyright (c) 2023 Jason Liu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def _remove_keys(d: dict, remove_keys: list[str]) -> None:
    """Remove a key from a dictionary recursively"""
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key in remove_keys and "type" in d.keys():
                del d[key]
            else:
                _remove_keys(d[key], remove_keys)


class SchemaCheckMeta(type(BaseModel)):
    def __init__(
        cls: BaseModel,
        name: str,
        bases: tuple,
        attrs: dict[str, Any],
    ):
        super().__init__(name, bases, attrs)

        if name == "FunctionSchemaBase":
            return

        schema = cls.model_json_schema()

        if "description" not in schema:
            raise MissingFunctionDescription(
                "Function 'description' is missing. Use doc strings on the class definition to provide description'"
            )


class FunctionSchemaBase(BaseModel, metaclass=SchemaCheckMeta):
    @classmethod
    @property
    def function_schema(cls):
        """
        Return the schema in the format of OpenAI's schema as jsonschema
        """
        schema = cls.model_json_schema()
        parameters = {
            key: value
            for key, value in schema.items()
            if key not in ("title", "description")
        }

        parameters["required"] = sorted(
            key
            for key, value in parameters["properties"].items()
            if not "default" in value
        )

        if "description" not in schema:
            raise MissingFunctionDescription(
                "Function 'description' is missing. Use doc strings on the class definition to provide description'"
            )

        _remove_keys(parameters, ["title", "additionalProperties"])
        return {
            "name": schema["title"],
            "description": schema["description"],
            "parameters": parameters,
        }

    @classmethod
    def from_response(
        cls,
        completion: dict[str, Any],
        context: dict[str, Any] | None = None,
        strict: bool | None = None,
    ):
        """Execute the function from the response of an openai chat completion"""
        message = completion["choices"][0]["message"]

        if not "function_call" in message:
            raise NotAFunctionCall("No function call detected in message")

        if not message["function_call"]["name"] == cls.function_schema["name"]:
            raise FunctionNameMismatch("Function name does not match")

        return cls.model_validate_json(
            message["function_call"]["arguments"],
            context=context,
            strict=strict,
        )


class SearchArticlesFunction(FunctionSchemaBase):
    """
    Function to search for articles in an article database.
    Usefull for when you want to answer questions related to an archive
    """

    query: str = Field(
        description="The query string to search with. Can be anything related to articls",
        examples=["Who won the Danish election in 2022?"],
    )
    publish_years: list[int] = Field(
        description="The publishing years to filter the search by. Should be a list of one or more integers.",
        examples=[[2010], [2022, 2023]],
    )


def get_all_function_schemas() -> list[Function]:
    return [_class.function_schema for _class in get_function_classes().values()]


def get_function_schemas(function_names: list[str]) -> list[dict[str, Any]]:
    function_classes = get_function_classes()
    return [
        function_classes.get(function_name).function_schema
        for function_name in function_names
    ]


def get_function_classes() -> dict[str, FunctionSchemaBase]:
    """
    List all functions to be callable in the API.
    """
    return {SearchArticlesFunction.__name__: SearchArticlesFunction}


def pascal_to_upper(class_name: str) -> str:
    result = [get_character(char) for char in class_name]
    return "".join(result)[1:]


def get_character(character: str) -> str:
    return f"_{character.upper()}" if character.isupper() else character.upper()


FunctionName = StrEnum(
    "FunctionName",
    [
        (pascal_to_upper(cls.__name__), cls.__name__)
        for cls in get_function_classes().values()
    ],
)
