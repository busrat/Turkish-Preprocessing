#!/usr/bin/env python
#coding:utf8
import pandas as pd
import os
import re
import difflib
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import make_pipeline
from sklearn import metrics
from sklearn.linear_model import LogisticRegressionCV

class StopWordElimination:
    def __init__(self):
        self.stopwords = self.readStopWords()

    def readStopWords(self):
        return pd.read_csv('stopwords.txt', error_bad_lines=False, sep=',', header=None)

    def eliminatorUsingList(self, contentArr):
        for ca in contentArr:
            if ca in self.stopwords[0].values:
                contentArr.remove(ca)
        return contentArr

    def dynamicEliminator(self, lastList):
        frequencyDictionary = {}
        for wordList in lastList:
            for word in wordList:
                if word in frequencyDictionary:
                    frequencyDictionary[word] = frequencyDictionary[word] + 1
                else:
                    frequencyDictionary[word] = 1
        sortedArr = sorted(frequencyDictionary, key=frequencyDictionary.get, reverse=True)
        sortedArr = sortedArr[:int(len(sortedArr) / 5)]
        for wordList in lastList:
            for word in wordList:
                if word in sortedArr:
                    wordList.remove(word)
        return lastList

class Tokenization:
    def splitter(self, content):
        content = content.lower()
        return content.split()

    def removeSomeCharacters(self, content):
        someCharacters = ['\r', '!', '"', '#', '$', '%', '&', '(', ')', '*', '+', '/', ':', ';', '<', '=', '>', '@', '[', '\\', ']', '^', '`', '{', '|', '}', '~', '\t']
        for i in someCharacters:
            content = content.replace(i, '')
        return self.splitter(content)

class SentenceSplitting:
    def __init__(self):
        self.abbreviations = self.format_abbreviations(self.read_list_of_abbreviations())
        self.lower = "([a-zçğıöşü])"
        self.caps = "([A-ZÇĞİÖŞÜ])"
        self.digits = "([0-9])"
        self.abbreviations = "(%s)[.]" % self.abbreviations
        self.acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        self.websites = "[.](www|edu|com|net|org|io|gov|tr)"

    def read_list_of_abbreviations(self):
        with open("Turkish_Abbreviations.txt", encoding="utf8") as f:
            abbreviations = f.readlines()
        abbreviations = [x.strip() for x in abbreviations]
        return abbreviations

    def format_abbreviations(self, abbreviations):
        return '|'.join(abbreviations)

    def split_sentences(self, text):
        text = text.replace("\n", "")  # Remove all the new lines
        text = re.sub(self.lower + "[.]" + self.lower + "[.]", "\\1<ambiguity>\\2<ambiguity>", text)  # Replace the full stop like v.b. with <ambiguity>
        text = re.sub(self.caps + "[.]" + self.caps + "[.]", "\\1<ambiguity>\\2<ambiguity>", text)  # Replace the full stop like A.Ş. with <ambiguity>
        text = re.sub(self.caps + "[.]" + self.caps + "[.]" + self.caps + "[.]", "\\1<ambiguity>\\2<ambiguity>\\3<ambiguity>", text)  # Replace the full stop like T.S.E. with <ambiguity>
        text = re.sub(self.abbreviations, "\\1<ambiguity>", text)  # Replace the full stop on abbreviations with <ambiguity>
        text = re.sub(self.digits + "[.]" + self.digits, "\\1<ambiguity>\\2", text)  # Replace the full stop on decimal numbers with <ambiguity>
        text = re.sub(self.websites, "<ambiguity>\\1", text)  # Replace the full stop on the web URLs with <ambiguity>
        text = re.sub("\s" + self.caps + "[.] ", " \\1<ambiguity> ", text)
        text = re.sub(self.digits + "[.] " + self.lower, " \\1<ambiguity> \\2", text)
        text = re.sub(self.lower + "[.]" + "[\"] " + self.lower, "\\1<fullStopQuotes>\\2", text)  # Replace the full stop that is ."
        text = re.sub(self.lower + "[?]" + "[\"] " + self.lower, "\\1<questionMarkQuotes> \\2", text)  # Replace the question mark that is ?"
        text = re.sub(self.lower + "[!]" + "[\"] " + self.lower, "\\1<exclamationMarkQuotes> \\2", text)  # Replace the exclamation mark that is !"

        if "..." in text:
            text = text.replace("...", "<ambiguity><ambiguity><ambiguity>")

        text = text.replace(".", ".<stop>")
        text = text.replace("?", "?<stop>")
        text = text.replace("!", "!<stop>")
        text = text.replace("<ambiguity>", ".")
        text = text.replace("<fullStopQuotes>", ".\" ")
        text = text.replace("<exclamationMarkQuotes>", "!\" ")
        text = text.replace("<questionMarkQuotes>", "?\" ")
        text = text.replace("<stop> ", "<stop>")  # To get rid of the space after the punctuations in the end of the sentence
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        return sentences

