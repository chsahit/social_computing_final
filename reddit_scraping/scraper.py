# from os.path import isfile
# import praw
# import pandas as pd
# from time import sleep
# # from pprint import pprint
# # import logging

# # Get credentials from DEFAULT instance in praw.ini
# reddit = praw.Reddit()

# # Setup a logger
# # logger = logging.getLogger(__name__)
# # logger.setLevel(10)

# # formatter = logging.Formatter('%(levelname)s | %(funcName)s | %(message)s')
# # file_handler = logging.FileHandler('praw_scraper.log')
# # file_handler.setFormatter(formatter)

# # logger.addHandler(file_handler)


# class SubredditScraper:

#     def __init__(self, sub, sort='new', lim=900, mode='w'):
#         self.sub = sub
#         self.sort = sort
#         self.lim = lim
#         self.mode = mode

#         print(
#             f'SubredditScraper instance created with values '
#             f'sub = {sub}, sort = {sort}, lim = {lim}, mode = {mode}')

#     def set_sort(self):
#         if self.sort == 'new':
#             return self.sort, reddit.subreddit(self.sub).new(limit=self.lim)
#         elif self.sort == 'top':
#             return self.sort, reddit.subreddit(self.sub).top(limit=self.lim)
#         elif self.sort == 'hot':
#             return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
#         else:
#             self.sort = 'hot'
#             print('Sort method was not recognized, defaulting to hot.')
#             return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)

#     def get_posts(self):
#         """Get unique posts from a specified subreddit."""

#         # sub_dict = {
#         #     'selftext': [], 'title': [], 'id': [], 'sorted_by': [],
#         #     'num_comments': [ ], 'score': [], 'ups': [], 'downs': []}
#         sub_dict = {
#             'title': [], 'id': [], 'text': [],
#             'num_comments': [ ], 'score': [], 'ups': [], 'downs': []}
#         csv = f'{self.sub}_posts.csv'

#         # Attempt to specify a sorting method.
#         sort, subreddit = self.set_sort()

#         # Set csv_loaded to True if csv exists since you can't evaluate the
#         # truth value of a DataFrame.
#         df, csv_loaded = (pd.read_csv(csv), 1) if isfile(csv) else ('', 0)

#         print(f'csv = {csv}')
#         print(f'After set_sort(), sort = {sort} and sub = {self.sub}')
#         print(f'csv_loaded = {csv_loaded}')

#         print(f'Collecting information from r/{self.sub}.')
#         for i, post in enumerate(subreddit):

#             # Check if post.id is in df and set to True if df is empty.
#             # This way new posts are still added to dictionary when df = ''
#             unique_id = post.id not in tuple(df.id) if csv_loaded else True

#             # Save any unique, non-stickied posts with descriptions to sub_dict.
#             if unique_id:
#                 sub_dict['title'].append(post.title)
#                 sub_dict['id'].append(post.id)
#                 sub_dict['text'].append(post.selftext)
#                 sub_dict['num_comments'].append(post.num_comments)
#                 sub_dict['score'].append(post.score)
#                 sub_dict['ups'].append(post.ups)
#                 sub_dict['downs'].append(post.downs)

#                 post.comments.replace_more(limit=None)
#                 comment_queue = post.comments[:]  # Seed with top-level
#                 while comment_queue:
#                   comment = comment_queue.pop(0)
#                   sub_dict['title'].append('')
#                   sub_dict['id'].append(comment.id)
#                   sub_dict['text'].append(comment.body)
#                   sub_dict['num_comments'].append(-1)
#                   sub_dict['score'].append(comment.score)
#                   sub_dict['ups'].append(comment.ups)
#                   sub_dict['downs'].append(comment.downs)
#                   comment_queue.extend(comment.replies)
#                   sleep(0.1)
#             if i % 5 == 0:
#               print ("added post {}".format(i))
#             sleep(0.1)

#         # pprint(post_dict)
#         new_df = pd.DataFrame(sub_dict)

#         # Add new_df to df if df exists then save it to a csv.
#         if 'DataFrame' in str(type(df)) and self.mode == 'w':
#             pd.concat([df, new_df], axis=0, sort=0).to_csv(csv, index=False)
#             print(
#                 f'{len(new_df)} new posts collected and added to {csv}')
#         elif self.mode == 'w':
#             new_df.to_csv(csv, index=False)
#             print(f'{len(new_df)} posts collected and saved to {csv}')
#         else:
#             print(
#                 f'{len(new_df)} posts were collected but they were not '
#                 f'added to {csv} because mode was set to "{self.mode}"')

