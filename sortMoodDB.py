from tabnanny import check
from pymongo import MongoClient
from calIndexSearch  import calIndexSearch
from moodMonthSearch import stringToInt

client = MongoClient('localhost', 27017)
db = client['survey']

bigdata = ["S119", "S010", "S011", "S501"]

cursor_memb = db.members.find()

for member in cursor_memb:              # 전체 멤버에 대하여
    print(member['id'])
    if member['id'] in bigdata:
        pass
    else:
        col_cursor = db[member['id']].find() # 해당 컬렉션 접근
        reg_m = member["register_month"]    # 가입 월
        reg_d = member["register_day"]      # 가입 일
        same_date = []; check_date = 0      # same_date -> 같은 날짜를 가지는 document의 _id; check_date -> 확인하고자 하는 날짜
        daily_list = []                     # Daily survey를 제출여부 저장 리스트. 최종 목적
        
        for i in col_cursor:                # doucument 접근
            try:
                original_date = i['date']
                splited_date = original_date.split(" ")                      # 다큐먼트의 날짜, 시간

                month = stringToInt(splited_date[1]); date = splited_date[2] # e.g.(다큐먼트의)8월 25일

                gmt = splited_date[4].split(":")                             # 시간 
                hour = gmt[0]; mininute = gmt[1]; second = gmt[2]            # 다큐먼트의 시, 분, 초

                if month == 9:                                               # 8월 31일 이후 9월1일을 8월31일 취급
                    date = date + 31

                # if len(same_date) == 0:                                      
                #     check_date = date                                        # 체크 날짜 초기화 
                #     same_date.append(i["_id"])
                # else:
                #     if date - check_date == 0:
                #         if hour < 5:
                #             pass
                #         elif hour > 5:                                       # 같은 날일때
                #             same_date.append(i["_id"])
                #     elif date - check_date == 1:
                #         if hour < 5:                                         # 같은 날일때
                #             same_date.append(i["_id"])
                #         elif hour > 5:                                       # 날이 바뀌었을 때
                #             daily_list.append(1)
                #             same_date = []; check_date = date
                #             same_date.append(i["_id"])
                #     elif date - check_date > 2:                       
                #         if hour < 5:                                         
                #             check_date = date
                #             submit_date = date - 1
                #         elif hour > 5:                                       # 날이 바뀌고 중간에 한 날이 비었을때
                #             daily_list.append(0)
                #             same_date = []; check_date = date
                #             same_date.append(i["_id"])

                # 마지막에 데일리 리스트 업데이트
                # db.members.update_one({ "id": id }, { "$set": { "daily_list": daily_list }, upsert=true })
                print(original_date)
            except:
                pass


















##################################################################################
# for i in cursor: # doucument 보기
#     if "date" in i:
#         date = i['date']
#         original_date = date.split(" ") # 1차 나누기
#         sub_date = original_date[4].split(":") # 2차 나누기

#     if 'a' in sub_date: # 하나라도 있으면
#         if int(sub_date[0]) > 15 and int(sub_date[0]) < 20:
#             object_id_list.append(i["_id"])
#             if len(object_id_list) > 1:
#                 for j in range(len(object_id_list)-1): # 바깥으로 이동
#                     db.S002.delete_one({ "_id": j })
#                     reg_m = s002["register_month"]
#                     reg_d = s002["register_day"]
                    
#                     month = int(stringToInt(original_date[1]))
#                     date = int(original_date[2])

#                     index = int(calIndexSearch(reg_m, reg_d, month, date))
#                     ## 인덱스에 1
#         else: #하나라도 없으면
#             ## 인덱스에 0
#             pass
        