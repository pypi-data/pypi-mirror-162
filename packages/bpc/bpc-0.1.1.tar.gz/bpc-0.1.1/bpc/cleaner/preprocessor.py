import re
import string
import emoji
from typing import List

from .converter import Converter
from myanmartools import ZawgyiDetector


class Preprocessor:
    """
    This class contains common preprocessing functions for Myanmar Language.

    Example:
        အချို့သော အကြောင်းအရာများကို အသုံးပြုပါသည်။ 😄 https://github.com/1chimaruGin/burmese_phoneme
        
    Output:
        အချို့သော အကြောင်းအရာများကို အသုံးပြုပါသည်

    Usage :
     For all preprocessing
     >>> preprocessor = Preprocessor()
     >>> preporcessor.preprocess()
     For specific preprocessing
     >>> preprocessor = Preprocessor()
     >>> preprocessor.removeLinks() # [zawgyi2unicode, unicode2zawgyi, cleanSentence, removePunctuation, removeEmoji, removeNumeric]
    """

    def __init__(self) -> None:
        self.detector = ZawgyiDetector()
        self.converter = Converter()

    def detectZawgyi(self, sentence: str) -> bool:
        """
        Detect based on score, mm words and sentence length
        args: 
            sentence <str>
        return: 
            mask <bool>
            False unicode
            True Zawgyi
        """
        unicode_score = 0.5
        score = self.detector.get_zawgyi_probability(sentence)
        if score <= unicode_score:
            mask = False
        else:
            mask = True
        return mask

    def zawgyi2unicode(self, sentence: str) -> str:
        """
        Detect Zawgyi and change Unicode.

        args: 
            sentence <str>
        return: 
            sentence False <str> [changed sentence]
        """
        mask = self.detectZawgyi(sentence)
        if mask:
            sentence = self.converter.Zawgyi2Unicode(sentence)
        return sentence

    def unicode2zawgyi(self, sentence: str) -> str:
        """
        Change Unicode to Zawgyi

        args: 
            sentence <str>
        return: 
            sentence <str> [changed sentence]
        """
        sentence = self.converter.Unicode2Zawgyi(sentence)
        return sentence

    def isMyanmar(self, sentence: str, whole: bool = False) -> bool:
        symbol_ka = chr(0x1000)  # က
        symbol_genitive = chr(0x104F)  # ၏
        ismyanmar = lambda c: (c >= symbol_ka and c <= symbol_genitive)
        """
        Check if sentence is Myanmar
        
        args: 
            sentence <str>
        return: 
            bool <bool>
        """
        return (
            any(map(ismyanmar, sentence))
            if not whole
            else all(map(ismyanmar, sentence))
        )

    def isEnglish(self, sentence: str, whole: bool = False) -> bool:
        """
        Check if sentence is English

        args: 
            sentence <str>
        return: 
            bool <bool>
        """
        pattern = re.compile(r"[a-zA-Z0-9]+")
        isEng = pattern.fullmatch(sentence) if whole else pattern.re.search(sentence)
        return True if isEng else False

    def isNumeric(self, sentence: str) -> bool:
        """
        Check if sentence is numeric

        args: 
            sentence <str>
        return: 
            True <bool>
        """
        return True if re.fullmatch(r"[0-9]+|[၀-၉]+", sentence) else False

    def removeNumeric(self, sentence: str) -> str:
        """
        Remove numeric from sentence
        args: 
            sentence <str>
        return: 
            sentence <str>
        """
        return re.sub(r"[0-9]+|[၀-၉]+", "", sentence)

    def cleanSentence(self, sentence: str) -> str:
        """
        Clean sentence
        args : sentence <str>
        return : sentence <str>
        """
        pattern = re.compile(
            "["
            u"\ufeff"
            u"\u200a"
            u"\u200b"
            u"\u200c"
            u"\u200d"
            u"\u200e"
            u"\u200f"
            "\r"
            "\n"
            "\u202d"
            "“"
            '"'
            "၊"
            "]+",
            re.UNICODE,
        )
        return pattern.sub("", sentence)

    def removeEmoji(self, sentence: str) -> str:
        """
        Remove emojis
        args : sentence <str>
        return : sentence <str>
        """
        emoj = re.compile(
            "["
            u"\U000027B0-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027A8"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            "]+",
            re.UNICODE,
        )
        return emoj.sub("", sentence)

    def removePunctuation(self, sentence: str) -> str:
        """
        Remove punctuation
        args : sentence <str>
        return : sentence <str>
        """
        punc = re.compile("[%s]" % re.escape(string.punctuation))
        return punc.sub("", sentence)

    def removeLinks(self, sentence: str) -> str:
        """
        Remove link
        args : sentence <str>
        return : sentence <str>
        """
        link = re.compile(r"^https?:\/\/.*[\r\n]*")
        return link.sub("", sentence)

    def number2mynumber(self, sentence: str) -> str:
        """
        English numbers to Myanmar numbers
        args:

        """

    def locateEmoji(self, sentence: str) -> List[int]:
        """
        Locate emoji
        args : sentence <str>
        return : emoji_index and emojis <list>
        """
        emoji_index = [i for i, c in enumerate(sentence) if c in emoji.UNICODE_EMOJI]
        return emoji_index, [sentence[i : i + 1] for i in emoji_index]

    def preprocess(self, sentence: str) -> str:
        """
        Preprocess sentence
        args : sentence <str>
        return : sentence <str>
        """
        sentence = self.zawgyi2unicode(sentence)
        sentence = self.cleanSentence(sentence)
        sentence = self.removeEmoji(sentence)
        sentence = self.removePunctuation(sentence)
        sentence = self.removeLinks(sentence)
        return sentence
