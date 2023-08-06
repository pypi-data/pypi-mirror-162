

def run(username, password):
    import requests
    import random
    import uuid

    gok = uuid.uuid1()
    url = "https://i.instagram.com/api/v1/accounts/login/"
    response = requests.post('https://i.instagram.com/api/v1/accounts/login/').cookies
    user00 = '1234567890'
    us1 = str("".join(random.choice(user00) for i in range(int(1))))
    us2 = str("".join(random.choice(user00) for i in range(int(1))))
    us3 = str("".join(random.choice(user00) for i in range(int(1))))
    us7 = str("".join(random.choice(user00) for i in range(int(1))))
    user000 = 'qwertyuiopasdfghjklzxcvbnm'
    us4 = str("".join(random.choice(user000) for i in range(int(1))))
    us5 = str("".join(random.choice(user000) for i in range(int(1))))
    us6 = str("".join(random.choice(user000) for i in range(int(1))))
    us8 = str("".join(random.choice(user000) for i in range(int(1))))
    csrf = response['csrftoken']
    mid = response['mid']
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'i.instagram.com',
        'Connection': 'Keep-Alive',
        'User-Agent': 'Instagram 6.12.1 Android (25/7.1.2; 160dpi; 383x680; LENOVO/Android-x86; 4' + us1 + us3 + us7 + us4 + us5 + us2 + '; x86_64; android_x86_64; en_US)',
        'Cookie': 'mid=' + mid + '; csrftoken=' + csrf,
        'Cookie2': 'Version=1',
        'Accept-Language': 'en-US',
        'X-IG-Connection-Type': 'WIFI',
        'X-IG-Capabilities': 'AQ==',
    }
    data = {
        'ig_sig_key_version': '4',
        'signed_body': 'a11515fe' + us4 + '5816ac216fa36' + us1 + '3387025' + us8 + '28c5ec14d563fd60eb9d5ca9eea6d8d' + us2 + '7.{"username":"' + username + '","password":"' + password + '","device_id":"android-ad2d1a' + us4 + 'b' + us3 + '8' + us1 + 'a4' + us2 + '5e","guid":"' + str(
            gok) + '","_csrftoken":"' + csrf + '"}',
    }
    reqq = requests.post(url, data=data, headers=headers)
    return reqq
