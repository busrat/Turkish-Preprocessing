import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize import word_tokenize
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer

sents = nltk.corpus.treebank_raw.sents() 
tokens = []
boundaries = set()
offset = 0
for sent in sents:
    tokens.extend(sent)
    offset += len(sent)
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
a,b = map(list,zip(*trainSet))
from sklearn.linear_model import LogisticRegressionCV
c,d = map(list,zip(*testSet))

from sklearn.pipeline import make_pipeline
pipe = make_pipeline(DictVectorizer(), LogisticRegressionCV())
pipe.fit(a, b)
y_new = pipe.predict(c)
from sklearn import metrics
accuracy = metrics.accuracy_score(d, y_new)

def sentenceSplitter(words):
    start = 0
    sents = []
    for i, word in enumerate(words):
        extracted = featureExtractor(words, i)
        if word in '.?!' and pipe.predict(extracted) == True:
            sents.append(TreebankWordDetokenizer().detokenize(words[start:i+1]))
            start = i+1
    if start < len(words):
        sents.append(words[start:])
    return sents

text = "Planla Kıbrıs'ın Rumların denetimi altına verildiğini,nüfus aktarımının da Rumlar lehine gelişeceğini ifade eden Linn, Bu da Kıbrıslı Türklerin kendi ülkelerinde bağımsızlıklarının sonu olacaktır dedi. Sözlerine 20.02.2020'de şöyle devam etti. Anayasanın 5. maddesine göre sen Dr. olamazsın."
arr = word_tokenize(text)
print(arr)
deneme = sentenceSplitter(arr)
print(deneme)
