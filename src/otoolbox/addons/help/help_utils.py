from __future__ import annotations


from otoolbox import env
from otoolbox.base import Resource
from otoolbox.constants import PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


BEGIN_MARKER = ".. ODOONIX-AUTO-GENERATED-CONTENT-BEGIN"
END_MARKER = ".. ODOONIX-AUTO-GENERATED-CONTENT-END"


def _strip_markers(text: str) -> str:
    lines = [
        line
        for line in text.splitlines()
        if line.strip() not in (BEGIN_MARKER, END_MARKER)
    ]
    return "\n".join(lines).strip("\n")


def _find_first_markers(lines: list[str]) -> tuple[int, int] | None:
    begin_idx = None
    for i, line in enumerate(lines):
        if line.strip() == BEGIN_MARKER:
            begin_idx = i
            break
    if begin_idx is None:
        return None
    for j in range(begin_idx + 1, len(lines)):
        if lines[j].strip() == END_MARKER:
            return begin_idx, j
    return None


def copy_into_marked_section(src_text: str, dst_path: str) -> None:
    with open(dst_path, "r", encoding="utf-8") as f:
        dst_text = f.read()

    cleaned_src = _strip_markers(src_text)
    dst_lines = dst_text.splitlines()

    first_pair = _find_first_markers(dst_lines)

    if first_pair is None:
        if dst_text and not dst_text.endswith("\n"):
            dst_text += "\n"
        new_text = (
            dst_text
            + f"{BEGIN_MARKER}\n"
            + cleaned_src
            + ("\n" if cleaned_src else "")
            + f"{END_MARKER}\n"
        )
        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        return

    begin_idx, end_idx = first_pair

    # Remove any extra marker pairs after the first one
    pruned_lines: list[str] = []
    i = 0
    removed_ranges = []
    while i < len(dst_lines):
        if i == begin_idx:
            pruned_lines.extend(dst_lines[:begin_idx])
            pruned_lines.append(BEGIN_MARKER)
            if cleaned_src:
                pruned_lines.extend(cleaned_src.splitlines())
            pruned_lines.append(END_MARKER)
            i = end_idx + 1
            removed_ranges.append((begin_idx, end_idx))
        else:
            if dst_lines[i].strip() in (BEGIN_MARKER, END_MARKER):
                # Skip any stray markers outside the first pair
                i += 1
                continue
            pruned_lines.append(dst_lines[i])
            i += 1

    new_text = "\n".join(pruned_lines).rstrip("\n") + "\n"
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(new_text)


def update_readme(context: Resource):
    """Copies content of WORKSPACE_README.rst file to root README.rst file between markers.

    If there is no marker, it will add the content at the end of the file with markers.

    """
    readme_path = env.get_workspace_path(context.path)
    content = env.resource_string("addons/help/data/README.rst")
    copy_into_marked_section(src_text=content, dst_path=readme_path)

    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
