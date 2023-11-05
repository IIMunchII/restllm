from pydantic import BaseModel, Field
from enum import UNIQUE, verify, StrEnum

from typing import Optional, Union, Any
from .functions import FunctionName
from .base import MetaModel


@verify(UNIQUE)
class ModelTypes(StrEnum):
    GPT3_TURBO = "gpt-3.5-turbo"
    GPT3_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT4 = "gpt-4"
    GPT4_32K = "gpt-4-32k"


class CompletionParameters(BaseModel):
    model: ModelTypes
    functions: Optional[list[FunctionName]] = Field(
        default=[],
        description="A list of functions that the model may use to generate JSON inputs. Each function should have the following properties",
        examples=[["SearchArticlesFunction"]],
    )
    temperature: Optional[Union[float, None]] = Field(
        default=0.2,
        ge=0,
        le=2,
        description="The sampling temperature to be used, between 0 and 2. Higher values like 0.8 produce more random outputs, while lower values like 0.2 make outputs more focused and deterministic.",
    )
    top_p: Optional[Union[float, None]] = Field(
        description="An alternative to sampling with temperature. It instructs the model to consider the results of the tokens with top_p probability. For example, 0.1 means only the tokens comprising the top 10% probability mass are considered."
    )
    n: Optional[int] = Field(
        default=None,
        description="The number of chat completion choices to generate for each input message.",
        examples=[None],
    )
    stop: Optional[Union[str, list[str], None]] = Field(
        default=None,
        description="Up to 4 sequences where the API will stop generating further tokens.",
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="The maximum number of tokens to generate in the chat completion.",
        examples=[None],
    )
    presence_penalty: Optional[Union[float, None]] = Field(
        default=None,
        description="It is used to penalize new tokens based on their existence in the text so far.",
        examples=[None],
    )
    frequency_penalty: Optional[Union[float, None]] = Field(
        description="It is used to penalize new tokens based on their frequency in the text so far.",
        examples=[None],
    )
    logit_bias: Optional[dict[str, float]] = Field(
        default={},
        description="Used to modify the probability of specific tokens appearing in the completion.",
        examples=[None],
    )
    user: Optional[str] = Field(
        default=None,
        description="A unique identifier representing your end-user. This can help OpenAI to monitor and detect abuse.",
        examples=[None],
    )
    function_call: Optional[Union[str, dict[str, Any]]] = Field(
        description="Controls how the model responds to function calls.",
        default="auto",
        examples=["auto", None],
    )


class CompletionParametersWithMeta(MetaModel):
    object: CompletionParameters
