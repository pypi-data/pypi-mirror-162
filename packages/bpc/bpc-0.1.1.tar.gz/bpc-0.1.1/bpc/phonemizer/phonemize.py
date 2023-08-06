import pandas as pd

from typing import Dict, Optional
from .bootphonemizer import Phonemizer


class BurmesePhonemizer:
    """
    Burmese text to phoneme

    Usage:
        >>> from burmese_phonemizer import BurmesePhonemizer
        With lexicon:
        >>> bp = BurmesePhonemizer("lexicon.txt")
        >>> bp.text_to_phone("မင်္ဂလာပါ")
        With espeak:
        >>> bp = BurmesePhonemizer()
        >>> bp.text_to_phone("မင်္ဂလာပါ")
        ['m', 'ŋ', 'ð', 't', 's', 't', 'ˈo2', 'k', 'ˌo', 't', 'e', 'ˈa', 'u2', 'l', 'w', 'ˈa', 'n', 'p', 'ˈe2', 't', 'j'


    """
    def __init__(self, lexicon: Optional[str] = None):
        if lexicon is None:
            self.lexicon_dict = None
            try:
                self.phomize = Phonemizer(
                    language="my",
                    backend="espeak",
                    with_stress=True,
                    preserve_punctuation=True,
                )
            except:
                raise Exception(
                    "Please install espeak (https://bootphon.github.io/phonemizer/install.html) or provide a lexicon file"
                )
        else:
            self.lexicon_dict = self.dict_lexicon(lexicon)

    def dict_lexicon(self, lexicon: str) -> Dict[str, str]:
        """
        Create a dictionary from lexicon

        Args:
            lexicon: (str) path to lexicon file
        return:
            dictionary of lexicon
        """
        if lexicon.endswith("txt"):
            with open(lexicon, "r") as f:
                lexicon_dict = {}
                for line in f:
                    line = line.strip()
                    line = line.split(" ")
                    lexicon_dict[line[0]] = " ".join(line[1:])
        elif lexicon.endswith("xlsx"):
            lexicon_dict = pd.read_excel(lexicon)
            lexicon_dict = {
                k: v for k, v in zip(lexicon_dict["word"], lexicon_dict["phoneme"])
            }
        elif lexicon.endswith("csv"):
            lexicon_dict = pd.read_csv(lexicon)
            lexicon_dict = {
                k: v for k, v in zip(lexicon_dict["word"], lexicon_dict["phoneme"])
            }
        return lexicon_dict

    def dataframe_to_phone(self, dataframe: str, output: str = "phoneme.csv"):
        """
        Args:
            data_frame: path to text file
        return:
            path to output file
        """
        dataframe = pd.read_csv(dataframe)
        dataframe["phn"] = dataframe["text"].apply(
            lambda x: " ".join([self.lexicon_dict[w] for w in x.split(" ")])
        )
        dataframe.to_csv(output, index=False)

    def text_to_phone(self, text: str) -> str:
        """
        :text: text to be phonemized
        :return: phomized text
        """
        if self.lexicon_dict:
            return " ".join([self.lexicon_dict[w] for w in text.split(" ")])
        else:
            return self.phomize(text)

if __name__ == '__main__':
    mizer = BurmesePhonemizer()
    print(mizer.text_to_phone("မင်းသားတို့ကိုကျော်လွန်းပါတယ်"))