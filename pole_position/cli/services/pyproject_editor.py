import re
from pathlib import Path

try:
    from packaging.version import InvalidVersion, Version
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    InvalidVersion = ValueError  # type: ignore[assignment]
    Version = None  # type: ignore[assignment]


SECTION_HEADER_PATTERN = re.compile(r"^\s*\[([^\]]+)\]\s*(?:#.*)?$")
DEPENDENCIES_ARRAY_PATTERN = re.compile(
    r"^(?P<indent>\s*)dependencies\s*=\s*\[(?P<rest>.*)$"
)
DEPENDENCY_ENTRY_PATTERN = re.compile(
    r"^(?P<indent>\s*)(?P<quote>[\"'])(?P<value>.+?)(?P=quote)"
    r"(?P<trailing>\s*,?\s*(?:#.*)?)$"
)
ARRAY_END_PATTERN = re.compile(r"^\s*\]\s*(?:#.*)?$")
DEPENDENCY_NAME_PATTERN = re.compile(r"^\s*(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)")
DEPENDENCY_EXTRAS_PATTERN = re.compile(
    r"^\s*[A-Za-z0-9][A-Za-z0-9._-]*(?:\[(?P<extras>[^\]]*)\])?"
)
DEPENDENCY_SPECIFIER_PATTERN = re.compile(
    r"(?P<operator>~=|===|==|!=|<=|>=|<|>)\s*(?P<version>[^,;\s]+)"
)


def ensure_project_dependency(path: Path, dependency: str | None) -> None:
    if dependency is None:
        return

    content = path.read_text(encoding="utf-8")
    updated = ensure_project_dependency_text(
        content,
        dependency,
        path_label=str(path),
    )

    if updated != content:
        path.write_text(updated, encoding="utf-8")


def ensure_project_dependency_text(
    content: str,
    dependency: str | None,
    *,
    path_label: str = "pyproject.toml",
) -> str:
    if dependency is None:
        return content

    lines = content.splitlines()
    project_start, project_end = _find_project_section(lines, path_label)
    array_start, array_end, array_indent, inline_values = _find_project_dependencies(
        lines,
        project_start,
        project_end,
        path_label,
    )
    existing_dependencies = _dependency_values(
        lines=lines,
        start_index=array_start,
        end_index=array_end,
        inline_values=inline_values,
    )

    if _dependency_contract_satisfied(existing_dependencies, dependency):
        return content

    if inline_values is not None:
        _replace_inline_dependencies_array(
            lines=lines,
            start_index=array_start,
            end_index=array_end,
            array_indent=array_indent,
            dependencies=_replace_or_append_dependency(inline_values, dependency),
        )
    else:
        replaced_dependency = _replace_dependency_line(
            lines=lines,
            start_index=array_start,
            end_index=array_end,
            dependency=dependency,
        )
        if not replaced_dependency:
            _insert_dependency_line(
                lines=lines,
                start_index=array_start,
                end_index=array_end,
                array_indent=array_indent,
                dependency=dependency,
            )

    return "\n".join(lines) + "\n"


def _find_project_section(lines: list[str], path_label: str) -> tuple[int, int]:
    for index, line in enumerate(lines):
        match = SECTION_HEADER_PATTERN.match(line)
        if match is None or match.group(1).strip() != "project":
            continue

        for end_index in range(index + 1, len(lines)):
            if SECTION_HEADER_PATTERN.match(lines[end_index]):
                return index + 1, end_index

        return index + 1, len(lines)

    raise RuntimeError(f"Unsupported dependency layout: {path_label}")


def _find_project_dependencies(
    lines: list[str],
    project_start: int,
    project_end: int,
    path_label: str,
) -> tuple[int, int, str, list[str] | None]:
    for index in range(project_start, project_end):
        match = DEPENDENCIES_ARRAY_PATTERN.match(lines[index])
        if match is None:
            continue

        inline_values = _parse_inline_dependency_values(match.group("rest"))
        if inline_values is not None:
            return index, index, match.group("indent"), inline_values

        end_index = _find_array_end_index(
            lines=lines,
            start_index=index,
            stop_index=project_end,
            path_label=path_label,
        )
        return index, end_index, match.group("indent"), None

    raise RuntimeError(f"Unsupported dependency layout: {path_label}")


def _parse_inline_dependency_values(rest: str) -> list[str] | None:
    close_index = _find_unquoted_closing_bracket(rest)
    if close_index is None:
        return None

    return _quoted_values(rest[:close_index])


def _find_unquoted_closing_bracket(text: str) -> int | None:
    quote: str | None = None
    escaped = False

    for index, char in enumerate(text):
        if quote is not None:
            if quote == '"' and char == "\\" and not escaped:
                escaped = True
                continue
            if char == quote and not escaped:
                quote = None
            escaped = False
            continue

        if char in {"'", '"'}:
            quote = char
            continue

        if char == "]":
            return index

    return None


def _quoted_values(text: str) -> list[str]:
    values: list[str] = []
    index = 0

    while index < len(text):
        quote = text[index]
        if quote not in {"'", '"'}:
            index += 1
            continue

        index += 1
        value: list[str] = []
        escaped = False
        while index < len(text):
            char = text[index]
            if quote == '"' and char == "\\" and not escaped:
                escaped = True
                value.append(char)
                index += 1
                continue
            if char == quote and not escaped:
                break
            value.append(char)
            escaped = False
            index += 1

        values.append("".join(value))
        index += 1

    return values


def _dependency_values(
    *,
    lines: list[str],
    start_index: int,
    end_index: int,
    inline_values: list[str] | None,
) -> list[str]:
    if inline_values is not None:
        return inline_values

    values: list[str] = []
    for line in lines[start_index + 1 : end_index]:
        value = _dependency_value_from_line(line)
        if value is not None:
            values.append(value)
    return values


