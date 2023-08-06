import re
import numpy as np


class Normalizer(object):
    """
    This class normalizes common errors for Burmese Language.
    Example: ၇ > ရ , ၀ > ဝ , င့် > င့် (i.e, sequence order error)

    Usage :
     For all normalization
     >>> from cleaner.normalize import Normalizer
     >>> n = Normalizer()
     >>> n.normalize('ယဥ််')
     For sentence validation only >>
     >>> n = Normalizer()
     >>> n.validate_sentence('ဖြင့်') ... etc. xD
     pre_rule_fix function is only for fixing ရ & ၀ case.
     >>> n = Normalizer()
     >>> n.pre_rule_fix('၇ပါတယ်။')
    """
    def __init__(self):
        pass

    def validate_sentence(self, sentence: str) -> str:
        """
        Vaidate the sequence of the sentence.
        Eg: င့် > င့်

        Args: 
            sentence (str)
        return: 
            fixed sentence (str)
        """
        sentence= (
            sentence.replace("့်", "့်")
            .replace("််", "်")
            .replace("ိိ", "ိ")
            .replace("ီီ", "ီ")
            .replace("ံံ", "ံ")
            .replace("ဲဲ", "ဲ")
        )
        sentence = sentence.replace("စျ", "ဈ").replace("ဥ့်", "ဉ့်").replace("ဥ်", "ဉ်")
        sentence = sentence.replace("ဩော်", "ဪ").replace("သြော်", "ဪ").replace("သြ", "ဩ")
        sentence = sentence.replace("ဉီ", "ဦ").replace("ဦ", "ဦ")
        return sentence

    def remove_whitespace(self, sentence: str) -> str:
        """
        Remove whitespace from the sentence.

        Args: 
            sentence (str)
        return: 
            fixed sentence (str)
        """
        sentence = sentence.replace("\u200a", "")
        sentence = sentence.replace("\u200b", "")
        sentence = sentence.replace("\u200c", "")
        sentence = sentence.replace("\u200d", "")
        sentence = sentence.replace("\u200e", "")
        sentence = sentence.replace("\u200f", "")
        sentence = sentence.replace("\xa0", "")
        sentence = sentence.replace("•", "")
        sentence = sentence.replace("\u202d", "")
        return sentence

    def Zero2Walone(self, sentence: str) -> str:
        """
        Fix number ၀ within characters.
        Args: sentence (str)
        return: fixed sentence (str)
        """
        sentence = list(sentence)
        for i in np.where(np.asarray(sentence) == "၀")[0]:
            if i < len(sentence) - 1:
                if sentence[i + 1] not in list(" ၀၁၂၃၄၅၆၇၈၉၊။"):
                    sentence[i] = "ဝ"
                elif sentence[i - 1] not in list(" ၀၁၂၃၄၅၆၇၈၉၊။"):
                    sentence[i] = "ဝ"
            elif sentence[-1] == "၀" and sentence[-2] not in list(" ၀၁၂၃၄၅၆၇၈၉၊။"):
                sentence[i] = "ဝ"
        return "".join(sentence)

    def Walone2Zero(self, sentence: str) -> str:
        """
        Fix character ဝ within numbers.

        Args: 
            sentence (str)
        return: 
            fixed sentence (str)
        """
        sentence = list(sentence)
        for t in np.where(np.asarray(sentence) == "ဝ")[0]:
            if t < len(sentence) - 1:
                if sentence[t + 1] in list("၀၁၂၃၄၅၆၇၈၉၊။"):
                    sentence[t] = "၀"
        return "".join(sentence)

    def Seven2Yagouk(self, sentence: str) -> str:
        """
        Fix number ၇ within characters.

        Args: 
            sentence (str)
        return: 
            fixed sentence (str)
        """
        sentence = np.asarray(list(sentence))
        for i in np.where(sentence == "၇")[0]:
            if i < len(sentence) - 1:
                if sentence[i + 1] not in list("၀၁၂၃၄၅၆၇၈၉၊။"):
                    sentence[i] = "ရ"
        return "".join(sentence)

    def pre_rule_fix(self, text: str) -> str:
        """
        Fix ဝ & ၇ within characters.

        Args: 
            text (str)
        return: 
            fixed text (str)
        """
        text = [str(y) for y in text]
        text = self.Zero2Walone(text)
        text = self.Walone2Zero(text)
        text = self.Seven2Yagouk(text)
        return text

    def normalize(self, sentence):
        """
        Normalize the sentence.

        Args: 
            sentence (str)
        return: 
            fixed sentence (str)
        """
        word_ls = []
        sentence = self.delete_miss_character(sentence)
        sentence = self._normalize_numbers(sentence)
        sentence = self._normalize_english_text(sentence)
        for word in sentence.strip().split():
            new_word = self.normalize_data(word)
            word_ls.append(new_word)
        new_sentence = " ".join(word_ls)
        return new_sentence

    def normalize_data(self, text: str) -> str:
        """
        Normalize the text.

        Args:  
            text (str)
        return: 
            normalized text (str)
        """
        try:
            text = self.remove_whitespace(text)
            text = self.validate_sentence(text)
            text = self.pre_rule_fix(text)
        except:
            raise Exception(f'[ERROR] Normalizing {text}')
        return text

    @staticmethod
    def delete_miss_character(sentence: str) -> str:
        """
        Delete miss character.
        
        Args: 
            sentence (str)
        return: 
            fixed sentence (str)
        """
        if "�" in sentence:
            print('[Warning] "�" character is found in the sentence.')
            sentence = sentence.replace("�", "")
        return sentence

    @staticmethod
    def _normalize_numbers(text: str) -> str:
        number_to_myn = {
            "0": "၀",
            "1": "၁",
            "2": "၂",
            "3": "၃",
            "4": "၄",
            "5": "၅",
            "6": "၆",
            "7": "၇",
            "8": "၈",
            "9": "၉",
        }
        new_text = "".join(
            number_to_myn[char] if char in number_to_myn.keys() else char
            for char in text
        )
        return new_text

    @staticmethod
    def _normalize_english_text(text: str) -> str:
        """
        Normalize the English Characters to Myanmar characters

        Args:
            text (str): English text
        return:
            text (str): Myanmar text
        """
        upper_alphabet_to_myn = {
            "A": "အေ",
            "B": "ဘီ",
            "C": "စီ",
            "D": "ဒီ",
            "E": "အီး",
            "F": "အက်ဖ်",
            "G": "ဂျီ",
            "H": "အိတ်ချ်",
            "I": "အိုင်",
            "J": "ဂျေ",
            "K": "ကေ",
            "L": "အန်လ်",
            "M": "အမ်",
            "N": "အန်",
            "O": "အို",
            "P": "ပီ",
            "Q": "ကျူ",
            "R": "အာ",
            "S": "အက်စ်",
            "T": "တီ",
            "U": "ယူ",
            "V": "ဗွီ",
            "W": "ဒဘလျူ",
            "X": "အိတ်စ်",
            "Y": "ဝိုင်",
            "Z": "ဇီ",
        }
        new_text = re.sub("[a-z]+", lambda x: str.upper(x.group()), text)
        new_text = "".join(
            upper_alphabet_to_myn[char]
            if char in upper_alphabet_to_myn.keys()
            else char
            for char in new_text
        )

        return new_text
