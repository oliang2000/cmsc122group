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

ANALYZER = SentimentIntensityAnalyzer()

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
        #analyze_comments(submission)
    return l_name


def analyze_posts(allposts):
    '''
    Inputs: list of tuple
    '''
    l_words_title = []
    l_post_sentiment = []
    for title, post in allposts:
        l_words_title += get_words(title)
        if post == '':
            l_post_sentiment.append(None)
        else:
            l_post_sentiment.append(calculate_sentiment(post))
    counter = collections.Counter(l_words_title)

    #generate word cloud
    wordcloud = WordCloud(stopwords = STOPWORDS, width = 1000, \
        height = 500, background_color="white").generate_from_frequencies(counter)
    plt.figure(figsize=(200,100))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig('yourfile.png', bbox_inches='tight')
    plt.close()

    print(counter.most_common(100))
    print(statistics.mean(filter(None, l_post_sentiment)))


def calculate_sentiment(text):
    '''
    '''
    return ANALYZER.polarity_scores(text)['compound']

def analyze_comments(post):
    '''
    check whether people are happy or sad in the comments section
    Input:
        post(a submmission object)
    Returns:
        a list of emotions for each comment

    '''
    l_comment_sentiments = []
    for comment in post.comments:
        print(comment.body)
        l_comment_sentiments.append(calculate_sentiment(comment.body))
    plt.bar(x = list(range(len(l_comment_sentiments))), height = l_comment_sentiments)
    plt.savefig('comments.png', bbox_inches='tight')
    plt.close()


posts = get_group_content('china', 200) 
analyze_posts(posts)









