# crawl-python-mongodb

## Installation

Python

```sh
https://www.python.org/downloads/
```

pymongo

```no-highlight
pip install pymongo
```

Mongodb

```sh
https://www.mongodb.com/try/download/community
```

## Get started

#### Create database 
- Mongo doesn't create database without collection & data.

```no-highlight
    CONNECTION_STRING = "mongodb://localhost:27017/"

    client = MongoClient(CONNECTION_STRING)
    # Create database name
    mydb = client['mydatabase']
    # Create collection name
    mycol = mydb["customers"]
    document = {"user_id": 1, "user": "test"}
    mycol.insert_one(document)
    print(mydb.list_collection_names())
```

- You can check if a database exist by listing all databases in you system:
```no-highlight
    print(myclient.list_database_names())
```

#### Create Collection
- Create Collection
```no-highlight
    import pymongo

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]

    mycol = mydb["customers"]
```
- Check if Collection Exists
```
    print(mydb.list_collection_names())
```