# if __name__ == '__main__':
#     SubredditScraper('economics', lim=15, mode='w', sort='hot').get_posts()


from os.path import isfile
import praw
import pandas as pd
from time import sleep
from collections import Counter
from datetime import datetime
from praw import Reddit
from praw.models import MoreComments
import pandas as pd
import datetime as dt
from psaw import PushshiftAPI
import json
from datetime import date
from dateutil.relativedelta import relativedelta


# Get credentials from DEFAULT instance in praw.ini
# reddit = praw.Reddit()
reddit = Reddit(client_id='',
                     client_secret='',
                     user_agent='',
                     username='',
                     password='')
api = PushshiftAPI(reddit)

comment_fields = ('body')
post_fields = ('created', 'title', 'id', 'selftext', 'num_comments', 'score', 'num_comments')


class SubredditScraper:

    def __init__(self, sub, sort='hot', lim=900, mode='w'):
        self.sub = sub
        self.sort = sort
        self.lim = lim
        self.mode = mode

        print(
            f'SubredditScraper instance created with values '
            f'sub = {sub}, sort = {sort}, lim = {lim}, mode = {mode}')

    def set_sort(self):
        if self.sort == 'new':
            return self.sort, reddit.subreddit(self.sub).new(limit=self.lim)
        elif self.sort == 'top':
            return self.sort, reddit.subreddit(self.sub).top(limit=self.lim)
        elif self.sort == 'hot':
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
        else:
            self.sort = 'hot'
            print('Sort method was not recognized, defaulting to hot.')
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)

    def get_posts(self, times, csv=None):

        """Get unique posts from a specified subreddit."""

        # sub_dict = {
        #     'selftext': [], 'title': [], 'id': [], 'sorted_by': [],
        #     'num_comments': [ ], 'score': [], 'ups': [], 'downs': []}
        sub_dict = {
            'title': '', 'id': 0, 'text': '', 'score': 0, 'created': '', 'num_comments': 0, 'comment1': '', 'comment2': '', 'comment3': ''}
        csv = f'{self.sub}_posts_2.csv'

        # Attempt to specify a sorting method.
        # sort, subreddit = self.set_sort()
        subreddit = reddit.subreddit(self.sub)
        for k, x in enumerate(times[:-1]):
            after = x 
            before = [times[k+1]]

            submissions = api.search_submissions(after=after, before=before, subreddit=subreddit, limit=self.lim, sort="date:asc", sort_type='num_comments')

            # Set csv_loaded to True if csv exists since you can't evaluate the
            # truth value of a DataFrame.
            df_og = pd.DataFrame(columns = ['title', 'id', 'text', 'score', 'created', 'num_comments', 'comment1', 'comment2', 'comment3'])

            df, csv_loaded = (pd.read_csv(csv), 1) if isfile(csv) else (df_og, 0)

            print(f'csv = {csv}')
            # print(f'After set_sort(), sort = {sort} and sub = {self.sub}')
            print(f'csv_loaded = {csv_loaded}')

            print(f'Collecting information from r/{self.sub}.')
            for submission in submissions:
                unique_id = post.id not in tuple(df.id) if csv_loaded else True

                if True:
                    post = vars(submission)
                    post_dict = {field:post[field] for field in post_fields[:-2]}
                    # ignore meta, update, etc. posts
                    sub_dict['title'] = post_dict['title']
                    print(post_dict)
                    sub_dict['text'] = post_dict['selftext']
                    sub_dict['created'] = post_dict['created']
                    sub_dict['id'] = post_dict['id']
                    sub_dict['score'] = post_dict['score']
                    sub_dict['num_comments'] = post_dict['num_comments']

                    top_comments = []
                    counts = Counter()
                    for i, comment in enumerate(submission.comments):
                        content = vars(comment)
                        comment_dict = {field:content[field] for field in comment_fields if field in content}
                        if isinstance(comment, MoreComments):
                            continue
                        commentbody = comment_dict['body'].lower()
                        if i < 4 and i > 0:
                            sub_dict['comment{}'.format(i)] = comment_dict['body']
                            # top_comments.append(commentbody)
                        if i >= 4:
                            break

                df = df.append(sub_dict, ignore_index=True)
            
        return df

if __name__ == '__main__':


    times = [relativedelta(months=-12*6),relativedelta(months=-12*5),relativedelta(months=-12*4),relativedelta(months=-12*3),relativedelta(months=-12*2),relativedelta(months=-12*1),relativedelta(months=-12*0)]

    df = SubredditScraper('economics', lim=1000, mode='w', sort='top').get_posts(times)
    file_name = 'trial.csv'
    print (df)
    df.to_csv(file_name, index=False)




