
#Collabrative filtering with K Nearest Neighbours Technique

import pandas as pd
import numpy as np
from scipy.spatial.distance import hamming

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



data['rating'] = data['rating'].astype('str').astype('float64')


data['user'] = data['user'].astype('str')
data['isbn'] = data['isbn'].astype('str')



userItemRatingMatrix = pd.pivot_table(data, values=['rating'],index=['user'],columns=['isbn'])



def distance(user1, user2):
	try:
		user1Ratings = userItemRatingMatrix.transpose()[user1]
		user2Ratings = userItemRatingMatrix.transpose()[user2]	
		distance = hamming(user1Ratings, user2Ratings)	
	except:
		distance = np.NaN
	return distance




def nearestNeighbours(user, K=10):
	allUsers = pd.DataFrame(userItemRatingMatrix.index)
	allUsers = allUsers[allUsers.user!=user]
	allUsers['distance'] = allUsers['user'].apply(lambda x: distance(user,x))
	KnearestUsers = allUsers.sort_values(["distance"], ascending=True)["user"][:K]
	return KnearestUsers


def recommendedBooks(user, N=10):
	Knearest = nearestNeighbours(user)
	NNRatings = userItemRatingMatrix[userItemRatingMatrix.index.isin(Knearest)]
	avgRating = NNRatings.apply(np.nanmean).dropna()
	booksAlreadyRead = userItemRatingMatrix.transpose()[user].dropna().index
	avgRating = avgRating[~avgRating.index.isin(booksAlreadyRead)]
	avgRating = avgRating.sort_values(ascending=False)[:N]
	topNISBNs = avgRating.index.get_level_values('isbn')	
	return pd.Series(topNISBNs).apply(bookMeta)


print(faveBooks("204813",10))

print(recommendedBooks("204813",10))








