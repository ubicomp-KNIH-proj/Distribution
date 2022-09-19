# Ubi_Lab, Dept. of Internet of Things, ML, SCH Univ.
# Author: Changwon Lee - Chaewon Song

from flask import *
from flask_pymongo import PyMongo
from pymongo import MongoClient
import datetime
from flask import flash
from flask import url_for
import gridfs
import time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
from datetime import timedelta
from flask import session, app
from calIndexSearch import calIndexSearch

######### Config #########
app = Flask(__name__)
app.config['SECRET_KEY'] = "2019"
app.config["MONGO_URI"] = "mongodb://localhost:27017/survey"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
mongo = PyMongo(app)
client = MongoClient('localhost', 27017)
members = mongo.db.members
db = client['survey']
IoT_1 = "http://114.71.220.59:7579"
######### Config #########


#홈화면
@app.route('/')
def home():
   return render_template('login.html')

#홈화면_영어
@app.route('/en')
def home_en():
   return render_template('login_en.html')

# 회원가입
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        id =  'S' + request.form.get("id", type=str)
        pwd = request.form.get("pwd", type=str)
        pwd2 = request.form.get("pwd2", type=str)
        
        now = datetime.datetime.now()
        today_y = now.year
        today_m = now.month
        today_d = now.day
        post = {
            "id": id,                  # SID (개인식별번호)
            "pwd": pwd,                # 비밀번호
            "register_year": today_y,  # 가입 연도 
            "register_month": today_m, # 가입 월
            "register_day": today_d,   # 가입 날짜
            "gyro_count": 0,           # 자이로 파일 개수 for iOS
            "acc_count": 0,            # 가속도 파일 개수 for iOS
            "health_count": 0,         # 헬스   파일 개수 for iOS
            "submit_count": 0,         # 설문 제출 횟수
            "weekly_count": 0,         # 주간 설문 여부
            "attach_count": 0,         # 파일 제출 횟수 for Android
            "daily": 0,                # 핸드폰 종류
            "CIN_count": 0,            # Mobius 컨테이너 개수
            "cal_list": [],            # Mobius 컨테이너 충족 여부
            "daily_list": [],          # 1일 설문 여부 - Added 25 Aug
            "daily_flag": 0            # 1일 설문 가능 - Added 25 Aug
        }

        if id in mongo.db.list_collection_names() :          # 회원가입 되어있는 Sid 접근시
            flash("이미 가입한 계정이 있습니다.")
            return render_template("register.html", data=id)
        else :
            mongo.db.create_collection(id)                   #회원가입시 컬렉션 생성
        
        if not (id and pwd and pwd2):                        # 아이디, 비밀번호 중 하나라도 미입력시
            return "모두 입력해주세요"
        elif pwd != pwd2:                                    # 비밀번호가 틀렸을 시
            return "비밀번호를 확인해주세요."
        else:                                                # 정상 가입 완료
            members.insert_one(post)
            return render_template("one_time.html", data=id) # One-time Survey 

# 회원가입_영어
@app.route('/register_en', methods=['GET','POST'])
def register_en():
    if request.method == 'GET':
        return render_template("register_en.html")
    else:
        id =  'S' + request.form.get("id", type=str)
        pwd = request.form.get("pwd", type=str)
        pwd2 = request.form.get("pwd2", type=str)
        
        now = datetime.datetime.now()
        today_y = now.year
        today_m = now.month
        today_d = now.day
        post = {
            "id": id,                  # SID (개인식별번호)
            "pwd": pwd,                # 비밀번호
            "register_year": today_y,  # 가입 연도 
            "register_month": today_m, # 가입 월
            "register_day": today_d,   # 가입 날짜
            "gyro_count": 0,           # 자이로 파일 개수 for ios
            "acc_count": 0,            # 가속도 파일 개수 for ios
            "health_count": 0,         # 헬스   파일 개수 for ios
            "submit_count": 0,         # 설문 제출 횟수
            "weekly_count": 0,         # 주간 설문 여부
            "attach_count": 0,         # 파일 제출 횟수 for Android
            "daily": 0,                # 핸드폰 종류
            "CIN_count": 0,            # Mobius 컨테이너 개수
            "cal_list": [],            # Mobius 컨테이너 충족 여부
            "daily_list": [],          # 1일 설문 여부 - Added 25 Aug
            "daily_flag": 0            # 1일 설문 가능 - Added 25 Aug
        }

        if id in mongo.db.list_collection_names() :             # 회원가입 되어있는 Sid 접근시 
            flash("Already signed up for an account. Please check again!")
            return render_template("register_en.html", data=id)
        else :
            mongo.db.create_collection(id)                      #회원가입시 컬렉션 생성
        
        if not (id and pwd and pwd2):                           # 아이디, 비밀번호 중 하나라도 미입력시
            return "Please enter all"
        elif pwd != pwd2:                                       # 비밀번호가 틀렸을 시
            return "Please confirm your password."
        else:                                                   # 정상 가입 완료 
            members.insert_one(post)
            return render_template("one_time_en.html", data=id) # One-time Survey 

