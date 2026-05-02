def to_class_name(module_name: str) -> str:
    return "".join(part.capitalize() for part in module_name.split("_"))
