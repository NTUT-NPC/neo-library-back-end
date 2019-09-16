import requests
import jwt
import json
import time


host = "http://127.0.0.1:5000/"
token = ""


# 驗證
def auth():
    global token
    url = host + "api/games/auth"

    data = {
        "student_id": "106300125",
        "password": "c121212c",
        "ladder": "108/09/14"
    }

    response = requests.request("post", url, data=data)
    token = json.loads(response.text)["token"]

    print(response)
    print(response.text)

    # Output:
    # <Response [201]>
    # {
    #     "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Njg0NjU5MzAsIm5iZiI6MTU2ODQ2NTkzMCwianRpIjoiZTA0N2I0NTAtZWI4ZC00NzI1LTk0YzQtNjQ0YjNiZDkxZGVmIiwiZXhwIjoxNTY4NDY2ODMwLCJpZGVudGl0eSI6eyJsYWRkZXIiOiIxMDgvMDkvMTQiLCJzdHVkZW50X2lkIjoiMTA2MzAwMTI0In0sImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.P0_WWp5ldoGQVwxbMTld2p37l-xPHvYDMIDDS-HjXHI"
    # }


# 設定目前梯次的代號
def set_current_ladder():
    url = host + "api/manage/games/current_ladder"

    data = {
        "ladder": "108/09/14"
    }

    response = requests.request("put", url, data=data)

    print(response)

    # Output:
    # <Response [204]>


# 取得目前梯次代號
def get_current_ladder():
    url = host + "/api/games/current_ladder"

    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.request("get", url, headers=headers)

    print(response)
    print(response.text)


# 設定角色的開放狀態
def set_game_status():
    url = host + "api/manage/games/status"

    data = {
        "ladder": "108/09/14",
        "character_index": 0,
        "is_open": True
    }

    response = requests.request("put", url, data=data)

    print(response)

    # Output:
    # <Response [204]>


# 取得角色的開放狀態
def get_game_status():
    url = host + "/api/games/status"

    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.request("get", url, headers=headers)

    print(response)
    print(response.text)

    # Output:
    # <Response [200]>
    # {
    #     "is_open": "True"
    # }


# 待圖書館更改 API
# 取得借書數量
def get_book_count():
    url = host + "/api/games/mission/books/count"

    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.request("get", url, headers=headers)

    print(response)
    print(response.text)

    # Output:
    # <Response [200]>
    # ...


# 取得座位資訊
def get_seat_count():
    url = host + "/api/games/mission/seats/count"

    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.request("get", url, headers=headers)

    print(response)
    print(response.text)

    # Output:
    # <Response [200]>
    # ...

# 取得光碟資訊


def get_video_count():
    url = host + "/api/games/mission/videos/count"

    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.request("get", url, headers=headers)

    print(response)
    print(response.text)

    # Output:
    # <Response [200]>
    # ...


def add_video_count():
    url = host + "/api/manage/games/mission/videos/count"
    data = {
        "student_id": "106300124"
    }

    response = requests.request("post", url, data=data)

    print(response)


def delete_video_count():
    url = host + "/api/manage/games/mission/videos/count"
    data = {
        "student_id": "106300124"
    }

    response = requests.request("delete", url, data=data)

    print(response)


def lottery():
    url = host + "/api/games/present"

    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.request("post", url, headers=headers)

    print(response)
    print(response.text)


def get_lottery():
    url = host + "/api/games/present"

    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.request("get", url, headers=headers)

    print(response)
    print(response.text)


auth()
set_current_ladder()
get_current_ladder()
set_game_status()
get_game_status()
get_book_count()
get_seat_count()
get_video_count()
add_video_count()
delete_video_count()
lottery()
get_lottery()
