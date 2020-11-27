import pandas as pd

def splitter(content):
 return content.split()

def removeSomeCharacters(content):
    someCharacters = ['\r','!','"','#','$','%','&','(',')','*','+','/',':',';','<','=','>','@','[','\\',']','^','`','{','|','}','~','\t']
    for i in someCharacters: 
        content = content.replace(i, '')
    return content

stopwords = pd.read_csv('stopwords.txt', error_bad_lines=False, sep=',', header=None);
def stopwordsElimination(content): 
    if content in stopwords[0].values:
        return True
    else: 
        return False
        

contentArray = []
excelDF = pd.ExcelFile('news.xls')
df1 = pd.read_excel(excelDF, sheet_name=0)
for content in df1.content.values:
    content = removeSomeCharacters(content)
    content = splitter(content)
    for c in content:
        if stopwordsElimination(c) == False:
          contentArray.append(c)
        
    
print(len(contentArray))
    
