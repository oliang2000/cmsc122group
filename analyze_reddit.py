import praw
from collections import Counter
import csv
import collections
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import statistics
import passwords
from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt


reddit = praw.Reddit(client_id = passwords.CLIENT_ID, 
                    client_secret = passwords.CLIENT_SECRET,
                    password = passwords.PASSWORD, 
                    user_agent = 'USERAGENT',
                    username = passwords.USERNAME)

WORD_IRGNORE = ['', 'i', 'have', 'was', 'it', 'you', 'people', 'your', 'like',
                    'because', 'would', 'all', 'if', 'what', 'who', 'my',
                    'me', 'think', 'it', 'do', 'me', 'about', 'ever',
                    'a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'in', 'include', 'is', 'not', 'of', 'want', "you're",
                    'on', 'or', 'so', 'such', 'that', 'the', 'their', 
                    'this', 'through', 'to', 'we', 'were', 'which', 'will', 
                    'with', 'yet', 'https', 'put', 'they','get', 'why', 'even', 
                    'though', 'done', 'i’m', 'going', 'go', 'when', 'person', 'some', 'feel',
                    '-', "it's", "gonna", 'i’ve', 'probably', 'could', 'can']

def get_words(post):
    words = []
    words_list = post.split(" ")
    for word in words_list:
        word = word.lower()
        word = re.search("[a-z0-9\-'’]+", word)
        if word != None:
            word = word.group(0)
            if (word not in WORD_IRGNORE) and (word not in words):
                words.append(word)
    return words


def get_group_content(groupname, num_of_posts):
    '''
    Returns: a list of tuple
    '''
    l_name = []
    for submission in reddit.subreddit(groupname).hot(limit = num_of_posts):
        l_name.append((submission.title, submission.selftext))
    return l_name

def analyze_posts(allposts):
    '''
    Inputs: list of tuple
    '''
    analyzer = SentimentIntensityAnalyzer()
    l_words_title = []
    l_post_sentiment = []
    for title, post in allposts:
        l_words_title += get_words(title)
        if post == '':
            l_post_sentiment.append(None)
        else:
            l_post_sentiment.append(analyzer.polarity_scores(post)['compound'])
    counter = collections.Counter(l_words_title)



    wordcloud = WordCloud(stopwords = STOPWORDS, width = 1000, height = 500).generate_from_frequencies(counter)
    plt.figure(figsize=(200,100))
    plt.imshow(wordcloud)
    plt.axis("off")
    #plt.show()
    plt.savefig('yourfile.png', bbox_inches='tight')
    plt.close()

    print(counter.most_common(100))
    print(statistics.mean(filter(None, l_post_sentiment)))

posts = get_group_content('uchicago', 500) 
analyze_posts(posts)









