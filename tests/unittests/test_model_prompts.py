import pytest
from pydantic import ValidationError

from restllm.models.prompts import (
    PromptTemplate,
    PromptTagName,
    is_valid_jinja2_template,
)


@pytest.fixture
def valid_test_messages() -> dict:
    return [{"role": "user", "content": "Hello, {{ test }}"}]


@pytest.fixture
def invalid_test_messages() -> dict:
    return [{"role": "user", "content": "Hello, {{ test."}]


@pytest.fixture
def invalid_test_variables() -> list[dict]:
    return [{"role": "user", "content": "Hello, {{ test }}, {{ invalid }}"}]


@pytest.fixture
def invalid_test_variables() -> list[dict]:
    return [{"role": "user", "content": "Hello, {{ test }}, {{ invalid }}"}]


@pytest.fixture
def valid_test_variables() -> list[dict]:
    return [{"role": "user", "content": "Hello, {{ test }}, {{ test2 }}"}]


@pytest.fixture
def valid_multiple_messages() -> list[dict]:
    return [
        {"role": "system", "content": "Hello, {{ test_system }}"},
        {"role": "user", "content": "Hello, {{ test_user }}"},
    ]


def test_is_valid_jinja2_template():
    assert is_valid_jinja2_template("Hello, {{ test }}") == True
    assert is_valid_jinja2_template("Hello, {{ test.") == False


def test_valid_prompt_template(valid_test_messages):
    instance = PromptTemplate(
        name="test",
        description="Test description",
        messages=valid_test_messages,
        arguments=[{"name": "test", "type": "str"}],
        language={"iso639_3": "eng"},
        tags=[PromptTagName.ZEROSHOT],
    )
    assert valid_test_messages == [
        message.model_dump(mode="json") for message in instance.messages
    ]


def test_valid_prompt_template_multiple(valid_multiple_messages):
    instance = PromptTemplate(
        name="test",
        description="Test description",
        messages=valid_multiple_messages,
        arguments=[
            {"name": "test_system", "type": "str"},
            {"name": "test_user", "type": "str"},
        ],
        language={"iso639_3": "eng"},
        tags=[PromptTagName.ZEROSHOT],
    )
    assert valid_multiple_messages == [
        message.model_dump(mode="json") for message in instance.messages
    ]


def test_invalid_prompt_template(invalid_test_messages):
    with pytest.raises(ValidationError):
        instance = PromptTemplate(
            name="test",
            description="Test description",
            messages=invalid_test_messages,
            arguments=[{"name": "test", "type": "str"}],
            language={"iso639_3": "eng"},
            tags=[PromptTagName.ZEROSHOT],
        )


def test_invalid_template_variables(invalid_test_variables):
    with pytest.raises(ValidationError):
        PromptTemplate(
            name="test",
            description="Test description",
            messages=invalid_test_variables,
            arguments=[{"name": "test", "type": "str"}],
            language={"iso639_3": "eng"},
            tags=[PromptTagName.ZEROSHOT],
        )


def test_invalid_parameter_keys(valid_test_messages):
    with pytest.raises(ValidationError):
        PromptTemplate(
            name="test",
            description="Test description",
            messages=valid_test_messages,
            arguments=[
                {"name": "test", "type": "str"},
                {"invalid": "invalid", "type": "str"},
            ],
            language={"iso639_3": "eng"},
            tags=[PromptTagName.ZEROSHOT],
        )


def test_create_model_from_template(valid_test_variables):
    instance = PromptTemplate(
        name="test",
        description="Test description",
        messages=valid_test_variables,
        arguments=[{"name": "test", "type": "str"}, {"name": "test2", "type": "str"}],
        language={"iso639_3": "eng"},
        tags=[PromptTagName.ZEROSHOT],
    )
    model_class = instance.create_model()
    assert "test" in model_class.model_fields.keys()
    assert "test2" in model_class.model_fields.keys()


def test_model_render_from_template(valid_test_variables):
    instance = PromptTemplate(
        name="test",
        description="Test description",
        messages=valid_test_variables,
        arguments=[{"name": "test", "type": "str"}, {"name": "test2", "type": "str"}],
        language={"iso639_3": "eng"},
        tags=[PromptTagName.ZEROSHOT],
    )
    rendered_string = instance.render({"test": "name1", "test2": "name2"})
    assert rendered_string.get("messages")[0].get("content") == "Hello, name1, name2"


def test_model_render_from_template_multiple(valid_multiple_messages):
    instance = PromptTemplate(
        name="test",
        description="Test description",
        messages=valid_multiple_messages,
        arguments=[
            {"name": "test_system", "type": "str"},
            {"name": "test_user", "type": "str"},
        ],
        language={"iso639_3": "eng"},
        tags=[PromptTagName.ZEROSHOT],
    )
    rendered_string = instance.render({"test_system": "name1", "test_user": "name2"})
    assert rendered_string.get("messages")[0].get("content") == "Hello, name1"
    assert rendered_string.get("messages")[1].get("content") == "Hello, name2"
