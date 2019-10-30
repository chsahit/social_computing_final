import numpy as np
import pandas as pd
import sys

dir_data="../" # specify the directory to data files
dir_lasso="../" # where the outputs are saved

### Bring in word count matrix X
#word_counts=np.load("twitter_data.npy")
word_counts = np.load("reddit_data.npy")
print("full X: ", word_counts.shape)
X=word_counts
#X_train = X[:1500]
#X_test = X[1500:]
X_train = X[:2000]
X_test = X[2000:]

'''y = np.load("twitter_labels.npy")
y_train = y[:1500]'''
y = np.load("reddit_labels.npy")
y_train = y[:2000]
print(y_train.sum())

### Select Predictors: most frequent 10K excluding gender classifiers & additional last names
vocab10K=pd.read_csv(dir_data+"vocab10K.csv")
vocab10K['exclude'].sum()
exclude_vocab=vocab10K.loc[vocab10K['exclude']==1,:]
i_exclude=exclude_vocab['index']-1 # indexing in Python starts from 0, while the indices for vocab are 1 to 10,000

i_columns=range(10000)
i_keep_columns=list(set(i_columns)-set(i_exclude))
np.savetxt(dir_lasso+"i_keep_columns.txt",i_keep_columns) # later this can be merged by estimated coefficients (in the same order as these indices)

X_train=X_train[:,i_keep_columns]
print("train: ", X_train.shape)
print("train: ", y_train.shape)
X_test=X_test[:,i_keep_columns]
print("test: ", X_test.shape)


################################################################################################################
											### logistic LASSO Model ###
################################################################################################################
# from sklearn import linear_model
from sklearn.linear_model import LogisticRegressionCV
model=LogisticRegressionCV(Cs=20,cv=5,penalty='l1',solver='liblinear',refit=True, n_jobs = -1, verbose = 1).fit(X_train,y_train)

coef=model.coef_
print(coef[0].sum())
np.savetxt(dir_lasso+"coef_twitter.txt",coef[0])

# predicted probability for a post being Female
ypred_train=model.predict_proba(X_train)[:,1] # Pr(female=1)
ypred_test=model.predict_proba(X_test)[:,1]

# ypred in the files below have been brought back into "genderd_posts.csv"
np.savetxt(dir_lasso+"reddit_train.txt",ypred_train)
np.savetxt(dir_lasso+"reddit_test.txt",ypred_test)
'''np.savetxt(dir_lasso+"twitter_train.txt",ypred_train)
np.savetxt(dir_lasso+"twitter_test.txt",ypred_test)'''

