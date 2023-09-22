# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import csv
import re

import nltk
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
# from Levenshtein import distance as lev
from itertools import chain
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import time

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 5000)


def top10_most_rated():
    ratings = pd.read_csv('recommender/data/ratings.csv', usecols=['userId', 'movieId', 'rating'],
                          engine='python')
    movies = pd.read_csv('recommender/data/movies.csv', engine='python')

    ratings_titles = ratings.merge(movies, on='movieId', how='left').drop(columns=['genres', 'userId', 'rating'])
    most_rated_series = ratings['movieId'].value_counts(ascending=False).reset_index()
    most_rated_series.columns = ['movieId', 'rating_count']
    most_rated = pd.DataFrame(most_rated_series)

    most_popular = most_rated.merge(ratings_titles, on='movieId', how='inner').drop_duplicates().reset_index().drop(
        columns='index')

    return print(most_popular[0:10])


def is_valid_user(id):
    ratings = pd.read_csv('recommender/data/ratings.csv', engine='python')
    return int(id) in ratings['userId'].unique()


def collaborative_filtering(query_index):
    ratings = pd.read_csv('recommender/data/ratings.csv', usecols=['userId', 'movieId', 'rating'],
                          engine='python')
    movies = pd.read_csv('recommender/data/movies.csv', engine='python')
    links = pd.read_csv('recommender/data/links.csv', engine='python')

    user_item_table = ratings.pivot(index='userId', columns='movieId', values='rating').fillna(0)

    print(links[:10])
    print(user_item_table.head())

    user_item_matrix = csr_matrix(user_item_table.values)

    # query_index = np.random.choice(user_item_table.shape[0])
    # query_index = 1

    query_index = int(query_index)
    query_index = query_index - 1

    print("Izabrani korisnik: ", user_item_table.index[query_index])

    model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    model_knn.fit(user_item_matrix)

    # znaci - moras da nadjes imena kolona za sve vrednosti koje je korisnik ocenio
    # i onda da iz resenja za sve usere izbacis te filmove to jest anuliras ih uh.

    # nadji 6 najsličnijih korisnika

    distances, indices = model_knn.kneighbors(user_item_table.iloc[query_index, :].values.reshape(1, -1),
                                              n_neighbors=6)

    # selektovan korisnik
    # moras da izbacis iz resenja filmove koje je korisnik vec ocenio/gledao

    df = pd.DataFrame(user_item_table.iloc[query_index, :])

    already_rated = []
    for index, value in df.itertuples():
        if value != 0.0:
            already_rated.append(index)

    similar_usersId = indices.flatten()
    similar_usersId = similar_usersId[similar_usersId != query_index]

    print(similar_usersId)

    print('Top 5 similar users IDs: ', similar_usersId)
    print('With distances: ', distances)
    print('-----------------------------------------------')

    most_similar_users = pd.DataFrame(similar_usersId, columns=['userId'])
    merged = most_similar_users.merge(ratings, on='userId', how='inner')
    s_user_item = merged.pivot(index='userId', columns='movieId', values='rating').fillna(0)

    print('Identifikacioni brojevi vec ocenjenih filmova datog korisnika:')
    print(already_rated)
    print('-------------------------------------------------')

    # anuliraju se rejtinzi najslicnijih korisnika za filmove koji je ponudjeni korisnik vec gledao/rejtovao
    # tako da se nece vrsiti ta preporuka zato sto se predlaze na osnovu najbolje rejtovanih filomova
    # najslicnijih korisnika

    for id in already_rated:
        s_user_item.loc[:, [id]] = 0.0

    # index = movieIds , items = ratings , sort Series by biggest ratings
    best_rated_movies = s_user_item.max().sort_values(ascending=False).index
    best_recommendations = pd.DataFrame(best_rated_movies[0:20]).merge(movies, on='movieId', how='inner')
    return_value_df = best_recommendations.merge(links, on='movieId', how='inner')
    return_value = return_value_df['imdbId']

    return return_value


