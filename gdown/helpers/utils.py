def indent(text: str, prefix: str) -> str:
    """Indent each line of a given text with a specified prefix.

    Parameters
    ----------
    text : str
        The input text to be indented.
    prefix : str
        The prefix to add at the beginning of each non-empty line.

    Returns
    -------
    str
        The indented text with the prefix applied to each non-empty line.
    """

    def prefixed_lines() -> str:
        for line in text.splitlines(True):
            yield (prefix + line if line.strip() else line)

    return "".join(prefixed_lines())