# 초기설문 처리 아이폰, 안드로이드 사용자 구분
@app.route('/ajax', methods=['GET', 'POST'])
def ajax():
    data = request.get_json()
    x_survey = list(data.values())[0]
    survey_result = mongo.db.get_collection(x_survey)
    del data['ID']
    survey_result.insert_one(data)
    data.pop('_id')
    daily = data['1_formData1']
    daily_f = list(m['value'] for m in daily)

    if daily_f[3] == '1':        # 안드로이드 사용자
        members.update_one({'id':x_survey}, {'$set':{'daily':1}})
    else:
        if daily_f[3] == '2':    # 아이폰 사용자
            members.update_one({'id':x_survey}, {'$set':{'daily':2}})

    return jsonify(result = "success", result2= data, result3=daily)
    
#로그인 시도 
@app.route('/user/login', methods = ['POST'])
def login():
    id = 'S' + request.form['id']
    pwd = request.form['pwd']
    session['id'] = id
    user = members.find_one({'id':id}, {'pwd':pwd})

    if user is None:                                   # members에 없음
        flash("접속하신 계정은 존재하지 않는 계정입니다.")
        return render_template('login.html')
    else: #members에 있음
        member_id = members.find_one({'id': id})
        if member_id['pwd'] == pwd:                    # 비밀번호가 맞는지 확인
            reg_coll = mongo.db.get_collection(id) 
            reg_check = reg_coll.find_one({'check':1}) # 해당 컬렉션에 onetime 결과가 있는지 확인

            if reg_check is None:                      # 초기 설문 결과가 없다면
                flash("회원가입을 이어서 진행합니다.")
                return render_template('one_time.html', data=id)
            else:                                      # 초기 설문 결과가 있다면
                session['id'] = request.form['id'] 
                session.permanent = True

                daily_cal = member_id["daily"]
                cin_count = member_id["CIN_count"]
                cal_list = member_id["cal_list"]
                daily_list = member_id["daily_list"]
                reg_y = member_id["register_year"]
                reg_m = member_id["register_month"]
                reg_d = member_id["register_day"]

                if daily_cal == 1 :                    # 안드로이드 사용자 -> 파일 캘린더 
                    return render_template('calendar.html', sid=id, cin=cin_count, cal=cal_list, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d)
                else:
                    if daily_cal == 2:                 #아이폰 사용자 -> 데일리 캘린더
                        return render_template('daily_calendar.html', sid=id, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d)

        else:                                          #비밀번호가 틀리면
            flash('비밀번호가 일치하지 않습니다.')
            return render_template('login.html')

#로그인 시도 Eng ver
@app.route('/user/login_en', methods = ['POST'])
def login_en():
    id = 'S' + request.form['id']
    pwd = request.form['pwd']
    session['id'] = id
    user = members.find_one({'id':id}, {'pwd':pwd})

    if user is None:                                   # members에 없음
        flash("The account you accessed does not exist")
        return render_template('login_en.html')
    else: #members에 있음
        member_id = members.find_one({'id': id})
        if member_id['pwd'] == pwd:                    # 비밀번호가 맞는지 확인
            reg_coll = mongo.db.get_collection(id) 
            reg_check = reg_coll.find_one({'check':1}) # 해당 컬렉션에 onetime 결과가 있는지 확인

            if reg_check is None:                      # 초기 설문 결과가 없다면
                flash("The survey for membership registration has not been completed.")
                return render_template('one_time.html', data=id)
            else:                                      # 초기 설문 결과가 있다면
                session['id'] = request.form['id'] 
                session.permanent = True

                daily_cal = member_id["daily"]
                cin_count = member_id["CIN_count"]
                cal_list = member_id["cal_list"]
                daily_list = member_id["daily_list"]
                reg_y = member_id["register_year"]
                reg_m = member_id["register_month"]
                reg_d = member_id["register_day"]

                if daily_cal == 1 :                    # 안드로이드 사용자 -> 파일 캘린더 
                    return render_template('calendar_en.html', sid=id, cin=cin_count, cal=cal_list, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d)
                else:
                    if daily_cal == 2:                 #아이폰 사용자 -> 데일리 캘린더
                        return render_template('daily_calendar_en.html', sid=id, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d)

        else:                                          #비밀번호가 틀리면
            flash('비밀번호가 일치하지 않습니다.')
            return render_template('login.html')


