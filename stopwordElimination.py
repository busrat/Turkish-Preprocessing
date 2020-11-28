import pandas as pd

stopwords = pd.read_csv('stopwords.txt', error_bad_lines=False, sep=',', header=None);
    
def eliminate(contentArr): 
    for ca in contentArr:
        if ca in stopwords[0].values:
            contentArr.remove(ca)
    return contentArr
