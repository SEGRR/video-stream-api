from fastapi import APIRouter, HTTPException, Depends , Query ,status
from typing import List
from pydantic import BaseModel
from models.movie import Movie
from config.db import movies as movies_db
from models.user import User
import pickle
from . import auth
import pandas as pd
import numpy as np

similarity_vector = pickle.load(open("./router/similarity.pkl","rb"))
df = pickle.load(open("./router/index_df","rb"))

def serialize(entity):
   return {**{i:str(entity[i]) for i in entity if i == '_id'} , **{i:entity[i] for i in entity if i != '_id'}}

def serialize_all(en):
   return [serialize(i) for i in en]

router = APIRouter(
   dependencies=[Depends(auth.authenticate_request)],
    responses={404: {"description": "Not found"}}
)


@router.get('/detailed/{movie_id}')
async def get_movie(movie_id:int):
    if not auth:
        raise HTTPException(status_code=401 , detail="Authentication Error")
    movie = movies_db.find_one({"moive_id":movie_id})
    if not movie:
        raise HTTPException(status_code=404 , detail="Movie not found")
    return serialize(movie)


@router.get("/genre/{genre}")
async def get_by_genre(genre:str, limit:int = Query(10)):
    movie_list = movies_db.find({"genres" : genre.title()} , { "id":1,"title":1 , "popularity":1 , "poster_path":1 , "backdrop_path":1}).sort("popularity",-1).limit(limit)
    return serialize_all(movie_list)



@router.get("/language/{lang}")
async def get_by_language(lang:str, limit:int = Query(10)):
    movie_list = movies_db.find({"original_language" : lang} , { "id":1,"title":1 , "popularity":1 , "poster_path":1 , "backdrop_path":1}).sort("popularity",-1).limit(limit)
    return serialize_all(movie_list)


@router.get("/related/{movie_id}")
async def recommend_movie_by_id(movie_id:int, limit:int = Query(10)):
    recommended_list = recommend(id=movie_id , limit=limit)
    movie_list = movies_db.find({"id":{"$in":recommended_list}} ,  { "id":1,"title":1 , "popularity":1 , "poster_path":1 , "backdrop_path":1})
    return serialize_all(movie_list)


@router.get("/recommended/fav_genres")
async def recommend_movie_by_fav_genres(user:User = Depends(auth.get_current_user) , limit:int = Query(10)):
    result = dict()
    for g in user['fav_genres']:
        movies = movies_db.find({"genres" : g.title()} , { "id":1,"title":1 , "popularity":1 , "poster_path":1 , "backdrop_path":1}).sort("popularity",-1).limit(limit)
        result[g.title()] = serialize_all(movies)
    return result

@router.post("/recommended/genres")
async def recommend_on_genres(genre_list:list[str] , ratings:int , limit:int = Query(10)):
    result = dict()
    for g in genre_list:
        movies = movies_db.find({"$and":[{"genres": g.title()} , {"vote_average" :{"$eq": ratings}}]} , { "id":1,"title":1 , "popularity":1 , "poster_path":1 , "backdrop_path":1}).sort("popularity",-1).limit(limit)
        result[g.title()] = serialize_all(movies)
    return result


@router.get("/recommended/watch_history")
async def recommend_movie_by_watch_historys(user:User = Depends(auth.get_current_user) , limit:int = Query(5)):
    result = []
    for watch_hist in user['watch_history'][-3:]:
        movie_ids = recommend(id=watch_hist , limit=limit)
        movie_list = movies_db.find({"id":{"$in":movie_ids}} ,  { "id":1,"title":1 , "popularity":1 , "poster_path":1 , "backdrop_path":1})
        result.extend(serialize_all(movie_list))
    return result

    


def recommend(id , limit=10):
    
    movie_index = df[df['id'] == id].index[0]
    movie_list = sorted(list(enumerate(similarity_vector[movie_index])), reverse=True, key= lambda x: x[1])[1:limit+1]
    return [int(df.iloc[i[0]].id) for i in movie_list]




