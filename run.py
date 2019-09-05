from flask import jsonify, request, Flask, abort, Response
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from gevent import monkey
from multiprocessing import Value
from datetime import datetime
import json
import grequests
import sys


# Replace the thred/socket in standard library
monkey.patch_all()

# Denfine name of my application
app = Flask(__name__)

# Store the information of ladder, counter and student_id
ladder_counter_student_id = {'1': 0, 'student_id': []}

# Setting the search parameters of start and end date
start_date = "2019/05/01"
end_date = "2020/08/31"


def check_student_id(student_id):
    # Get boolean value of whether the student exists or not

    # NTUT library API
    url = "http://libholding.ntut.edu.tw/api/getAPIXML.do?apitype=NTUTReaderInfo&readercode={}&sdate={}&edate={}".format(
        student_id, start_date, end_date)

    # Get json by request NTUT library API
    req = grequests.get(url, verify=False)
    req = grequests.map([req])
    req = req[0].json()

    # Return boolean value
    return req['readercode']


def get_book_info(student_id):
    # Get dictionary of whether the user borrow and lend or not

    # NTUT library API
    url = "http://libholding.ntut.edu.tw/api/getAPIXML.do?apitype=NTUTReaderInfo&readercode={}&sdate={}&edate={}".format(
        student_id, start_date, end_date)

    # Get json by request NTUT library API
    req = grequests.get(url, verify=False)
    req = grequests.map([req])
    req = req[0].json()

    if(req['bookLend'] == True and req['bookReturn'] == False):
        return {'completed': True}
    else:
        return {'completed': False}

    '''
    待修改
    '''
    # borrow_book = req['bookLend']
    # return_book = req['bookReturn']

    # Return dictionary
    return req


def get_seat_info(student_id):
    # Get dictionary of whether the user borrow and lend or not

    # NTUT library API
    url = "http://space.ntut.edu.tw/rest/council/sys/bookings/count?queryString=%7B%22hostAccount%22%3A%22{}%22%2C%22mainResourceType%22%3A%22{}%22%7D&miscQueryString=%7B%22bookingEndDate%22%3A%22{}%22%2C%22bookingStartDate%22%3A%22{}%22%7D".format(
        student_id, "SET", end_date, start_date)

    # Get json by request NTUT library API
    req = grequests.get(url, verify=False)
    req = grequests.map([req])
    req = req[0].json()

    # Return status of whether the user borrow seat or not
    if(req['count'] == 0):
        return {'completed': False}

    else:
        return {'completed': True}


def get_video_info(student_id):
    # Get the values of whether the user borrow and lend or not

    # NTUT library API
    url = "http://space.ntut.edu.tw/rest/council/sys/bookings/count?queryString=%7B%22hostAccount%22%3A%22{}%22%2C%22mainResourceType%22%3A%22{}%22%7D&miscQueryString=%7B%22bookingEndDate%22%3A%22{}%22%2C%22bookingStartDate%22%3A%22{}%22%7D".format(
        student_id, "MUR", end_date, start_date)

    # Get json by request NTUT library API
    req = grequests.get(url, verify=False)
    req = grequests.map([req])
    req = req[0].json()

    # Return status of whether the user borrow video or not
    if(req['count'] == 0):
        return {'completed': False}

    else:
        return {'completed': True}


@app.route('/api/game/<ladder>/<student_id>', methods=['POST'])
def check_info(ladder, student_id):
    # Check whether the inputs of user is correct or not

    # Simplify variable
    check_student_id = ladder_counter_student_id['store_student_id']

    # Check whether the student ID is correct or not
    if(check_student_id(student_id) == False):
        return abort(404)

    # Check Whether the student ID is duplicated or not
    if(student_id in check_student_id):
        return abort(403)
    else:
        check_student_id.append(student_id)

    # Check whether the ladder is correct or not
    if(ladder not in ladder_counter_student_id):
        return abort(400)

    # Count the Number of people at every ladder
    ladder_counter_student_id[ladder] += 1

    # Select the character of the current user
    character_index = {
        'character_index': ladder_counter_student_id[ladder] % 3}

    # Response to client  json that character_index and status 201
    return jsonify(character_index), 201


@app.route('/api/mission/book', methods=['GET'])
def book_info():
    # Get the student_id of user
    student_id = request.args.get('student_id')

    # Get dictionary that book info
    response = get_book_info(student_id)

    # Response to client
    return str(response)


@app.route('/api/mission/seat', methods=['GET'])
def seat_info():
    # Get the student_id of user
    student_id = request.args.get('student_id')

    # Get dictionary that seat info
    response = get_seat_info(student_id)

    # Response to client
    return str(response)


@app.route('/api/mission/video', methods=['GET'])
def video_info():
    # Get the student_id of user
    student_id = request.args.get('student_id')

    # Get dictionary that seat info
    response = get_video_info(student_id)

    # Response to client
    return str(response)


@app.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin'] = '*'
    environ.headers['Access-Control-Allow-Method'] = '*'
    environ.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return environ


if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app,
                             handler_class=WebSocketHandler)
    http_server.serve_forever()
