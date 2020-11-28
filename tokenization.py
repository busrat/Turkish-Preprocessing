import pandas as pd
from stopwordElimination import eliminatorUsingList, dynamicEliminator

def splitter(content):
    content = content.lower()
    return content.split()

def removeSomeCharacters(content):
    someCharacters = ['\r','!','"','#','$','%','&','(',')','*','+','/',':',';','<','=','>','@','[','\\',']','^','`','{','|','}','~','\t']
    for i in someCharacters: 
        content = content.replace(i, '')
    return content

lastList = []
excelDF = pd.ExcelFile('news.xls')
df1 = pd.read_excel(excelDF, sheet_name=0)
contentArray = df1.content.values
for content in contentArray:
   content = removeSomeCharacters(content)
   content = splitter(content)
   content = eliminatorUsingList(content)
   lastList.append(content)    
listAfterDynamicEliminator = dynamicEliminator(lastList)
