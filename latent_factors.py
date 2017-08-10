
#Collabrative filtering with latent factors technique

import pandas as pd
import numpy as np
from numpy.linalg import norm
from scipy.spatial.distance import hamming
from scipy.sparse import coo_matrix

dataFile = 'BX-Book-Ratings.csv'

data = pd.read_csv(dataFile,sep=";",header=0,names=['user','isbn','rating'])



bookFile = 'BX-Books.csv'
books = pd.read_csv(bookFile,sep=";",header=0,error_bad_lines=False, usecols=[0,1,2],index_col=0,names=['isbn','title','author'])



def bookMeta(isbn):
	title = books.at[isbn,'title']
	author = books.at[isbn, 'author']
	return title,author



def faveBooks(user, N):
	userRatings = data[data['user']==user]
	sortedRatings = pd.DataFrame.sort_values(userRatings,['rating'],ascending=[0])[:N]
	sortedRatings['title'] = sortedRatings['isbn'].apply(bookMeta)	
	return sortedRatings

data = data[data['isbn'].isin(books.index)]



usersPerISBN = data.isbn.value_counts()

ISBNsPerUser = data.user.value_counts()



data = data[data['isbn'].isin(usersPerISBN[usersPerISBN>10].index)]
data = data[data['user'].isin(ISBNsPerUser[ISBNsPerUser>10].index)]

data['user'] = data['user'].astype("category")
data['isbn'] = data['isbn'].astype("category")

R = coo_matrix((data['rating'].astype(float),(data['user'].cat.codes.copy(), data['isbn'].cat.codes.copy())))

print(R.shape)




def error(R, P, Q, lamda=0.02):
    ratings = R.data
    rows = R.row
    cols = R.col
    e = 0
    for ui in range(len(ratings)):
        rui = ratings[ui]
        u = rows[ui]
        i = cols[ui]
        if(rui>0):
            e = e + pow(rui - np.dot(P[u,:],Q[:,i]), 2) + lamda*(pow(norm(P[u,:]), 2) + pow(norm(Q[:,i]), 2))        
    return e



def SGD(R, K, lamda=0.02, steps=10, gamma = 0.001):
    M,N = R.shape
    P = np.random.rand(M,K)
    Q = np.random.rand(K,N)
    rmse = np.sqrt(error(R,P,Q,lamda)/len(R.data))
    print("Initial RMSE: "+str(rmse))

    for step in xrange(steps):
        for ui in range(len(R.data)):
            rui = R.data[ui]
            u = R.row[ui]
            i = R.col[ui] 
            if rui>0:
                eui = rui - np.dot(P[u,:],Q[:,i])
                P[u,:] = P[u,:] + gamma*2*(eui*Q[:,i] - lamda*P[u,:])
                Q[:,i] = Q[:,i] + gamma*2*(eui*P[u,:] - lamda*Q[:,i]) 
        rmse = np.sqrt(error(R,P,Q,lamda)/len(R.data))
        if rmse<0.5:
            break
    
    print("Final RMSE: "+str(rmse))
    return P,Q

P,Q = SGD(R,K=2, gamma = 0.0007, lamda=0.01, steps = 10)