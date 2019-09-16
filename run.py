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

# Replace the thred/socket in standard library
monkey.patch_all()

# Denfine name of my application
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'NTUT_NPC'
jwt = JWTManager(app)

ladders_info = {}
current_ladder = {
    "ladder": None
}
videos_count = {}

# Change the error message of invalid token loader
@jwt.invalid_token_loader
def invalid_token_callback(expired_token):
    return abort(401)


def data_record():
    threading.Timer(3600, data_record).start()

    t = time.strftime('%m_%d_%H_', time.localtime(time.time()))

    with open(t + "users_info_record.json", mode='w', encoding='utf-8') as file:
        json.dump(ladders_info, file, indent=4,
                  sort_keys=True, separators=(",", ":"))


# def user_info_record(ladder, student_id, lottery, character_index):
#     with open("user_info_record.json", mode='r', encoding='utf-8') as file:
#         ladders_info = json.load(file)

#     with open("user_info_record.json", mode='w', encoding='utf-8') as file:
#         user_info = {student_id: {
#             "lottery": lottery,
#             "character_index": character_index
#         }}

#         if(ladder not in ladders_info):
#             ladders_info[ladder] = {}

#         ladders_info[ladder].update(user_info)

#         json.dump(ladders_info, file, indent=4,
#                   sort_keys=True, separators=(",", ":"))


def generate_lottery_pool(ladder):
    # Number of special awards
    award_count = 15
    pool = [1] * award_count + \
        ([0] * (len(ladders_info[ladder]) - award_count))
    random.shuffle(pool)
    return pool


def async_request(url):
    req = grequests.get(url, verify=False)
    req = grequests.map([req])
    req = req[0].json()

    # Return dictionary
    return req

# def get_book_info(student_id):
    # 待更改
    # NTUT library API
    # start_date = "2019/09/17"
    # end_date = "2020/09/17"

    # url = "http://libholding.ntut.edu.tw/api/getAPIXML.do?apitype=NTUTReaderInfo&readercode={}&sdate={}&edate={}".format(
    #     student_id, start_date, end_date)

    # response = async_request(url)

    # bookReturn = response["bookReturn"]
    # bookLend = response["bookLend"]

    # if not bookLend:
    #     return {"count": 0}
    # elif bookLend and not bookReturn:
    #     return {"count": 1}
    # else:
    #     return {"count": 0}


def get_seat_info(student_id):
    # 待更改
    # NTUT library API
    url = "http://space.ntut.edu.tw/rest/council/api/bookings/currentUseCount?hostAccount={}&resourceType=SET".format(
        student_id)

    req = async_request(url)

    # Return status of whether the user borrow seat or not
    return req


@app.route('/api/games/mission/books/count', methods=['GET'])
@jwt_required
def book_info():
    user_info = get_jwt_identity()

    # 待用 404
    # 待改 API
    # response = get_book_info(user_info["student_id"])

    # return json.dumps(response, indent=4)
    return json.dumps({"test": "test"})


@app.route('/api/games/mission/seats/count', methods=['GET'])
@jwt_required
def seat_info():
    user_info = get_jwt_identity()

    # 待用 404
    # 待改 API
    response = get_seat_info(user_info["student_id"])

    return json.dumps(response, indent=4)


@app.route('/api/games/mission/videos/count', methods=['GET'])
@jwt_required
def video_info():
    user_info = get_jwt_identity()
    student_id = user_info["student_id"]

    if student_id not in videos_count:
        videos_count[student_id] = 0
    return json.dumps({
        "count": videos_count[student_id]
    }, indent=4)


@app.route('/api/games/auth', methods=['POST'])
def auth():

    # 等待更改 key
    user_info = dict(request.form)
    student_id = user_info["student_id"]
    ladder = user_info["ladder"]

    # 向威任的後端驗證
    # if 登入成功
    # return jwt
    # else return 401

    user_info = {}

    user_info[student_id] = {
        "lottery": None,
        "character_index": 0,
        "game_data": {
            "current_chapter_index": 0,
            "current_stage_index": 0,
            "inventory": []
        }
    }

    if ladder in ladders_info:
        ladders_info[ladder].update(user_info)
    else:
        ladders_info[ladder] = {}
        ladders_info[ladder].update(user_info)

    ladders_info[ladder][student_id]["character_index"] = (
        len(ladders_info[ladder])-1) % 2

    token_info = {
        "ladder": ladder,
        "student_id": student_id
    }

    access_token = create_access_token(identity=token_info)
    return json.dumps({
        "token": access_token
    }, indent=4), 201


