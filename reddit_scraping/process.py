import json
import praw
from praw import Reddit
import pandas as pd
from praw.models import MoreComments

reddit = Reddit(client_id='',
                     client_secret='',
                     user_agent='',
                     username='',
                     password='')


years = ['2013', '2014', '2015', '2016', '2017', '2018']
df = pd.DataFrame(columns = ['title', 'id', 'text', 'score', 'created', 'num_comments', 'comment1', 'comment2', 'comment3'])
for year in years:
  print(year)
  with open(year) as f:
    k = json.load(f)
    data = k['data']
    for i, post in enumerate(data):
      try:
        if i % 50 is 0:
          print (i)
        sub_dict = {
          'title': post['title'], 
          'id': post['id'], 
          'score': post['score'],
          'created': post['created_utc'], 
          'num_comments': post['num_comments'],
        }
        if ('selftext' not in post.keys() or post['selftext'] != ''):
          sub_dict['text'] = post['url']
        else:
          sub_dict['text'] = post['selftext']


        submission = reddit.submission(id=post['id'])
        ratio = submission.upvote_ratio
        sub_dict['ups'] = round((ratio*submission.score)/(2*ratio - 1)) if ratio != 0.5 else round(submission.score/2)
        sub_dict['downs'] = sub_dict['ups'] - submission.score

        submission.comment_sort = 'top'
        submission.comment_limit = 5
        # submission.comments.replace_more(limit=5)

        i = 1
        for top_level_comment in submission.comments:
          if top_level_comment is MoreComments:
            continue
          sub_dict['comment{}'.format(i)] = top_level_comment.body
          i += 1
          if i == 4:
            break

        df = df.append(sub_dict, ignore_index=True)
      except:
        print("BROKEN POST")
        print (post)
        continue

  df.to_csv("all_{}_posts.csv".format(year), index=False)