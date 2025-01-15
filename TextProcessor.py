#from pydantic import BaseModel
#from enum import Enum
#from functools import total_ordering

import re

class TextProcessor:
    @staticmethod
    def Remove(pattern : re.Pattern, input : str)->str:
        output : str =  re.sub(pattern, '', input)
        return output

    @staticmethod
    def Replace (pattern : re.Pattern, replacement : str, input : str)->str:
        output : str =  re.sub(pattern, replacement, input)
        return output

    @staticmethod
    def Lowercase (input:str)-> str:
        output:str = input.lower()
        return output
    
    @staticmethod
    def RemoveChars(text:str, chars : str)->str:
        # Convert list of chars to a set for faster lookups
        chars_to_remove = set(chars)
    
        # Keep only the characters not in chars_to_remove
        return "".join(ch for ch in text if ch not in chars_to_remove)

    @staticmethod
    def HasMatch(text:str, pattern:re.Pattern)->bool:
        return bool(pattern.search(text))