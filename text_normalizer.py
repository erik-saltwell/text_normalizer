from FileNormalizer import *
from TextProcessor import *
from typing import Any
from os import path, listdir
from RegexHelper import *
from LineMatchHelper import *
from OpenAISummarizer import *
from ChapterComparer import *
from FileHelper import FileHelper


def main()->Any:
    input_dir = r"D:\tmp\dracula\src"
    output_dir = r"D:\tmp\dracula\target"
    files = [r"u000.txt", r"o000.txt"] #r"u001.txt", r"o001.txt",

    regex : RegexHelper = RegexHelper()


    original_file_path=path.join(output_dir, r"o000.txt")
    unredacted_file_path=path.join(output_dir, r"u000.txt")

    BaseNormalization(input_dir,output_dir, files, regex)
    dump_chapters("o000.txt", output_dir, "oc")
    dump_chapters("u000.txt", output_dir, "uc")

    oc_dir:str = path.join(output_dir, "oc")
    uc_dir:str = path.join(output_dir, "uc")

    LineMatchHelper.CreateFileWithoutExtraLines(path.join(uc_dir,"uc001.txt"), path.join(oc_dir, "oc001.txt"), "uc_trimmed001.txt", uc_dir, regex)

    #print_matched_chapters(path.join(output_dir,"oc"), path.join(output_dir, "uc"))

    #summarize_chapters(output_dir, ["oc","uc"])
    return

    
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