class SentenceSplittingLogisticReg:
    def __init__(self):
        self.sents = nltk.corpus.treebank_raw.sents()
        self.tokens = []
        self.boundaries = set()
        self.offset = 0

        for sent in self.sents:
            self.tokens.extend(sent)
            self.offset += len(sent)
            self.boundaries.add(self.offset - 1)

    def trainModel(self):
        self.featuresets = [(self.featureExtractor(self.tokens, i), (i in self.boundaries))
                       for i in range(1, len(self.tokens) - 1)
                       if self.tokens[i] in '.?!']
        size = int(len(self.featuresets) * 0.5)
        trainSet, testSet = self.featuresets[size:], self.featuresets[:size]
        a, b = map(list, zip(*trainSet))
        c, d = map(list, zip(*testSet))

        pipe = make_pipeline(DictVectorizer(), LogisticRegressionCV())
        pipe.fit(a, b)
        y_new = pipe.predict(c)
        accuracy = metrics.accuracy_score(d, y_new)
        return pipe, accuracy

    def sentenceSplitter(self, text):
        self.words = word_tokenize(text)
        pipe, accuracy = self.trainModel()
        start = 0
        sents = []
        for i, word in enumerate(self.words):
            extracted = self.featureExtractor(self.words, i)
            if word in '.?!' and pipe.predict(extracted):
                sents.append(TreebankWordDetokenizer().detokenize(self.words[start:i + 1]))
                start = i + 1
        if start < len(self.words):
            sents.append(self.words[start:])
        return sents, accuracy

    def featureExtractor(self, tokens, i):
        return {'isNextWordCapitalized': tokens[i][0].isupper(),
                'previousWord': tokens[i - 1].lower(),
                'punctuation': tokens[i],
                'isPreviousWordIsOneChar': len(tokens[i - 1]) == 1}

