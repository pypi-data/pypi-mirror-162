from __future__ import annotations

import ctypes
import math
from typing import Sequence

import jax
import jax.numpy as jnp
import requests
from jax.tree_util import tree_flatten

from .tree_util import (
    _reduce_count_and_size,
    is_treeclass,
    is_treeclass_leaf,
    sequential_model_shape_eval,
)

# Node formatting


def _format_size(node_size, newline=False):
    """return formatted size from inexact(exact) complex number"""
    mark = "\n" if newline else ""
    order_kw = ["B", "KB", "MB", "GB"]

    # define order of magnitude
    real_size_order = int(math.log(node_size.real, 1024)) if node_size.real > 0 else 0
    imag_size_order = int(math.log(node_size.imag, 1024)) if node_size.imag > 0 else 0
    return (
        f"{(node_size.real)/(1024**real_size_order):.2f}{order_kw[real_size_order]}{mark}"
        f"({(node_size.imag)/(1024**imag_size_order):.2f}{order_kw[imag_size_order]})"
    )


def _format_count(node_count, newline=False):
    mark = "\n" if newline else ""
    return f"{int(node_count.real):,}{mark}({int(node_count.imag):,})"


def _format_node(node):
    """format shape and dtype of jnp.array"""

    if isinstance(node, (jnp.ndarray, jax.ShapeDtypeStruct)):
        replace_tuple = (
            ("int", "i"),
            ("float", "f"),
            ("complex", "c"),
            (",)", ")"),
            ("(", "["),
            (")", "]"),
            (" ", ""),
        )

        formatted_string = f"{node.dtype}{jnp.shape(node)!r}"

        for lhs, rhs in replace_tuple:
            formatted_string = formatted_string.replace(lhs, rhs)
        return formatted_string

    else:
        return f"{node!r}"


# Box drawing


def _hbox(*text):

    boxes = list(map(_vbox, text))
    boxes = [(box).split("\n") for box in boxes]
    max_col_height = max([len(b) for b in boxes])
    boxes = [b + [" " * len(b[0])] * (max_col_height - len(b)) for b in boxes]
    fmt = ""

    for _, line in enumerate(zip(*boxes)):
        fmt += _resolve_line(line) + "\n"
    return fmt


def _hstack(boxes):

    boxes = [(box).split("\n") for box in boxes]
    max_col_height = max([len(b) for b in boxes])

    # expand height of each col before merging
    boxes = [b + [" " * len(b[0])] * (max_col_height - len(b)) for b in boxes]

    fmt = ""

    _cells = tuple(zip(*boxes))

    for i, line in enumerate(_cells):
        fmt += _resolve_line(line) + ("\n" if i != (len(_cells) - 1) else "")

    return fmt


def _vbox(*text: tuple[str, ...]) -> str:
    """Create vertically stacked text boxes

    Returns:
        str: stacked boxes string

    Examples:
    >>> _vbox("a","b")
        ┌───┐
        │a  │
        ├───┤
        │b  │
        └───┘

    >>> _vbox("a","","a")
        ┌───┐
        │a  │
        ├───┤
        │   │
        ├───┤
        │a  │
        └───┘
    """

    max_width = (
        max(tree_flatten([[len(t) for t in item.split("\n")] for item in text])[0]) + 0
    )

    top = f"┌{'─'*max_width}┐"
    line = f"├{'─'*max_width}┤"
    side = [
        "\n".join([f"│{t}{' '*(max_width-len(t))}│" for t in item.split("\n")])
        for item in text
    ]
    btm = f"└{'─'*max_width}┘"

    formatted = ""

    for i, s in enumerate(side):

        if i == 0:
            formatted += f"{top}\n{s}\n{line if len(side)>1 else btm}"

        elif i == len(side) - 1:
            formatted += f"\n{s}\n{btm}"

        else:
            formatted += f"\n{s}\n{line}"

    return formatted