#로그아웃
@app.route('/logout')
def logout():
    session.pop('id', None) # 세션 종료
    return render_template('login.html')

#Daily_아이폰 사용자 - 당일 제출
@app.route('/moody', methods=['POST'])
def moody():  
    data = request.files['data']
    st = data.read(); l = st.decode(); evl = eval(l)
    s_id = evl['sid']; mood = evl['mood']; date = evl['date']

    md = { "mood": mood , "date": date }
    survey_coll = mongo.db.get_collection(s_id)
    survey_coll.insert_one(md)
    members.update_one({'id': s_id}, {'$set': {'daily_flag': 1}})   # 1일 설문 제출 완료 Added 13 Sep

    if 'filed' in request.files:
        f = request.files['filed']
        contents = f.read()
        fs = gridfs.GridFS(db, s_id)
        fname = f.filename
        members.update_one({'id': s_id}, {'$inc': {'gyro_count': 1}})
        fs.put(contents, filename=fname)
    if 'filed2' in request.files:
        f2 = request.files['filed2']
        contents = f2.read()
        fs2 = gridfs.GridFS(db, s_id)
        fname2 = f2.filename
        members.update_one({'id': s_id}, {'$inc': {'acc_count': 1}})
        fs2.put(contents, filename=fname2)
    if 'filed3' in request.files:
        f3 = request.files['filed3']
        contents = f3.read()
        fs3 = gridfs.GridFS(db, s_id)
        fname3 = f3.filename
        members.update_one({'id': s_id}, {'$inc': {'health_count': 1}})
        fs3.put(contents, filename=fname3)

    members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}})
    return render_template('login.html')

#Daily_아이폰 사용자 Eng ver - 당일 제출
@app.route('/moody_en', methods=['POST'])
def moody_en():  
    data = request.files['data']
    st = data.read(); l = st.decode(); evl = eval(l)
    s_id = evl['sid']; mood = evl['mood']; date = evl['date']

    md = { "mood": mood , "date": date }
    survey_coll = mongo.db.get_collection(s_id)
    survey_coll.insert_one(md)
    members.update_one({'id': s_id}, {'$set': {'daily_flag': 1}})   # 1일 설문 제출 완료 Added 13 Sep


    if 'filed' in request.files:
        f = request.files['filed']
        contents = f.read()
        fs = gridfs.GridFS(db, s_id)
        fname = f.filename
        members.update_one({'id': s_id}, {'$inc': {'gyro_count': 1}})
        fs.put(contents, filename=fname)
    if 'filed2' in request.files:
        f2 = request.files['filed2']
        contents = f2.read()
        fs2 = gridfs.GridFS(db, s_id)
        fname2 = f2.filename
        members.update_one({'id': s_id}, {'$inc': {'acc_count': 1}})
        fs2.put(contents, filename=fname2)
    if 'filed3' in request.files:
        f3 = request.files['filed3']
        contents = f3.read()
        fs3 = gridfs.GridFS(db, s_id)
        fname3 = f3.filename
        members.update_one({'id': s_id}, {'$inc': {'health_count': 1}})
        fs3.put(contents, filename=fname3)

    members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}})
    return render_template('login_en.html')