class Stemming:
    def __init__(self):
        self.hardeningLettersDict = {"c": "ç", "d": "t", "b": "p", "g": "k"}
        self.softeningLettersDict = {"ç": "c", "t": "d", "p": "b", "k": "ğ", "g": "ğ"}
        self.dotlessVowelsDict = {"ı", "O", "o", "u", "I", "A", "a", "U"}
        self.dottedVowelsDict = {"i", "Ö", "e", "Ü", "E", "İ", "ö", "ü"}
        self.vowelsDict = self.dotlessVowelsDict.union(self.dottedVowelsDict)

        self.stemsDict = {}
        self.suffixesDict = {}
        self.deletedLettersDict = {}

    def removePunctuations(self, word):
        punctuations = ['.', ',', ';', ':', '-,', '...', '?', '!', '(', ')', '[', ']', '{', '}', '<', '>', '"', '/', '\'', '#', '-', '@']
        for letter in word:
            if letter in punctuations:
                word = word.replace(letter, "")
        return word

    def removeNewLine(self, word):
        normalized = word.replace("\n", "")
        return normalized

    def convertToLowercase(self, word):
        normalized = word.lower()
        return normalized

    def readStemsList(self):
        with open("Turkish_Stems.txt", "r", encoding="utf-8") as file:
            for line in file.readlines():
                line = line.strip().split()
                stem = line[0].strip()
                stemType = line[1].strip()

                if len(line) > 1:
                    for i in range(2, len(line)):
                        stemType += ' ' + line[i].strip()

                if stem in self.stemsDict.keys():
                    if stemType not in self.stemsDict[stem]:
                        self.stemsDict[stem] += ' ' + stemType
                else:
                    self.stemsDict[stem] = stemType

                if "DUS" in stemType:  # unlu dusmesi
                    if len(stem) > 2:
                        placeholder = stem
                        stem = stem[:-2] + stem[
                            -1]  # move away the second last letter of the word, because it is a vowel
                        self.deletedLettersDict[placeholder] = stem
                        if stem not in self.stemsDict.keys():
                            self.stemsDict[stem] = stemType + " DUS"
                        else:
                            if "DUS" not in self.stemsDict[stem]:
                                self.stemsDict[stem] = stemType + " DUS"
        self.readSuffixesList()

    def readSuffixesList(self):
        with open("Turkish_Suffixes.txt", "r", encoding="utf-8") as file:
            for line in file.readlines():
                line = line.strip().split()
                if len(line) > 1:
                    suffix = line[0].strip()
                    suffixType = line[1].strip()
                    if suffix in self.suffixesDict.keys():
                        if suffixType not in self.suffixesDict[suffix]:
                            self.suffixesDict[suffix] += ' ' + suffixType
                    else:
                        self.suffixesDict[suffix] = suffixType

    def checkNegativitySuffix(self, stem, index, word):
        if (word[index - 2] == "m") and (word[index - 3] in ["e", "a"]):

            if "amıyor" in word:
                negativityIndex = word.find("amıyor")
                stem = word[:negativityIndex]

                if (stem not in self.stemsDict.keys()) and ("FI" not in self.stemsDict[stem]):  # check whether stem is a verbal noun (fiilimsi)
                    negativityIndex += 1
                    stem = word[:negativityIndex]
                    negativityIndex += 1
                elif ((stem + "a") in self.stemsDict.keys()) and ("FI" in self.stemsDict[stem + "a"]):
                    stem += "a"
                    negativityIndex += 2
                else:
                    negativityIndex += 1
                return stem, negativityIndex

            elif "emiyor" in word:
                negativityIndex = word.find("emiyor")
                stem = word[:negativityIndex]
                if stem == "yiy":  # verb "yemek" has a special case
                    stem = "ye"
                    negativityIndex = 1
                elif stem == "y":  # verb "yemek" has a special case
                    stem = "ye"
                    negativityIndex += 1
                elif stem == "d":  # verb "demek" has a special case
                    stem = "de"
                    negativityIndex += 1
                elif stem == "diy":  # verb "demek" has a special case
                    stem = "de"
                    negativityIndex = 1

                if (stem not in self.stemsDict.keys()) and ("FI" not in self.stemsDict[stem]):
                    negativityIndex += 1
                    stem = word[:negativityIndex]
                    negativityIndex += 1
                else:
                    negativityIndex += 1
                return stem, negativityIndex
        else:
            return stem, None

    def checkLastVowel(self, stem):
        for i in range(len(stem), 0, -1):
            if stem[-i] in self.vowelsDict:
                return stem[-i]
        return None

    def checkSuffixes(self, word):
        index = word.find("yor")

        if word[index - 1] not in ["u", "ü", "ı", "i"]:
            return None, None

        stem = word[:index - 1]
        if len(stem) > 2:
            stem, negativityIndex = self.checkNegativitySuffix(stem, index, word)
        elif stem == "ed":
            stem = "et"
        if stem == "diy":
            stem = "de"
        elif stem == "yiy":
            stem = "ye"
        elif stem == "d":
            stem = "de"
        elif stem == "y":
            stem = "ye"
        elif stem == "söyl":
            stem = "söyle"
        suffix = word[index - 1:]

        if suffix in self.suffixesDict.keys():
            if "FI" in self.suffixesDict[suffix]:
                if stem in self.stemsDict.keys():
                    if "FI" in self.stemsDict[stem]:
                        return stem, suffix

        if suffix in self.suffixesDict.keys():
            lastVowel = self.checkLastVowel(stem)
            if lastVowel in self.dottedVowelsDict:
                if word[index - 1] == "ü" or word[index - 1] == "i":
                    if stem not in ["de", "ye"]:
                        stem += "e"
                    if stem in self.stemsDict.keys():
                        return stem, suffix
            if lastVowel in self.dotlessVowelsDict:
                if word[index - 1] == "u" or word[index - 1] == "ı":
                    stem += "a"
                    if stem in self.stemsDict.keys():
                        return stem, suffix
        return None, None

    def findStem(self, word):
        self.readStemsList()
        word = self.removeNewLine(word)
        word = self.removePunctuations(word)
        word = self.convertToLowercase(word)

        stemAndSuffixes = []

        if word in self.stemsDict.keys():  # if the user input exists in the stem dictionary
            stemAndSuffixes.append(word)
            return stemAndSuffixes, word, self.stemsDict[word]

        if len(word) < 3:  # if the user input is less than 3 characters and does not exist in the stem dictionary
            stemAndSuffixes.append(word)
            return stemAndSuffixes, word, None

        # if "-yor" suffix exists in the word and the word ends with a vowel letter either "-a" or "-e", this vowel letter converts to either "-ı" or "-i" or "-u" or "-ü"
        # unlu daralmasi
        if "yor" in word:
            stem, suffix = self.checkSuffixes(word)
            if stem is not None and suffix is not None:
                stemAndSuffixes.append(stem + ":" + suffix)
                return stemAndSuffixes, stem, "FI"

        if word[0] in ["y", "d"]:  # verb "ye" and verb "de" have special cases
            for sfx in ["iyeceğ", "iyecek", "iyeme", "iyebil", "iyen", "iyip", "iyince", "iyerek"]:
                if sfx in word:
                    suffix = word[1:]
                    stem = word[0] + "e"
                    stemAndSuffixes.append(stem + ":" + suffix)
                    return stemAndSuffixes, stem, "FI"

        for i in range(len(word), -1, -1):
            stem = word[:i]
            suffix = word[i:]
            stemType = ""
            suffixType = ""

            if suffix in self.suffixesDict.keys():
                suffixType = self.suffixesDict[suffix]
                if stem in self.stemsDict.keys():
                    stemType = self.stemsDict[stem]
                    suffixesTypes = suffixType.split(' ')  # if more than one types of suffixes exist

                    for sufType in suffixesTypes:
                        if sufType in stemType:
                            if ("DUS" in stemType) and (stem in self.deletedLettersDict.values()):  # unlu dusmesi
                                stem = list(self.deletedLettersDict.keys())[list(self.deletedLettersDict.values()).index(stem)]
                            stemAndSuffixes.append(stem + ":" + suffix)
                            return stemAndSuffixes, stem, stemType

            if stemType != "":
                if ("EKSI" in stemType) and (stem[-1] in self.softeningLettersDict.values()):  # unsuz yumusamasi
                    for key in self.softeningLettersDict.keys():
                        if stem[-1] == self.softeningLettersDict[key]:
                            stem = stem[:-1] + key
                            break

                if ("DUS" in stemType) and (stem in self.deletedLettersDict.keys()):
                    stem = self.deletedLettersDict[stem]

            elif (suffixType != "") and (len(stem) != 0):
                if stem[-1] in self.hardeningLettersDict.keys():
                    for key in self.hardeningLettersDict.keys():
                        if key == stem[-1]:
                            stem = stem[:-1] + self.hardeningLettersDict[key]
                            if stem in self.stemsDict.keys():
                                stemType = self.stemsDict[stem]
                                if "YUM" in stemType:
                                    suffixesTypes = suffixType.split(' ')
                                    for sufType in suffixesTypes:
                                        if sufType in stemType:
                                            stemAndSuffixes.append(stem + ":" + suffix)
                                            return stemAndSuffixes, stem, stemType

                if stem[-1] in self.softeningLettersDict.values():
                    for key in self.softeningLettersDict.keys():
                        if self.softeningLettersDict[key] == stem[-1]:
                            stem = stem[:-1] + key
                            if stem in self.stemsDict.keys():
                                stemType = self.stemsDict[stem]
                                suffixesTypes = suffixType.split(' ')
                                for sufType in suffixesTypes:
                                    if sufType in stemType:
                                        stemAndSuffixes.append(stem + ":" + suffix)
                                        return stemAndSuffixes, stem, stemType
        stemAndSuffixes.append(word)
        return stemAndSuffixes, stem, stemType

