import re
from typing import NamedTuple

class WordReplacement(NamedTuple):
    Pattern : re.Pattern
    NewString : str

class RegexHelper:
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|edu|me)"
    digits = "([0-9])"
    multiple_dots = r'\.{2,}'

    LeadingWhiteSpace : re.Pattern
    Annotation : re.Pattern
    Punctuation : re.Pattern
    ChapterHeading : re.Pattern
    DotTime : re.Pattern
    DoubleAt : re.Pattern
    WordReplacements : list[WordReplacement]    
    TripleStar : re.Pattern
    DoubleSpace : re.Pattern

    def __init__(self):
        self.LeadingWhiteSpace = re.compile(r'^[ \t]+', re.MULTILINE)
        self.Annotation = re.compile(r'\[[^\]]*\]', re.MULTILINE)
        self.Punctuation = re.compile(r'[\'\*"‘’“”-]+')
        self.ChapterHeading = re.compile(r'(chapter [ixv]+)([\.]?)')
        self.DotTime = re.compile(r'(\d+)[\.:](\d+)')                                     
        self.DoubleAt = re.compile(r'@@')
        self.TripleStar = re.compile(r'\* \* \*')
        self.DoubleSpace = re.compile(r'[ \t]+')

        self.WordReplacements = []
        self.WordReplacements.append(WordReplacement(re.compile("housemade"), "homemade"))
        self.WordReplacements.append(WordReplacement(re.compile("st\."), "st"))
        self.WordReplacements.append(WordReplacement(re.compile("mem\."), "mem"))
        self.WordReplacements.append(WordReplacement(re.compile("dr\."), "dr"))
        self.WordReplacements.append(WordReplacement(re.compile("hon\."), "hon"))

    def replace_all_matches(self, pattern, replacement, text):
        return re.sub(pattern, replacement, text)


    def split_into_sentences(self, text: str):
        #text = "(Spiders at present are his hobby, and the notebook is filling up with columns of small figures.) To "

        text = " " + text + "  "
        text = text.replace("\n","")
        text= text.replace("\r" ,"")
        text = re.sub(self.prefixes,"\\1<prd>",text)
        text = re.sub(self.websites,"<prd>\\1",text)
        text = re.sub(self.digits + "[.]" + self.digits,"\\1<prd>\\2",text)
        text = re.sub(self.multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
        if "Ph.D" in text: 
            text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + self.alphabets + "[.] "," \\1<prd> ",text)
        text = re.sub(self.acronyms+" "+self.starters,"\\1<stop> \\2",text)
        text = re.sub(self.alphabets + "[.]" + self.alphabets + "[.]" + self.alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(self.alphabets + "[.]" + self.alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+self.suffixes+"[.] "+self.starters," \\1<stop> \\2",text)
        text = re.sub(" "+self.suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + self.alphabets + "[.]"," \\1<prd>",text)
        text = text.replace("Mem.", "Remember")
        text = text.replace("Remember,d ", "Remember")

        text = self.replace_all_matches(',[A-Za-z] ', ', ', text)

        for punct in ['.', '?', '!']:
            for quot in ["'", '"', '’', '”', ')',']']:
                text=text.replace(punct + quot, quot+punct)
        text = text.replace("<stop><stop>","<stop>")

        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = [s.strip() for s in sentences]
        if sentences and not sentences[-1]: 
            sentences = sentences[:-1]
        return sentences
