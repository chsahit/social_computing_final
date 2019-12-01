import numpy as np
import pandas as pd
import sys

def train_lasso(platform = "twitter", shrink = False):
    assert platform == "twitter" or platform == "reddit"

    dir_data="../" # specify the directory to data files
    dir_lasso="../" # where the outputs are saved

    ### Bring in word count matrix X
    global X, y
    if platform == "twitter":
        X = np.load("twitter_data.npy")
        y = np.load("twitter_labels.npy")
    if platform == "reddit":
        X = np.load("reddit_data.npy")
        y = np.load("reddit_labels.npy")
    train_samples = int(0.9 * X.shape[0])
    X_train = X[:train_samples]
    X_test = X[train_samples:]
    print("full X: ", X.shape)
    y_train = y[:train_samples]
    y_test = y[train_samples:]

    ### Select Predictors: most frequent 10K excluding gender classifiers & additional last names
    vocab10K=pd.read_csv(dir_data+"vocab10K.csv")
    vocab10K['exclude'].sum()
    exclude_vocab=vocab10K.loc[vocab10K['exclude']==1,:]
    i_exclude=exclude_vocab['index']-1 # indexing in Python starts from 0, while the indices for vocab are 1 to 10,000

    i_columns=range(10000)
    i_keep_columns=list(set(i_columns)-set(i_exclude))
    np.savetxt(dir_lasso+"i_keep_columns.txt",i_keep_columns) # later this can be merged by estimated coefficients (in the same order as these indices)

    X_train=X_train[:,i_keep_columns]
    X_test=X_test[:,i_keep_columns]
    print("train x before: ", X_train.shape)
    print("train y: ", y_train.shape)
    print("test: ", X_test.shape)
    if shrink:
        X_train = X_train[:,:2000]
        X_test = X_test[:,:2000]
    print("train x: ", X_train.shape)
    print("train y: ", y_train.shape)
    print("test: ", X_test.shape)


    ################################################################################################################
                                                                                            ### logistic LASSO Model ###
    ################################################################################################################
    # from sklearn import linear_model
    from sklearn.linear_model import LogisticRegressionCV
    model=LogisticRegressionCV(Cs=20,cv=5,penalty='l1',solver='liblinear',refit=True, n_jobs = -1, verbose = 1).fit(X_train,y_train)

    coef=model.coef_
    print(coef[0].sum())
    if platform == "twitter":
        np.savetxt(dir_lasso+"coef_twitter.txt",coef[0])
    elif platform == "reddit":
        np.savetxt(dir_lasso+"coef_reddit.txt",coef[0])

    # predicted probability for a post being Female
    ypred_train=model.predict_proba(X_train)[:,1] # Pr(female=1)
    ypred_test=model.predict_proba(X_test)[:,1]

    # ypred in the files below have been brought back into "genderd_posts.csv"
    if platform == "twitter":
        np.savetxt(dir_lasso+"twitter_train.txt",ypred_train)
        np.savetxt(dir_lasso+"twitter_test.txt",ypred_test)
    elif platform == "reddit":
        np.savetxt(dir_lasso+"reddit_train.txt",ypred_train)
        np.savetxt(dir_lasso+"reddit_test.txt",ypred_test)