def _resolve_line(cols: Sequence[str, ...]) -> str:
    """combine columns of single line by merging their borders

    Args:
        cols (Sequence[str,...]): Sequence of single line column string

    Returns:
        str: resolved column string

    Example:
        >>> _resolve_line(['ab','b│','│c'])
        'abb│c'

        >>> _resolve_line(['ab','b┐','┌c'])
        'abb┬c'

    """

    cols = list(map(list, cols))  # convert each col to col of chars
    alpha = ["│", "┌", "┐", "└", "┘", "┤", "├"]

    for index in range(len(cols) - 1):

        if cols[index][-1] == "┐" and cols[index + 1][0] in ["┌", "─"]:
            cols[index][-1] = "┬"
            cols[index + 1].pop(0)

        elif cols[index][-1] == "┘" and cols[index + 1][0] in ["└", "─"]:
            cols[index][-1] = "┴"
            cols[index + 1].pop(0)

        elif cols[index][-1] == "┤" and cols[index + 1][0] in ["├", "─", "└"]:  #
            cols[index][-1] = "┼"
            cols[index + 1].pop(0)

        elif cols[index][-1] in ["┘", "┐", "─"] and cols[index + 1][0] in ["├"]:
            cols[index][-1] = "┼"
            cols[index + 1].pop(0)

        elif cols[index][-1] == "─" and cols[index + 1][0] == "└":
            cols[index][-1] = "┴"
            cols[index + 1].pop(0)

        elif cols[index][-1] == "─" and cols[index + 1][0] == "┌":
            cols[index][-1] = "┬"
            cols[index + 1].pop(0)

        elif cols[index][-1] == "│" and cols[index + 1][0] == "─":
            cols[index][-1] = "├"
            cols[index + 1].pop(0)

        elif cols[index][-1] == " ":
            cols[index].pop()

        elif cols[index][-1] in alpha and cols[index + 1][0] in [*alpha, " "]:
            cols[index + 1].pop(0)

    return "".join(map(lambda x: "".join(x), cols))


def _table(lines):
    """

    === Explanation
        create a _table with self aligning rows and cols

    === Args
        lines : list of lists of cols values

    === Examples
        >>> print(_table([['1\n','2'],['3','4000']]))
            ┌─┬────────┐
            │1│3       │
            │ │        │
            ├─┼────────┤
            │2│40000000│
            └─┴────────┘


    """
    # align _cells vertically
    for i, _cells in enumerate(zip(*lines)):
        max__cell_height = max(map(lambda x: x.count("\n"), _cells))
        for j in range(len(_cells)):
            lines[j][i] += "\n" * (max__cell_height - lines[j][i].count("\n"))
    cols = [_vbox(*col) for col in lines]

    return _hstack(cols)


def _layer_box(name, indim=None, outdim=None):
    """
    === Explanation
        create a keras-like layer diagram

    ==== Examples
        >>> print(_layer_box("Test",(1,1,1),(1,1,1)))
        ┌──────┬────────┬───────────┐
        │      │ Input  │ (1, 1, 1) │
        │ Test │────────┼───────────┤
        │      │ Output │ (1, 1, 1) │
        └──────┴────────┴───────────┘

    """

    return _hstack(
        [
            _vbox(f"\n {name} \n"),
            _table([[" Input ", " Output "], [f" {indim} ", f" {outdim} "]]),
        ]
    )


# Summary utils


def _summary_line(leaf):

    dynamic, static = leaf.__tree_fields__
    is_dynamic = not leaf.frozen
    class_name = leaf.__class__.__name__

    if is_dynamic:
        name = f"{class_name}"
        count, size = _reduce_count_and_size(dynamic)
        return (name, count, size)

    else:
        name = f"{class_name}\n(frozen)"
        count, size = _reduce_count_and_size(static)
        return (name, count, size)


def _cell(text):
    return f"<td align = 'center'> {text} </td>"


def _summary_str(model, array=None, render: str = "string") -> str:

    ROW = [["Type ", "Param #", "Size ", "Config", "Output"]]

    excluded_kw = ["__frozen_treeclass__", "__frozen_tree_fields__"]

    dynamic_count, static_count = 0, 0
    dynamic_size, static_size = 0, 0

    if array is not None:
        params_shape = sequential_model_shape_eval(model, array)[1:]

    # all dynamic/static leaves
    all_leaves = (
        *model.__tree_fields__[0].values(),
        *model.__tree_fields__[1].values(),
    )
    treeclass_leaves = [leaf for leaf in all_leaves if is_treeclass(leaf)]

    for index, leaf in enumerate(treeclass_leaves):
        name, count, size = _summary_line(leaf)

        shape = _format_node(params_shape[index]) if array is not None else ""

        if leaf.frozen:
            static_count += count
            static_size += size
            fmt = "\n".join(
                [
                    f"{k}={_format_node(v)}"
                    for k, v in leaf.__tree_fields__[1].items()
                    if k not in excluded_kw
                ]
            )

        else:
            dynamic_count += count
            dynamic_size += size
            fmt = "\n".join(
                [f"{k}={_format_node(v)}" for k, v in leaf.__tree_fields__[0].items()]
            )

        ROW += [
            [name, _format_count(count, True), _format_size(size, True), fmt, shape]
        ]

    COL = [list(c) for c in zip(*ROW)]
    if array is None:
        COL.pop()

    layer__table = _table(COL)
    _table_width = len(layer__table.split("\n")[0])

    # summary row
    total_count = static_count + dynamic_count
    total_size = static_size + dynamic_size

    param_summary = (
        f"Total # :\t\t{_format_count(total_count)}\n"
        f"Dynamic #:\t\t{_format_count(dynamic_count)}\n"
        f"Static/Frozen #:\t{_format_count(static_count)}\n"
        f"{'-'*_table_width}\n"
        f"Total size :\t\t{_format_size(total_size)}\n"
        f"Dynamic size:\t\t{_format_size(dynamic_size)}\n"
        f"Static/Frozen size:\t{_format_size(static_size)}\n"
        f"{'='*_table_width}"
    )

    return layer__table + "\n" + param_summary


