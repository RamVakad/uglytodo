from pymongo import MongoClient

client = MongoClient("mongodb://masteruser:HFjlXvSDQvQBMbKC@cluster0-shard-00-00-tu9pd.mongodb.net:27017,cluster0-shard-00-01-tu9pd.mongodb.net:27017,cluster0-shard-00-02-tu9pd.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")

adminDB = client.admin
db = client.todoapp


serverStatusResult = adminDB.command("serverStatus")
print(serverStatusResult)
