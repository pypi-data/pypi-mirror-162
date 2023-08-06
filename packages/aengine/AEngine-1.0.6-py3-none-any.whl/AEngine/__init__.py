import rich
from AEngine.Data import String


def print(text, color=""):
    pre = f"[{color}]" if color else ""
    post = f"[/{color}]" if color else ""
    rich.print(pre + str(text) + post)
