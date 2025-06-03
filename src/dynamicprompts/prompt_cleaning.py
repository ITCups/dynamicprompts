import re
from pyparsing import (
    Optional, Literal, ZeroOrMore, Suppress, White, pyparsing_common
)

__all__ = ["clean_prompt"]

def remove_repeating_commas(text: str) -> str:
    return re.sub(r"([^\S\r\n]*,*)*,", ", ", text)

def remove_repeating_newline_space(text: str) -> str:
    return re.sub(r"[^\S\r\n]$", "\n", text)


def add_new_line_at_the_end(text: str) -> str:
    return text + "\n"

def remove_brackets_commas(text: str) -> str:
    # Define bracket types
    brackets = [
        (Literal("("), Literal(")")),
        (Literal("{"), Literal("}")),
        (Literal("["), Literal("]")),
    ]
    
    for open_bracket, close_bracket in brackets:
        # Pattern for comma right after opening bracket
        pattern = open_bracket + Suppress(Literal(",") + ZeroOrMore(White(ws=" \t\r")))
        text = pattern.transformString(text)
        
        # Pattern for comma right before closing bracket
        pattern = Suppress(ZeroOrMore(White(ws=" \t\r")) + Literal(",")) + close_bracket
        text = pattern.transformString(text)
    return text

def remove_empty_brackets(text: str) -> str:
    # Define bracket types
    brackets = [
        (Literal("("), Literal(")")),
        (Literal("["), Literal("]")),
    ]
    
    for open_bracket, close_bracket in brackets:
        # Pattern for comma right after opening bracket
        pattern = Suppress(open_bracket + (ZeroOrMore(Literal(",")) + ZeroOrMore(White()) + Optional(Literal(':')) + Optional(pyparsing_common.real())) + close_bracket + ZeroOrMore(Literal(",")))
        text = pattern.transformString(text)
    return text

def remove_symbols_commas(text: str) -> str:
    # Define bracket types
    symbols = [Literal(":")]
    for s in symbols:
        # Pattern for comma right after opening bracket
        pattern = Suppress(Literal(",") | ZeroOrMore(White(ws=" \t\r"))) + s + Suppress(Literal(",") | ZeroOrMore(White(ws=" \t\r")))
        text = pattern.transformString(text)
    return text

def strip_lines_from_whitespaces(text: str) -> str:
    return "\n".join([line.strip() for line in text.splitlines()])

def transfer_start_line_commas(text: str) -> str:
    def find_non_empty_line_index(line_arr: list[str], starting_index: int) -> int:
        """Iterates over array of strings backwards and returns index of first non empty line.
        Lines consisting of tabs and spaces are considered empty"""
        while starting_index >= 0:
            if not line_arr[starting_index].strip():
                starting_index -= 1
            else:
                return starting_index
        return -1
        
        
    lines = text.splitlines()
    cleaned_lines = []
    lines_to_add = []
    for i, _ in enumerate(lines):
        lines[i] = lines[i].strip()
        # Relocate leading commas
        if lines[i].startswith(","):
            non_empty_index = find_non_empty_line_index(lines, i)
            if non_empty_index > 0 and not lines[non_empty_index].endswith(','):
                lines[non_empty_index] = lines[non_empty_index] + ','
            lines[i] = lines[i].lstrip(',') # Remove the leading comma
            if not re.match("^\\s*$", lines[i]):
                lines_to_add.append(i)
        else:
            lines_to_add.append(i)
    for i in lines_to_add:
        cleaned_lines.append(lines[i])

    return "\n".join(cleaned_lines)

def clean_prompt(text: str):
    """
    Cleans the input text using pyparsing-based transformations.
    """
    # order is important here
    parsers = [
        remove_repeating_commas,
        strip_lines_from_whitespaces,
        remove_repeating_newline_space,
        transfer_start_line_commas,
        remove_brackets_commas,
        remove_symbols_commas,
        remove_empty_brackets,
        add_new_line_at_the_end
    ]
    parsed_text = text
    for p in parsers:
        parsed_text = p(parsed_text)
    return parsed_text