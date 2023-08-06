from . import substitution


class Romanizer:
    """Transforms Cyrillic Ukrainian script to Roman(Latin) Ukrainian script:

       > > > translation = Romanizer(<cyrillic_ukrainian_text>).romanize()

    As the first arg this class takes a text in standard Cyrillic Ukrainian script;
    Second argument is for specyfying which version of Latin Ukrainian script is wanted (currently only one is available
    and set as default).
    """
    def __init__(self, text=None, rules=substitution.LatynkaMapsa()):
        self.rules = rules
        self.text = text
        self.text_divided = None
        self.cached = {}

    def romanize(self):
        """Call this method to perform conversion"""
        self._convert_preliminary()
        return self._convert_finally()

    def _convert_preliminary(self):
        """This method is called by 'romanize()';
        All unambiguous characters in text are replaced with their counterparts;
        The text is being split with a staticmethod '_split_text' and stored to an instance variable 'self.text_divided'
        """
        self.text_divided = self._split_text(self.text.translate(self.rules.UNAMBIGUOUS_CHAR_TAB))

    @staticmethod
    def _split_text(text):
        """This one is called by '_convert_prelimenary';
        Splits the text(string) by a whitespace char, returns a generator object
        """
        for word in text.split(' '):
            yield word

    def _convert_finally(self):
        """Called by 'romanize()' after '_convert_perlimenary()';
        Iterates over generator object('self.text_divided') and gets word subsletutions from 'self.cache'(which is a
        dict) using current element as key; if there's no such key in 'self.cached', calls '_resolve_ambiguity(),
        appends result to local variable 'res', and stores it to 'self.cached' for further use.
        """
        res = []  # each fully converted srting is appended here.
        for word in self.text_divided:
            if word not in self.cached:
                self.cached[word] = self._resolve_ambiguity(word)
            res.append(self.cached[word])
        return ' '.join(res)

    def _resolve_ambiguity(self, word):
        """Performs replacement of ambiguous characters if such were found"""
        # Since Python 3.7 upate dict elements are guaranteed to be ordered, so further loops work ok.
        # Loop through a dict to get a siquence of chars of certain type of ambiguity;
        for amb in self.rules.AMBIGUOUS_CHAR_TAB:
            # Loop thorough a sequence to get a specific ambiguous char
            for char in self.rules.AMBIGUOUS_CHAR_TAB[amb]:
                if char in word:
                    word = getattr(self.rules, amb)(word, char)
        return word
