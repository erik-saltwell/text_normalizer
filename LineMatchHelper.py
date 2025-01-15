import difflib
from enum import Enum
from TextProcessor import *
from RegexHelper import *
from FileHelper import FileHelper
import Levenshtein
from sentence_transformers import SentenceTransformer, util
from typing import NamedTuple, TextIO, Optional, Callable
import numpy as np

class EmbeddingsData(NamedTuple):
    source_embeddings:list[np.ndarray]
    target_embeddings:list[np.ndarray]

class LineMatchType(int, Enum):
    DO_NOT_MATCH=0,
    SHORT_MATCH=1,
    NORMAL_MATCH=2

class MatchingContext:
    Transformer:Optional[SentenceTransformer]
    Source_Sentences:list[str]
    Target_Sentences:list[str]
    Source_Embeddings:list[np.ndarray]
    Target_Embeddings:list[np.ndarray]
    Source_WordSets:list[set[str]]
    Target_WordSets:list[set[str]]

    def __init__(self) -> None:
        self.Transformer=None

    def SetTransformer(self, transformer:SentenceTransformer)->None:
        self.Transformer=transformer

    def SetText(self, source:str, target:str)->None:
        self.Source_Sentences = source.splitlines()
        self.Target_Sentences = target.splitlines()

        self.Source_WordSets=[]
        self.Target_WordSets=[]
        for i in range(len(self.Source_Sentences)):
            self.Source_WordSets.append(set(self.Source_Sentences[i].split()))

        for i in range(len(self.Target_Sentences)):
            self.Target_WordSets.append(set(self.Target_Sentences[i].split()))

        if self.Transformer is not None:
            source_embeddings: np.ndarray = self.Transformer.encode(self.Source_Sentences)
            target_embeddings: np.ndarray = self.Transformer.encode(self.Target_Sentences)
            self.Source_Embeddings = [embedding for embedding in source_embeddings]
            self.Target_Embeddings=[embedding for embedding in target_embeddings]

    
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

        ctxt:MatchingContext =MatchingContext()
        ctxt.SetText(src,target)
        filtered_lines = LineMatchHelper.__GetMatches(ctxt, regex)

        # Join the kept lines with newlines to form the filtered string
        return "\n".join(filtered_lines)

    @staticmethod 
    def __GetMatches(ctxt: MatchingContext, regex: RegexHelper)->list[str]:
        regular_threshold:float=0.45
        short_threshold:float = 0.35

        filtered_lines = []
        for current_source_line in range(len(ctxt.Source_Sentences)):
            match_type:LineMatchType=LineMatchHelper.__ShouldCheckForMatch(ctxt, current_source_line, regex)
            if match_type==LineMatchType.DO_NOT_MATCH:
                filtered_lines.append(ctxt.Source_Sentences[current_source_line])
                continue
            threshold:float = regular_threshold
            if match_type==LineMatchType.SHORT_MATCH:
                threshold=short_threshold
            # Check against all lines in target to see if we find a "similar" line.
            for current_target_line in range(len(ctxt.Target_Sentences)):
                if LineMatchHelper.__IsMatch(ctxt, current_source_line, current_target_line, threshold):
                    filtered_lines.append(ctxt.Source_Sentences[current_source_line])
                    break  # No need to check other lines in target once a match is found.
        return filtered_lines
        
    @staticmethod
    def __IsMatch(ctxt: MatchingContext, current_source_line:int, current_target_line:int, threshold: float)->bool:
        #if source.startswith('there were many things') and target.startswith('there were many things') :
        #   print('<debug>')
        similarity:float = LineMatchHelper.jaccard_similarity(ctxt, current_source_line, current_target_line)
        return_value:bool = similarity >=threshold
        return return_value

    @staticmethod
    def __ShouldCheckForMatch(ctxt: MatchingContext, current_source_line:int, regex:RegexHelper)->LineMatchType:
        shortest_match_len:int = 30
        short_match_len:int = 50
        line:str = ctxt.Source_Sentences[current_source_line]
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
    def jaccard_similarity(ctxt:MatchingContext, current__source_line:int, current_target_line:int)->float:
        src_set = ctxt.Source_WordSets[current__source_line]
        target_set = ctxt.Target_WordSets[current_target_line]
        intersection = float(len(src_set.intersection(target_set)))
        union = float(len(src_set.union(target_set)))
        similarity:float = intersection / union
        return similarity
    
    @staticmethod
    def levenshtein_similarity(ctxt:MatchingContext, current__source_line:int, current_target_line:int)->float:
        similarity:float = Levenshtein.ratio(ctxt.Source_Sentences[current__source_line], ctxt.Target_Sentences[current_target_line])
        return similarity
    
    @staticmethod
    def difflib_similarity(ctxt:MatchingContext, current__source_line:int, current_target_line:int)->float:
        similarity:float = difflib.SequenceMatcher(None, ctxt.Source_Sentences[current__source_line], ctxt.Target_Sentences[current_target_line]).ratio()
        return similarity

    @staticmethod
    def sentence_transformer_similarity(ctxt:MatchingContext, current__source_line:int, current_target_line:int)->float:
        similarity:float = util.cos_sim(ctxt.Source_Embeddings[current__source_line], ctxt.Target_Embeddings[current_target_line]).item()
        similarity = (similarity + 1.0)/2.0 
        return similarity
    
    @staticmethod
    def CreateTransformer()->SentenceTransformer:
        model:SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')
        return model


    @staticmethod 
    def DumpSimilarities( ctxt:MatchingContext, file:TextIO, source_file:str, target_file:str, algorithm_name:str, similarity_func: Callable[[MatchingContext, int, int], float])->None:
        source:str = FileHelper.LoadString(source_file)
        target:str = FileHelper.LoadString(target_file)
        ctxt.SetText(source, target)
        for source_line_number in range(len(ctxt.Source_Sentences)):
            scores:list[float]=[]
            for target_line_number in range(len(ctxt.Target_Sentences)):
                similarity:float = similarity_func(ctxt, source_line_number, target_line_number)
                scores.append(similarity)
            max_similarity:int = (int(max(scores)*100) //5 )*5
            line_len:int = len(ctxt.Source_Sentences[source_line_number])
            line_len=line_len//10
            line_len=line_len*10
            file.write(f"{algorithm_name}\t{line_len}\t{max_similarity:02}\n")

    @staticmethod
    def process_file_into_buckets(file_path: str, output_path: str) -> None:
        """
        Processes a file containing floating point numbers between 0 and 1, counts how many
        rows fall into 20 buckets (0.00-0.05, 0.05-0.10, ..., 0.95-1.00), and writes the results to an output file.
        
        Args:
            file_path (str): The path to the input file.
            output_path (str): The path to the output file where results will be written.
        
        Returns:
            None
        """
        # Initialize 20 buckets, each representing a range of 0.05
        bucket_counts = [0] * 20
        
        # Read and process each line in the input file
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    number = float(line.strip())
                    if 0 <= number <= 1:
                        # Determine which bucket the number belongs to
                        bucket_index = min(int(number // 0.05), 19)
                        bucket_counts[bucket_index] += 1
                except ValueError:
                    # Skip lines that can't be converted to a float
                    continue
        
        # Write the results to the output file
        with open(output_path, 'w') as output_file:
            for i, count in enumerate(bucket_counts):
                bucket_range = f"{i * 0.05:.2f}-{(i + 1) * 0.05:.2f}"
                output_file.write(f"{bucket_range}: {count}\n")