@app.route('/api/games/save', methods=['GET', 'PATCH'])
@jwt_required
def game_save():
    current_user = get_jwt_identity()
    student_id = current_user["student_id"]
    ladder = current_user["ladder"]

    if request.method == 'PATCH':
        ladders_info[ladder][student_id]["game_data"]
    else:
        return ladders_info[ladder][student_id]["game_data"]


@app.route('/api/games/status', methods=['GET'])
@jwt_required
def status():
    current_user = get_jwt_identity()
    student_id = current_user["student_id"]
    ladder = current_user["ladder"]
    ladder_info = ladders_info[ladder]

    character_index = str(ladder_info[student_id]["character_index"])
    is_open = ladder_info["is_open"][character_index]

    return json.dumps({
        "is_open": bool(is_open)
    }, indent=4)


@app.route('/api/games/current_ladder', methods=['GET'])
def get_current_ladder():
    if(current_ladder["ladder"] == ""):
        return 404
    else:
        return json.dumps(current_ladder, indent=4), 200


@app.route('/api/games/present', methods=['GET', 'POST'])
@jwt_required
def present():
    current_user = get_jwt_identity()
    student_id = current_user["student_id"]
    ladder = current_user["ladder"]
    student_info = ladders_info[ladder][student_id]

    if request.method == 'POST':
        if student_info["lottery"] is not None:
            return "", 403
        elif "is_lottery" in ladders_info[ladder]:
            ladders_info[ladder][student_id]['lottery'] = 0

            return json.dumps({
                "type": 0
            }, indent=4)
        else:
            pool = generate_lottery_pool(ladder)
            ladders_info_temp = ladders_info
            # Give award for all student
            for local_student_id, award in ladders_info_temp[ladder].items():
                if(not local_student_id == "is_open"):
                    ladders_info_temp[ladder][local_student_id]['lottery'] = pool[0]
                    pool.pop(0)

            ladders_info[ladder]["is_lottery"] = True

            return json.dumps({
                "type": ladders_info[ladder][student_id]['lottery']
            }, indent=4)

    else:
        if(student_info['lottery'] != None):
            lottery = student_info['lottery']
            return json.dumps({
                'type': lottery
            }, indent=4)

        else:
            return abort(404)


@app.route('/api/manage/games/current_ladder', methods=['PUT'])
def set_current_ladder():
    current_ladder["ladder"] = request.form["ladder"]
    return "", 204


@app.route('/api/manage/games/status', methods=['PUT'])
def set_ladder_status():
    req = dict(request.form)
    ladder = req["ladder"]
    character_index = req["character_index"]
    is_open = req["is_open"]

    if(ladder in ladders_info):
        if("is_open" not in ladders_info[ladder]):
            ladders_info[ladder]["is_open"] = {
                "0": False,
                "1": False,
                # "2": False
            }

        ladders_info[ladder]["is_open"][character_index] = bool(is_open)
        return "", 204
    else:
        return abort(404)


@app.route('/api/manage/games/mission/videos/count', methods=['POST', 'DELETE'])
def video():
    if request.method == 'POST':
        student_id = request.form['student_id']

        if(student_id in videos_count):
            videos_count[student_id] += 1
        else:
            videos_count[student_id] = 1
        return "", 204
    else:
        student_id = request.form['student_id']

        if(student_id in videos_count):
            videos_count[student_id] -= 1
        else:
            videos_count[student_id] = 0
        return "", 204


@app.route('/<path>')
def provide(path):
    print(path)
    return app.send_static_file(path)


@app.route('/')
def home():
    return app.send_static_file('index.html')


@app.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin'] = '*'
    environ.headers['Access-Control-Allow-Method'] = '*'
    environ.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return environ


if __name__ == '__main__':
    data_record()

    http_server = WSGIServer(('0.0.0.0', 5000), app,
                             handler_class=WebSocketHandler)
    http_server.serve_forever()
