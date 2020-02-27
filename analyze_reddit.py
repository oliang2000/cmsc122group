#https://github.com/pushshift/api
#https://github.com/dmarx/psaw

from psaw import PushshiftAPI
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

ANALYZER = SentimentIntensityAnalyzer()
api = PushshiftAPI()

def get_posts(start_date, end_date, n, subreddit):
    '''
    Extract posts from a subreddit with criteria.
    Inputs:
        start_date, end_date (lists): two lists of three elements contaiining
          year, month, date of limit to extract the posts
        n (int): limit on number of posts to extract
        subreddit (string): name of subresddit to extract
    Returns: a list of submissions
    Sample use: test.get_posts([2020, 1,1],[2020, 1,2], 10, 'china')
    '''
    year1, month1, day1 = start_date
    year2, month2, day2 = end_date
    start_epoch = int(dt.datetime(year1, month1, day1).timestamp())
    end_epoch = int(dt.datetime(year2, month2, day2).timestamp())
    return list(api.search_submissions(before = end_epoch, after=start_epoch, \
        subreddit = subreddit, filter=['title', 'author', 'selftext', 'subreddit'], limit = n))


def calculate_sentiment(text):
    '''
    Calculates sentiment score of a string.
    Inputs:
        text(str): the text to be analyzed
    Returns: an int between 1(very positive) and -1(vert negative)
    '''
    return ANALYZER.polarity_scores(text)['compound']


def create_df(submissions):
    '''
    Create a pandas dataframe from a list of submissions.
    Inputs: 
        submissions(list): a list of reddit submissions
    Returns: a pandas dataframe with author, post title, post content, 
      time the post was created (ymd, hour, minute, second) and sentiment 
      score of the post
    '''
    l_author = []
    l_title = []
    l_selftext = []
    l_time = []
    l_sent = []
    for sub in submissions:
        l_title.append(sub.title)
        l_author.append(sub.author)
        l_time.append(sub.created_utc)
        if hasattr(sub, 'selftext'):
            l_selftext.append(sub.selftext)
            l_sent.append(calculate_sentiment(sub.title + sub.selftext))
        else:
            l_selftext.append('')
            l_sent.append(calculate_sentiment(sub.title))

    df = pd.DataFrame({'author': l_author, 'title': l_title, 'text': l_selftext, \
        'epoch_time':l_time, 'sentiment_score': l_sent})
    df['time'] = df.apply(lambda row: dt.datetime.fromtimestamp(row['epoch_time']), axis = 1)
    ymd, hour, minute, second = \
    zip(*[(d.strftime("%Y%m%d"), d.hour, d.minute, d.second) \
        for d in df['time']])
    df = df.assign(ymd = ymd, hour = hour, minute = minute, second = second)
    return df


def compare_group_sent(subreddits, start_date, end_date, n, plot_title):
    '''
    Compare sentiment scores vs. time for any number of subreddits.
    Inputs:
        subreddits(list): names of the subreddit groups
        start_date, end_date (list): two lists of three elements contaiining
          year, month, date of limit to extract the posts
        n (int): limit on number of posts to extract
        plot_title (str): name of plot, also filename of .png file
    Returns:
        a list of pandas DataFrame of all subreddits, with author, post title, 
          post content, time the post was created (ymd, hour, minute, second) 
          and sentiment score of the post.
    Outputs:
        plot_title.png file with scores vs. time for all subreddits
    Sample use:  k = test.compare_group_sent(['SandersForPresident', 'Pete_Buttigieg'], 
    [2020, 2,6], [2020, 2, 12], 50000, 'bernie_vs_pete')
    '''
    dfs = []
    max_min_time = 0
    for name in subreddits:
        df = create_df(get_posts(start_date, end_date, n, name))
        max_min_time = max(max_min_time, min(df['epoch_time']))
        dfs.append(df)
    plt.clf()
    i = 0
    for df in dfs:
        df = df[df['epoch_time']> max_min_time]
        df_count = df.groupby('ymd', as_index=False)['sentiment_score'].mean()
        plt.plot(df_count.ymd, df_count.sentiment_score, '-o', label = subreddits[i])
        i += 1
    plt.xticks(rotation=90)
    plt.legend(loc='best')
    plt.title(plot_title)
    plt.savefig(plot_title + '.png', bbox_inches='tight', dpi = 300)
    return dfs







def analyze_users(dfs, groups, min_num_post = 10):
    '''
    Analyze users who post frequently in all groups.
    '''

    dfs[0] = dfs[0].add_suffix('_0')
    all_groups = dfs[0]
    i = 1
    while i < len(dfs):
        dfs[i] = dfs[i].add_suffix('_' + str(i))
        all_groups = all_groups.merge(dfs[i], \
            left_on = 'author_0',  right_on = 'author_' + str(i))
        i += 1
    s_count = all_groups.groupby('author_0').size()
    df_count = pd.DataFrame({'author': s_count.index, 'num_post': s_count.values})
    df_count = df_count.sort_values(by = 'num_post', ascending=False)
    freq_authors = list(df_count[df_count['num_post'] >= min_num_post].author)
    freq_authors.remove('[deleted]')
    for author in freq_authors:
        posts_from_author = all_groups[all_groups['author_0'] == author]
        plt.clf()
        i = 0
        while i < len(dfs):
            plt.plot(posts_from_author['ymd_' + str(i)], \
                posts_from_author['sentiment_score_'+ str(i)], 'o', label = groups[i])
            i += 1
        plt.xticks(rotation=90)
        plt.legend(loc='best')
        plt.savefig(author + '.png', bbox_inches='tight', dpi = 300)


def extreme(sent, threshold):
    '''
    '''
    if (sent > threshold) or (sent < - threshold):
        return True
    return False


def get_extreme_users(df, threshold):
    '''
    Analyze users who have strong emotions.....
    '''
    df["extreme"] = df.apply(lambda row: test.extreme(row.sentiment_score, threshold), axis = 1)
    df_count = pd.DataFrame({'author': s.index, 'num_post': s.values})
    df_count = df_count.sort_values(by = 'num_post', ascending=False)
    freq_authors = list(df_count[df_count['num_post'] >= 5].author)
    freq_authors.remove('[deleted]')
    for author in freq_authors:
        posts_from_author = df[df['author'] == author]
        plt.clf()
        plt.plot(posts_from_author.ymd, posts_from_author.sentiment_score, 'o')
        plt.xticks(rotation=90)
        plt.legend(loc='best')
        plt.savefig(author + '.png', bbox_inches='tight', dpi = 300)


