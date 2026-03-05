import requests
import time

wait = 0.7

# 视频长度, 单位 s, 这里默认 30min
d = 2000  
# 用户 ID
u = 1145141919810
# 课程 ID
c = 1145141919810
# 库存量单位 ID
skuid = 1145141919810
# 课程代码
cc = '1145141919810'
# 学校 + 课程 ID
school_course_id = '1145141919810'
# 课程 ID
classroomid = '1145141919810'  

# X-Csrftoken
X_Csrftoken = '1145141919810'  
# Cookie
Cookie = '1145141919810'

# 第一节课 ID
video_start = 1145141919810
# 最后一节课 ID  
video_end = 1145141919810

url = 'https://www.xuetangx.com/video-log/heartbeat/'
headers = {
    'Host': 'www.xuetangx.com',
    'Cookie': Cookie,
    'Content-Length': '597',
    'Terminal-Type': 'web',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'X-Csrftoken': X_Csrftoken,
    'App-Name': 'xtzx',
    'Accept-Language': 'zh',
    'Sec-Ch-Ua': '"Not=A?Brand";v="24", "Chromium";v="140"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Xtbz': 'xt',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Django-Language': 'zh',
    'X-Client': 'web',
    'Origin': 'https://www.xuetangx.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://www.xuetangx.com/learn/space/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Priority': 'u=4, i'
}

for video_offset in range(video_end - video_start):
    # 更新 headers
    v = video_start + video_offset
    d += 1

    headers['Referer'] = f'https://www.xuetangx.com/learn/space/{school_course_id}/{school_course_id}/{classroomid}/video/{v}'

    # 生成发出的 JSON
    heart_data = []
    for i in range(d // 5):
        # 构造 heartbeat 数据
        heart_data.append({
            "c": c,
            "cards_id": 0,
            "cc": cc,
            "classroomid": classroomid,
            "cp": i * 5,
            "d": d,
            "et": "heartbeat",
            "fp": 0,
            "i": 5,
            "lob": "plat2",
            "n": "ali-cdn.xuetangx.com",
            "p": "web",
            "pg": f"{v}_vw2x",
            "skuid": skuid,
            "slide": 0,
            "sp": 1,
            "sq": 1 + i,
            "t": "video",
            "tp": 1,
            "ts": str(1678360614546 + i * 5000),
            "u": u,
            "uip": "",
            "v": v,
            "v_url": ""
        })

    # 添加 videoend 数据
    heart_data.append({
        "c": c,
        "cards_id": 0,
        "cc": cc,
        "classroomid": classroomid,
        "cp": d // 5 * 5 + 5,
        "d": d,
        "et": "videoend",
        "fp": 0,
        "i": 5,
        "lob": "plat2",
        "n": "ali-cdn.xuetangx.com",
        "p": "web",
        "pg": f"{v}_vw2x",
        "skuid": skuid,
        "slide": 0,
        "sp": 1,
        "sq": 2 + d // 5,
        "t": "video",
        "tp": 1,
        "ts": str(1678360614546 + d // 5 * 5000 + 5000),
        "u": u,
        "uip": "",
        "v": v,
        "v_url": ""
    })

    # 转 JSON
    data = {"heart_data": heart_data}

    # 发包
    try:
        ret = requests.post(url=url, headers=headers, json=data)
        print(f"Data request status: {ret.status_code}")
    except Exception as e:
        print(f"[Error]: {str(e)}")
    time.sleep(wait)