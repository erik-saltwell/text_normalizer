from FileNormalizer import *
from TextProcessor import *
from typing import Any
from os import path
from RegexHelper import *
from LineMatchHelper import *

from datetime import datetime


def main()->Any:
    input_dir = r"D:\tmp\dracula\src"
    output_dir = r"D:\tmp\dracula\target"
    files = [r"u001.txt", r"o001.txt",r"u000.txt", r"o000.txt"]

    regex : RegexHelper = RegexHelper()

    BaseNormalization(input_dir,output_dir, files, regex)

    original_file_path=path.join(output_dir, r"o000.txt")
    unredacted_file_path=path.join(output_dir, r"u000.txt")

    dump_chapters("o000.txt", output_dir, "oc")
    dump_chapters("u000.txt", output_dir, "uc")
#    TrimExtraLines("o000.txt", "u000.txt", output_dir, .9, "90")
    # for i in range(75,100,1):
    #     n=i+1
    #     floatN = float(n) / 100.0
    #     strN = str(n)
    #     TrimExtraLines("o000.txt", "u000.txt", output_dir, floatN, strN)

def dump_chapters(file_name : str,output_dir:str, output_pref:str)->None:
    file_path=path.join(output_dir, file_name)
    text : str = FileNormalizer.LoadString(file_path)
    LineMatchHelper.SaveChapters(text, output_dir, output_pref)
    return

def TrimExtraLines(original_file_name : str, unredacted_file_name : str, output_dir:str, threshold : float, output_file_tag : str)->None:
    print("start")
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    original_file_path=path.join(output_dir, original_file_name)
    unredacted_file_path=path.join(output_dir, unredacted_file_name)

    original_text = FileNormalizer.LoadString(original_file_path)
    unredacted_text = FileNormalizer.LoadString(unredacted_file_path)
    trimmed_unredacted_text = LineMatchHelper.filter_lines_by_similarity(unredacted_text, original_text, threshold)
    FileNormalizer.SaveText("u"+output_file_tag+"t000.txt", output_dir, trimmed_unredacted_text)
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    print("stop")

def BaseNormalization(input_dir:str, output_dir:str, files : List[str], regex:RegexHelper)->None:
    for file_name in files:
        full_path = path.join(input_dir, file_name)
        FileNormalizer.ProcessFile(full_path, output_dir, regex)

if __name__ == "__main__":
    main()