#Daily_갤럭시 사용자 - 당일 제출
@app.route('/moody2', methods=['POST'])
def moody2():  
    data = request.files['data']
    st = data.read(); l = st.decode(); evl = eval(l)
    s_id = evl['sid']; mood = evl['mood']; date = evl['date']

    md = { "mood": mood , "date": date }
    survey_coll = mongo.db.get_collection(s_id)                     # 해당 SID의 컬렉션
    survey_coll.insert_one(md)                                      # 해당 SID의 컬렉션에 Daily Survey 설문 결과 저장
    members.update_one({'id': s_id}, {'$set': {'daily_flag': 1}})   # 1일 설문 제출 완료 Added 25 Aug
    
    if 'filed[]' in request.files:                                  # 저장할 파일이 있다면 for Bigdata
        f = request.files.getlist('filed[]')
        for file in f:
          print("file is", file)
          contents = file.read()
          fs = gridfs.GridFS(db, s_id)
          fname = file.filename
          fs.put(contents, filename=fname)
        members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
    
    members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}}) # 제출 횟수 증가 
    return render_template('weekly.html')

#Daily_갤럭시 사용자_영어 - 당일 제출 
@app.route('/moody2_en', methods=['POST'])
def moody2_en():  
    data = request.files['data']
    st = data.read(); l = st.decode(); evl = eval(l)
    s_id = evl['sid']; mood = evl['mood']; date = evl['date']

    md = { "mood": mood , "date": date }
    survey_coll = mongo.db.get_collection(s_id)                     # 해당 SID의 컬렉션
    survey_coll.insert_one(md)                                      # 해당 SID의 컬렉션에 Daily Survey 설문 결과 저장
    members.update_one({'id': s_id}, {'$set': {'daily_flag': 1}})   # 1일 설문 제출 완료 Added 25 Aug
    
    if 'filed[]' in request.files:                                  # 저장할 파일이 있다면 for Bigdata
        f = request.files.getlist('filed[]')
        for file in f:
          print("file is", file)
          contents = file.read()
          fs = gridfs.GridFS(db, s_id)
          fname = file.filename
          fs.put(contents, filename=fname)
        members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
    
    members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}}) # 제출 횟수 증가 
    return render_template('weekly_en.html')

#마지막 페이지
@app.route('/final', methods=['GET', 'POST'])
def final():
    session.pop('id', None)
    return render_template("final.html")

#마지막 페이지_영어
@app.route('/final_en', methods=['GET', 'POST'])
def final_en():
    session.pop('id', None)
    return render_template("final_en.html")

# 주간 설문 
@app.route('/weekly', methods=['GET', 'POST'])
def weekly():
    data = request.get_json()
    s_id = list(data.values())[0]
    survey_coll = mongo.db.get_collection(s_id)                      # 해당 SID의 설문 컬렉션 
    del data['ID']
    survey_coll.insert_one(data)                                     # 해당 SID의 설문 컬렉션에 주간 설문 저장
    data.pop('_id')
    member_id = members.find_one({'id': s_id})
    members.update_one({'id': s_id}, {'$inc': {'weekly_count': -1}}) # 주간 설문 완료시-> count가 1씩 감소

    count = member_id['submit_count']
    hcount = member_id['health_count']
    gcount = member_id['gyro_count']
    acount = member_id['acc_count']
    fcount = member_id['attach_count']
    wcount = member_id['weekly_count']
    daily_flag = member_id['daily_flag']

    if daily_flag == 0:
        if member_id['daily'] == 1:
            return jsonify(render_template('android_daily.html', sid=s_id, cnt=count, fcnt=fcount))
        else:
            if member_id['daily'] == 2:
                return jsonify(render_template('ios_daily.html', sid=s_id, cnt=count, hcnt=hcount, gcnt=gcount, acnt=acount))
    elif daily_flag == 1:
        flash("이미 설문을 완료하셨습니다. 내일 설문해주세요")
        return jsonify(render_template('login.html'))

# 주간 설문_영어
@app.route('/weekly_en', methods=['GET', 'POST'])
def weekly_en():
    data = request.get_json()
    s_id = list(data.values())[0]
    survey_coll = mongo.db.get_collection(s_id)                      # 해당 SID의 설문 컬렉션 
    del data['ID']
    survey_coll.insert_one(data)                                     # 해당 SID의 설문 컬렉션에 주간 설문 저장
    data.pop('_id')
    member_id = members.find_one({'id': s_id})
    members.update_one({'id': s_id}, {'$inc': {'weekly_count': -1}}) # 주간 설문 완료시-> count가 1씩 감소

    count = member_id['submit_count']
    hcount = member_id['health_count']
    gcount = member_id['gyro_count']
    acount = member_id['acc_count']
    fcount = member_id['attach_count']
    wcount = member_id['weekly_count']
    daily_flag = member_id['daily_flag']

    if daily_flag == 0:
        if member_id['daily'] == 1:
            return jsonify(render_template('android_daily_en.html', sid=s_id, cnt=count, fcnt=fcount))
        else:
            if member_id['daily'] == 2:
                return jsonify(render_template('ios_daily_en.html', sid=s_id, cnt=count, hcnt=hcount, gcnt=gcount, acnt=acount))
    elif daily_flag == 1:
        flash("You have already completed the survey. please submit tomorrow")
        return jsonify(render_template('login_en.html'))

