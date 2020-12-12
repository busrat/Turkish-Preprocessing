# -*- coding: utf-8 -*-

hardeningLettersDict = {"c": "ç", "d": "t", "b": "p", "g": "k"}
softeningLettersDict = {"ç": "c", "t": "d", "p": "b", "k": "ğ", "g": "ğ"}
dotlessVowelsDict = {"ı", "O", "o", "u", "I", "A", "a", "U"}
dottedVowelsDict = {"i", "Ö", "e", "Ü", "E", "İ", "ö", "ü"}
vowelsDict = dotlessVowelsDict.union(dottedVowelsDict)

stemsDict = {}
suffixesDict = {}
deletedLettersDict = {}

def readStemsList():
    with open("Turkish_Stems.txt", "r", encoding="utf-8") as file:
        for line in file.readlines():
            line = line.strip().split()
            stem = line[0].strip()
            stemType = line[1].strip()

            if len(line) > 1:
                for i in range(2, len(line)):
                    stemType += ' ' + line[i].strip()

            if stem in stemsDict.keys():
                if stemType not in stemsDict[stem]:
                    stemsDict[stem] += ' ' + stemType
            else:
                stemsDict[stem] = stemType

            if "DUS" in stemType:  # unlu dusmesi
                if len(stem) > 2:
                    placeholder = stem
                    stem = stem[:-2] + stem[-1]  # move away the second last letter of the word, because it is a vowel
                    deletedLettersDict[placeholder] = stem
                    if stem not in stemsDict.keys():
                        stemsDict[stem] = stemType + " DUS"
                    else:
                        if "DUS" not in stemsDict[stem]:
                            stemsDict[stem] = stemType + " DUS"


def readSuffixesList():
    with open("Turkish_Suffixes.txt", "r", encoding="utf-8") as file:
        for line in file.readlines():
            line = line.strip().split()
            if len(line) > 1:
                suffix = line[0].strip()
                suffixType = line[1].strip()
                if suffix in suffixesDict.keys():
                    if suffixType not in suffixesDict[suffix]:
                        suffixesDict[suffix] += ' ' + suffixType
                else:
                    suffixesDict[suffix] = suffixType


def checkNegativitySuffix(stem, index, word):
    if (word[index - 2] == "m") and (word[index - 3] in ["e", "a"]):

        if "amıyor" in word:
            negativityIndex = word.find("amıyor")
            stem = word[:negativityIndex]

            if (stem not in stemsDict.keys()) and ("FI" not in stemsDict[stem]):  # check whether stem is a verbal noun (fiilimsi)
                negativityIndex += 1
                stem = word[:negativityIndex]
                negativityIndex += 1
            elif ((stem + "a") in stemsDict.keys()) and ("FI" in stemsDict[stem + "a"]):
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

            if (stem not in stemsDict.keys()) and ("FI" not in stemsDict[stem]):
                negativityIndex += 1
                stem = word[:negativityIndex]
                negativityIndex += 1
            else:
                negativityIndex += 1
            return stem, negativityIndex
    else:
        return stem, None


def checkLastVowel(stem):
    for i in range(len(stem), 0, -1):
        if stem[-i] in vowelsDict:
            return stem[-i]
    return None


def checkSuffixes(word):
    index = word.find("yor")

    if word[index-1] not in ["u", "ü", "ı", "i"]:
        return None, None

    stem = word[:index - 1]
    if len(stem) > 2:
        stem, negativityIndex = checkNegativitySuffix(stem, index, word)
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
    suffix = word[index-1:]

    if suffix in suffixesDict.keys():
        if "FI" in suffixesDict[suffix]:
            if stem in stemsDict.keys():
                if "FI" in stemsDict[stem]:
                    return stem, suffix

    if suffix in suffixesDict.keys():
        lastVowel = checkLastVowel(stem)
        if lastVowel in dottedVowelsDict:
            if word[index-1] == "ü" or word[index-1] == "i":
                if stem not in ["de", "ye"]:
                    stem += "e"
                if stem in stemsDict.keys():
                    return stem, suffix
        if lastVowel in dotlessVowelsDict:
            if word[index-1] == "u" or word[index-1] == "ı":
                stem += "a"
                if stem in stemsDict.keys():
                    return stem, suffix
    return None, None


