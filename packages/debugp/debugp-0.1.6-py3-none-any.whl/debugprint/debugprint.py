from typing import Optional

from rich.console import Console
import inspect
import linecache
from .ast2py import *

MISSING = object()

console = Console()
dp_alias = []
last_line_no: int = -1
same_line_call_cache: Optional[list[ast.Call]] = None
same_line_counter: int = 0


def prepare(line_no, file, caller) -> ast.Call:
    """Prepare same_line_call_cache and returns correct arguments"""
    global same_line_counter, same_line_call_cache, last_line_no, dp_alias
    if line_no == last_line_no:
        same_line_counter += 1
        return same_line_call_cache[same_line_counter]

    if c.print_file:
        console.log(f"[{c.op}]Debug info of[/{c.op}] [{c.const}]'{file}'[/{c.const}][{c.op}],"
                    f" line [/{c.op}]{line_no} in [{c.const}]'{caller.f_code.co_name}'[/{c.const}]:")
    else:
        console.log(f"[{c.op}]Debug info of line [/{c.op}]{line_no} [{c.op}]in[/{c.op}]"
                    f" [{c.const}]{caller.f_code.co_name}:")

    tree = get_correct_tree(file, line_no)

    same_line_counter = 0
    last_line_no = line_no

    if len(tree.body) != 1:
        console.log(f"[{c.op}][WARNING] Multiple statements on one line (semicolon),"
                    f" incorrect output expected[/{c.op}]")
    get_dp_alias(caller.f_globals | caller.f_locals)
    same_line_call_cache = get_line_nodes(tree.body[0].value)
    return same_line_call_cache[0]


def debug_print(*objects):
    """
    Print the debug info of a line with expr on the left and result on the right

    :param objects: objects to debug
    :return: the same object back (tuple if multiple)
    """
    if not c.enabled:
        return objects if len(objects) > 1 else objects[0]

    global same_line_counter
    caller = inspect.currentframe().f_back
    line_no = caller.f_lineno
    file = caller.f_globals["__file__"]

    tree = prepare(line_no, file, caller)
    # check if starred is in the first layer, if so it means do dp to each element rather than return a whole

    tree_args = list(tree.args)
    args = []
    starred_index = []
    for i, arg in enumerate(tree_args):
        if isinstance(arg, ast.Starred):
            starred_index.append(i)
            args.extend(process_args(arg.value.elts))
    for index_to_pop in reversed(starred_index):
        tree_args.pop(index_to_pop)

    args.extend(process_args(tree_args))

    for arg, obj in zip(args, objects):
        be_print = c.print_hook(obj).replace('\n', '\n\t\t')
        console.print(f"\t{arg}: {be_print}")
    print()

    return objects if len(objects) > 1 else objects[0]


def get_dp_alias(caller_ns):
    for k, v in caller_ns.items():
        if v is dp:
            dp_alias.append(k)


def read_backward(file, guess, line_no) -> str:
    """
    Read the file backward and trying to fix unmatched ')'

    :param file: file path
    :param guess: string of existing line
    :param line_no: current line number
    :return: string of code that won't cause "unmatched ')'"
    """
    def eliminate_previous_dp(_guess):
        new_line = []
        for pre_line in _guess.split("\n")[:-1]:
            line = pre_line
            for alias in dp_alias:
                line = line.replace(alias, "a")
            new_line.append(line)
        return "".join(new_line) + _guess.split("\n")[-1]

    while True:
        line_no -= 1
        for char in linecache.getline(file, line_no).replace("\n", "\\n") \
                            .strip().replace("\\n", "\n")[::-1]:
            guess = char + guess
            try:
                ast.parse(guess)
                return eliminate_previous_dp(guess)
            except SyntaxError as e:
                if e.args[0] == "'(' was never closed":
                    return eliminate_previous_dp(guess)


def get_correct_tree(file, line_no) -> ast.AST:
    """
    Read a line first, if syntax error, read additional char one by one

    :param file: file path
    :param line_no: start line number
    :return: string of code that is syntactically correct
    """
    guess = linecache.getline(file, line_no).strip()
    try:
        return ast.parse(guess)
    except SyntaxError as e:  # not single line
        if e.args[0] == "unmatched ')'":
            guess = read_backward(file, guess, line_no)
            try:
                return ast.parse(guess)
            except SyntaxError:
                pass

    while True:
        line_no += 1
        for char in linecache.getline(file, line_no).replace("\n", "\\n") \
                            .strip().replace("\\n", "\n"):
            guess += char
            try:
                return ast.parse(guess)
            except SyntaxError:
                pass


def get_line_nodes(tree) -> list[ast.Call]:
    """
    Returns a list of nodes which every single element is call of dp,
    and follows order of operation.

    :param tree: AST tree
    :return: list of ast.Call
    """
    dps = []
    nodes = reverse_tree(tree)
    for call in nodes:
        try:
            func_name = call.func.id
        except AttributeError:
            continue
        if func_name in dp_alias:
            dps.append(call)
    dps = list(sorted(dps, key=lambda _tree: sort_by_recursion_level(_tree)))
    return dps


def sort_by_recursion_level(tree, level=0, budget=1):
    """
    Sort print calls from left to right, inner to outer

    :param budget: each recursion can add 1 level, so if a tree has two dp child nodes, only 1 level is added
    :param level: how many layers of dp the tree has
    :param tree: ast tree
    :return: the actual function used to sort
    """

    line_no = float("-inf") if not isinstance(tree, ast.Call) else tree.lineno
    offset = float("-inf") if not isinstance(tree, ast.Call) else tree.col_offset
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Call):
            try:
                if node.func.id in dp_alias and budget:
                    level += 1
                    budget -= 1
            except AttributeError:
                continue
        rec = sort_by_recursion_level(node, level)
        line_no, level, offset = max([(-line_no, level, offset), (-rec[0], *rec[1:])])
    return line_no, level, offset


def reverse_tree(tree) -> list[ast.Call]:
    """
    Returns a list of ast.Calls with the correct order of visiting

    :param tree: AST tree
    :return: list of nodes
    """
    node_with_depth = {tree: 0}

    def get_node_with_depth(_tree, depth=1):
        for node in ast.iter_child_nodes(_tree):
            node_with_depth[node] = depth
            get_node_with_depth(node, depth + 1)

    get_node_with_depth(tree)
    nodes = sorted(node_with_depth.keys(), key=lambda key: node_with_depth[key], reverse=True)
    nodes = filter(lambda node: isinstance(node, ast.Call), nodes)
    return list(nodes)


dp = debug_print
dp_conf = c

__all__ = ["dp", "dp_conf"]
