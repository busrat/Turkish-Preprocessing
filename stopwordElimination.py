import pandas as pd

stopwords = pd.read_csv('Turkish_Stopwords.txt', error_bad_lines=False, sep=',', header=None);
    
def eliminatorUsingList(contentArr): 
    for ca in contentArr:
        if ca in stopwords[0].values:
            contentArr.remove(ca)
    return contentArr


#en çok frequencysi olan kelimelerin baştan %20sini siliyoruz
def dynamicEliminator(lastList): 
    frequencyDictionary = {}
    for wordList in lastList:
        for word in wordList:
                if word in frequencyDictionary:
                    frequencyDictionary[word] = frequencyDictionary[word] + 1
                else:
                    frequencyDictionary[word] = 1
    sortedArr = sorted(frequencyDictionary, key=frequencyDictionary.get, reverse=True)
    sortedArr = sortedArr[:int(len(sortedArr)/5)]
    for wordList in lastList:
        for word in wordList:
            if word in sortedArr:
                wordList.remove(word) 
    return lastList
