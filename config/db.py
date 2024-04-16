from pymongo import MongoClient

conn = MongoClient("mongodb+srv://admin:admin2003@cluster0.ysemorc.mongodb.net/")
db = conn.get_database('video_stream')
user = db.get_collection("user")
movies = db.get_collection("movies")