def findStem(word):
    stemAndSuffixes = []

    if word in stemsDict.keys():  # if the user input exists in the stem dictionary
        stemAndSuffixes.append(word)
        return stemAndSuffixes, word, stemsDict[word]

    if len(word) < 3:  # if the user input is less than 3 characters and does not exist in the stem dictionary
        stemAndSuffixes.append(word)
        return stemAndSuffixes, word, None

    # if "-yor" suffix exists in the word and the word ends with a vowel letter either "-a" or "-e", this vowel letter converts to either "-ı" or "-i" or "-u" or "-ü"
    # unlu daralmasi
    if "yor" in word:
        stem, suffix = checkSuffixes(word)
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

        if suffix in suffixesDict.keys():
            suffixType = suffixesDict[suffix]
            if stem in stemsDict.keys():
                stemType = stemsDict[stem]
                suffixesTypes = suffixType.split(' ')  # if more than one types of suffixes exist

                for sufType in suffixesTypes:
                    if sufType in stemType:
                        if ("DUS" in stemType) and (stem in deletedLettersDict.values()):  # unlu dusmesi
                            stem = list(deletedLettersDict.keys())[list(deletedLettersDict.values()).index(stem)]
                        stemAndSuffixes.append(stem + ":" + suffix)
                        return stemAndSuffixes, stem, stemType

        if stemType != "":
            if ("EKSI" in stemType) and (stem[-1] in softeningLettersDict.values()):  # unsuz yumusamasi
                for key in softeningLettersDict.keys():
                    if stem[-1] == softeningLettersDict[key]:
                        stem = stem[:-1] + key
                        break

            if ("DUS" in stemType) and (stem in deletedLettersDict.keys()):
                stem = deletedLettersDict[stem]

        elif (suffixType != "") and (len(stem) != 0):
            if stem[-1] in hardeningLettersDict.keys():
                for key in hardeningLettersDict.keys():
                    if key == stem[-1]:
                        stem = stem[:-1] + hardeningLettersDict[key]
                        if stem in stemsDict.keys():
                            stemType = stemsDict[stem]
                            if "YUM" in stemType:
                                suffixesTypes = suffixType.split(' ')
                                for sufType in suffixesTypes:
                                    if sufType in stemType:
                                        stemAndSuffixes.append(stem + ":" + suffix)
                                        return stemAndSuffixes, stem, stemType

            if stem[-1] in softeningLettersDict.values():
                for key in softeningLettersDict.keys():
                    if softeningLettersDict[key] == stem[-1]:
                        stem = stem[:-1] + key
                        if stem in stemsDict.keys():
                            stemType = stemsDict[stem]
                            suffixesTypes = suffixType.split(' ')
                            for sufType in suffixesTypes:
                                if sufType in stemType:
                                    stemAndSuffixes.append(stem + ":" + suffix)
                                    return stemAndSuffixes, stem, stemType

    stemAndSuffixes.append(word)
    return stemAndSuffixes, stem, stemType

def main():
    readStemsList()
    readSuffixesList()

    user_input=[]
    say=0

    # dosya='alice'
    # fad="veri/{}-cozulenler.txt".format(dosya)
    # ftamam = open(fad,"w",encoding="utf-8")
    # fad="veri/{}-cozulen-kokler.txt".format(dosya)
    # ftamamkok = open(fad,"w",encoding="utf-8")
    # fname = "veri/{}_kelimeler.txt".format(dosya)
    # with open(fname,"r") as f:
    #     for line in f.readlines():
    #         l = line.split()
    #         for k in l:
    #             user_input.append(k.strip())
    #             say+=1
    #             #if say>=1000: break


    user_input = ["kitapçılarınki", "bardağın"]
    for word in user_input:
        if len(word) == 0:
            continue
        stemAndSuffixes, stem, stemType = findStem(word)

        if (stemAndSuffixes is None) or len(stemAndSuffixes) == 0:
            print("Bulunamadı!")

        print("{} {} {}".format(word, stemAndSuffixes, stemType))
        print("{} -> {}\n".format(word, stem))


if __name__ == "__main__":
    main()