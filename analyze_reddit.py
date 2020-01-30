from bs4 import BeautifulSoup
import requests
import re
from collections import Counter

WORD_IRGNORE = ['', 'i', 'have', 'was', 'it', 'you', 'people', 'your', 'like',
                    'because', 'would', 'all', 'if', 'what', 'who', 'my'
                    'me', 'think', 'it', 
                    'a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet']

def count_freq(lst):
    '''
    Returns a counter object
    '''
    assert lst != [], "list is empty"
    words = []
    for par in lst:
        words_list = par.split(" ")
        for word in words_list:
            if word not in WORD_IRGNORE:
                words.append(word.lower())
    return Counter(words)

def get_posts(url):
    requests.utils.default_headers()
    headers = requests.utils.default_headers()
    headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')  
    all_comments = soup.find_all('p') 
    lst = []
    for comment in all_comments:
        comment = comment.getText()
        lst.append(comment)
    return lst



url = "https://www.facebook.com/pg/secretsuchicago/posts/" 
#"https://www.facebook.com/BruinSecrets/posts/" 
#"https://www.facebook.com/beaverconfessions/posts/" doesnt work
counter = count_freq(get_posts(url))
print(counter.most_common(20))




#ref: https://hackersandslackers.com/scraping-urls-with-beautifulsoup/
