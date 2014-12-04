import IPAParser
from IPATabulator import CONS_ROW_NAMES, CONS_COL_NAMES
from IPATabulator import VOW_ROW_NAMES, VOW_COL_NAMES

class LangSearchEngine:
    """Objects of this class know which languages have which phonemes."""

    def __init__(self):
        self.lang_dic = {}
        self.all_langs = set()
        self.all_phonemes = {} # Frozenset -> glyph map. Needed for feature search.
        # Prepairing tables for lookup.
        self.cons_table = [[{} for i in CONS_COL_NAMES] for j in CONS_ROW_NAMES]
        self.cons_x_coords = {}
        for pair in enumerate(CONS_COL_NAMES):
            self.cons_x_coords[pair[1]] = pair[0]
        self.cons_y_coords = {}
        for pair in enumerate(CONS_ROW_NAMES):
            self.cons_y_coords[pair[1]] = pair[0]
        self.vow_table = [[{} for i in VOW_COL_NAMES] for j in VOW_ROW_NAMES]
        self.vow_x_coords = {}
        for pair in enumerate(VOW_COL_NAMES):
            self.vow_x_coords[pair[1]] = pair[0]
        self.vow_y_coords = {}
        for pair in enumerate(VOW_ROW_NAMES):
            self.vow_y_coords[pair[1]] = pair[0]
        self.cons_rows = set(CONS_ROW_NAMES)
        self.cons_cols = set(CONS_COL_NAMES)
        self.vow_rows = set(VOW_ROW_NAMES)
        self.vow_cols = set(VOW_COL_NAMES)

    def add_language(self, lang_name, phonemes):
        self.lang_dic[lang_name] = phonemes
        self.all_langs.add(lang_name)
        # We do not account for polyphthongs and apical vowels for now -- todo!
        for phoneme in phonemes:
            glyph = phoneme
            phoneme = set.union(*IPAParser.parsePhon(phoneme))
            phoneme_key = frozenset(phoneme)
            if phoneme_key not in self.all_phonemes:
                self.all_phonemes[phoneme_key] = glyph
            if 'vowel' in phoneme:
                if phoneme.intersection({'apical', 'diphthong', 'triphthong'}):
                    continue # Not supported for now.
                height = phoneme.intersection(VOW_ROW_NAMES).pop()
                y_coord = self.vow_y_coords[height]
                row = phoneme.intersection(VOW_COL_NAMES).pop()
                x_coord = self.vow_x_coords[row]
                if phoneme_key not in self.vow_table[y_coord][x_coord]:
                    self.vow_table[y_coord][x_coord][phoneme_key] = (glyph, [])
                self.vow_table[y_coord][x_coord][phoneme_key][1].append(lang_name)
            else:
                try:
                    manner = phoneme.intersection(CONS_ROW_NAMES).pop()
                except KeyError:
                    raise Exception("A consonant does not have a manner:", phoneme)
                y_coord = self.cons_y_coords[manner]
                place = phoneme.intersection(CONS_COL_NAMES).pop()
                x_coord = self.cons_x_coords[place]
                if phoneme_key not in self.cons_table[y_coord][x_coord]:
                    self.cons_table[y_coord][x_coord][phoneme_key] = (glyph, [])
                self.cons_table[y_coord][x_coord][phoneme_key][1].append(lang_name)

    def IPA_exact_query(self, phoneme_string):
        """Returns a list of languages containing this phoneme."""

        phoneme = set.union(*IPAParser.parsePhon(phoneme_string))
        result = {}
        if 'vowel' in phoneme:
            if phoneme.intersection({'apical', 'diphthong', 'triphthong'}):
                return result
            height = phoneme.intersection(self.vow_rows).pop()
            y_coord = self.vow_y_coords[height]
            row = phoneme.intersection(self.vow_cols).pop()
            x_coord = self.vow_x_coords[row]
            for key in self.vow_table[y_coord][x_coord]:
                if key == phoneme:
                    return self.vow_table[y_coord][x_coord][key][1]
            return []         
        else:
            manner = phoneme.intersection(self.cons_rows).pop()
            y_coord = self.cons_y_coords[manner]
            place = phoneme.intersection(self.cons_cols).pop()
            x_coord = self.cons_x_coords[place]
            for key in self.cons_table[y_coord][x_coord]:
                if key == phoneme:
                    return self.cons_table[y_coord][x_coord][key][1]
            return []
        raise Exception("Unreachable!")

    def IPA_query(self, phoneme_string):
        """Returns a dictionary with languages containing this phoneme and its derivatives."""

        phoneme = set.union(*IPAParser.parsePhon(phoneme_string))
        result = {}
        if 'vowel' in phoneme:
            if phoneme.intersection({'apical', 'diphthong', 'triphthong'}):
                return result
            height = phoneme.intersection(self.vow_rows).pop()
            y_coord = self.vow_y_coords[height]
            row = phoneme.intersection(self.vow_cols).pop()
            x_coord = self.vow_x_coords[row]
            for key in self.vow_table[y_coord][x_coord]:
                if key.issuperset(phoneme):
                    glyph = self.vow_table[y_coord][x_coord][key][0]
                    langs = self.vow_table[y_coord][x_coord][key][1]
                    result[glyph] = langs
            return result
        else:
            manner = phoneme.intersection(self.cons_rows).pop()
            y_coord = self.cons_y_coords[manner]
            place = phoneme.intersection(self.cons_cols).pop()
            x_coord = self.cons_x_coords[place]
            for key in self.cons_table[y_coord][x_coord]:
                if key.issuperset(phoneme):
                    glyph = self.cons_table[y_coord][x_coord][key][0]
                    langs = self.cons_table[y_coord][x_coord][key][1]
                    result[glyph] = langs
            return result
        raise Exception("Unreachable!")

    def IPA_query_multiple(self, *args):
        result = set()
        positive = []
        negative = []
        for phoneme in args:
            if phoneme[0] == '-':
                negative.append(phoneme[1:])
            else:
                positive.append(phoneme)
        if not negative and not positive:
            raise Exception("Nothing to search for")
        if not positive:
            result = self.all_langs
        else:
            for phoneme in positive:
                result.update(self._dict2set(self.IPA_query(phoneme)))
        for phoneme in negative:
            result = result.difference(self._dict2set(self.IPA_query(phoneme)))
        return result

    def inject_laterals(self, arg):
        pass

    def features_query(self, *args):
        positive = set()
        negative = set()
        all_positives = []
        for arg in args:
            if 'lateral affricate' in arg:
                arg = arg.replace('lateral affricate', 'lateral_affricate')
            if 'lateral fricative' in arg:
                arg = arg.replace('lateral fricative', 'lateral_fricative')
            if 'lateral approximant' in arg:
                arg = arg.replace('lateral approximant', 'lateral_approximant')
        for arg in args:
            if arg[0] == '-':
                negative.add(arg[1:])
            else:
                positive.add(arg)
        if not positive:
            result = self.all_langs
        else:
            for feature in positive:
                feature = set(feature.split())
                temp = set()
                for key in self.all_phonemes:
                    if feature.issubset(key):
                        temp.update(self._dict2set(self.IPA_query(self.all_phonemes[key])))
                all_positives.append(temp)
            result = set.intersection(*all_positives)
        for feature in negative:
            print(feature)
            feature = set(feature.split())
            for key in self.all_phonemes:
                if feature.issubset(key):
                    result = result.difference(self._dict2set(self.IPA_query(self.all_phonemes[key])))
        return result

    def feature_query_stat(self):
        pass

    def _dict2set(self, dic):
        result = set()
        for key in dic:
            for lang in dic[key]:
                result.add(lang)
        return result

    def feature_rating(self, feature):
        feature_havers = {}
        for lang in self.features_query(feature):
            counter = 0
            for phon in engine.lang_dic[lang]:
                if feature in set.union(*IPAParser.parsePhon(phon)):
                    counter += 1
            feature_havers[lang] = counter
        rating = []
        for key, value in feature_havers.items():
            rating.append((value, key))
        rating.sort(reverse = True)
        return rating

    def IPA_query_rating(self):
        pass # todo

