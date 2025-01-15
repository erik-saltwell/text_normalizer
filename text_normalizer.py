from FileNormalizer import *
from TextProcessor import *
from typing import Any
from os import path, listdir
from RegexHelper import *
from LineMatchHelper import *
from OpenAISummarizer import *
from ChapterComparer import *
from FileHelper import FileHelper
import time

def main()->Any:
    input_dir = r"D:\tmp\dracula\src"
    output_dir = r"D:\tmp\dracula\target"
    files = [r"u000.txt", r"o000.txt"] #r"u001.txt", r"o001.txt",

    regex : RegexHelper = RegexHelper()


    original_file_path=path.join(output_dir, r"o000.txt")
    unredacted_file_path=path.join(output_dir, r"u000.txt")

    BaseNormalization(input_dir,output_dir, files, regex)



    oc_dir:str = path.join(output_dir, "oc")
    uc_dir:str = path.join(output_dir, "uc")

    TrimExtraLines(uc_dir, oc_dir, "uc", "oc", "uc_trimmed", regex)
    TrimExtraLines(oc_dir, uc_dir, "oc", "uc_trimmed", "oc_trimmed", regex)


    dump_chapters("o000.txt", output_dir, "oc")
    dump_chapters("u000.txt", output_dir, "uc")

 #   similarity_file_name = "similarities.txt"
 #   processed_similarities_filename = "similarities_processed.txt"
 #   process_similarity_timings(output_dir, oc_dir, uc_dir, similarity_file_name, processed_similarities_filename)

    

    #LineMatchHelper.CreateFileWithoutExtraLines(path.join(uc_dir,"uc001.txt"), path.join(oc_dir, "oc001.txt"), "uc_trimmed001.txt", uc_dir, regex)

    #print_matched_chapters(path.join(output_dir,"oc"), path.join(output_dir, "uc"))

    #summarize_chapters(output_dir, ["oc","uc"])
    return

def TrimExtraLines(source_dir:str, target_dir:str, source_prefix:str, target_prefix:str, output_prefix:str, regex: RegexHelper)->None:
    for chapter_id in range(30):
        source_filename:str =path.join(source_dir, f"{source_prefix}{chapter_id:03}.txt")
        target_filename:str=path.join(target_dir, f"{target_prefix}{chapter_id:03}.txt")
        output_filename:str=path.join(source_dir, f"{output_prefix}{chapter_id:03}.txt")
        LineMatchHelper.CreateFileWithoutExtraLines(source_filename, target_filename, output_filename, source_dir, regex)
        print(chapter_id)

def process_similarity_timings(output_dir:str, source_dir:str, target_dir:str, similarity_file_name:str, processed_similarities_filename:str)->None:
    start_time=time.time()
    ctxt:MatchingContext=MatchingContext()
    transformer:SentenceTransformer = LineMatchHelper.CreateTransformer()
    ctxt.SetTransformer(transformer)
    similarity_typenames:list[str]=["jaccard", "levenshtein", "sentence_transformer"]
    for similarity_typename in similarity_typenames:
        with open(path.join(output_dir, similarity_typename+"_"+similarity_file_name), 'w', encoding='utf-8') as f:
            for i in range(30):
                if i==17 or i==18:
                    continue
                oc_file = path.join(source_dir, f"oc{i:03}.txt")
                uc_file = path.join(target_dir, f"uc{i:03}.txt")
                
                similarity_funcs:dict[str, Callable[[MatchingContext, int, int], float]]={}
                similarity_funcs[similarity_typenames[0]]=lambda ctxt, src, tgt: LineMatchHelper.jaccard_similarity(ctxt, src, tgt)
                similarity_funcs[similarity_typenames[1]]=lambda ctxt, src, tgt: LineMatchHelper.levenshtein_similarity(ctxt, src, tgt)
                similarity_funcs[similarity_typenames[2]]=lambda ctxt, src, tgt: LineMatchHelper.sentence_transformer_similarity(ctxt, src, tgt)

                LineMatchHelper.DumpSimilarities(ctxt,f, uc_file, oc_file, similarity_typename,similarity_funcs[similarity_typename])
                f.flush()
                print(i)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken: {elapsed_time:.3f} seconds")
        #LineMatchHelper.process_file_into_buckets(path.join(output_dir, similarity_typename+"_"+similarity_file_name), path.join(output_dir, similarity_typename+"_"+processed_similarities_filename))

    
    #TrimExtraLines("o000.txt", "u000.txt", output_dir, .9, "90")
    # for i in range(75,100,1):
    #     n=i+1
    #     floatN = float(n) / 100.0
    #     strN = str(n)
    #     TrimExtraLines("o000.txt", "u000.txt", output_dir, floatN, strN)

def print_matched_chapters(original_dir:str, unredactred_dir:str)->None:
    originals = load_files_to_strings(original_dir)
    unredacteds = load_files_to_strings(unredactred_dir)
    print_matched_chaptersd_for_side(originals,unredacteds,"original")
    print_matched_chaptersd_for_side(unredacteds,originals,"unredacted")
    return

def print_matched_chaptersd_for_side(sources:list[str], targets:list[str], tag:str)->None:
    for i in range(len(sources)):
        result:ChapterMatchResult = ChapterComparer.FindMostSimilarChapter(sources[i], targets)
        print(f"{tag}\t{i:03}\t{result.ChapterId:03}\t{result.Similarity}")

def load_files_to_strings(directory):
    """
    Load all files in a directory into a list of strings, sorted alphabetically by filename.

    Args:
        directory (str): The path to the directory containing the files.

    Returns:
        list: A list of strings, where each string contains the content of a file.
    """
    file_contents = []
    
    # Get all file names in the directory and sort them alphabetically
    filenames = sorted(f for f in listdir(directory) if path.isfile(path.join(directory, f)))
    
    # Read the content of each file and store it in the list
    for filename in filenames:
        file_path = path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            file_contents.append(file.read())
    
    return file_contents

def summarize_chapters(dir:str, prefixes:list[str])->None:
    for prefix in prefixes:
        summaries:list[str] = summarize_chapters_for_prefix(dir,prefix)
        for i in range(len(summaries)):
            print(f"{prefix}\t{i:03}\t{summaries[i]}")

def summarize_chapters_for_prefix(dir:str, prefix:str)->list[str]:
    return_value:list[str] = []
    n:int=0
    filename:str = f"{prefix}{n:03}.txt"
    filepath:str = path.join(dir,filename)
    while path.exists(filepath):
        summary:str = OpenAISummarizer.LoadAndSummarize(dir, filename)
        summary_obj:Any = OpenAISummarizer.extract_json(summary)
        summary = OpenAISummarizer.get_last_denser_summary(summary_obj)
        return_value.append(summary)
        print(f"{prefix}\t{n:03}\t{summary}")
        n=n+1
        filename = f"{prefix}{n:03}.txt"
        filepath = path.join(dir,filename)
    return return_value
    

def dump_chapters(file_name : str,output_dir:str, output_prefix:str)->None:
    file_path=path.join(output_dir, file_name)
    text : str = FileHelper.LoadString(file_path)
    ChapterComparer.SaveChapters(text, output_dir, output_prefix)
    return

def BaseNormalization(input_dir:str, output_dir:str, files : List[str], regex:RegexHelper)->None:
    for file_name in files:
        full_path = path.join(input_dir, file_name)
        rename_late_chapters = False
        if file_name == r"o000.txt":
            rename_late_chapters=True
        FileNormalizer.ProcessFile(full_path, output_dir, regex, rename_late_chapters)

if __name__ == "__main__":
    main()