# 파일 캘린더 처리 - 갤럭시 사용자
@app.route('/ajax3', methods=['GET', 'POST'])
def ajax3():
    data = request.get_json()
    x_survey = list(data.values())[0]
    member_id = members.find_one({'id': x_survey})

    count = member_id['submit_count']
    wcount = member_id['weekly_count']
    hcount = member_id['health_count']
    gcount = member_id['gyro_count']
    acount = member_id['acc_count']
    fcount = member_id['attach_count']
    daily_list = member_id["daily_list"]
    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]

    if member_id['daily'] == 1:
        return jsonify(render_template('daily_calendar.html', sid=x_survey, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))
    else:
        if member_id['daily'] == 2:
            return jsonify(render_template('ios_daily.html', sid=x_survey, cnt=count, wcnt=wcount, hcnt=hcount, gcnt=gcount, acnt=acount))

#파일 캘린더_갤럭시 사용자_영어
@app.route('/ajax3_en', methods=['GET', 'POST'])
def ajax3_en():
    data = request.get_json()
    x_survey = list(data.values())[0]
    member_id = members.find_one({'id': x_survey})

    count = member_id['submit_count']
    wcount = member_id['weekly_count']
    hcount = member_id['health_count']
    gcount = member_id['gyro_count']
    acount = member_id['acc_count']
    fcount = member_id['attach_count']
    daily_list = member_id["daily_list"]
    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]

    if member_id['daily'] == 1:
        return jsonify(render_template('daily_calendar_en.html', sid=x_survey, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))
    else:
        if member_id['daily'] == 2:
            return jsonify(render_template('ios_daily_en.html', sid=x_survey, cnt=count, wcnt=wcount, hcnt=hcount, gcnt=gcount, acnt=acount))

# 설문 캘린더
@app.route('/ajax4', methods=['GET', 'POST'])
def ajax4():
    data = request.get_json()
    s_id = list(data.values())[0]
    print(s_id)
    member = members.find_one({'id': s_id})  # members의 s_id를 가지고 있는 다큐먼트

    count = member['submit_count']           # s_id를 가지고 있는 다큐먼트의 제출 횟수
    wcount = member['weekly_count']          # s_id를 가지고 있는 다큐먼트의 Weekly Survey 제출 여부
    daily_flag = member['daily_flag']        # s_id를 가지고 있는 다큐먼트의 하루 Daily Survey 제출 여부
    hcount = member['health_count']          # s_id를 가지고 있는 다큐먼트의 헬스   제출 횟수 for iOS
    gcount = member['gyro_count']            # s_id를 가지고 있는 다큐먼트의 각속도 제출 횟수 for iOS
    acount = member['acc_count']             # s_id를 가지고 있는 다큐먼트의 가속도 제출 횟수 for iOS
    fcount = member['attach_count']          # s_id를 가지고 있는 다큐먼트의 파일   제출 횟수 for Android
    
    if wcount > 0:
        return jsonify(render_template('weekly.html', sid=s_id, cnt=count, fcnt=fcount, wcnt=wcount))
    else:
        if daily_flag == 0:
            if member['daily'] == 1:
                return jsonify(render_template('android_daily.html', sid=s_id, cnt=count, fcnt=fcount))
            else:
                if member['daily'] == 2:
                    return jsonify(render_template('ios_daily.html', sid=s_id, cnt=count, hcnt=hcount, gcnt=gcount, acnt=acount))
        elif daily_flag == 1:
            flash("이미 설문을 완료하셨습니다. 내일 설문해주세요")
            return jsonify(render_template('login.html'))
        

