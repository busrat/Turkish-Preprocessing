import pandas as pd

def splitter(content):
 return content.split()

def removeSomeCharacters(content):
    someCharacters = ['\r','!','"','#','$','%','&','(',')','*','+','/',':',';','<','=','>','@','[','\\',']','^','`','{','|','}','~','\t']
    for i in someCharacters: 
        content = content.replace(i, '')
    return content


excelDF = pd.ExcelFile('news.xls')
df1 = pd.read_excel(excelDF, sheet_name=0)
for content in df1.content:
    content = removeSomeCharacters(content)
    content = splitter(content)
    print(content)
    
