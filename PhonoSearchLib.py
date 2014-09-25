import IPAParser
from IPATabulator import CONS_ROW_NAMES, CONS_COL_NAMES
from IPATabulator import VOW_ROW_NAMES, VOW_COL_NAMES

class LangSearchEngine:
    """Objects of this class know which languages have which phonemes."""

    def __init__(self):
        self.lang_dic = {}
        # Prepairing tables for lookup.
        self.cons_table = [[set() for i in CONS_COL_NAMES] for j in CONS_ROW_NAMES]
        self.cons_x_coords = {}
        for pair in enumerate(CONS_COL_NAMES):
            self.cons_x_coords[pair[1]] = pair[0]
        self.cons_y_coords = {}
        for pair in enumerate(CONS_ROW_NAMES):
            self.cons_y_coords[pair[1]] = pair[0]
        self.vow_table = [[set() for i in VOW_COL_NAMES] for j in VOW_ROW_NAMES]
        self.vow_x_coords = {}
        for pair in enumerate(VOW_COL_NAMES):
            self.vow_x_coords[pair[1]] = pair[0]
        self.vow_y_coords = {}
        for pair in enumerate(VOW_ROW_NAMES):
            self.vow_y_coords[pair[1]] = pair[0]

    def add_language(self, lang_name, phonemes):
        self.lang_dic[lang_name] = phonemes
        # We do not account for polyphthongs and apical vowels for now -- todo!
        for phoneme in phonemes:
            if 'vowel' in phoneme and not phoneme.intersection({'apical', 'diphthong', 'triphthong'}):
                height = phoneme.intersection(VOW_ROW_NAMES).pop()
                y_coord = self.vow_y_coords[height]
                row = phoneme.intersection(VOW_COL_NAMES).pop()
                x_coord = self.vow_x_coords[row]
                self.vow_table[y_coord][x_coord].add(lang_name)
            else:
                manner = phoneme.intersection(CONS_ROW_NAMES).pop()
                y_coord = self.cons_y_coords[manner]
                place = phoneme.intersection(CONS_COL_NAMES).pop()
                x_coord = self.cons_x_coords[place]
                self.cons_table[y_coord][x_coord].add(lang_name)

    def phoneme_query(self, phoneme_string):
        """Returns a set of languages containing this phoneme and its derivatives."""

        phoneme = set.union(*IPAParser.parsePhon(phoneme_string))
        result = set()
        if 'vowel' in phoneme:
            if phoneme.intersection({'apical', 'diphthong', 'triphthong'}):
                return result
            height = phoneme.intersection(VOW_ROW_NAMES).pop()
            y_coord = self.vow_y_coords[height]
            row = phoneme.intersection(VOW_COL_NAMES).pop()
            x_coord = self.vow_x_coords[row]
            return self.vow_table[y_coord][x_coord]
        else:
            manner = phoneme.intersection(CONS_ROW_NAMES).pop()
            y_coord = self.cons_y_coords[manner]
            place = phoneme.intersection(CONS_COL_NAMES).pop()
            x_coord = self.cons_x_coords[place]
            return self.cons_table[y_coord][x_coord]

# Test code

if __name__ == '__main__':
    import csv
    engine = LangSearchEngine()
    with open('ffli-dbase.tsv', 'r', encoding='utf-8') as inp:
        # Todo: check multiple items.
        records = list(csv.reader(inp, delimiter='\t'))[1:]
    for i in range(0, 3):
        name = records[i][1]
        inv = "%s, %s" % (records[0][10].strip().replace('\u0361', '').replace('\u2009', ''), records[0][11].strip())
        inv = inv.split(', ')
        phonemes = [set.union(*IPAParser.parsePhon(el)) for el in inv]
        engine.add_language(name, phonemes)
    for phoneme in inv:
        print(phoneme, engine.phoneme_query(phoneme))