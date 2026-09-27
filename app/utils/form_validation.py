from typing import Any

# Minimal type-checking per field "type" string from form_schema.
# form_schema entries look like:
# {"key": "id_number", "label": "National ID Number", "type": "text", "required": True}
_TYPE_CHECKS = {
    "text": lambda v: isinstance(v, str),
    "textarea": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "select": lambda v: isinstance(v, str),
}


def validate_form_data(form_schema: list[dict] | None, form_data: dict[str, Any]) -> str | None:
    """Returns an error message if form_data doesn't match form_schema, else None."""
    schema = form_schema or []
    allowed_keys = {field["key"] for field in schema}

    unexpected = set(form_data.keys()) - allowed_keys
    if unexpected:
        return f"Unexpected field(s) submitted: {', '.join(sorted(unexpected))}"

    for field in schema:
        key = field["key"]
        is_required = field.get("required", False)
        field_type = field.get("type", "text")

        if key not in form_data or form_data[key] in (None, ""):
            if is_required:
                return f"'{field.get('label', key)}' is required"
            continue

        value = form_data[key]
        checker = _TYPE_CHECKS.get(field_type)
        if checker and not checker(value):
            return f"'{field.get('label', key)}' has an invalid value"

        if field_type == "select":
            options = field.get("options", [])
            if options and value not in options:
                return f"'{field.get('label', key)}' must be one of the allowed options"

    return None