# Test code

if __name__ == '__main__':
    import csv
    engine = LangSearchEngine()
    with open('ffli-dbase.tsv', 'r', encoding='utf-8') as inp:
        # Todo: check multiple items.
        records = list(csv.reader(inp, delimiter='\t'))[1:]
    for i in range(len(records)):
        name = records[i][1]
        inv = "%s, %s" % (records[i][10].strip().replace('\u0361', '').replace('\u2009', ''), records[i][11].strip())
        # print("%s: %s" % (name, inv))
        inv = inv.split(', ')
        engine.add_language(name, inv)
    # test_set = MAIN_GLYPHS = ['ɿ', 'ʅ', 'ʮ', 'ʯ', 'a', 'b', 'c', 'd', 'e', 'f', 'ɡ', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'æ', 'ç', 'ð', 'ø', 'ħ', 'ŋ', 'œ', 'ɐ', 'ɑ', 'ɒ', 'ɓ', 'ɔ', 'ɕ', 'ᶑ', 'ɖ', 'ɗ', 'ɘ', 'ə', 'ɛ', 'ɜ', 'ɞ', 'ɟ', 'ɠ', 'ɢ', 'ɣ', 'ɤ', 'ɥ', 'ɦ', 'ɨ', 'ɪ', 'ɬ', 'ɭ', 'ɮ', 'ɯ', 'ɰ', 'ɱ', 'ɲ', 'ɳ', 'ɴ', 'ɵ', 'ɶ', 'ɸ', 'ɹ', 'ɺ', 'ɻ', 'ɽ', 'ɾ', 'ʀ', 'ʁ', 'ʂ', 'ʃ', 'ʄ', 'ʈ', 'ʉ', 'ʊ', 'ʋ', 'ʌ', 'ʍ', 'ʎ', 'ʏ', 'ʐ', 'ʑ', 'ʒ', 'ʔ', 'ʕ', 'ʙ', 'ʛ', 'ʜ', 'ʝ', 'ʟ', 'ʡ', 'ʢ', 'β', 'θ', 'χ', 'ɚ', 'ɫ', '\u026a\u0308', '\u028a\u0308', '\xe4', '\xf8\u031e', 'e\u031e', '\u0264\u031e', 'o\u031e', 'ƺ', 'ʓ']
    # rating = engine.feature_rating('consonant')
    # # rating.sort()
    # rates = [el[0] for el in rating]
    # print(', '.join([str(el) for el in rates]))
    result = engine.IPA_query('i')
    for key, value in result.items():
        print(key, value)

