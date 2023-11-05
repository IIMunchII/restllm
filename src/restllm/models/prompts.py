import re
from enum import Enum, auto, UNIQUE, verify, StrEnum

from jinja2 import Template
from pydantic import (
    BaseModel,
    Field,
    computed_field,
    create_model,
    model_validator,
    field_validator,
)

from .base import MetaModel
from .validators import is_valid_jinja2_template, names_and_variables_match

import iso639
import iso639.exceptions


class LanguageProperties(BaseModel):
    name: str = Field(description="Langauge name", examples=["English"])
    pt1: str = Field(description="ISO 639-1 language code", examples=["en"])
    pt2b: str = Field(description="ISO 639-2/B language code", examples=["eng"])
    pt2t: str = Field(description="ISO 639-2/B language code", examples=["eng"])
    pt3: str = Field(description="ISO 639-3 language code", examples=["eng"])
    pt5: str = Field(description="ISO 639-5 language code", examples=["cpe"])


class Language(BaseModel):
    iso639_3: str = Field(
        max_length=3,
        min_length=3,
        description="iso639-3 language code.",
        examples=["eng"],
    )

    @field_validator("iso639_3")
    def validate_language_code(cls, value):
        try:
            iso639.Lang(value)
        except iso639.exceptions.InvalidLanguageValue as exec:
            raise ValueError(f"Invalid ISO 639-3 language code: {value}") from exec
        return value

    @computed_field(return_type=LanguageProperties)
    @property
    def properties(self) -> LanguageProperties:
        return LanguageProperties(**iso639.Lang(self.iso639_3).asdict())


def get_name_pattern() -> re.Pattern:
    return r"^[a-zA-Z_][a-zA-Z0-9_]*$"


@verify(UNIQUE)
class PromptRole(StrEnum):
    USER = auto()
    SYSTEM = auto()


class VariableType(Enum):
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    LIST = "list"
    DICT = "dict"

    @property
    def type(self):
        return eval(self._value_)


class PromptTagName(StrEnum):
    ZEROSHOT = "Zero-shot Prompting"
    FEWSHOT = "Few-shot Prompting"
    MANYSHOT = "Many-shot Prompting"
    CURRICULUMLEARNING = "Curriculum Learning Prompting"
    META = "Meta-Prompting"
    CONTINUOUS = "Continuous Prompting"
    ADAPTIVE = "Adaptive Prompting"
    COMPARATIVE = "Comparative Prompting"
    CHAIN = "Chain Prompting"
    HIERARCHICAL = "Hierarchical Prompting"


class PromptTagDescriptionMapping:
    _mapping = {
        PromptTagName.ZEROSHOT: "The model is provided with a prompt and is expected to generate a relevant response without any prior examples.",
        PromptTagName.FEWSHOT: "Providing a few examples along with the prompt to guide the model towards the desired output.",
        PromptTagName.MANYSHOT: "Providing a larger number of examples along with the prompt to further guide the model.",
        PromptTagName.CURRICULUMLEARNING: "Arranging prompts in an order of increasing complexity, training the model progressively.",
        PromptTagName.META: "Designing prompts that instruct the model to consider certain variables or conditions while generating a response.",
        PromptTagName.CONTINUOUS: "Employing a sequence of prompts in a continuous manner, where the model’s response to one prompt serves as a part of the prompt for the next task.",
        PromptTagName.ADAPTIVE: "Dynamically adjusting the prompt based on the model’s previous responses to better guide it towards the desired output.",
        PromptTagName.COMPARATIVE: "Providing comparisons within the prompt to guide the model towards generating more accurate or nuanced responses.",
        PromptTagName.CHAIN: "Creating a chain of interlinked prompts where the output of one task serves as the prompt for the subsequent task.",
        PromptTagName.HIERARCHICAL: "Structuring prompts in a hierarchical manner, where higher-level prompts guide the overall narrative and lower-level prompts guide the details.",
    }

    @classmethod
    def get_description(cls, prompt_tag: PromptTagName):
        return cls._mapping.get(prompt_tag, "Technique not found")


class PromptTag(BaseModel):
    name: PromptTagName

    @property
    def description(self) -> str:
        return PromptTagDescriptionMapping.get_description(self.name)


class BasePrompt(BaseModel):
    name: str = Field(
        description="Name of the prompt",
        pattern=get_name_pattern(),
        examples=[
            "EditPythonCodePrompt",
            "SummariseArticlePrompt",
        ],
    )
    description: str = Field(
        description="Description of the prompt and what it does.",
        examples=["Prompt to edit python code according to Clean Code principles."],
    )
    language: Language = Field(description="Language of the text in the prompt")
    tags: list[PromptTagName] | None = Field(
        description="List of prompt tags descripting the type of prompt"
    )


class PromptMessage(BaseModel):
    role: PromptRole = Field(
        description="User or System role for prompt", examples=[PromptRole.SYSTEM]
    )
    content: str = Field(
        description="Text based prompt for user or system role.'",
        examples=[
            "You are an expert Python programmer that values Clean Code and simplicity."
        ],
    )


class Prompt(BasePrompt):
    messages: list[PromptMessage] = Field(
        description="List of prompt messages. Role System must preceed user",
        max_length=2,
        min_length=1,
    )

    @field_validator("messages", mode="before")
    def validate_messages(cls, value):
        if len(value) == 2:
            if value[0].role == PromptRole.USER:
                raise ValueError("First role must be system when two messages is used")
            if value[0].role == value[1].role:
                raise ValueError("Consecutive roles cannot be the same")
        return value


class PromptTemplateArgument(BaseModel):
    name: str = Field(
        pattern=get_name_pattern(),
        examples=["python_code", "article_body"],
    )
    type: VariableType


class TemplateMessage(BaseModel):
    role: PromptRole
    content: str = Field(
        description="Valid Jinja2 template for the prompt",
        examples=[
            'Please edit this python code to follow Clean Code best pratices: "{{ python_code }}"'
        ],
    )


class PromptTemplate(BasePrompt):
    arguments: list[PromptTemplateArgument] = Field(
        description="Parameter name and type for the Jinja2 template. Keys must match the template"
    )
    messages: list[TemplateMessage] = Field(
        description="List of template messages containing valid Jinja2 template strings."
    )

    @model_validator(mode="after")
    def check_valid_template(self) -> "PromptTemplate":
        template = self._get_template_text()
        if not is_valid_jinja2_template(template):
            raise ValueError(f"String is invalid Jinja2 template: {template}")
        if not names_and_variables_match(template, self._get_variable_names()):
            raise ValueError(f"Parameter keys and template variables must match.")
        return self

    def _get_template_text(self):
        return "\n".join([message.content for message in self.messages])

    def _get_variable_names(self) -> list[str]:
        return [item.name for item in self.arguments]

    def _get_pydantic_types(self) -> dict[str, tuple[type, ...]]:
        return {item.name: (item.type.type, ...) for item in self.arguments}

    def create_model(self) -> BaseModel:
        return create_model(self.name, **self._get_pydantic_types())

    def render(self, parameters: dict) -> dict:
        template_model = self.create_model()
        parameter_instance = template_model.model_validate(parameters, strict=True)
        messages = [
            {
                "role": message.role,
                "content": Template(message.content).render(
                    parameter_instance.model_dump()
                ),
            }
            for message in self.messages
        ]
        prompt_dict = self.model_dump()
        prompt_dict.update({"messages": messages})
        return prompt_dict


class PromptTemplateWithMeta(MetaModel):
    object: PromptTemplate


class PromptWithMeta(MetaModel):
    object: Prompt
