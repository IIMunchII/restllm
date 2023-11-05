from jinja2 import Environment, TemplateSyntaxError, meta


def is_valid_jinja2_template(template: str) -> bool:
    env = Environment()
    try:
        env.parse(template)
        return True
    except TemplateSyntaxError:
        return False


def names_and_variables_match(template: str, parameters: list[str]) -> bool:
    env = Environment()
    parsed_content = env.parse(template)
    required_keys = meta.find_undeclared_variables(parsed_content)
    return set(required_keys) == set(parameters)
