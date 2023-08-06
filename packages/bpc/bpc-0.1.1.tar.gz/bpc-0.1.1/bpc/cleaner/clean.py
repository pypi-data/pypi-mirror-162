from .normalizer import Normalizer
from .preprocessor import Preprocessor


class Cleaner:
    """
    Clean raw text

    Normalization
    1. Delete miss character  (Normalizer)
    2. Normalize numbers (Normalizer)
    3. Normalize english text (Normalizer)
    4. Normalize data (Normalizer)

    Preprocessing
    1. Change Zawgyi to Unicode (Preprocessor)
    2. Clean sentence (Preprocessor)
    3. Remove punctuation (Preprocessor)
    4. Remove emoji (Preprocessor)
    5. Remove Links (Preprocessor)


    Usage :
    >>> cleaner = Cleaner()
    >>> text = "A သည် အေဖြစ်သည်။ ဝ၁၂ 4b "
    >>> cleaner.clean_text(text)

    Output:
        အေ သည် အေဖြစ်သည်။ ၀၁၂ ၄ဘီ
    """

    def __init__(self) -> None:
        self.normalizer = Normalizer()
        self.preprocessor = Preprocessor()

    def clean_text(self, raw_text: str) -> str:
        """
        Clean text

        Args:
            raw_text (str)
        return:
            text (str)
        """
        text = self.normalizer.normalize(raw_text)
        text = self.preprocessor.preprocess(text)
        return text


if __name__ == "__main__":
    cleaner = Cleaner()
    text = "A သည် အေဖြစ်သည်။ ဝ၁၂ 4b "
    cleaned_text = cleaner.clean_text(text)
    print(cleaned_text)