class Normalization:
    def __init__(self):
        self.wordDict = {}

    def readMisspelledWords(self):
        with open("Turkish_Misspelled_Words.txt", encoding="utf8") as f:
            for line in f.readlines():
                line = line.strip().split()
                if len(line) > 1:
                    misspelledWords = line[0].strip()
                    spelledWords = line[1].strip()
                    if misspelledWords in self.wordDict.keys():
                        if spelledWords not in self.wordDict[misspelledWords]:
                            self.wordDict[misspelledWords] += ' ' + spelledWords
                    else:
                        self.wordDict[misspelledWords] = spelledWords
        return self.wordDict

    def removeNewLine(self, text):
        normalized = text.replace("\n", "")
        return normalized

    def convertToLowercase(self, text):
        normalized = text.lower()
        return normalized

    def removePunctuations(self, text):
        punctuations = ['.', ',', ';', ':', '-,', '...', '?', '!', '(', ')', '[', ']', '{', '}', '<', '>', '"', '/',
                        '\'', '#', '-', '@']
        for letter in text:
            if letter in punctuations:
                text = text.replace(letter, "")
        return text

    def checkNotEmpty(self, text):
        if len(text) == 0:
            return False
        else:
            return True

    def removeRepeatedCharacters(self, text):
        for match in re.findall(r'((\w)\2{2,})', text):
            text = re.sub(match[0], match[1] + match[1], text)
        return text

    def calculateDistance(self, text):
        minimumDistance = 0
        possibleValues = []

        for value in self.wordDict.values():
            seq = difflib.SequenceMatcher(a=text.lower(), b=value.lower())
            if seq.ratio() > minimumDistance:
                minimumDistance = seq.ratio()
                possibleValues.clear()
                possibleValues.append(value)
            elif seq.ratio() == minimumDistance:
                if value not in possibleValues:
                    possibleValues.append(value)
        return possibleValues

    def checkInputWord(self, text):
        if (self.checkNotEmpty(text)):
            self.wordDict = self.readMisspelledWords()
            text = self.removeNewLine(text)
            text = self.convertToLowercase(text)
            text = self.removePunctuations(text)
            text = self.removeRepeatedCharacters(text)

            if text in self.wordDict.keys():
                return self.wordDict[text]
            else:
                possibleValues = self.calculateDistance(text)
                return possibleValues