def _summary_md(model, array=None) -> str:

    fmt = (
        "<table>\n"
        "<tr>\n"
        "<td align = 'center'> Type </td>\n"
        "<td align = 'center'> Param #</td>\n"
        "<td align = 'center'> Size </td>\n"
        "<td align = 'center'> Config </td>\n"
        "<td align = 'center'> Output </td>\n"
        "</tr>\n"
    )

    excluded_kw = ["__frozen_treeclass__", "__frozen_tree_fields__"]

    dynamic_count, static_count = 0, 0
    dynamic_size, static_size = 0, 0

    if array is not None:
        params_shape = sequential_model_shape_eval(model, array)[1:]

    # all dynamic/static leaves
    all_leaves = (
        *model.__tree_fields__[0].values(),
        *model.__tree_fields__[1].values(),
    )
    treeclass_leaves = [leaf for leaf in all_leaves if is_treeclass(leaf)]

    for index, leaf in enumerate(treeclass_leaves):
        name, count, size = _summary_line(leaf)

        shape = _format_node(params_shape[index]) if array is not None else ""

        if leaf.frozen:
            static_count += count
            static_size += size
            config = "<br>".join(
                [
                    f"{k}={_format_node(v)}"
                    for k, v in leaf.__tree_fields__[1].items()
                    if k not in excluded_kw
                ]
            )

        else:
            dynamic_count += count
            dynamic_size += size
            config = "<br>".join(
                [f"{k}={_format_node(v)}" for k, v in leaf.__tree_fields__[0].items()]
            )

        fmt += (
            "<tr>"
            + _cell(name)
            + _cell(_format_count(count, True))
            + _cell(_format_size(size, True))
            + _cell(config)
            + _cell(shape)
            + "</tr>"
        )

    # summary row
    total_count = static_count + dynamic_count
    total_size = static_size + dynamic_size

    fmt += "</table>"

    param_summary = (
        "<table>"
        f"<tr><td>Total #</td><td>{_format_count(total_count)}</td></tr>"
        f"<tr><td>Dynamic #</td><td>{_format_count(dynamic_count)}</td></tr>"
        f"<tr><td>Static/Frozen #</td><td>{_format_count(static_count)}</td></tr>"
        f"<tr><td>Total size</td><td>{_format_size(total_size)}</td></tr>"
        f"<tr><td>Dynamic size</td><td>{_format_size(dynamic_size)}</td></tr>"
        f"<tr><td>Static/Frozen size</td><td>{_format_size(static_size)}</td></tr>"
        "</table>"
    )

    return fmt + "\n\n#### Summary\n" + param_summary


def summary(model, array=None, render: str = "string") -> str:
    if render in ["string", "str"]:
        return _summary_str(model, array=array)

    elif render in ["markdown", "md"]:
        return _summary_md(model, array=array)

    else:
        raise ValueError(
            f"render keyword should be in [string,str,markdown,md]. Found {render}"
        )


# tree_**


def tree_box(model, array=None):
    """
    === plot tree classes
    """

    def recurse(model, parent_name):

        nonlocal shapes

        if is_treeclass_leaf(model):
            box = _layer_box(
                f"{model.__class__.__name__}({parent_name})",
                _format_node(shapes[0]) if array is not None else None,
                _format_node(shapes[1]) if array is not None else None,
            )

            if shapes is not None:
                shapes.pop(0)
            return box

        else:
            level_nodes = []

            for fi in model.__dataclass_fields__.values():
                cur_node = model.__dict__[fi.name]

                if is_treeclass(cur_node):
                    level_nodes += [f"{recurse(cur_node,fi.name)}"]

                else:
                    level_nodes += [_vbox(f"{fi.name}={_format_node(cur_node)}")]

            return _vbox(
                f"{model.__class__.__name__}({parent_name})", "\n".join(level_nodes)
            )

    shapes = sequential_model_shape_eval(model, array) if array is not None else None
    return recurse(model, "Parent")


