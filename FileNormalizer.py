from TextProcessor import *
from typing import List 
from os import path
from RegexHelper import *

class FileNormalizer:
    filename : str
    text : str
    regex : RegexHelper

    def __init__(self, file_path:str, regex : RegexHelper):
        self.text = FileNormalizer.LoadString(file_path)
        self.filename = path.basename(file_path)
        self.regex = regex
    
    @staticmethod 
    def ProcessFile(input_file_path:str, output_dir:str, regex : RegexHelper, rename_late_chapters:bool=False)->None:
        file = FileNormalizer(input_file_path, regex)   
        file.Lowercase()
        if rename_late_chapters:
            file.RenameLatechapters()

        file.NormalizeTimes()
        file.RemoveTripleStar()
        
        file.RemoveAnnotations()
        file.UpdateWordReplacements()
        #file.RemovePunctuation()
        
        file.UpdateChapterHeadings()
        
        file.PutBackTimeDelimeter()
        file.RemoveLeadingWhiteSpaceInLine()

        file.RemoveDoubleSpace()
        file.StripEmptyLines()
        file.Sentencize()
        file.TrimLeadingNewlines()

        file.Save(output_dir)
    


    @staticmethod    
    def LoadString(file_path : str)->str:
        output:str = ''
        with open(file_path, 'r', encoding='utf-8') as f:
            output = f.read()
        return output
    
    def TokenizeSentences(self, text : str) -> List[str]:
        sentences = self.regex.split_into_sentences(self.text)
        return sentences
        #nlp = spacy.load("en_core_web_sm")
        #text_spacy = nlp(text)
        #output = [str(sentence) for sentence in text_spacy.sents ]
        #return output
    
    def RemoveLeadingWhiteSpaceInLine(self)->None:
        output : str = TextProcessor.Remove(self.regex.LeadingWhiteSpace, self.text)
        self.text= output

    def Lowercase(self)->None:
        output:str = TextProcessor.Lowercase(self.text)
        self.text = output

    def Save(self, output_dir:str)->None:
        FileNormalizer.SaveText(self.filename, output_dir, self.text)

    def StripEmptyLines(self)->None:
        lines : List[str] = self.text.splitlines()
        filtered_lines : List[str] = [line for line in lines if line.strip()]
        self.text = "\n".join(filtered_lines)

    def RemoveAnnotations(self)->None:
        output : str = TextProcessor.Remove(self.regex.Annotation, self.text)
        self.text = output

    def RemovePunctuation(self)->None:
        output:str = TextProcessor.Remove(self.regex.Punctuation, self.text)
        output = TextProcessor.RemoveChars(output, "—:,")
        self.text = output

    def Sentencize(self)->None:
        output:str = self.text 
        lines : List[str] = self.TokenizeSentences(output)
        output = "\n".join(lines)
        self.text=output
    
    def RemoveChapterHeading(self)->None:
        output:str = TextProcessor.Remove(self.regex.ChapterHeading, self.text)
        self.text = output

    def UpdateChapterHeadings(self)->None:
        output:str = TextProcessor.Replace(self.regex.ChapterHeading, r'<stop>\1<stop>' ,self.text)
        self.text = output

    def NormalizeTimes(self)->None:
        output : str = self.regex.DotTime.sub(r'\1@@\2', self.text)   #the '@@ will be replaced in a later step after removing spurious ':'s
        self.text = output

    def PutBackTimeDelimeter(self)->None:
        output : str =  TextProcessor.Replace(self.regex.DoubleAt, ":", self.text)
        self.text = output

    def UpdateWordReplacements(self)->None:
        output : str = self.text
        for replacement in self.regex.WordReplacements:
            output = TextProcessor.Replace(replacement.Pattern, replacement.NewString, output)
        self.text = output

    def TrimLeadingNewlines(self)->None:
        output:str = self.text
        while output[0]=='\n' or output[0]=='\r':
            output = output[1:]
        self.text=output

    def RemoveTripleStar(self)->None:
        output:str = self.text
        output = TextProcessor.Remove(self.regex.TripleStar, output)
        self.text=output

    def RemoveDoubleSpace(self)->None:
        output:str = self.text
        output = TextProcessor.Replace(self.regex.DoubleSpace, ' ', output)
        self.text=output

    def RenameLatechapters(self)->None:
        output:str = self.text  
        chapter_start = r'chapter '
        chapter_end_slug :str='<chapter_end>'
        output = self.regex.ChapterHeading.sub(r'\1'+chapter_end_slug, output)
        chapter_title_texts:dict[int,str] = {}
        for x in range(1,30):
            title_text = chapter_start+FileNormalizer.int_to_roman(x).lower()+chapter_end_slug
            chapter_title_texts[x]=title_text
        
        for id in range(27,16,-1):
            output = output.replace(chapter_title_texts[id],chapter_title_texts[id+2])
        output = output.replace(chapter_title_texts[19], f"{chapter_title_texts[17]}\n{chapter_title_texts[18]}\n{chapter_title_texts[19]}")
        output = output.replace(chapter_end_slug, '')
        self.text=output

    @staticmethod
    def SaveText(filename:str, output_dir : str, text : str)->None:
        file_path = path.join(output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            output = f.write(text)

    @staticmethod
    def int_to_roman(num:int)->str:
        """
        Convert an integer to a Roman numeral.

        Args:
            num (int): The integer to be converted. Must be between 1 and 3999.

        Returns:
            str: The Roman numeral representation of the input integer.
        """
        if not (1 <= num <= 3999):
            raise ValueError("Input must be an integer between 1 and 3999.")

        # Define Roman numeral symbols and their values
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        symbols = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]

        roman_numeral = ""
        for i in range(len(val)):
            while num >= val[i]:
                roman_numeral += symbols[i]
                num -= val[i]

        return roman_numeral
    

