from typing import NamedTuple
from os import path, makedirs
import difflib
from LineMatchHelper import *
import diagnostics

class ChapterMatchResult(NamedTuple):
    ChapterId:int
    Similarity:float

class ChapterComparer:
    @staticmethod
    def SaveChapters(src: str, output_dir : str, outfile_prefix:str)->None:
        ChapterComparer.ensure_directory_exists(path.join(output_dir, outfile_prefix))
        src_lines = src.splitlines()
        match : str = "chapter "
        nested_src_lines : list[list[str]] = LineMatchHelper.SplitLists(src_lines, match)
        n=0
        for chapter_lines in nested_src_lines:
            # outuput_lines:list[str]=[]
            # for line in chapter_lines:
            #     outuput_lines.append(line)
            #     outuput_lines.append("<empty_line>")
            output : str = "\n".join(chapter_lines)
            # assert diagnostics.is_healthy(output)
            file_path = path.join(output_dir, outfile_prefix, outfile_prefix+f"{n:03}"+".txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(output)
            n=n+1
        return
    

    @staticmethod
    def ensure_directory_exists(directory_path: str)->None:
        if not path.exists(directory_path):
            makedirs(directory_path)

    @staticmethod
    def FindMostSimilarChapter(src:str, targets:list[str])->ChapterMatchResult:
        return_value:int=-1
        best_similarity:float=-1.0
        for i in range(len(targets)):
            similarity = difflib.SequenceMatcher(None, src, targets[i]).ratio()
            if similarity > best_similarity:
                return_value=i
                best_similarity=similarity
        return ChapterMatchResult(return_value,best_similarity)

    @staticmethod
    def roman_to_int(roman:str)->int:
        """
        Convert a Roman numeral string to an integer.

        Args:
            roman (str): The Roman numeral string. Must be a valid Roman numeral.

        Returns:
            int: The integer representation of the input Roman numeral.
        """
        # Define a mapping of Roman numeral symbols to their values
        roman_to_value = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000
        }

        total = 0
        prev_value = 0

        # Iterate over the Roman numeral string in reverse order
        for char in reversed(roman):
            value = roman_to_value[char]
            if value < prev_value:
                total -= value  # Subtract if the current value is less than the previous one
            else:
                total += value  # Add otherwise
            prev_value = value

        return total