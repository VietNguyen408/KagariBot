from pymongo import MongoClient


client = MongoClient('mongodb+srv://mckenzie:29112001@jojo-quotes.n5rr3.mongodb.net/kagari?retryWrites=true&w=majority')

# Pull content from MongoDB
question_db = client['kagari']['question']
setting_db = client['kagari']['setting']
