

from pymongo import MongoClient
import pymongo
import pandas as pd
    

DB = None


def get_mongo_db():

    global DB
    
    if not DB is None:
        return DB

    client = MongoClient()
    DB = client['mad2']
    return DB


def get_transact_dbs():
    db = get_mongo_db()
    coll = db['csum']

    return db['shasum2transaction'], db['transaction']


def get_latest_csum():
    db = get_mongo_db()
    coll = db['csum']
    
    raw = list(coll.find().sort('time', pymongo.DESCENDING).limit(1))[0]
    data = pd.DataFrame(raw['data'])
    return raw['time'], data


def get_latest_waste():
    db = get_mongo_db()
    coll = db['waste']
    
    raw = list(coll.find().sort('time', pymongo.DESCENDING).limit(1))[0]
    data = pd.DataFrame(raw['data'])
    return raw['time'], data


def get_trans_db():
    db = get_mongo_db()
    return db['transient']


def get_waste_db():
    db = get_mongo_db()
    return db['waste']


    
