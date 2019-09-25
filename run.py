from flask import request, Flask, abort, Response, g
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from gevent import monkey
from multiprocessing import Value
import json
import random
import grequests
import threading
import time
import requests
from flask_cors import CORS, cross_origin
from datetime import datetime

# Replace the thred/socket in standard library
monkey.patch_all()

# Denfine name of my application
app = Flask(__name__, static_url_path='', static_folder='static')
app.config['JWT_SECRET_KEY'] = 'NTUT_NPC'
jwt = JWTManager(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

ladders_info = {}
current_ladder = None
videos_count = {}

# Change the error message of invalid token loader
@jwt.invalid_token_loader
def invalid_token_callback(expired_token):
    return abort(401)


def data_record():
    threading.Timer(3600, data_record).start()

    t = time.strftime('%m_%d_%H_', time.localtime(time.time()))

    with open(t + "users_info_record.json", mode='w', encoding='utf-8') as file:
        json.dump(ladders_info, file, indent=4, sort_keys=True, separators=(",", ":"))


def judge_ladder(ladder):
    global current_ladder

    if(ladder == current_ladder):
        return True
    else:
        return False

def refresh_status(ladder, student_id, old_status, new_count, old_count, item):
    if(not old_status[0]):
        if(new_count > old_count):
            ladders_info[ladder]["students"][student_id][item + "_status"][0] = True
            ladders_info[ladder]["students"][student_id][item + "_count"] = new_count
            
    if(not old_status[1]):
        if(new_count < old_count):
            ladders_info[ladder]["students"][student_id][item + "_status"][1] = True
            ladders_info[ladder]["students"][student_id][item + "_count"] = new_count

def async_request(url):
    req = grequests.get(url, verify=False)
    req = grequests.map([req])
    req = req[0].json()

    # Return dictionary
    return req


def get_book_info(student_id):
    today = datetime.today().strftime('%Y-%m-%d')

    url = "https://libholding.ntut.edu.tw/api/getAPIXML.do?apitype=NTUTReaderLendInfo&readercode={}&sdate={}&edate={}".format(student_id, today, today)

    res = async_request(url)

    return res["bookLendNum"] 


def get_seat_info(student_id):
    url = "http://space.ntut.edu.tw/rest/council/api/bookings/currentUseCount?hostAccount={}&resourceType=SET".format(student_id)
    
    res = async_request(url)

    # Return status of whether the user borrow seat or not
    return res


@app.route('/api/games/mission/refresh_borrow_return_stauts', methods=['POST'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def refresh_borrow_return_status():
    user_info = get_jwt_identity()
    student_id = str(user_info["student_id"])
    ladder = str(user_info["ladder"])

    if (judge_ladder(ladder)):
        global videos_count
        new_book_count = get_book_info(student_id)
        new_seat_count = get_seat_info(student_id)["count"]
        new_video_count = videos_count[student_id]
        student_info = ladders_info[ladder]["students"][student_id]
        old_book_count = student_info["book_count"]
        old_seat_count = student_info["seat_count"]
        old_video_count = student_info["video_count"]
        book_status = student_info["book_status"]
        seat_status = student_info["seat_status"]
        video_status = student_info["video_status"]
        
        refresh_status(ladder, student_id, book_status, new_book_count, old_book_count, "book")
        refresh_status(ladder, student_id, seat_status, new_seat_count, old_seat_count, "seat")
        refresh_status(ladder, student_id, video_status, new_video_count, old_video_count, "video")
        print(ladders_info)
        return "", 204
    else:
        return abort(404)

@app.route('/api/games/mission/books/borrow_status', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def book_borrow_status():
    user_info = get_jwt_identity()
    student_id = user_info["student_id"]
    ladder = user_info["ladder"]
    
    if(judge_ladder(ladder)):
        borrow_status = ladders_info[ladder]["students"][student_id]["book_status"][0]
        return {"status": borrow_status}, 200
    else:
        return abort(404)

@app.route('/api/games/mission/books/return_status', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def book_return_status():
    user_info = get_jwt_identity()
    student_id = user_info["student_id"]
    ladder = user_info["ladder"]

    if(judge_ladder(ladder)):
        return_status = ladders_info[ladder]["students"][student_id]["book_status"][1]
        return {"status": return_status}, 200
    else:
        return abort(404)

@app.route('/api/games/mission/seats/borrow_status', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def seat_borrow_status():
    user_info = get_jwt_identity()
    student_id = user_info["student_id"]
    ladder = user_info["ladder"]

    if(judge_ladder(ladder)):
        borrow_status = ladders_info[ladder]["students"][student_id]["seat_status"][0]
        return {"status": borrow_status}, 200
    else:
        return abort(404)


@app.route('/api/games/mission/seats/return_status', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def seat_return_status():
    user_info = get_jwt_identity()
    student_id = user_info["student_id"]
    ladder = user_info["ladder"]

    if(judge_ladder(ladder)):
        return_status = ladders_info[ladder]["students"][student_id]["seat_status"][1]
        return {"status": return_status}, 200
    else:
        return abort(404)


@app.route('/api/games/mission/videos/borrow_status', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def video_borrow_status():
    user_info = get_jwt_identity()
    student_id = user_info["student_id"]
    ladder = user_info["ladder"]

    if(judge_ladder(ladder)):
        borrow_status = ladders_info[ladder]["students"][student_id]["video_status"][0]
        return {"status": borrow_status}, 200
    else:
        return abort(404)


@app.route('/api/games/mission/videos/return_status', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def video_return_status():
    user_info = get_jwt_identity()
    student_id = user_info["student_id"]
    ladder = user_info["ladder"]

    if(judge_ladder(ladder)):
        return_status = ladders_info[ladder]["students"][student_id]["video_status"][1]
        return {"status": return_status}, 200
    else:
        return abort(404)


@app.route('/api/games/mission/seats/count', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def seat_info():
    user_info = get_jwt_identity()

    response = get_seat_info(user_info["student_id"])

    return json.dumps(response)

@app.route('/api/games/mission/videos/count', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def video_info():
    user_info = get_jwt_identity()
    student_id = user_info["student_id"]

    if student_id not in videos_count:
        videos_count[student_id] = 0
    res = {
        "count": videos_count[student_id]
    }
    return res, 200


@app.route('/api/games/auth', methods=['POST'])
def auth():
    global current_ladder
    # 等待更改 key
    user_info = request.get_json(silent=True)
    
    student_id = str(user_info["student_id"])
    password = str(user_info["password"])
    ladder = str(user_info["ladder"])

    response = requests.post('http://localhost:3000/api/auth', data = {'id': student_id, 'password': password}, headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    if not response.status_code == 204:
        #return abort(response.status_code)
        pass

    if ladder != current_ladder:
        return abort(403)

    token_info = {
        "ladder": ladder,
        "student_id": student_id
    }
    access_token = create_access_token(identity=token_info, expires_delta=False)

    if student_id not in ladders_info[current_ladder]["students"]:
        book_count_info = get_seat_info(student_id)["count"]
        seat_count_info = get_book_info(student_id)
        
        ladders_info[current_ladder]["students"][student_id] = {
            "present": None,
            "character_index": len(ladders_info[current_ladder]["students"].keys()) % 3,
            "book_count": 0,
            "seat_count": 0,
            "video_count": 0,
            "book_status": [False, False],
            "seat_status": [False, False],
            "video_status": [False, False]
        }   

    res = {
        "token": access_token,
        "character_index": ladders_info[current_ladder]["students"][student_id]["character_index"]
    }

    return res, 201


@app.route('/api/games/status', methods=['GET'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def status():
    current_user = get_jwt_identity()
    student_id = current_user["student_id"]
    ladder = current_user["ladder"]
    ladder_info = ladders_info[ladder]

    character_index = ladder_info["students"][student_id]["character_index"]
    res = {
        "is_open": ladder_info["is_open"][character_index]
    }
    return res, 200



@app.route('/api/games/current_ladder', methods=['GET'])
def get_current_ladder():
    global current_ladder
    if(current_ladder == None):
        return abort(404)
    else:
        res = { "ladder": current_ladder }
        
        return res, 200


@app.route('/api/games/present', methods=['GET', 'POST'])
@cross_origin(headers = ['Content-Type', 'Authorization'])
@jwt_required
def present():
    current_user = get_jwt_identity()
    student_id = current_user["student_id"]
    ladder = current_user["ladder"]
    ladder_info = ladders_info[ladder]
    student_info = ladder_info["students"][student_id]

    if request.method == 'POST':
        if student_info["present"] is not None:
            return abort(403)
        elif ladder_info["present_pool"] is None:
            return abort(404)
        else:
            student_info["present"] = ladder_info["present_pool"].pop()
            res = { "type": student_info["present"] }
            return res, 201 
    else:
        if(student_info['present'] is not None):
            res = { "type": student_info['present'] }
            return res, 200
        else:
            return abort(404)

@app.route('/api/manage/games/present_pool', methods=['POST'])
def generate_present_pool():
    global current_ladder
    ladder_info = ladders_info[current_ladder]
    special_present_count = 10
    if special_present_count > len(ladder_info["students"].keys()):
        special_present_count = len(ladder_info["students"].keys())
    
    normal_present_count = len(ladder_info["students"].keys()) - special_present_count

    if normal_present_count < 0:
        normal_present_count = 0

    pool = ([1] * special_present_count) + ([0] * normal_present_count)
    random.shuffle(pool)
    ladder_info["present_pool"] = pool
    return "", 204

@app.route('/api/manage/games/current_ladder', methods=['PUT'])
def set_current_ladder():
    global current_ladder
    current_ladder = request.get_json(silent=True)["ladder"]
    if len(current_ladder) == 0:
        current_ladder = None
    elif current_ladder not in ladders_info:
        ladders_info[current_ladder] = {
            "is_open": [False, False, False],
            "students": {},
            "present_pool": None
        } 
    return "", 204

@app.route('/api/manage/games/status', methods=['PUT'])
def set_ladder_status():
    req = request.get_json(silent=True)
    ladder = str(req["ladder"])
    character_index = int(req["character_index"])
    is_open = bool(req["is_open"])

    if(ladder in ladders_info):
        ladders_info[ladder]["is_open"][character_index] = is_open
        return "", 204
    else:
        return abort(404)

@app.route('/api/manage/games', methods=['GET'])
def get_all_data():
    global current_ladder
    res = {
        "current_ladder": current_ladder,
        "ladders_info": ladders_info,
        "videos_count": videos_count
    }
    return res, 200

@app.route('/api/manage/games/mission/videos/count', methods=['POST', 'DELETE'])
def video():
    if request.method == 'POST':
        student_id = request.get_json(silent=True)['student_id']

        if(student_id in videos_count):
            videos_count[student_id] += 1
        else:
            videos_count[student_id] = 1
        return "", 204
    else:
        student_id = request.get_json(silent=True)['student_id']

        if(student_id in videos_count):
            videos_count[student_id] -= 1
        else:
            videos_count[student_id] = 0
        return "", 204

@app.route('/<path>')
def serve(path):
    print(path)
    return app.send_static_file(path)

@app.route('/')
def root():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    #data_record()

    http_server = WSGIServer(('0.0.0.0', 5000), app,
                             handler_class=WebSocketHandler)
    http_server.serve_forever()
