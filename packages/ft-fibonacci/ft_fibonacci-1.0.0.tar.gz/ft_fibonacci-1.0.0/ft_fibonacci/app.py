# Code file to perform fibonacci sequence calculation via recursion

def fibonacci(x: int) -> int:
    """
        Calculates fibonacci sequence with recursion
        Sample output: 0 1 1 2 3 5 8 ...
    """
    assert isinstance(x, int) and x >= 0, "Input x needs to be a positive integer"
    if x in (0, 1):
        return x
    return fibonacci(x - 1) + fibonacci(x - 2)