def jaccard_similarity(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))

    return intersection_cardinality / float(union_cardinality)

    # ako series sadrzi string koji ima u sebi cetvorocifren broj
    # nadji indekse pozicije u seriesu gde se ti brojevi nalaze
    # izvuci ih i na njihova mesta stavi na vrednosti i onda ih izbaci


def extract_year(temp):
    result = temp.str.contains(pat=r'\d{4}')
    print('Rezultati\n')
    print(result)
    if result.any():
        print('Indeksi\n')
        indices = result[result].index.values
        print(indices)
        years_df = temp[indices].str.extract(r'(\d{4})')
        print('years_df\n')
        print(years_df
              )
        years_list = years_df.values.tolist()
        flatten_list = list(chain.from_iterable(years_list))
        temp = temp.drop(indices)

        return flatten_list, temp
    else:
        return [], temp


def extract_genres(input_series, genres_series):
    input_series_no_genres = input_series[~input_series.isin(genres_series)]
    input_series_genres = input_series[~input_series.isin(input_series_no_genres)].values
    return input_series_genres, input_series_no_genres


def Sorting(lst):
    lst2 = sorted(lst, key=len)
    return lst2


def get_subsets(full_set):
    setlist = list(full_set)
    subsets = []
    for i in range(2 ** len(setlist)):
        subset = []
        for k in range(len(setlist)):
            if i & 1 << k:
                subset.append(setlist[k])
        subsets.append(subset)

    subset = Sorting(subsets)
    subset = list(reversed(subset))

    return subset


def get_year_exact(input_series_years, temp):
    df_year_exact = pd.DataFrame()
    for year in input_series_years:
        mask = temp.year.apply(lambda x: str(year) == x)
        df1 = temp[mask]
        df_year_exact = pd.concat([df_year_exact, df1])

    return df_year_exact


def get_year_span(input_series_years, temp):
    df_year_tolerance = pd.DataFrame()

    for year in input_series_years:
        for i in range(int(year) - 2, int(year) + 2, 1):
            mask = temp.year.apply(lambda x: str(i) == x)
            df1 = temp[mask]
            df_year_tolerance = pd.concat([df_year_tolerance, df1])

    return df_year_tolerance


def deal_with_genres(movies, subsets):
    movie_list = []
    for index, row in movies.iterrows():
        if set(subsets[0]).issubset(set(row['genres'])):
            movie_list.append(row)

    df = pd.DataFrame(movie_list)
    df['len'] = df['genres'].str.len()
    df_sorted_by_genres = df.sort_values(by='len', ascending=True)
    df_sorted_by_genres = df_sorted_by_genres.drop(columns=['len'])

    return df_sorted_by_genres


def deal_with_tags(df, tags, input_series_tags):
    merged = df.merge(tags, on='movieId', how='inner')

    temp = []
    for word in input_series_tags:
        for index, row in merged.iterrows():
            if word in row['tag']:
                temp.append(row)

    highest_score_matched_tag = pd.DataFrame(temp)\
        .drop_duplicates(subset=['movieId'])
    return highest_score_matched_tag


def datasets_preprocessing(movies, tags, lemmatizer):
    movies['genres'] = movies['genres'].str.lower()
    movies['genres'] = movies['genres'].str.split("|")
    movies['year'] = movies['title'].str.extract(r'(?:\((\d{4})\))?\s*$')
    movies['title'] = movies['title'].str.replace(r'(?:\((\d{4})\))?\s*$', '')

    # make a df where there's a single genre in column
    temp = movies.apply(lambda x: pd.Series(x['genres']), axis=1).stack().reset_index(level=1, drop=True)
    temp.name = 'genres'
    movies_split_genres = movies.drop('genres', axis=1).join(temp)
    movies_split_genres['genres'] = movies_split_genres['genres'].str.lower()

    # list of unique genres in dataset
    genres_series = pd.Series(movies_split_genres['genres'].unique()).str.lower()

    tags = tags.drop(axis=1, columns=['timestamp', 'userId']).drop_duplicates()
    tags['tag'] = tags['tag'].str.lower()
    tags['tag'] = tags['tag'].str.split(' ')

    temp = tags.apply(lambda x: pd.Series(x['tag']), axis=1).stack().reset_index(level=1, drop=True)
    temp.name = 'tag'
    tags_split = tags.drop('tag', axis=1).join(temp)
    tags_split['tag'] = tags_split['tag'].apply(lambda word: lemmatizer.lemmatize(word))
    tags = tags_split.groupby('movieId')['tag'].apply(list).reset_index()

    return movies, tags, genres_series


