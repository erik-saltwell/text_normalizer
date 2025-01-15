import difflib
from enum import Enum
from TextProcessor import *
from RegexHelper import *
from FileHelper import FileHelper
import Levenshtein



class LineMatchType(int, Enum):
    DO_NOT_MATCH=0,
    SHORT_MATCH=1,
    NORMAL_MATCH=2
    
class LineMatchHelper:

    @staticmethod
    def CreateFileWithoutExtraLines(source_file_path : str, target_file_path : str, output_file_name:str, output_dir:str, regex:RegexHelper )->None:
        #print("start")
        #print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

        source_text:str = FileHelper.LoadString(source_file_path)
        target_text:str = FileHelper.LoadString(target_file_path)
        trimmed_unredacted_text:str = LineMatchHelper.__FilterLinesBySimilarity(source_text, target_text, regex)
        FileHelper.SaveString(output_file_name, output_dir, trimmed_unredacted_text)
        #print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        #print("stop")

    @staticmethod
    def __FilterLinesBySimilarity(src: str, target: str, regex:RegexHelper) -> str:
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

        filtered_lines = LineMatchHelper.__GetMatches(src_lines, target_lines, regex)

        # Join the kept lines with newlines to form the filtered string
        return "\n".join(filtered_lines)

    @staticmethod 
    def __GetMatches(src_lines : list[str], target_lines : list[str], regex: RegexHelper)->list[str]:
        regular_threshold:float=0.75
        short_threshold:float = 0.5

        filtered_lines = []
        for s_line in src_lines:
            print('+')
            match_type:LineMatchType=LineMatchHelper.__ShouldCheckForMatch(s_line, regex)
            if match_type==LineMatchType.DO_NOT_MATCH:
                filtered_lines.append(s_line)
                continue
            threshold:float = regular_threshold
            if match_type==LineMatchType.SHORT_MATCH:
                threshold=short_threshold
            # Check against all lines in target to see if we find a "similar" line.
            for t_line in target_lines:
                if LineMatchHelper.__IsMatch(s_line, t_line, threshold):
                    filtered_lines.append(s_line)
                    break  # No need to check other lines in target once a match is found.
        return filtered_lines
        
    @staticmethod
    def __IsMatch(source:str,target:str, threshold:float)->float:
        if source.startswith('there were many things') and target.startswith('there were many things') :
            print('<debug>')
        similarity:float = difflib.SequenceMatcher(None, source, target).ratio()
        return_value:bool = similarity >=threshold
        return return_value

    @staticmethod
    def __ShouldCheckForMatch(line:str, regex:RegexHelper)->LineMatchType:
        shortest_match_len:int = 30
        short_match_len:int = 75
        line_len:int = len(line)
        if line_len <=short_match_len and TextProcessor.HasMatch(line, regex.SimpleDate):
            return LineMatchType.DO_NOT_MATCH
        if line_len <= short_match_len:
            return LineMatchType.SHORT_MATCH
        return LineMatchType.NORMAL_MATCH

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
    def jaccard_similarity(str1:str, str2:str)->float:
        set1 = set(str1.split())
        set2 = set(str2.split())
        intersection = float(len(set1.intersection(set2)))
        union = float(len(set1.union(set2)))
        similarity:float = intersection / union
        return similarity
    
    @staticmethod
    def levenshtein_similarity(str1:str,str2:str)->float:
        similarity:float = Levenshtein.ratio(str1, str2)
        return similarity
    
    @staticmethod
    def difflib_similarity(str1:str,str2:str)->float:
        similarity:float = difflib.SequenceMatcher(None, str1, str2).ratio()
        return similarity