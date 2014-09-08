#! /usr/bin/env python3

import sys
import re
from io import StringIO
from IPAParser import parsePhon

SERIES_FORMING_FEATURES = {'pre-glottalised', 'pre-aspirated', 'pre-aspirated', 'pre-nasalised', 'pre-labialised', 'pharyngealised', 'nasalised', 'labialised', 'velarised', 'faucalised', 'palatalised', 'half-long', 'long', 'creaky-voiced', 'breathy-voiced', 'lateral-released', 'rhotic', 'advanced-tongue-root', 'retracted-tongue-root'}

CONS_ROW_NAMES = ['plosive', 'implosive', 'nasal', 'trill', 'tap', 'fricative', 'affricate', 'lateral fricative', 'lateral affricate', 'appoximant', 'lateral approximant']
CONS_COL_NAMES = ['bilabial', 'labial-velar', 'labial-palatal', 'labiodental', 'dental', 'alveolar', 'postalveolar', 'hissing-hushing', 'retroflex', 'alveolo-palatal', 'palatal', 'velar', 'uvular', 'pharyngeal', 'glottal', 'epiglottal']

VOW_ROW_NAMES = ['close', 'near-close', 'close-mid', 'mid', 'open-mid', 'near-open', 'open']
VOW_COL_NAMES = ['front', 'near-front', 'central', 'near-back', 'back']

class Phoneme:
    """A phoneme unit consisting of a string representation and two frozensets of features.
    coreSet is used to draw a table; seriesSet is used to choose the appopriate table
    to put the phoneme in."""
    def __init__(self, phon, preSet, coreSet, postSet):
        self.phon      = phon
        self.coreSet   = coreSet
        self.seriesSet = frozenset(
            SERIES_FORMING_FEATURES.intersection(set.union(preSet, postSet))
            )
        self.coreSet.update(set.difference(set.union(preSet, postSet), self.seriesSet))
        self.coreSet = frozenset(self.coreSet)

    def __str__(self):
        return self.phon

    def summary(self):
        return self.phon + "\n" + ", ".join(set.union(set(self.coreSet), set(self.seriesSet)))

def makeTableCons(consList):
    checkList = set(consList)
    """Transforms a list of consonant Phonemes into a 2-D array for subsequent formatting."""
    pooledFeatures = set()
    for phon in consList:
        pooledFeatures.update(phon.coreSet)
    columns = [item for item in CONS_COL_NAMES if item in pooledFeatures]
    rows    = [item for item in CONS_ROW_NAMES if item in pooledFeatures]
    table   = [['' for i in range(len(columns) + 1)] for j in range(len(rows) + 1)]
    table[0][1:] = columns
    for i in range(1, len(table)):
        table[i][0] = rows[i - 1]
    for i in range(1, len(table)):
        for j in range(1, len(table[0])):
            temp = []
            for phon in consList:
                if rows[i - 1] in phon.coreSet and columns[j - 1] in phon.coreSet:
                    checkList.discard(phon)
                    temp.append(str(phon))
            if temp:
                table[i][j] = ", ".join(sorted(temp))
    if checkList:
        raise Exception("Not all consonants made their way into the table: " + ", ".join([str(item) for item in checkList]))
    return table

def makeTableVow(vowList):
    checkList = set(vowList)
    pooledFeatures = set()
    for phon in vowList:
        pooledFeatures.update(phon.coreSet)
    columns = [item for item in VOW_COL_NAMES if item in pooledFeatures]
    rows    = [item for item in VOW_ROW_NAMES if item in pooledFeatures]
    table   = [['' for i in range(len(columns) + 1)] for j in range(len(rows) + 1)]
    table[0][1:] = columns
    for i in range(1, len(table)):
        table[i][0] = rows[i - 1]
    for i in range(1, len(table)):
        for j in range(1, len(table[0])):
            temp = []
            for phon in vowList:
                if rows[i - 1] in phon.coreSet and columns[j - 1] in phon.coreSet:
                    checkList.discard(phon)
                    temp.append(str(phon))
            if temp:
                table[i][j] = ", ".join(sorted(temp))
    if checkList:
        raise Exception("Not all vowels made their way in the table: " + ", ".join(checkList))
    return table


