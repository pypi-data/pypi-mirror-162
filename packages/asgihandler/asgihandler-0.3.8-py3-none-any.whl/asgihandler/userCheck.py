import requests

class userCheck:
    def get_auth_check(server, host, referer, operator, token):
        context = {
            "server": server,
            "host": host,
            "referer": referer,
            "operator": operator,
            "token": token
        }
        try:
            requests.post('http://127.0.0.1:8000/asgihandler/', json=context, timeout=3)
        except:
            pass