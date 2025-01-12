from FileNormalizer import *
from TextProcessor import *
from typing import Any
from os import path
from RegexHelper import *

def main()->Any:
    input_dir = r"D:\tmp\dracula\src"
    output_dir = r"D:\tmp\dracula\target"
    files = [r"u001.txt", r"o001.txt",r"u000.txt", r"o000.txt"]

    regex : RegexHelper = RegexHelper()

    for file_name in files:
        full_path = path.join(input_dir, file_name)
        FileNormalizer.ProcessFile(full_path, output_dir, regex)

if __name__ == "__main__":
    main()
