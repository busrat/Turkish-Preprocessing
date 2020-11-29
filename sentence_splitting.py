import pandas as pd
import re  #RegEx
import csv

def read_corpus():
    excelFile = pd.ExcelFile('news.xls')
    corpus = pd.read_excel(excelFile, sheet_name=0)
    contentArray = corpus.content.values
    return contentArray

def read_list_of_abbreviations():
    with open("turkish_abbreviations.txt", encoding="utf8") as f:
        abbreviations = f.readlines()
    abbreviations = [x.strip() for x in abbreviations]
    return abbreviations

def format_abbreviations(abbreviations):  # Prepare abbreviations by adding '|' sign for RegEx
    return '|'.join(abbreviations)

def write_splitted_sentences_to_file(sentences):
    with open('splitted_news.csv', 'a') as result:
        writer = csv.writer(result, delimiter=",")
        writer.writerow(["\n".join(sentences)])

def split_sentences(text):
    text = text.replace("\n", "")  # Remove all the new lines
    text = re.sub(lower + "[.]" + lower + "[.]", "\\1<ambiguity>\\2<ambiguity>", text)  # Replace the full stop like v.b with <ambiguity>
    text = re.sub(caps + "[.]" + caps + "[.]", "\\1<ambiguity>\\2<ambiguity>", text)  # Replace the full stop like A.Ş. with <ambiguity>
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]", "\\1<ambiguity>\\2<ambiguity>\\3<ambiguity>", text)  # Replace the full stop like T.S.E. with <ambiguity>
    text = re.sub(abbreviations, "\\1<ambiguity>", text)  # Replace the full stop on abbreviations with <ambiguity>
    text = re.sub(digits + "[.]" + digits, "\\1<ambiguity>\\2", text)  # Replace the full stop on decimal numbers with <ambiguity>
    text = re.sub(websites, "<ambiguity>\\1", text)  # Replace the full stop on the web URLs with <ambiguity>
    text = re.sub("\s" + caps + "[.] ", " \\1<ambiguity> ", text)

    text = re.sub(lower + "[.]" + "[\"] " + lower, "\\1<fullStopQuotes>\\2", text)  # Replace the full stop that is ."
    text = re.sub(lower + "[?]" + "[\"] " + lower, "\\1<questionMarkQuotes>\\2", text)  # Replace the question mark that is ?"
    text = re.sub(lower + "[!]" + "[\"] " + lower, "\\1<exclamationMarkQuotes>\\2", text)  # Replace the exclamation mark that is !"

    if "..." in text:
        text = text.replace("...", "<ambiguity><ambiguity><ambiguity>")
    if "”" in text:
        text = text.replace(".”", "”.")
    if "\"" in text:
        text = text.replace(".\"", "\".")
    if "?\" %s" % lower in text:
        text = text.replace("?\"", "<questionMark_quotes>")
    if "!" in text:
        text = text.replace("!\"", "\"!")
    if "?" in text:
        text = text.replace("?\"", "\"?")

    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<ambiguity>", ".")
    text = text.replace("<fullStopQuotes>", ".\" ")
    text = text.replace("<exclamationMarkQuotes>", "!\" ")
    text = text.replace("<questionMarkQuotes>", "?\" ")

    text = text.replace("<stop> ",
                        "<stop>")  # To get rid of the space after the punctuations in the end of the sentence
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    return sentences

abbreviations = format_abbreviations(read_list_of_abbreviations())

lower = "([a-z])"
caps = "([A-Z])"
digits = "([0-9])"
abbreviations = "(%s)[.]"%abbreviations
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](edu|com|net|org|io|gov|tr)"

contentArray, category, headline = read_corpus()

text = """İngiltere'de, "Türkiye AB'ye girmeli mi?" sorusuna yanıt arayan Independent gazetesindeki yazıda, İngiliz tarihçi Norman Stone, "Türkler gerçekten AB'ye girmek istiyorlarsa bizim üyeliğimizi alabilirler" yorumunu yaptı."""
splitted = split_sentences(text)
write_splitted_sentences_to_file(splitted)