def tree_diagram(model):
    """
    === Explanation
        pretty print treeclass model with tree structure diagram

    === Args
        tree : boolean to create tree-structure
    """

    def recurse(model, parent_level_count):

        nonlocal fmt

        if is_treeclass(model):

            cur_children_count = len(model.__dataclass_fields__)

            for i, fi in enumerate(model.__dataclass_fields__.values()):

                if fi.repr:
                    cur_node = model.__dict__[fi.name]

                    fmt += "\n" + "".join(
                        [
                            (("│" if lvl > 1 else "") + "\t")
                            for lvl in parent_level_count
                        ]
                    )

                    is_static = "static" in fi.metadata and fi.metadata["static"]
                    mark = "x" if is_static else ("#" if model.frozen else "─")

                    if is_treeclass(cur_node):

                        layer_class_name = cur_node.__class__.__name__

                        fmt += (
                            f"├{mark}─ "
                            if i < (cur_children_count - 1)
                            else f"└{mark}─ "
                        ) + f"{fi.name}={layer_class_name}"
                        recurse(cur_node, parent_level_count + [cur_children_count - i])

                    else:
                        fmt += (
                            f"├{mark}─ "
                            if i < (cur_children_count - 1)
                            else f"└{mark}─ "
                        )
                        fmt += f"{fi.name}={_format_node(cur_node)}"
                        recurse(cur_node, parent_level_count + [1])

                elif not is_treeclass(model):
                    recurse(cur_node, parent_level_count + [1])

            fmt += "\t"

    fmt = f"{(model.__class__.__name__)}"

    recurse(model, [1])

    return fmt.expandtabs(4)


def tree_indent(model, width: int = 40) -> str:
    """Prertty print `treeclass_leaves`

    Returns:
        str: indented model leaves.
    """

    def format_width(string, width=width):
        """strip newline/tab characters if less than max width"""
        stripped_string = string.replace("\n", "").replace("\t", "")
        children_length = len(stripped_string)
        return string if children_length > width else stripped_string

    def recurse(model, depth):

        nonlocal fmt

        if is_treeclass(model):
            cur_children_count = len(model.__dataclass_fields__)

            for i, fi in enumerate(model.__dataclass_fields__.values()):

                if fi.repr:
                    cur_node = model.__dict__[fi.name]

                    # add newline by default
                    fmt += ("\n" + "\t" * depth) if fi.repr else ""

                    if is_treeclass(cur_node):
                        layer_class_name = f"{cur_node.__class__.__name__}"
                        fmt += f"{fi.name}={layer_class_name}" + "("

                        # capture children repr
                        start_cursor = len(fmt)

                        recurse(cur_node, depth + 1)

                        # format children repr width
                        fmt = fmt[:start_cursor] + format_width(fmt[start_cursor:])

                        fmt += ")" + ("," if i < (cur_children_count - 1) else "")

                    else:
                        fmt += f"{fi.name}={_format_node(cur_node)}" + (
                            "," if i < (cur_children_count - 1) else ("")
                        )
                        recurse(cur_node, depth)

                elif not is_treeclass(model):
                    recurse(cur_node, depth)

    fmt = ""
    recurse(model, 1)
    fmt = f"{(model.__class__.__name__)}({format_width(fmt,width)})"

    return fmt.expandtabs(2)


