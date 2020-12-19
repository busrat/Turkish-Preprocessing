import difflib
import re

def readMisspelledWords():
    with open("Turkish_Misspelled_Words.txt", encoding="utf8") as f:
        for line in f.readlines():
            line = line.strip().split()
            if len(line) > 1:
                misspelledWords = line[0].strip()
                spelledWords = line[1].strip()
                if misspelledWords in wordDict.keys():
                    if spelledWords not in wordDict[misspelledWords]:
                        wordDict[misspelledWords] += ' ' + spelledWords
                else:
                    wordDict[misspelledWords] = spelledWords
    return wordDict

def removeNewLine(text):
    normalized = text.replace("\n", "")
    return normalized

def convertToLowercase(text):
    normalized = text.lower()
    return normalized

def removePunctuations(text):
    punctuations = ['.', ',', ';', ':', '-,', '...', '?', '!', '(', ')', '[', ']', '{', '}', '<', '>', '"', '/', '\'',
                    '#', '-', '@']
    for letter in text:
        if letter in punctuations:
            text = text.replace(letter, "")
    return text

def checkNotEmpty(text):
    if len(text) == 0:
        return False
    else:
        return True

def removeRepeatedCharacters(text):
    for match in re.findall(r'((\w)\2{2,})', text):
        text = re.sub(match[0], match[1] + match[1], text)
    return text

def calculateDistance(text):
    minimumDistance = 0
    possibleValues = []

    for value in wordDict.values():
        seq = difflib.SequenceMatcher(a=text.lower(), b=value.lower())
        if seq.ratio() > minimumDistance:
            minimumDistance = seq.ratio()
            possibleValues.clear()
            possibleValues.append(value)
        elif seq.ratio() == minimumDistance:
            if value not in possibleValues:
                possibleValues.append(value)
    return possibleValues

def checkInputWord(text):
    if (checkNotEmpty(text)):
        text = removeNewLine(text)
        text = convertToLowercase(text)
        text = removePunctuations(text)
        text = removeRepeatedCharacters(text)

        if text in wordDict.keys():
            return wordDict[text]
        else:
            possibleValues = calculateDistance(text)
            return possibleValues
        
wordDict = {}
wordDict = readMisspelledWords()
text = checkInputWord("klem")
print(text)