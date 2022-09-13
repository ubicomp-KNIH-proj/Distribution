from tabnanny import check
from pymongo import MongoClient
from calIndexSearch  import calIndexSearch, listLength
from moodMonthSearch import stringToInt

client = MongoClient('localhost', 27017)
db = client['survey']

bigdata = ["S119", "S010", "S011", "S501"]

cursor_memb = db.members.find()

for member in cursor_memb:              # 전체 멤버에 대하여
    print(member['id'])
    id = member['id']
    if member['id'] in bigdata:
        pass
    else:
        col_cursor = db[member['id']].find() # 해당 컬렉션 접근
        reg_m = member["register_month"]     # 가입 월
        reg_d = member["register_day"]       # 가입 일
        # same_date = []; check_date = 0     # same_date -> 같은 날짜를 가지는 document의 _id; check_date -> 확인하고자 하는 날짜
        date_list = []
        daily_list = []                      # Daily survey를 제출여부 저장 리스트. 최종 목적
        total_length = listLength(reg_m, reg_d, 9, 4)
        print(total_length)

        for i in col_cursor:                 # doucument 접근
            try:
                original_date = i['date']
                splited_date = original_date.split(" ")                      # 다큐먼트의 날짜, 시간

                month = stringToInt(splited_date[1]); day = splited_date[2] # e.g.(다큐먼트의)8월 25일

                gmt = splited_date[4].split(":")                             # 시간 
                hour = gmt[0]; mininute = gmt[1]; second = gmt[2]            # 다큐먼트의 시, 분, 초

                if len(str(month)) == 1:
                    month = '0' + str(month)
                if len(hour) == 1:
                    hour = '0' + hour
                if len(mininute) == 1:
                    mininute = '0' + mininute

                date = str(month) + str(day) + '-' + hour + mininute
                date_list.append(date)
            except:
                pass
        print(date_list)
        day_list = []

        for i in range(len(date_list)):
            now = date_list[i]
            now_month = int(now[0:2])  # 8  M
            now_day = int(now[2:4])    # 25 D
            now_hour = int(now[5:7])   # 19 H

            if i == 0:                 # 초기
                check = reg_d                                                           # 처음엔 무조건 check로 설정
                day_list.append(calIndexSearch(reg_m, reg_d, now_month, now_day))       # 그에 따른 인덱스

            if now_month != reg_m:                                                      # 월이 달라지면 8 -> 9
                sep_day = now_day
                now_day = now_day + 31                                                  # 비교를 쉽게 하기 위해
                print(sep_day)

            if now_hour < 5:                                                            # 5시이전이면 옛날                                           
                if now_day != reg_d:
                    now_day = now_day - 1
                    sep_day = 31
                    now_month = 8
                    
            elif now_hour > 5:                                                          # 5시이후면 그 날
                now_day

            if check != now_day:                                                        # 날이 달라지면
                if now_month == 9:
                    day_list.append(calIndexSearch(reg_m, reg_d, now_month, sep_day))   # 9월이면 
                else:
                    day_list.append(calIndexSearch(reg_m, reg_d, now_month, now_day))   # 8월이면
                check = now_day

        print(day_list)

        for i in range(total_length):
            if i in day_list:
                daily_list.append(1)                                                    # 인덱스 리스트에 있으면 1
            else:
                daily_list.append(0)                                                    # 인덱스 리스트에 없으면 0
        print(daily_list)

        ## 최종 데일리 리스트 업데이트 ##
        db.members.update_one({ "id": id }, { "$set": { "daily_list": daily_list }}, upsert=True ) 
        



    

        

        

