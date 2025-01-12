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
    def ProcessFile(input_file_path:str, output_dir:str, regex : RegexHelper)->None:
        file = FileNormalizer(input_file_path, regex)   
        file.Lowercase()
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

    @staticmethod
    def SaveText(filename:str, output_dir : str, text : str)->None:
        file_path = path.join(output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            output = f.write(text)