def _dependency_value_from_line(line: str) -> str | None:
    match = DEPENDENCY_ENTRY_PATTERN.match(line)
    if match is None:
        return None
    return match.group("value")


def _replace_or_append_dependency(
    existing_dependencies: list[str],
    dependency: str,
) -> list[str]:
    dependencies = list(existing_dependencies)
    for index, existing_dependency in enumerate(dependencies):
        if _dependency_names_match(existing_dependency, dependency):
            dependencies[index] = dependency
            return dependencies

    return [*dependencies, dependency]


def _replace_dependency_line(
    *,
    lines: list[str],
    start_index: int,
    end_index: int,
    dependency: str,
) -> bool:
    for index in range(start_index + 1, end_index):
        match = DEPENDENCY_ENTRY_PATTERN.match(lines[index])
        if match is None:
            continue

        if not _dependency_names_match(match.group("value"), dependency):
            continue

        lines[index] = (
            f"{match.group('indent')}{match.group('quote')}{dependency}"
            f"{match.group('quote')}{match.group('trailing')}"
        )
        return True

    return False


def _replace_inline_dependencies_array(
    *,
    lines: list[str],
    start_index: int,
    end_index: int,
    array_indent: str,
    dependencies: list[str],
) -> None:
    entry_indent = f"{array_indent}    "
    entries = _dependency_lines(
        dependencies=dependencies,
        entry_indent=entry_indent,
    )
    lines[start_index : end_index + 1] = [
        f"{array_indent}dependencies = [",
        *entries,
        f"{array_indent}]",
    ]


def _insert_dependency_line(
    *,
    lines: list[str],
    start_index: int,
    end_index: int,
    array_indent: str,
    dependency: str,
) -> None:
    entry_indent = _dependency_entry_indent(lines, start_index, end_index, array_indent)
    dependency_line = f'{entry_indent}"{dependency}",'
    insert_at = end_index

    for index in range(start_index + 1, end_index):
        existing_dependency = _dependency_value_from_line(lines[index])
        if existing_dependency is None:
            continue
        if dependency.lower() < existing_dependency.lower():
            insert_at = index
            break

    lines.insert(insert_at, dependency_line)


def _dependency_entry_indent(
    lines: list[str],
    start_index: int,
    end_index: int,
    array_indent: str,
) -> str:
    for line in lines[start_index + 1 : end_index]:
        match = DEPENDENCY_ENTRY_PATTERN.match(line)
        if match is not None:
            return match.group("indent")

    return f"{array_indent}    "


def _dependency_lines(*, dependencies: list[str], entry_indent: str) -> list[str]:
    return [
        f'{entry_indent}"{dependency}",'
        for dependency in sorted(dependencies, key=str.lower)
    ]


def _find_array_end_index(
    *,
    lines: list[str],
    start_index: int,
    stop_index: int,
    path_label: str,
) -> int:
    for index in range(start_index + 1, stop_index):
        if ARRAY_END_PATTERN.match(lines[index]):
            return index

    raise RuntimeError(f"Unsupported dependency layout: {path_label}")


def _dependency_contract_satisfied(
    dependencies: list[str],
    required_dependency: str,
) -> bool:
    required_name = _dependency_name(required_dependency)
    required_extras = _dependency_extras(required_dependency)
    required_min_version = _dependency_min_version(required_dependency)
    if required_name is None:
        return False

    for dependency in dependencies:
        if _dependency_name(dependency) != required_name:
            continue
        if not required_extras.issubset(_dependency_extras(dependency)):
            continue
        if required_min_version is None:
            return True

        dependency_min_version = _dependency_min_version(dependency)
        if dependency_min_version is None:
            continue
        if _version_at_least(dependency_min_version, required_min_version):
            return True

    return False


def _dependency_names_match(dependency: str, other_dependency: str) -> bool:
    dependency_name = _dependency_name(dependency)
    return dependency_name is not None and dependency_name == _dependency_name(
        other_dependency
    )


def _dependency_name(dependency: str) -> str | None:
    match = DEPENDENCY_NAME_PATTERN.match(dependency.split(";", 1)[0])
    if match is None:
        return None
    return _normalize_dependency_name(match.group("name"))


def _dependency_extras(dependency: str) -> frozenset[str]:
    match = DEPENDENCY_EXTRAS_PATTERN.match(dependency.split(";", 1)[0])
    if match is None:
        return frozenset()

    extras = match.group("extras")
    if not extras:
        return frozenset()

    return frozenset(
        _normalize_dependency_name(extra.strip())
        for extra in extras.split(",")
        if extra.strip()
    )


def _normalize_dependency_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _dependency_min_version(dependency: str) -> str | None:
    lower_bounds: list[str] = []
    dependency_spec = dependency.split(";", 1)[0]
    for match in DEPENDENCY_SPECIFIER_PATTERN.finditer(dependency_spec):
        operator = match.group("operator")
        if operator not in {">=", ">", "==", "===", "~="}:
            continue
        lower_bounds.append(match.group("version"))

    if not lower_bounds:
        return None

    return max(lower_bounds, key=_version_sort_key)


def _version_at_least(version: str, required_version: str) -> bool:
    if Version is not None:
        try:
            return Version(version) >= Version(required_version)
        except InvalidVersion:
            pass

    return _version_sort_key(version) >= _version_sort_key(required_version)


def _version_sort_key(version: str) -> tuple[int, ...]:
    parts = [int(part) for part in re.findall(r"\d+", version)]
    return tuple(parts)
