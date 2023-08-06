class LatynkaMapsa:
    """Defines the rules for character substitution.
    An instance of this class is passed as an argument for 'Romaniser(..rules=LatynkaMapsa()..)' object."""

    # This table is used for substitution of all unambiguous characters;
    # it's being passed as argument for str.translate() method, which is applied to the whole text to be converted.
    UNAMBIGUOUS_CHAR_TAB = 'АБГҐДЕЗИІКЛМНОПРСТУФЦабгґдезиіклмнопрстуфхцщ'.maketrans({
        'А': 'A', 'Б': 'B', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'З': 'Z', 'И': 'Y', 'І': 'I', 'К': 'K', 'Л': 'L',
        'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Ц': 'C', 'а': 'a',
        'б': 'b', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'з': 'z', 'и': 'y', 'і': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'ch', 'ц': 'c', 'щ': 'shj'
    })

    # This dict contains ambiguous chars and combinations of them, grouped in nested dicts by their type of ambiguity.
    # Each key for each nested dict is a sring and is equal to __name__ property of corresponding method defined further
    # below.
    # The '_resolve_ambiguity()' method of 'Romanizer' class loops throug 'amb_char_tab' and performs nested for loops
    # throug each of nested dicts.
    # If a key of a nested dict is found in the string, upon which '_resolve_ambiguity()' was called, a corresponding
    # method of 'LatinkaMapsa' class is called passing it the key of a nested dict as an argument.
    AMBIGUOUS_CHAR_TAB = {
        '_doubles': {'вв': 'wv',   # This group is placed firs because words may contain single characters of the same
                     'чч': 'ccj',  # kind, and having them replaced first will eliminate doubled variants.
                     'жж': 'jhh',
                     'шш': 'shh',
                     'Вв': 'Wv',
                     'ВВ': 'WV',
                     'ЧЧ': 'CCH',
                     'ЖЖ': 'JHH',
                     'ШШ': 'SSH'},

        '_sibilants': {'ч': ('cj',),
                       'ш': ('sh',),
                       'Ч': ('Cj', 'CJ'),
                       'Ш': ('Sh', 'SH'),
                       'Щ': ('Shj', 'SHJ')},

        '_v_or_w': {'в': ('v', 'w'),
                    'В': ('V', 'W')},

        '_vowels_small': {'я': ('ia', 'ya'),
                          'ї': ('iy', 'yi'),
                          'є': ('ie', 'ye'),
                          'ю': ('iu', 'yu')},

        '_vowels_capital': {'Я': ('IA', 'Ya', 'YA'),
                            'Є': ('IE', 'Ye', 'YE'),
                            'Ю': ('IU', 'Yu', 'YU'),
                            'Ї': ('IY', 'Yi', 'YI')},

        '_y_or_i': {'й': ('y', 'i', "'y"),  # This one should follow '_vowels_small' and '_vowels_capital'
                    'Й': ('Y', 'I', "'Y")},

        '_jh_or_j': {'ж': ('jh', '_', 'j'),
                     'Ж': ('Jh', 'JH', 'J')},

        '_softener': {'ь': 'i',
                      'Ь': 'I'},

        '_ch_capital': {'Х': ('Ch', 'CH')}}

    # These methods below define the character substitution rules for certain types of ambiguity:

    def _doubles(self, word, char):
        """Replaces certain doubled consonants"""
        while char in word:
            word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._doubles.__name__][char], 1)
            # __name__ prorerty is used to access eponymous nested dict of amb_char_tab dict.
            # '__count' parameter of '.replace()' method is needed, because different occurances of characters may meet
            # different substitution conditions.
        return word

    def _sibilants(self, word, char):
        while char in word:
            if not word.isupper():
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._sibilants.__name__][char][0], 1)
            else:
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._sibilants.__name__][char][1], 1)
        return word

    def _v_or_w(self, word, char):
        while char in word:
            nxt = word.index(char) + 1
            if word.index(char) == len(word) - 1:
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._v_or_w.__name__][char][1], 1)
            elif word[nxt] not in 'aeyoiuєяAEYOIUЄЯ':  # --why also cyrillic included?--
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._v_or_w.__name__][char][1], 1)
            else:
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._v_or_w.__name__][char][0], 1)
        return word

    def _vowels_small(self, word, char):
        while char in word:
            position = word.index(char)
            if position != 0 and word[position - 1] not in "'ь":
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._vowels_small.__name__][char][0], 1)
            else:
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._vowels_small.__name__][char][1], 1)
        return word

    def _vowels_capital(self, word, char):
        stripped = ''.join([smb if smb.isalpha() else '' for smb in word])
        while char in stripped:
            position = stripped.index(char)
            if stripped.index(char) != 0 and word[position - 1] not in "'Ь":
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._vowels_capital.__name__][char][0], 1)
                stripped = stripped.replace(char, '*', 1)
            elif (stripped.index(char) == 0 and len(stripped) == 1) or not word.isupper():
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._vowels_capital.__name__][char][1], 1)
                stripped = stripped.replace(char, '*', 1)
            else:
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._vowels_capital.__name__][char][2], 1)
                stripped = stripped.replace(char, '*', 1)
        return word

    def _y_or_i(self, word, char):
        while char in word:
            prvs, position = word.index(char) - 1, word.index(char)
            if position == 0 or word[prvs] == '\n':
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._y_or_i.__name__][char][0], 1)
            elif word[prvs] in 'aeiouyAEIOUY':
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._y_or_i.__name__][char][1], 1)
            else:
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._y_or_i.__name__][char][2], 1)
        return word

    def _jh_or_j(self, word, char):
        while char in word:
            position = word.index(char)
            if position != 0 and word[position - 1] in 'dD':
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._jh_or_j.__name__][char][2], 1)
            elif not word.isupper():
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._jh_or_j.__name__][char][0], 1)
            else:
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._jh_or_j.__name__][char][1], 1)
        return word

    def _softener(self, word, char):
        while char in word:
            position = word.index(char)
            if len(word) - position > 1 and word[position + 1] in 'oO':
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._softener.__name__][char], 1)
            else:
                try:
                    word = word.replace(char, word[position - 1], 1)
                except IndexError:
                    return word
        return word

    def _ch_capital(self, word, char):
        while char in word:
            if word.isupper():
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._ch_capital.__name__][char][1], 1)
            else:
                word = word.replace(char, self.AMBIGUOUS_CHAR_TAB[self._ch_capital.__name__][char][0], 1)
        return word
