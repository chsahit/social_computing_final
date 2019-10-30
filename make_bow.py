import pandas as pd
import numpy as np
import sys

if __name__ == "__main__":
    path = "custom_data/all_tweets.csv"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    data = pd.read_csv(path)
    vocab = pd.read_csv("vocab10K.csv")
    #print(data['text'])
    num_entries = data.shape[0]
    X = np.zeros((num_entries, 10000))
    word_set = set(vocab['word'].tolist())
    for i in range(num_entries):
        if i % 1000 == 0:
            print i
        post = data['text'][i].lower().split()
        for word, j in zip(post, range(len(post))):
            print(word)
            if word in word_set:
                X[i, j] += 1

    np.save("all_tweets_bow.npy", X)