def tree_str(model, width: int = 40) -> str:
    """Prertty print `treeclass_leaves`

    Returns:
        str: indented model leaves.
    """

    def format_width(string, width=width):
        """strip newline/tab characters if less than max width"""
        stripped_string = string.replace("\n", "").replace("\t", "")
        children_length = len(stripped_string)
        return string if children_length > width else stripped_string

    def recurse(model, depth):

        nonlocal fmt

        if is_treeclass(model):
            cur_children_count = len(model.__dataclass_fields__)

            for i, fi in enumerate(model.__dataclass_fields__.values()):

                if fi.repr:
                    cur_node = model.__dict__[fi.name]

                    # add newline by default
                    fmt += ("\n" + "\t" * depth) if fi.repr else ""

                    if is_treeclass(cur_node):
                        layer_class_name = f"{cur_node.__class__.__name__}"
                        fmt += f"{fi.name}={layer_class_name}" + "("

                        # capture children repr
                        start_cursor = len(fmt)

                        recurse(cur_node, depth + 1)

                        # format children repr width
                        fmt = fmt[:start_cursor] + format_width(fmt[start_cursor:])

                        fmt += ")" + ("," if i < (cur_children_count - 1) else "")

                    else:
                        multiline = "\n" in f"{cur_node!s}"
                        cur_node_fmt = ("\n" + "\t" * (depth + 1)) if multiline else ""
                        cur_node_fmt += ("\n" + "\t" * (depth + 1)).join(
                            f"{cur_node!s}".split("\n")
                        )

                        fmt += f"{fi.name}={cur_node_fmt}" + (
                            "," if i < (cur_children_count - 1) else ("")
                        )
                        recurse(cur_node, depth)

                elif not is_treeclass(model):
                    recurse(cur_node, depth)

    fmt = ""
    recurse(model, 1)
    fmt = f"{(model.__class__.__name__)}({format_width(fmt,width)})"

    return fmt.expandtabs(2)


def _tree_mermaid(model):
    def node_id(input):
        """hash a node by its location in a tree"""
        return ctypes.c_size_t(hash(input)).value

    def recurse(model, cur_depth, prev_id):

        nonlocal fmt

        if is_treeclass(model):
            is_frozen = model.frozen

            for i, fi in enumerate(model.__dataclass_fields__.values()):
                if fi.repr:
                    cur_node = model.__dict__[fi.name]
                    cur_order = i
                    fmt += "\n"

                    if is_treeclass(cur_node):
                        layer_class_name = cur_node.__class__.__name__
                        cur = (cur_depth, cur_order)
                        cur_id = node_id((*cur, prev_id))
                        fmt += f"\tid{prev_id} --> id{cur_id}({fi.name}\\n{layer_class_name})"
                        recurse(cur_node, cur_depth + 1, cur_id)

                    else:
                        cur = (cur_depth, cur_order)
                        cur_id = node_id((*cur, prev_id))
                        is_static = "static" in fi.metadata and fi.metadata["static"]
                        connector = (
                            "--x" if is_static else ("-.-" if is_frozen else "---")
                        )
                        fmt += f'\tid{prev_id} {connector} id{cur_id}["{fi.name}\\n{_format_node(cur_node)}"]'
                        recurse(cur_node, cur_depth + 1, cur_id)

                elif not is_treeclass(model):
                    recurse(cur_node, cur_depth + 1, cur_id)

    cur_id = node_id((0, 0, -1, 0))
    fmt = f"flowchart LR\n\tid{cur_id}[{model.__class__.__name__}]"
    recurse(model, 1, cur_id)
    return fmt.expandtabs(4)


def _generate_mermaid_link(mermaid_string: str) -> str:
    """generate a one-time link mermaid diagram"""
    url_val = "https://pytreeclass.herokuapp.com/generateTemp"
    request = requests.post(url_val, json={"description": mermaid_string})
    generated_id = request.json()["id"]
    generated_html = f"https://pytreeclass.herokuapp.com/temp/?id={generated_id}"
    return f"Open URL in browser: {generated_html}"


def tree_mermaid(model, link=False):
    mermaid_string = _tree_mermaid(model)
    return _generate_mermaid_link(mermaid_string) if link else mermaid_string


def save_viz(model, filename, method="tree_mermaid_md"):

    if method == "tree_mermaid_md":
        fmt = "```mermaid\n" + tree_mermaid(model) + "\n```"

        with open(f"{filename}.md", "w") as f:
            f.write(fmt)

    elif method == "tree_mermaid_html":
        fmt = "<html><body><script src='https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js'></script>"
        fmt += "<script>mermaid.initialize({ startOnLoad: true });</script><div class='mermaid'>"
        fmt += tree_mermaid(model)
        fmt += "</div></body></html>"

        with open(f"{filename}.html", "w") as f:
            f.write(fmt)

    elif method == "tree_diagram":
        with open(f"{filename}.txt", "w") as f:
            f.write(tree_diagram(model))

    elif method == "tree_box":
        with open(f"{filename}.txt", "w") as f:
            f.write(tree_box(model))

    elif method == "summary":
        with open(f"{filename}.txt", "w") as f:
            f.write(summary(model))

    elif method == "summary_md":
        with open(f"{filename}.md", "w") as f:
            f.write(summary(model, render="md"))