class Initialization:
    def MenuChoice(self):
        valid = ["0", "1", "2", "3", "4", "5"]
        while True:
            userInput = input()
            if userInput in valid:
                self.menuCheck(userInput)
                break
            else:
                print("{} is not a correct choice. Please try again.".format(userInput))
                continue

    def menuCheck(self, userInput):
        if userInput == "0":
            exit()
        elif userInput == "1":
            self.callTokenization()
        elif userInput == "2":
            self.callSentenceSplitting()
        elif userInput == "3":
            self.callNormalization()
        elif userInput == "4":
            self.callStemming()
        elif userInput == "5":
            self.callStopWordElimination()

    def callTokenization(self):
        print("\nPlease choose a tokenization model using a or b keywords. Press 0 to return to the previous menu.\n")
        print("\ta. Rule-based Model\n"
              "\tb. Machine Learning Model\n"
              "\t0. Return to the previous menu")

        valid = ["0", "a", "b"]
        while True:
            userInput = input()
            if userInput in valid:
                if userInput == "0":
                    main()
                elif userInput == "a":
                    text = self.getTextFromUser("rule-based tokenization")
                    text = Tokenization().removeSomeCharacters(text)
                    print("\nTokenized text: ", text)
                break
            else:
                print("{} is not a correct choice. Please try again.".format(userInput))
                continue

    def callStopWordElimination(self):
        print("\nPlease choose a stopword elimination approach using a or b keywords. Press 0 to return to the previous menu.\n")
        print("\ta. Static Approach\n"
              "\tb. Dynamic Approach\n"
              "\t0. Return to the previous menu")

        valid = ["0", "a", "b"]
        while True:
            userInput = input()
            if userInput in valid:
                if userInput == "0":
                    main()
                elif userInput == "a":
                    text = self.getTextFromUser("static stopword elimination approach")
                    text = Tokenization().removeSomeCharacters(text)
                    text = StopWordElimination().eliminatorUsingList(text)
                    print("\nOutput text: ", text)
                elif userInput == "b":
                    clearScreen()
                    lastList = []
                    excelDF = pd.ExcelFile('news.xls')
                    df1 = pd.read_excel(excelDF, sheet_name=0)
                    contentArray = df1.content.values
                    print("Up to 20% words with the highest frequency in corpus are deleted for dynamic stopword elimination approach. Please wait...")
                    for content in contentArray:
                        content = Tokenization().removeSomeCharacters(content)
                        lastList.append(content)
                    text = StopWordElimination().dynamicEliminator(lastList)
                    clearScreen()
                    print("Input text before dynamic stopword elimination: ", contentArray[0])
                    print("\nOutput text after dynamic stopword elimination: ", text[0])
                break
            else:
                print("{} is not a correct choice. Please try again.".format(userInput))
                continue

    def callSentenceSplitting(self):
        print("\nPlease choose a sentence splitting model using a or b keywords. Press 0 to return to the previous menu.\n")
        print("\ta. Rule-based Model\n"
              "\tb. Machine Learning Model\n"
              "\t0. Return to the previous menu")

        valid = ["0", "a", "b"]
        while True:
            userInput = input()
            if userInput in valid:
                if userInput == "0":
                    main()
                elif userInput == "a":
                    text = self.getTextFromUser("rule-based sentence splitting")
                    text = SentenceSplitting().split_sentences(text)
                    print("\nSplitted text:\n")
                    print(*text, sep='\n')
                elif userInput == "b":
                    text = self.getTextFromUser("sentence splitting with logistic regression")
                    splittedSentences, accuracy = SentenceSplittingLogisticReg().sentenceSplitter(text)
                    print(splittedSentences)
                    print(accuracy)
                break
            else:
                print("{} is not a correct choice. Please try again.".format(userInput))
                continue

    def callStemming(self):
        text = self.getTextFromUser("sentence splitting")
        text = Tokenization().removeSomeCharacters(text)
        stemList = []
        for word in text:
            if len(word) == 0:
                continue
            stemAndSuffixes, stem, stemType = Stemming().findStem(word)
            if (stemAndSuffixes is None) or len(stemAndSuffixes) == 0:
                stemList.append(word)
            else:
                stemList.append(stem)
        print("\nStems: ", stemList)

    def callNormalization(self):
        text = self.getTextFromUser("normalization")
        text = Tokenization().removeSomeCharacters(text)
        for word in text:
            normalizedList = Normalization().checkInputWord(word)
            if len(normalizedList) != 0:
                print("{} -> {}\n".format(word, normalizedList))

    def getTextFromUser(self, method):
        clearScreen()
        print("\nPlease enter a text for {}:\n".format(method))
        text = input()
        return text

def main():
    clearScreen()
    print("\t\t\tTEXT PREPROCESSING TOOLKIT\t\t\t")
    print("=====================================================================================")
    print("Please choose a preprocessing method using the numbers 1 through 5. Press 0 to exit.\n"
          "\t1. Tokenization\n"
          "\t2. Sentence Splitting\n"
          "\t3. Normalization\n"
          "\t4. Stemming\n"
          "\t5. StopWord Elimination\n"
          "\t0. Exit")
    Initialization().MenuChoice()

def clearScreen():
    clear = lambda: os.system("cls")
    clear()

if __name__ == "__main__":
    main()