# 설문 캘린더_ver en
@app.route('/ajax4_en', methods=['GET', 'POST'])
def ajax4_en():
    data = request.get_json()
    s_id = list(data.values())[0]
    print(s_id)
    member = members.find_one({'id': s_id})  # members의 s_id를 가지고 있는 다큐먼트

    count = member['submit_count']           # s_id를 가지고 있는 다큐먼트의 제출 횟수
    wcount = member['weekly_count']          # s_id를 가지고 있는 다큐먼트의 Weekly Survey 제출 여부
    daily_flag = member['daily_flag']        # s_id를 가지고 있는 다큐먼트의 하루 Daily Survey 제출 여부
    hcount = member['health_count']          # s_id를 가지고 있는 다큐먼트의 헬스   제출 횟수 for iOS
    gcount = member['gyro_count']            # s_id를 가지고 있는 다큐먼트의 각속도 제출 횟수 for iOS
    acount = member['acc_count']             # s_id를 가지고 있는 다큐먼트의 가속도 제출 횟수 for iOS
    fcount = member['attach_count']          # s_id를 가지고 있는 다큐먼트의 파일   제출 횟수 for Android
    
    if wcount > 0:
        return jsonify(render_template('weekly_en.html', sid=s_id, cnt=count, fcnt=fcount, wcnt=wcount))
    else:
        if daily_flag == 0:
            if member['daily'] == 1:
                return jsonify(render_template('android_daily_en.html', sid=s_id, cnt=count, fcnt=fcount))
            else:
                if member['daily'] == 2:
                    return jsonify(render_template('ios_daily_en.html', sid=s_id, cnt=count, hcnt=hcount, gcnt=gcount, acnt=acount))
        elif daily_flag == 1:
            flash("You have already completed the survey. please submit tomorrow")
            return jsonify(render_template('login_en.html'))

# 이전 파일 처리
@app.route('/justfile', methods=['POST'])
def justfile(): 
    data = request.files['data'] 
    st = data.read(); l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    date = evl['dt']
    member_id = members.find_one({'id': s_id})

    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]
    cin_count = member_id["CIN_count"]
    
    y, m, d = date.split('-')
    y = int(y); m = int(m); d = int(d)
    index = int(calIndexSearch(reg_m, reg_d, m, d))
    cal_list = member_id["cal_list"]

    if cal_list[index] == 0:
        if 'filed' in request.files:
            f = request.files['filed']
            print("file is", f)
            contents = f.read()
            fs = gridfs.GridFS(db, s_id)
            fname = f.filename
            members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
            fs.put(contents, filename=fname, attachDate=date)

            # 파일이 있어야만 색깔이 바뀌도록
            cal_list[index] = 1
            members.update_one({'id': s_id}, { '$set': {'cal_list': cal_list}})
        else:
            flash("파일을 제출해 주세요")
    else:
        flash("제출된 파일이 아니거나 제출이 가능한 날짜가 아닙니다.")
    
    return jsonify(render_template('calendar.html', sid=s_id, cin=cin_count, cal=cal_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))

# 이전 파일 처리 Eng ver
@app.route('/justfile_en', methods=['POST'])
def justfile_en(): 
    data = request.files['data'] 
    st = data.read(); l = st.decode()
    evl = eval(l)
    s_id = evl['sid']
    date = evl['dt']
    member_id = members.find_one({'id': s_id})

    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]
    cin_count = member_id["CIN_count"]
    
    y, m, d = date.split('-')
    y = int(y); m = int(m); d = int(d)
    index = int(calIndexSearch(reg_m, reg_d, m, d))
    cal_list = member_id["cal_list"]

    if cal_list[index] == 0:
        if 'filed' in request.files:
            f = request.files['filed']
            print("file is", f)
            contents = f.read()
            fs = gridfs.GridFS(db, s_id)
            fname = f.filename
            members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
            fs.put(contents, filename=fname, attachDate=date)

            # 파일이 있어야만 색깔이 바뀌도록
            cal_list[index] = 1
            members.update_one({'id': s_id}, { '$set': {'cal_list': cal_list}})
        else:
            flash("Please attach your file")
    else:
        flash("The file is not subitted or the date is not available for submission.") # Added 25 Aug 
    
    return jsonify(render_template('calendar_en.html', sid=s_id, cin=cin_count, cal=cal_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))