def content_based_filtering(input_text):
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    nltk.download('punkt')
    # vrati recommender/

    movies = pd.read_csv('recommender/data/movies.csv', engine='python')
    tags = pd.read_csv('recommender/data/tags.csv', engine='python')
    links = pd.read_csv('recommender/data/links.csv', engine='python')
    print(tags.head())
    sw = stopwords.words('english')
    lemmatizer = WordNetLemmatizer()

    movies, tags, genres_series = datasets_preprocessing(movies, tags, lemmatizer)
    print('Filmovi nakon procesuiranja\n')
    print(movies)
    print("---------")
    print('Tabela tagovi nakon procesuiranja\n')
    print(tags)
    print('---------')
    print(genres_series)
    # +++++++++++++++++++++++++++++++++++DONE PREPROCESSING++++++++++++++++++++++++++++++++

    # deal with genres from the input text

    print("Unesen tekst za pretragu: ", input_text)

    if input_text == '':
        print('No input text provided')
        exit()

    input_text_tokenized = [word.lower() for word in word_tokenize(input_text) if word.lower() not in sw]
    input_series = pd.Series(input_text_tokenized)

    input_series_genres, input_series_ng = extract_genres(input_series, genres_series)

    input_series_years, input_series_tags = extract_year(input_series)

    input_series_tags = [lemmatizer.lemmatize(word) for word in input_series_tags]

    print("Identifikovani žanrovi iz korisničkog unosa: ", input_series_genres)
    print("Identifikovane godine iz korisničkog unosa: ", input_series_years)
    print("Identifikovani tagovi iz korisničkog unosa: ", input_series_tags)

    subsets = get_subsets(input_series_genres)


    print("Originalni podskupovi zanrova : ", subsets)

    # zanrovi, funkcionise i ako je je lista podskupova prazna,
    # posto je tu prazan skup

    df_sorted_by_genres = deal_with_genres(movies, subsets)

    tags_final = pd.DataFrame()

    if input_series_tags:
        print("Uneseni tekst ima tagova")
        df_tags = deal_with_tags(df_sorted_by_genres, tags, input_series_tags)
        if len(df_tags.index) < 10:
            temp = [df_tags, df_sorted_by_genres]
            tags_final = pd.concat(temp)
        else:
            print("Uneseni tekst nema tagova")
            tags_final = df_tags

    result = pd.DataFrame()

    if input_series_years:
        print("Uneseni tekst ima godina")
        if tags_final.empty:
            year = get_year_exact(input_series_years, df_sorted_by_genres)
            year_span = get_year_span(input_series_years, df_sorted_by_genres)
        else:
            print("Uneseni tekst nema godina")
            year = get_year_exact(input_series_years, tags_final)
            year_span = get_year_span(input_series_years, tags_final)
        frames = [year, year_span]
        result = pd.concat(frames)
        if year.empty:
            result = get_year_span(input_series_years, tags_final)

    concat = [result, tags_final]
    filtered = pd.concat(concat)
    filtered = filtered.drop_duplicates(subset=['movieId'])

    if filtered.empty:
        output = df_sorted_by_genres
    else:
        output = filtered

    return_value_df = output.merge(links, on='movieId', how='inner')
    return_value = return_value_df['imdbId']
    return return_value

    print("---------------------------------")

    # print(f'Done: {time.time() - start_time:.2f}')
