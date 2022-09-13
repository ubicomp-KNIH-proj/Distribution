#_*_ coding:utf-8 _*_
from fileinput import filename
from pymongo import MongoClient
from flask_pymongo import PyMongo
import gridfs
import os

def mongo_conn():
    try:
        conn = MongoClient('localhost', 27017)
        print('MongoDB connected', conn)
        return conn['survey']
    except Exception as e:
        print("Error in mongo connection:", e)

db = mongo_conn()
#Input SID
coll = 'SID'
make_folder = './File/' + coll

os.mkdir(make_folder)

fs = gridfs.GridFS(db, collection=coll)

for grid_out in fs.find({}):
    data = grid_out.read().decode(errors='ignore')
    name = grid_out.filename
    # print(grid_out.filename, data)
    download = make_folder + '/' + name
    f = open(download, 'wb')
    f.write(data.encode())
    f.close()
    print("download complete") 