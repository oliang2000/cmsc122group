# User input: a group name

# Q1: what are the people talking about RIGHT NOW and how are they FEELING?
# get hottest # of posts
# extract key words from (title + post + comments) to generate HOT WORDS/PHRASES
# generate a WORDMAP based on the hot words

# Q2: how are people's feelings changing with time?
# extract as many recent posts as possible (list object)
# use the post utc to get change over time
# get sentiments/keywords/..

#Q3: maybe compare different groups?

#analyze how different users compare to each other (words + sentiment change with time)
#find duplicates or just find people that are generally similar?
#subset users with similar interests, common issues that people get happy/sad about
#use analysis to see if people is republican/democratic
#compare two users of contrasting group, their sentiment with time

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
import numpy as np

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
    '''
    Get words from a paragraph.
    Inputs: 
        post(string): a paragraph of words
    Returns:
        a list of words, containing letters, numbers and '
    '''
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


def get_group_content(groupname, num_of_posts, n_max_comments):
    '''
    Get submissions from a group.

    Inputs:
        groupname(String): name of the group
        num_of_posts(int): number of posts to get
        n_max_comments(int): maximum limit of number of comments 
            to get from each post.

    .hot(), .top(), .new()
    "top" is the most upvotes regardless of downvotes
    "hot" is the most upvotes recently

    Returns: a list of submission objects.
    '''
    l = []
    i = 0
    for submission in reddit.subreddit(groupname).hot(limit = num_of_posts):  #new
        l.append(submission) #submission.title, submission.selftext
    return l


def write_posts_to_cvs(name):
    with open(name + '.csv', 'w', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar=',')
        for post in posts:
            print(post.title, post.selftext, ' '.join(get_all_comments(post)))


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
    Calculates sentiment of a paragraph.

    Returns: int(between -1 and 1)
    '''
    return ANALYZER.polarity_scores(text)['compound']


def get_all_comments_wrapper(post, n_max_comments):
    '''
    Get all comments of a post.
    '''
    comments = []
    for comment in post.comments:
        comments += get_all_comments(comment, n_max_comments)
    return comments


def get_all_comments(comment, n_max_comments): ########max comments
    '''
    '''
    comments = []
    if isinstance(comment, praw.models.Comment):
        comments = [(comment.body, comment.score)]
        replies = comment.replies
        if len(comment.replies) == 0:
            return comments
        for comment in replies:
            comments += get_all_comments(comment, n_max_comments)
    elif isinstance(comment, praw.models.MoreComments):
        for c in comment.comments():
            comments += get_all_comments(c, n_max_comments)
    return comments


def analyze_comments(posts, n_max_comments):
    '''
    Check whether people are happy or sad in the comments section of a group
    Input:
        posts(list): a list of submission objects
        title(string): post title, used for title of the histogram
        filename(string): post id, used as name for .png file
        n_max_comments
    Returns:
        list of list of sentiment score
    Outputs:
        a histogram of sentiment scores 
    '''
    sent = []
    time = []
    for post in posts:
        all_com_sent = []
        all_comments = get_all_comments_wrapper(post, n_max_comments)
        all_com_sent = [calculate_sentiment(i) for i, j in all_comments]
        # plt.hist(all_com_sent)
        # plt.title('Post:' + post.title)
        # plt.savefig(post.id + '.png', bbox_inches='tight')
        # plt.close()
        sent.append(all_com_sent)
        time.append(post.created_utc)
    return (sent, time)


def get_time_change(sent, time):
    sent_avg = np.array([])
    time = np.array(time)
    for s in sent:
        if len(s) == 0:
            sent_avg = np.append(sent_avg, None)
        else:
            sent_avg = np.append(sent_avg, np.average(s)) # weigh by popularity
    sent_avg_mod = sent_avg[sent_avg != None]
    time_mod = time[sent_avg != None]
    plt.clf()
    plt.figure(figsize=(20,2))
    axes = plt.gca()
    axes.set_ylim([-1,1])
    plt.plot(time_mod, sent_avg_mod, 'o') #, '-o'
    plt.title('ElizabethWarren')
    plt.savefig('ElizabethWarren' + '.png', bbox_inches='tight', dpi = 300)
    return (sent_avg_mod, time_mod)



#posts = get_group_content('china', 200) 
#analyze_posts(posts)









