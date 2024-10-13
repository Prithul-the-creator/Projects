#import numpy


import pandas as pd
column_names=['user_id', 'item_id', 'rating', 'timestamp']
df = pd.read_csv('u.data', sep='\t', names=column_names)
movietitles = pd.read_csv('Movie_Id_Titles')
df=pd.merge(df, movietitles, on="item_id")

df.groupby(df['title'])['rating'].mean().sort_values(ascending=False)
ratings=pd.DataFrame(df.groupby('title')['rating'].mean())
ratings["num of reviews"]=pd.DataFrame(df.groupby("title")["rating"].count())

inpmovie=input()
moviemat = df.pivot_table(index='user_id',columns='title',values='rating')
ratings.sort_values('num of reviews',ascending=False).head()
newmovieratings = moviemat[inpmovie]
similar_to_newmovie = moviemat.corrwith(newmovieratings)
corr_newmovie = pd.DataFrame(similar_to_newmovie,columns=['Correlation'])
corr_newmovie.dropna(inplace=True)
corr_newmovie.sort_values('Correlation',ascending=False)
corr_newmovie = corr_newmovie.join(ratings['num of reviews'])
corr_newmovie[corr_newmovie['num of reviews']>200].sort_values('Correlation',ascending=False).head(6)
