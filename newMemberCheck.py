from pymongo import MongoClient
import pymongo
import csv


client = MongoClient('localhost', 27017)
db = client['survey']
user_coll = db["S000"]
members = db["members"]


user_mood = user_coll.find()
memb = members.find({ "id": "S000" })
for user_info in memb:
    month = user_info["register_month"]; day = user_info["register_day"]

f = open('./S002/mood.csv', 'a+')
header = 'date, type, contents\n' 
f.write(header)

for doc in user_mood:
    print(doc)
    try:           # Daily
        cont = doc['mood']
        try:    # Date - Daily
            date = doc['date']

        except: # None - Daily
            date= 'Unknown'
        
        finally:
            doc_type = '3'
            f.write(str(date) + ',' + doc_type + ',' + str(cont) + '\n')

    except:
        try:       # Weekly
            date = doc['date']
            doc_type = '2'
            cont = str(doc['formData1']) + str(doc['formData2'])

        except:    # One-time
            date = '2022-' + str(month) + '-' + str(day)
            doc_type = '1'
            cont = str(doc['1_formData1']) + str(doc['1_formData2'])

        finally:
            f.write(str(date) + ',' + doc_type +',' + str(cont) + '\n')