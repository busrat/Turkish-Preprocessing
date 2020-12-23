import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize import word_tokenize
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
import re
from nltk.tokenize.treebank import TreebankWordDetokenizer

sents = nltk.corpus.treebank_raw.words()
boundaries = set()
ozet = 'Şeker Portakalı , dünya klasikleri arasında en sevilerek okunan her yaşa hitap eden bir eserdir. Hayatınızın belli dönemlerinde farklı yaş gruplarında okuduğunuz da romanın sizin için anlamı ve değeri daha fazla değişecektir. Yazar Jose Mauro De Vasconceles bu eşsiz eserini on iki günde yazmıştır fakat biraz kendi hayatının bir kesiti gibi olan baş karakter Zeze bir ömür içinde taşıdığını söyler. Zeze aslında yazarın hayatının içerisinde anlam yüklediği tatlı karakteridir. TÜRÜ :  RomanYAZAR : Jose Mauro De Vasconceles KONUSU: Zeze , kalbi temiz ama çok yaramaz bir çocuktur. 5 yaşında olmasına rağmen Zeze hayat dolu , yaşına göre fazla zeki , yoksulluk içerisinde ki acı hayatını eser anlatmaktadır. Zeze çok yaramaz ve çok akıllı olduğu için çevresinde ki bir kaç insan hariç dışında ki herkes ona şeytan der. Zeze hatta o kadar zekidir ki okumayı erkenden söker ve öğretmeni tarafından çok sevilir. ÖNEMİ:  Şeker Portakalı yazarın bu serideki ilk kitabıdır. Eserin devamı niteliğinde ki ikinci kitabı ” Güneşi Uyandıralım ” dır. Serinin üçüncü romanı ise ” Delifişek”tir. Yazar Jose Mauro De Vasconceles bir çok farklı alanda iş yapmış ve çalışmıştır. Yazarlık cevherini ömrünün ileri ki yıllarında çok sonra keşfetmiştir. Bunun için bunca değiştiği meslek hayatı ve ömrünün birikmiş hikayeleri sayesinde romanlarını kaleme almıştır.Şeker Portakalı Roman Özeti Zeze ; 5 yaşında çok yaramaz fakat bir o kadar da yaşına göre fazla zeki bir çocuktur. Bu yaramazlığı ve zekiliğinden dolayı etrafındaki bir kaç kişi hariç herkes ona şeytan der. Onun şeytan olmadığına bir ablası bir de öğretmeni inanmaz , onu severler. Zekiliği sayesinde kendini öğretmenine sevdirmiştir çünkü okumayı erkenden sökmüştür. Zeze beş yaşında olmasına rağmen, bir yetişkin gibi davranıp olayları algılamaya çalışabiliyor. Babası işsiz olduğu için zor durumda olan aile; taşınmak zorunda kalır. Yoksulluk içerisinde yaşarken bir de bu taşınma olayı Zeze’yi üzer ve bir şeker portakalı seçmesini söylerler. Seçer ve bu şeker portakalı ; Zeze’nin en iyi arkadaşı sırdaşı olur. Her gün ne yaşadıysa , ne yaptıysa ona anlatmaya başlar karşılıklı sohbet ederler.Yılbaşı gelip çattığında Zeze babasından hediye bekler fakat yoksul baba hediye alamaz. Zeze’de babası da bu duruma üzülürler ama Zeze bu durumdan kendini suçlu hisseder . Bu yüzden ayakkabı boya kutusunu aldığı gibi dışarı çıkıp babasına hediye almak için para biriktirmeye başlar ve bunu başarır çok mutlu olur. Ama onun en büyük hayallerinden biri şehirde arabaların arkasına tutunup rüzgarı hissetmektir. Bu hayalini gerçekleştirir ama arabanın sahibi olan adamdan dayak yer. Orada araba sahibini bir gün öldüreceğine dair yemin eder. O adamı gördüğü yerde kaçar. Bir gün yine yaramazlık yaparken kendini keser. Okula giderken topallar tabii…  Adam Zeze’nin o halini görünce ona pansuman yaptırır ve limonata,pasta ısmarlar. Zeze ,adamı çok sever ilerleyen zamanda onu babası gibi görmeye başlar. Bu arada Zeze olağan yaramazlıklarına devam eder ve bunların sonucunda hep dayak yer. Bir gün çok ağır bir dayak yer ve o sırada birde bu Adamın arabasına tren çarpıp öldüğünü duyar. Ve Şeker Portakalı da kesilecektir artık Zeze iyice yıkılır. Fakat hayatına bu değerler olmadan artık devam etmek zorundadır.'
tokens = word_tokenize(ozet)
tokens.append("3.5")
   
def featureExtractor(tokens, i):
    return {'isNextWordCapitalized': tokens[i][0].isupper(),
              'previousWord': tokens[i-1].lower(),
              'nextWord': tokens[i+1 if i < len(tokens)-1 else 0].lower(),
              'punctuation': tokens[i],
              'isPreviousWordNumber': type(tokens[i-1]) == int,
              'isNextWordNumber': type(tokens[i+1 if i < len(tokens)-1 else 0]) == int}

featuresets = [(featureExtractor(tokens, i), (tokens[i] in ['.',',',':',';']))
                for i in range(0, len(tokens)-1)
                if any(x in tokens[i] for x in ['.',',',':',';'])]
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

def tokenizer(words):
    start = 0
    sents = []
    for i, word in enumerate(words):
        extracted = featureExtractor(words, i)
        if (any(x in word for x in ['.',',',':',';']) and word not in ['.',',',':',';']) and pipe.predict(extracted) == True:
            sents.extend(re.split("([.,:;])", word))
            start = i+1
    if start < len(words):
        sents.append(words[start:]) # splitle ekle sadece boşluğa bakarak
    return sents

text = "Son Dakika:İstanbul'da taksi,minibüs ve dolmuş ücretlerine yüzde 11 zam yapıldı.Vatandaş bu duruma tepkili."
deneme = tokenizer(text.split())
print(deneme)


