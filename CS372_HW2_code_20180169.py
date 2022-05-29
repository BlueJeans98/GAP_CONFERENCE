import csv
import requests
from urllib import request
from bs4 import BeautifulSoup
from http.client import HTTPException
from urllib.error import HTTPError
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk import ne_chunk, pos_tag
import nltk.corpus


# filter that counts how many times the name is shown in the text.
def counter_filter(text, a ,b):
    tokens = word_tokenize(text)
    count_a, count_b = 0, 0
    tagged_tokens = pos_tag(tokens)
    for chunk in ne_chunk(tagged_tokens):
        if hasattr(chunk, 'label') and chunk.label()=="PERSON":
            # select chunks that has label "Person"
            name = ' '.join(c[0] for c in chunk)
            # if the chunk is in a or b, increase the corresponding count by 1
            if name in a:
                count_a+=1
            elif name in b:
                count_b+=1
    if(count_a==0 and count_b==0):
        # if a nor b is shown in the text return False for both
        return ("FALSE","FALSE")
    elif(count_a > count_b):
        return ("TRUE", "FALSE")
    else:
        return ("FALSE", "TRUE")


# filter that uses name corpus, and filters if the name by gender.
def names_corpus_filter(p, a, b, pre_result):
    a_result = pre_result[0]
    b_result = pre_result[1]
    # categorize the pronoun by gender
    male = ['he','his','him']
    female = ['she','her']

    names = nltk.corpus.names
    male_names = names.words('male.txt')
    female_names = names.words('female.txt')

    gender = 'male'
    if p.lower() in male:
        gender = 'male'
    elif p.lower() in female:
        gender = 'female'
    
    
    a_first_name = a.split()[0]
    b_first_name = b.split()[0]
    # if the name is in oppsoite gender group, but not in same gender group, return False.
    if(gender == 'male'):
        if(a_first_name in female_names and a_first_name not in male_names):
            a_result = "FALSE"
        if(b_first_name in female_names and b_first_name not in male_names):
            b_result = "FALSE"
    elif(gender == 'female'):
        if(a_first_name in male_names and a_first_name not in female_names):
            a_result = "FALSE"
        if(b_first_name in male_names and b_first_name not in female_names):
            b_result = "FALSE"
    return (a_result, b_result)


# filters using offset of pronoun and instances
def offset_filter(p_o, a_o, b_o, pre_result):
    a_result = pre_result[0]
    b_result = pre_result[1]
    p_o, a_o, b_o = int(p_o), int(a_o), int(b_o)

    # if the position of the instance and pronoun is close enough, return true. 
    if(abs(p_o - a_o) < 30):
        a_result = "TRUE"
    if(abs(p_o - b_o) < 30):
        b_result = "TRUE"
    return (a_result, b_result)
    

# main algorithm function for snippet & page context
def algorithm(row,page):
    ID, text, p, p_o, a, a_o, a_c, b, b_o, b_c, url = row
    # snippet-context
    if(page==False):
        result = counter_filter(text, a, b)
        result = names_corpus_filter(p, a, b, result)
        result = offset_filter(p_o, a_o, b_o, result)
        return result
    # page-context
    elif(page==True):
        try:
            html = request.urlopen(url).read().decode('utf8')
        # if error happens in HTTP, use snippet-context instead
        except HTTPError as e:
            print(e)
            return algorithm(row,False)
        except HTTPException as e:
            print(e)
            return algorithm(row,False)
        raw = BeautifulSoup(html,'html.parser').get_text()
        tokens = sent_tokenize(raw)
        a_count = 0
        b_count = 0
        # if the word is in the raw text, increment the corresponding count.
        for t in tokens:
            if(a in t):
                a_count+=1
            elif(b in t):
                b_count+=1
        if(a_count == 0 and b_count == 0):
            return ("FALSE", "FALSE")
        elif(a_count>b_count):
            return ("TRUE", "FALSE")
        else:
            return ("FALSE","TRUE")


# making result tsv files.
def make_test(wikipedia):
    file_name = ""
    if(wikipedia==False):
        file_name = 'CS372_HW2_snippet_output_20180169.tsv'
    else:
        file_name = 'CS372_HW2_page_output_20180169.tsv'
    with open('gap-test.tsv') as f:
        i = 0
        tr = csv.reader(f, delimiter='\t')
        with open(file_name, 'w', encoding='utf-8', newline='') as f:
            for row in tr:
                    if(i==0):
                        i+=1
                        continue
                    test_num = 'test-' + str(i)
                    tw = csv.writer(f, delimiter='\t')
                    result = algorithm(row,wikipedia)
                    tw.writerow([test_num, result[0], result[1]])
                    i+=1

make_test(False)
make_test(True)

        




