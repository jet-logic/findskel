import jmespath


class BooleanResult:
    """Wrapper for boolean expression results"""

    value: bool
    is_expression: bool = True

    def __init__(self, value: bool):
        assert value is None or isinstance(value, bool), f"value is {value.__class__.__name__}"
        self.value = value

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        if isinstance(other, BooleanResult):
            return self.value == other.value
        return self.value == other

    def __repr__(self):
        return str(1 if self.value else 0)

    def __str__(self):
        return str(1 if self.value else 0)


class QueryInterpreter(jmespath.visitor.TreeInterpreter):
    """Interpreter that wraps boolean expression results"""

    def _is_false(self, value):
        # This looks weird, but we're explicitly using equality checks
        # because the truth/false values are different between
        # python and jmespath.
        if isinstance(value, BooleanResult):
            return bool(value) is False
        return value == "" or value == [] or value == {} or value is None or value is False

    def visit_comparator(self, node, value):
        result = super().visit_comparator(node, value)
        return BooleanResult(result)

    def visit_and(self, node, value):
        result = super().visit_and(node, value)
        return BooleanResult(result)

    def visit_or(self, node, value):
        result = super().visit_or(node, value)
        return BooleanResult(result)

    # def visit_not(self, node, value):
    #     result = super().visit_not(node, value)
    #     return BooleanResult(result)
    def visit_not_expression(self, node, value):
        result = super().visit_not_expression(node, value)
        return BooleanResult(result)

    def visit_function_expression(self, node, value):
        result = super().visit_function_expression(node, value)
        # Wrap results from functions that return booleans
        if node["value"] in [
            "contains",
            "ends_with",
            "starts_with",
            "is_empty",
            "is_number",
            "is_string",
            "is_array",
            "is_object",
            "is_boolean",
        ]:
            return BooleanResult(result)
        return result

    # def __init__(self, use_not_found_sentinel=True):
    #     super().__init__()
    #     self.use_not_found_sentinel = use_not_found_sentinel
    # FieldNotFound
    def visit_field(self, node, value):
        # return super().visit_field(node, value)
        return value.get(node["value"])


class NotFoundSentinel:
    """Sentinel value for not found/missing fields"""

    path: str = None  # Optional path information

    # def __init__(self, value: bool):
    #     self.value = value
    def __bool__(self):
        return False

    def __repr__(self):
        return "NOT_FOUND"


NOT_FOUND = NotFoundSentinel()


class FalseResult(Exception):
    pass


class FieldNotFound(Exception):
    pass


def create_compiled_searcher(expression: str):
    """Create a compiled search function with boolean wrapping"""
    if not expression or not expression.strip():
        raise ValueError("Expression string cannot be empty")
    parser = jmespath.parser.Parser()
    parsed = parser.parse(expression).parsed
    interpreter = QueryInterpreter()

    def search(data):
        return interpreter.visit(parsed, data)

    # print(parsed)

    return search


# def visit_field(self, node, value):
#     try:
#         result = super().visit_field(node, value)
#         if result is None and self.use_not_found_sentinel:
#             return NotFoundSentinel(node['value'])
#         return result
#     except (AttributeError, KeyError):
#         return NOT_FOUND

# def visit_comparator(self, node, value):
#     result = super().visit_comparator(node, value)
#     return BooleanResult(result)

# def visit_and(self, node, value):
#     left = self.visit(node['children'][0], value)
#     if isinstance(left, NotFoundSentinel):
#         return left
#     if not left:
#         return BooleanResult(False)
#     right = self.visit(node['children'][1], value)
#     return BooleanResult(bool(right))

# def visit_or(self, node, value):
#     left = self.visit(node['children'][0], value)
#     if isinstance(left, NotFoundSentinel):
#         return left
#     if left:
#         return BooleanResult(True)
#     right = self.visit(node['children'][1], value)
#     return BooleanResult(bool(right))

# def visit_not(self, node, value):
#     result = self.visit(node['children'][0], value)
#     if isinstance(result, NotFoundSentinel):
#         return result
#     return BooleanResult(not result)

# def visit_index(self, node, value):
#     try:
#         return super().visit_index(node, value)
#     except (IndexError, TypeError):
#         return NOT_FOUND

# def visit_slice(self, node, value):
#     try:
#         return super().visit_slice(node, value)
#     except (IndexError, TypeError):
#         return NOT_FOUND
