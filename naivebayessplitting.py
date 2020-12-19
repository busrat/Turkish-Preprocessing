import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize import word_tokenize
import pandas as pd

tokens = []
boundaries = set()
offset = 0
excelDF = pd.ExcelFile('news.xls')
df1 = pd.read_excel(excelDF, sheet_name=0)
contentArray = df1.content.values
for i in contentArray:
   for token in word_tokenize(i):
       tokens.append(token)  
       offset += 1
       boundaries.add(offset-1)

def featureExtractor(tokens, i):
    return {'isNextWordCapitalized': tokens[i][0].isupper(),
              'previousWord': tokens[i-1].lower(),
              'punctuation': tokens[i],
              'isPreviousWordIsOneChar': len(tokens[i-1]) == 1}

featuresets = [(featureExtractor(tokens, i), (i in boundaries))
                for i in range(1, len(tokens)-1)
                if tokens[i] in '.?!']
size = int(len(featuresets) * 0.5)
trainSet, testSet = featuresets[size:], featuresets[:size]
classifier = nltk.NaiveBayesClassifier.train(trainSet)
accuracy = nltk.classify.accuracy(classifier, testSet) 

def sentenceSplitter(words):
   words = word_tokenize(words)
    start = 0
    sents = []
    for i, word in enumerate(words):
        if word in '.?!' and classifier.classify(featureExtractor(words, i)) == True:
            sents.append(TreebankWordDetokenizer().detokenize(words[start:i+1]))
            start = i+1
    if start < len(words):
        sents.append(words[start:])
    return sents

text = "Planla Kıbrıs'ın Rumların denetimi altına verildiğini, nüfus aktarımının da Rumlar lehine gelişeceğini ifade eden Linn, Bu da Kıbrıslı Türklerin kendi ülkelerinde bağımsızlıklarının sonu olacaktır dedi. Sözlerine 20.02.2020'de şöyle devam etti. Anayasanın 5. maddesine göre sen Dr. olamazsın."
print(sentenceSplitter(text))
