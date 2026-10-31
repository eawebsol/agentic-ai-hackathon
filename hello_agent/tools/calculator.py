def calculate(expression: str) -> dict:
    """
    Evaluate a basic mathematical expression.

    Args:
        expression: Mathematical expression, such as "25 * 4 + 10".

    Returns:
        Dictionary containing the calculation result.
    """
    import ast
    import operator

    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in operations:
            return operations[type(node.op)](
                evaluate(node.left), evaluate(node.right)
            )

        if isinstance(node, ast.UnaryOp) and type(node.op) in operations:
            return operations[type(node.op)](evaluate(node.operand))

        raise ValueError("Unsupported mathematical expression")

    try:
        if len(expression) > 200:
            raise ValueError("Expression is too long")

        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree.body)

        if isinstance(result, (int, float)) and abs(result) > 1e100:
            raise ValueError("Result is too large")

        return {"expression": expression, "result": result}

    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as error:
        return {"expression": expression, "error": str(error)}
