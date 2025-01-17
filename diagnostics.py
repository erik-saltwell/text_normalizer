def extract_text(text: str, substring: str, length: int=50) -> str:
    """
    Searches for `substring` in `text`. If found, returns a substring of `length` characters
    starting from the found position. If not found, returns "<not_found>".

    :param text: The main string to search within.
    :param substring: The substring to look for.
    :param length: The number of characters to return from the found position.
    :return: The extracted substring or "<not_found>" if the substring is not found.
    """
    index = text.find(substring)
    
    if index == -1:
        return "<not_found>"
    
    return text[index:index + length]

def has_empty_lines(text: str) -> bool:
    """
    Checks if the given text contains any empty lines (ignoring whitespace).

    :param text: The input string.
    :return: True if there is at least one empty line, False otherwise.
    """
    lines = text.split("\n")  # Split the text into lines
    return any(line.strip() == "" for line in lines)  # Check if any line is empty after stripping whitespace

def contains_any(text: str, *substrings) -> bool:
    """
    Checks if any of the given substrings exist in the provided text.

    :param text: The main string to search within.
    :param substrings: An arbitrary number of substrings to look for.
    :return: True if at least one substring is found, False otherwise.
    """
    return any(substring in text for substring in substrings)

def contains_all(text: str, *substrings) -> bool:
    """
    Checks if any of the given substrings exist in the provided text.

    :param text: The main string to search within.
    :param substrings: An arbitrary number of substrings to look for.
    :return: True if at least one substring is found, False otherwise.
    """
    return all(substring in text for substring in substrings)

def is_healthy(text:str)->bool:
    if contains_any(text, 'mr.', 'mrs.', 'dr.'): 
            return False
    if(has_empty_lines(text)):
        return False
    return True