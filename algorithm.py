import csv
import requests
from urllib import request
from bs4 import BeautifulSoup
from http.client import HTTPException
from urllib.error import HTTPError
from nltk.tokenize import sent_tokenize



headers = requests.utils.default_headers()

headers.update(
    {
        'User-Agent': 'My User Agent 1.0',
    }
)


def algorithm(row,page):
    ID, text, p, p_o, a, a_o, a_c, b, b_o, b_c, url = row
    if(page==False):
        return (a_c, b_c)
    elif(page==True):
        try:
            html = request.urlopen(url).read().decode('utf8')
        except HTTPError as e:
            print(e)
            return ("FALSE", "FALSE")
        except HTTPException as e:
            print(e)
            return("FALSE", "FALSE")
        raw = BeautifulSoup(html,'html.parser').get_text()
        tokens = sent_tokenize(raw)
        a_count = 0
        b_count = 0
        for t in tokens:
            if(a in t):
                a_count+=1
            elif(b in t):
                b_count+=1
        print(a_count, b_count)
        if(a_count == 0 and b_count == 0):
            return ("FALSE", "FALSE")
        elif(a_count>b_count):
            return ("TRUE", "FALSE")
        else:
            return ("FALSE","TRUE")
        



with open('gap-development.tsv') as f:
    i = 0
    tr = csv.reader(f, delimiter='\t')
    with open('a.tsv', 'w', encoding='utf-8', newline='') as f:
        for row in tr:
                if(i==0):
                    i+=1
                    continue
                test_num = 'development-' + str(i)
                tw = csv.writer(f, delimiter='\t')
                result = algorithm(row,True)
                tw.writerow([test_num, result[0], result[1]])
                i+=1

