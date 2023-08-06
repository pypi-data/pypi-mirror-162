import re
import emoji
from typing import List
from itertools import chain


class WordBreak:
    """
    This class contains common WordBreak functions for Myanmar Language.

    Usage:
        >>> from cleaner.word_break import WordBreak
        >>> wb = WordBreak()
        >>> wb.syllable_break("မင်္ဂလာပါ")
        ['မင်္ဂလာ', 'ပါ']
    """

    def __init__(self) -> None:
        self.my_syllable_pattern = re.compile(
            r"(?:(?<!္)([\U00010000-\U0010ffffက-ဪဿ၊-၏]|[၀-၉]+|[^က-၏\U00010000-\U0010ffff]+)(?![ှျ]?[့္်]))",
            re.UNICODE,
        )
        self.eng_my_split_pattern = re.compile(
            r"[က-ဪဿ၊-၏^]+"
        )
        # check whole sentence for english
        self.eng_pattern = re.compile(r"^[a-zA-Z0-9]+$")

    def syllable_break(self, text: str) -> str:
        """
        Break text into syllables

        args:
            text <str>

        return:
            text <str>
        """
        return self.my_syllable_pattern.sub(r"𝕊\1", text).strip("𝕊").split("𝕊")

    def separate_eng_mm(self, text: str) -> str:
        """
        Separate English and Myanmar words

        args:
            text <str>
        return:
            separated <str>
        """
        return self.eng_my_split_pattern.findall(text)

    def syllable_break_both(self, text: str) -> List[str]:
        """
        Break text into syllables and separate english and myanmar

        args:
            text <str>

        return:
            syllables <List[str]>
        """
        return list(
            chain.from_iterable(
                [
                    self.syllable_break(i)
                    for i in self.separate_eng_mm(text)
                    if i != " " or i != ""
                ]
            )
        )

    def syllable_break_eng_my_split(self, text: str) -> List[str]:
        """
        Break sentence into syllables

        args:
            sentence <str>

        return:
            syllables <List[str]>
        """
        clean_data = " ".join(text.split())
        example_test = self.syllable_break_both(clean_data)
        temp_list = example_test
        for idx, data in enumerate(example_test):
            if self.eng_pattern.match(data):
                if idx + 1 < len(example_test):
                    if (
                        self.my_syllable_pattern.match(example_test[idx + 1])
                        and example_test[idx + 1] != " "
                        and not (self.eng_pattern.match(example_test[idx + 1]))
                    ):
                        temp_list.insert(idx + 1, " ")
        return temp_list

    def syllable_break_list(self, text: List[str]) -> List[str]:
        """
        Breaks a list of sentences into syllables
        args: text: List[str]
        returns: List[str]
        e.g. [['09950367221', 'တစ်', 'SwanAung', 'car', 'တယ်', 'OK', '$', '😁', '😂'],
                    ['slkfjlskfj', 'car', 'စာ', 'အုပ်', 'sfsfd']]
        """
        words = [self.syllable_break_both(data) for data in text]
        filtered_words = [list(filter(lambda word: word.strip(), msg)) for msg in words]
        return filtered_words

    def pos_filter(self, message_list: List[str]) -> List[str]:
        """
        Filter word and pos
        args:
            message_list: List[str]

        returns:
            word_list: List[str]
            pos_list : List[int]
        """
        word_list = []
        pos_list = []
        for pos_tagged_sentence in message_list:
            tokens = pos_tagged_sentence.split()
            res_word = []
            res_pos = []
            for t in tokens:
                try:
                    word, pos = t.split("/")
                    res_word.append(word)
                    res_pos.append(pos)
                except ValueError:
                    res_word.append("NA")
                    res_pos.append("NA")
            if not ("NA" in res_word):
                final_word = " ".join(res_word)
                final_pos = " ".join(res_pos)
                word_list.append(final_word)
                pos_list.append(final_pos)
            else:
                word_list.append("NA")
                pos_list.append("NA")
        return word_list, pos_list

    def syllable_data_categorization(self, text: str) -> List[List[str]]:
        """
        tagged the sentences with 0 for the words which have space ' ' in front of them and 1 otherwise.

        args:
          text: List[str]

        e.g. text = ['ဒေါက်တာ ထွန်းဝင်း လေ ဗျာ',
          'ဆယ်မိုင်ကုန်း ၊ ပြည် လမ်း ။ 09950367221 တစ် အုပ် လို ချင် ပါ တယ်']

        return:
          tagged_sent: List[List[str]]

        e.g. [['1', '1', '0', '1', '0', '0'],
            ['1', '1', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']]
        """
        syl = [self.syllable_break_eng_my_split(data) for data in text]
        total_sent = []
        for words in syl:
            sent = []
            for index, value in enumerate(words):
                if index == 0:
                    sent.append("1")
                elif value == " ":
                    sent.append("")
                elif value == "":
                    sent.append("")
                elif value != " ":
                    if self.eng_pattern.match(value):
                        sent.append("0")
                    elif emoji.emoji_count(value) != 0:
                        sent.append("0")
                    else:
                        if words[index - 1] == " ":
                            sent.append("0")
                        else:
                            sent.append("1")
            total_sent.append(sent)
        filter_sent = [list(filter(None, data)) for data in total_sent]
        return filter_sent

    def segment_sent(self, true_sent: str, pred_sent: str) -> List[str]:
        """
        segments predicted sentences according to true sentence length

        args:
            true sentence: str
            predicted sentence: str
        returns:
            segmented predictions: List[str]
        """
        predictions = []
        for index, sent in zip(true_sent, pred_sent):
            split_sent = sent[:index]
            data = [str(d) for d in split_sent]
            predictions.append(" ".join(data))
        return predictions

    def tag2_sent(self, text_list: List[str], predict_list: List[str]) -> List[str]:
        """
        changing tag to sentences

        args:
            text list eg. ['စာ ရေး ဆ ရာ ညိမ်း ကျော် ရှိ လာ']
            predict_list eg. ['1 1 1 1 0 1 0 0']
        returns:
            output_sentences = ['စာရေးဆရာ ညိမ်းကျော် ရှိ လာ']
        """
        output_sentences = []
        for text, predict in zip(text_list, predict_list):
            sent = []
            for word_sent, tag_sent in zip(text.split(), predict.split()):
                if tag_sent == "0":
                    sent.append(" ")
                    sent.append(word_sent)
                elif tag_sent == "1":
                    sent.append(word_sent)
            output_sentences.append("".join(sent))
        return output_sentences