def convert2HTML(twoDArr):
    out = ["<table>\n"]
    for item in twoDArr:
        out.append("<tr>\n")
        for cell in item:
            out.append("    <td>" + cell + "</td>\n")
        out.append("</tr>\n")
    out.append("</table>\n\n")
    return "".join(out)

def processInventory(idiomName, phonoString):
    """A function that takes a string of comma separated phonemes
    as an input and them as a <div>."""

    # Classifying phonemes: 
    # 0. Vowels vs. consonants
    # 1. Vowels:
    # 1.1. Monophthongs — with any combinations of secondary features.
    # Every combination of series-forming secondary features serves as a key in the dictionary.
    # All entries for this key are put into a separate table. The same procedure is applied to vowels.
    # 1.2. Diphthongs
    # 1.3. Triphthongs
    # 2. Consonants — with any combinations of secondary features.

    # print(idiomName) # For finding bugs in descriptions.

    conClassDict  = {}
    vowClassDict  = {}
    diphthongs    = []
    triphthongs   = []
    consonants    = []
    vowels        = []
    apical_vowels = []

    inputPhons = re.split(r'\s*,\s*', phonoString)

    for phon in inputPhons:
        phoneme = Phoneme(phon, *parsePhon(phon))
        if 'consonant' in phoneme.coreSet:
            consonants.append(phoneme)
            if phoneme.seriesSet:
                classMarker = " & ".join(sorted(phoneme.seriesSet))
            else:
                classMarker = "plain"
            if classMarker in conClassDict:
                conClassDict[classMarker].append(phoneme)
            else:
                conClassDict[classMarker] = []
                conClassDict[classMarker].append(phoneme)
        elif 'vowel' in phoneme.coreSet:
            if 'diphthong' in phoneme.coreSet:
                diphthongs.append(phon)
            elif 'triphthong' in phoneme.coreSet:
                triphthongs.append(phon)
            elif 'apical' in phoneme.coreSet:
                apical_vowels.append(phon)
            else:
                vowels.append(phoneme)
                if phoneme.seriesSet:
                    classMarker = " & ".join(sorted(phoneme.seriesSet))
                else:
                    classMarker = "plain"
                if classMarker in vowClassDict:
                    vowClassDict[classMarker].append(phoneme)
                else:
                    vowClassDict[classMarker] = []
                    vowClassDict[classMarker].append(phoneme)
        else:
            raise Exception("Neither a vowel nor a consonant?")

    out = StringIO()
    out.write('<div><h1>%s</h1>' % idiomName)
    if conClassDict:
        out.write("<h2>Consonants</h2>")
        keys = sorted(conClassDict.keys(), key = lambda x: len(x))
        for key in keys:
            out.write("<h3>" + key[0].upper() + key[1:] + " series:</h3>")
            out.write(convert2HTML(makeTableCons(conClassDict[key])))
    if vowClassDict:
        out.write("<h2>Vowels</h2>")
        keys = sorted(vowClassDict.keys(), key = lambda x: len(x))
        for key in keys:
            out.write("<h3>" + key[0].upper() + key[1:] + " series:</h3>")
            out.write(convert2HTML(makeTableVow(vowClassDict[key])))
    if apical_vowels:
        out.write("<h3>Apical vowels:</h3>")
        out.write("<p>" + ", ".join(str(el) for el in apical_vowels))
    if diphthongs:
        out.write("<h3>Diphthongs:</h3>")
        out.write("<p>" + ", ".join(str(el) for el in diphthongs))
    if triphthongs:
        out.write("<h3>Triphthongs:</h3>")
        out.write("<p>" + ", ".join(str(el) for el in triphthongs))
    out.write('</div>')

    return out.getvalue()

# Test client
if __name__ == '__main__':
    phons = "a, b, c, d, e, f, g"
    div = processInventory("dummy", phons)
    with open('test.html', 'w', encoding = 'utf-8') as out:
        out.write("""<html>
            <head>
            <title>%s</title>
            </head>
            <body>
            %s
            </body>
            </html>""" % ("dummy", div))