# 이전 설문 조사 Add 30 Aug
# 단순 redirecting
@app.route('/presurvey', methods=['POST'])
def presurvey():
    data = request.files['data'] 
    st = data.read(); l = st.decode(); evl = eval(l)
    s_id = evl['sid']; date = evl['dt']
    member_id = members.find_one({'id': s_id})

    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]
    daily_list = member_id["daily_list"]
    fcount = member_id['attach_count']
    count = member_id['submit_count']
    
    y, m, d = date.split('-')
    y = int(y); m = int(m); d = int(d)
    index = int(calIndexSearch(reg_m, reg_d, m, d))
    daily_list = member_id["daily_list"]

    if daily_list[index] == 0:
        return jsonify(render_template('previous_daily.html', sid=s_id, cnt=count, fcnt=fcount, dt=date)) # 이전 설문 화면으로 보내기

    else:
        flash("이미 해당 날짜의 설문을 진행하셨습니다.") # Added 30 Aug 

    return jsonify(render_template('daily_calendar.html', sid=s_id, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))

# 이전 설문 조사 Add 30 Aug
# 단순 redirecting Ver eng
@app.route('/presurvey_en', methods=['POST'])
def presurvey_en():
    data = request.files['data'] 
    st = data.read(); l = st.decode(); evl = eval(l)
    s_id = evl['sid']; date = evl['dt']
    member_id = members.find_one({'id': s_id})

    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]
    daily_list = member_id["daily_list"]
    fcount = member_id['attach_count']
    count = member_id['submit_count']
    
    y, m, d = date.split('-')
    y = int(y); m = int(m); d = int(d)
    index = int(calIndexSearch(reg_m, reg_d, m, d))
    daily_list = member_id["daily_list"]

    if daily_list[index] == 0:
        return jsonify(render_template('previous_daily_en.html', sid=s_id, cnt=count, fcnt=fcount, dt=date)) # 이전 설문 화면으로 보내기

    else:
        flash("You have already completed the survey for that date.") # Added 30 Aug 

    return jsonify(render_template('daily_calendar_en.html', sid=s_id, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))


# 지난 설문 처리
@app.route('/lastsurvey', methods=['POST'])
def lastsurvey(): 
    data = request.files['data'] 
    st = data.read()
    l = st.decode()
    evl = eval(l)
    mood = evl['mood']
    s_id = evl['sid']
    date = evl['dt']
    member_id = members.find_one({'id': s_id})

    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]
    daily_list = member_id["daily_list"]

    y, m, d = date.split('-')
    y = int(y); m = int(m); d = int(d)
    index = int(calIndexSearch(reg_m, reg_d, m, d))
    daily_list = member_id["daily_list"]
        
    if daily_list[index] == 0: # 인덱스에 해당하는 값이 0 이어야만
        members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
        md = { "mood": mood , "date": date }
        survey_coll = mongo.db.get_collection(s_id)
        survey_coll.insert_one(md)

        daily_list[index] = 1
        members.update_one({'id': s_id}, { '$set': {'daily_list': daily_list}})
        members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}})

    else:
        flash("이미 제출한 날짜입니다.")

    return jsonify(render_template('daily_calendar.html', sid=s_id, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))
    

# 지난 설문 처리 Ver eng
@app.route('/lastsurvey_en', methods=['POST'])
def lastsurvey_en(): 
    data = request.files['data'] 
    st = data.read()
    l = st.decode()
    evl = eval(l)
    mood = evl['mood']
    s_id = evl['sid']
    date = evl['dt']
    member_id = members.find_one({'id': s_id})

    reg_y = member_id["register_year"]
    reg_m = member_id["register_month"]
    reg_d = member_id["register_day"]
    daily_list = member_id["daily_list"]

    y, m, d = date.split('-')
    y = int(y); m = int(m); d = int(d)
    index = int(calIndexSearch(reg_m, reg_d, m, d))
    daily_list = member_id["daily_list"]
        
    if daily_list[index] == 0: # 인덱스에 해당하는 값이 0 이어야만
        members.update_one({'id': s_id}, {'$inc': {'attach_count': 1}})
        md = { "mood": mood , "date": date }
        survey_coll = mongo.db.get_collection(s_id)
        survey_coll.insert_one(md)

        daily_list[index] = 1
        members.update_one({'id': s_id}, { '$set': {'daily_list': daily_list}})
        members.update_one({'id': s_id}, {'$inc': {'submit_count': 1}})

    else:
        flash("Date already submitted.")

    return jsonify(render_template('daily_calendar_en.html', sid=s_id, dai=daily_list, reg_y=reg_y, reg_m=reg_m, reg_d=reg_d))

