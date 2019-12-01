import json
import pandas as pd
import string

df = pd.read_csv('all_2018_posts.csv')
print (df.shape)
df["allcomments"] = df["comment1"].map(str) + ' ' + df["comment2"].map(str) + ' ' + df["comment3"].map(str)
df["alltext"] = df["text"].map(str) + ' ' + df["allcomments"].map(str)
stopwords = set(['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','it','its','itself','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now'])
pronouns = set(['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves'])

words1 = pd.Series([x for x in ' '.join(df['alltext']).lower().translate(str.maketrans('', '', string.punctuation)).split() if x not in stopwords]).value_counts()[:50]
words2 = pd.Series([x for x in ' '.join(df['allcomments']).lower().translate(str.maketrans('', '', string.punctuation)).split() if x not in stopwords]).value_counts()[:50]
words3 = pd.Series([x for x in ' '.join(df['text']).lower().translate(str.maketrans('', '', string.punctuation)).split() if x not in stopwords]).value_counts()[:50]
# words = pd.Series([x for x in re.sub(r"[,.;@#?!&$]+", ' ', ' '.join(df['text']).lower()).split() if x not in stopwords]).value_counts()[:50]
words1 = pd.Series([x for x in ' '.join(df['alltext']).lower().translate(str.maketrans('', '', string.punctuation)).split() if x in pronouns]).value_counts()
words2 = pd.Series([x for x in ' '.join(df['allcomments']).lower().translate(str.maketrans('', '', string.punctuation)).split() if x in pronouns]).value_counts()
words3 = pd.Series([x for x in ' '.join(df['text']).lower().translate(str.maketrans('', '', string.punctuation)).split() if x in pronouns]).value_counts()

print("alltext")
print (words1)
print("allcomms")
print (words2)
print("text")
print (words3)

