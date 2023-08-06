# Copied from espnet2/bin/phonemize.py

from typing import Optional, List


class Phonemizer:
    """Phonemizer module for various languages.

    This is wrapper module of https://github.com/bootphon/phonemizer.
    You can define various g2p modules by specifying options for phonemizer.

    See available options:
        https://github.com/bootphon/phonemizer/blob/master/phonemizer/phonemize.py#L32

    """

    def __init__(
        self,
        backend,
        word_separator: Optional[str] = None,
        syllable_separator: Optional[str] = None,
        phone_separator: Optional[str] = " ",
        strip=False,
        split_by_single_token: bool = False,
        **phonemizer_kwargs,
    ):
        # delayed import
        from phonemizer.backend import BACKENDS
        from phonemizer.separator import Separator

        self.separator = Separator(
            word=word_separator,
            syllable=syllable_separator,
            phone=phone_separator,
        )

        # define logger to suppress the warning in phonemizer
        self.phonemizer = BACKENDS[backend](
            **phonemizer_kwargs,
        )
        self.strip = strip
        self.split_by_single_token = split_by_single_token

    def __call__(self, text) -> List[str]:
        tokens = self.phonemizer.phonemize(
            [text],
            separator=self.separator,
            strip=self.strip,
            njobs=1,
        )[0]
        if not self.split_by_single_token:
            return tokens.split()
        else:
            # "a: ab" -> ["a", ":", "<space>",  "a", "b"]
            # TODO(kan-bayashi): space replacement should be dealt in PhonemeTokenizer
            return [c.replace(" ", "<space>") for c in tokens]