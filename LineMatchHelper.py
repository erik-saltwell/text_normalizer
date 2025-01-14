import difflib
from os import path
from typing import NamedTuple

class ChapterMatchResult(NamedTuple):
    ChapterId:int
    Similarity:float

class LineMatchHelper:
    @staticmethod
    def filter_lines_by_similarity(src: str, target: str, min_diff_threshold: float) -> str:
        """
        Returns a copy of `src` where lines have been removed if there are no lines in `target`
        that are similar to the line in `src`, based on `min_diff_threshold`.
        
        :param src: The source string (with one or more lines).
        :param target: The target string (with one or more lines).
        :param min_diff_threshold: The minimum similarity ratio between 0.0 and 1.0
                                (e.g., 0.8 means 80% similar).
        :return: A filtered string containing only those lines from `src` that have
                at least one "similar" match in `target`.
        """

        src_lines = src.splitlines()
        target_lines = target.splitlines()
        #list_target_lines = list(target_lines)

        filtered_lines = LineMatchHelper.__GetMatched(src_lines, target_lines, min_diff_threshold)

        # Join the kept lines with newlines to form the filtered string
        return "\n".join(filtered_lines)
    
    @staticmethod
    def SaveChapters(src: str, output_dir : str, outfile_prefix:str)->None:
        src_lines = src.splitlines()
        match : str = "chapter "
        nested_src_lines : list[list[str]] = LineMatchHelper.SplitLists(src_lines, match)
        n=0
        for chapter_lines in nested_src_lines:
            output : str = "\n".join(chapter_lines)
            file_path = path.join(output_dir, outfile_prefix+f"{n:03}"+".txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(output)
            n=n+1
        return

    @staticmethod
    def __GetMatched(src_lines : list[str], target_lines : list[str], min_diff_threshold : float)->list[str]:
        match : str = "chapter "
        nested_src_lines : list[list[str]] = LineMatchHelper.SplitLists(src_lines, match)
        nested_target_lines : list[list[str]] =  LineMatchHelper.SplitLists(target_lines, match)
        LineMatchHelper.__TraceChapters(nested_src_lines, "src")
        LineMatchHelper.__TraceChapters(nested_target_lines, "target")

        src_count = len(nested_src_lines)
        t_count = len(nested_target_lines)
        
        assert len(nested_src_lines) == len(nested_target_lines)
        count:int = len(nested_src_lines)
        return_value : list[str]=list([])

        base_line_num : int=0
        for i in range(count):
            next_filtered_lines = LineMatchHelper.__GetMatchedFromSingleList(nested_src_lines[i], nested_target_lines[i], min_diff_threshold, base_line_num)
            for next in next_filtered_lines:
                return_value.append(next)
            base_line_num = base_line_num + len(next_filtered_lines)
        return return_value
    
    @staticmethod
    def __TraceChapters(chapters : list[list[str]], name:str)->None:
        print("***** " + name + " *****")
        for chapter in chapters:
            print(chapter[0])
            for i in range(1, min(7, len(chapter)-1),1):
                print("\t"+chapter[i])


    @staticmethod 
    def __GetMatchedFromSingleList(src_lines : list[str], target_lines : list[str], min_diff_threshold : float, base_line_num: int)->list[str]:
        filtered_lines = []
        n = 0

        for s_line in src_lines:
            n=n+1
            print(base_line_num+n)
            # Check against all lines in target to see if we find a "similar" line.
            for t_line in target_lines:
                similarity = difflib.SequenceMatcher(None, s_line, t_line).ratio()
                if similarity >= min_diff_threshold:
                    filtered_lines.append(s_line)
                    break  # No need to check other lines in target once a match is found.
        return filtered_lines

    @staticmethod 
    def SplitLists(src : list[str], check: str)->list [ list[str] ]:
        return_value : list[ list[str]] = []
        current : list[str] = []
        for line in src:
            if line.startswith(check):
                #print(line)
                return_value.append(current)
                current=[]
            current.append(line)
        return_value.append(current)
        return return_value
    
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