#팝업창
@app.route('/pop.html', methods=['GET'])
def window_pop():
    return render_template("pop.html")

#팝업창_영어
@app.route('/pop_en.html', methods=['GET'])
def window_pop_en():
    return render_template("pop_en.html")

#세션 유지
@app.before_request
def make_session_permanent():
    session.permanent = True
    #10분 후 세션 만료
    app.permanent_session_lifetime = timedelta(minutes=1)

#백그라운드 실행
asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
today = asia_seoul.strftime("%Y%m%d")

def count(): # function for increasing weekly_count
    asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
    t = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    now = t[asia_seoul.today().weekday()]
    print(now)
    if now == '토요일':
        members.update_many({}, {'$inc': {'weekly_count': 1}}) #collection에 있는 모든 id에서 count가 1씩 증가

def countCIN(name, aeName, today): #모비우스 cnt 개수 가져오기
    cra = datetime.datetime.strptime(today, "%Y%m%d")
    cra = cra - timedelta(1)
    cra = '&cra=' + cra.strftime("%Y%m%d") + 'T150000'
    crb = '&crb=' + today + 'T145959'
    
    url1 = IoT_1 + "/Mobius/" + aeName + "/mobile?fu=1&ty=4&rcn=4" + cra + crb
    url2 = IoT_1 + "/Mobius/" + aeName + "/watch?fu=1&ty=4&rcn=4"  + cra + crb
    payload={}
    headers = {
        'Accept': 'application/json',
        'X-M2M-RI': '12345',
        'X-M2M-Origin': 'ubicomp_super'
    }
    try:
        response1 = requests.request("GET", url1, headers=headers, data=payload)
        response2 = requests.request("GET", url2, headers=headers, data=payload)
        data1 = json.loads(response1.text)
        data2 = json.loads(response2.text)
        total = len(data1['m2m:uril'])
        total = total + len(data2['m2m:uril'])
        return total

    except:
        return None

def getCountDict(today): # Count number of container in Mobius Server
    dict_CIN = {}
    # f = open('./log/daily_cin_count.txt', 'a+')
    for i in range(0, 1000):
        aeName = str(i)

        if len(aeName) == 1:
            aeName = '00' + aeName
        elif len(aeName) == 2:
            aeName = '0' + aeName
        
        aeName = 'S' + aeName
        cnt = countCIN('IoT_1', aeName, today)
        

        if cnt == None:
            continue
        else:
            dict_CIN[aeName] = cnt
            
    for k,v in dict_CIN.items():
        k=str(k)
        v=int(v)
        member_id = members.find_one({'id': k})
        members.update_one({'id':k}, {'$set':{'CIN_count':v}})
        if member_id != None :
            cin_count = member_id["CIN_count"]
            print(cin_count)
            if cin_count < 143:
                members.update_one({'id': k}, {'$push': {'cal_list':0}})
                continue
            else:
                if cin_count >= 143:
                    members.update_one({'id': k}, {'$push': {'cal_list':1}})
                    continue
    return dict_CIN

def dailyCheck(): 
    docs = members.find()
    for i in docs:
        member_id = members.find_one({'id': i["id"]})
        if member_id != None :
            daily_flag = member_id["daily_flag"]
            if daily_flag == 0:
                members.update_one({'id': i["id"]}, {'$push': { 'daily_list': 0 }})
            else:
                if daily_flag == 1:
                    members.update_one({'id': i["id"]}, {'$push': { 'daily_list': 1 }})
                    members.update_one({'id':i["id"]}, {'$set':{ 'daily_flag': 0 }})
                    
    
if __name__ == '__main__':
    
    sched = BackgroundScheduler(daemon=True)
    asia_seoul = datetime.datetime.fromtimestamp(time.time(), pytz.timezone('Asia/Seoul'))
    today = asia_seoul.strftime("%Y%m%d")

    sched.add_job(count, 'cron', hour="05", minute="01", id="test_1") # 토요일 주간 설문 확인
    sched.add_job(dailyCheck, 'cron', hour="05", minute="30", id="test_3") # 매일 설문조사 했는지 체크
    sched.add_job(getCountDict, 'cron', hour="00", minute="05", id="test_2", args=[today]) # 매일 사용자에 대한 데이터 수 GET
    
    sched.start()

    app.run(host='0.0.0.0', port=2017)
