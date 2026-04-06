from config import *
import requests
import time

base_duration = max(int(d), 1)

for video_offset in range(video_end - video_start + 1):
    v = video_start + video_offset
    video_duration = base_duration

    # 每个视频使用独立 headers，避免遗留旧 referer
    req_headers = dict(headers)
    req_headers.pop('referer', None)
    req_headers['Referer'] = new_url + f'/{sign}/{sign}/{cid}/video/{v}'
    ts_start = int(time.time() * 1000)

    # 生成发出的 JSON
    heart_data = []
    for i in range(video_duration // 5):
        cp = i * 5
        # 构造 heartbeat 数据
        heart_data.append({
            "c": c,
            "cards_id": 0,
            "cc": cc,
            "classroomid": cid,
            "cp": cp,
            "d": video_duration,
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
            "tp": cp,
            "ts": str(ts_start + i * 5000),
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
        "classroomid": cid,
        "cp": video_duration,
        "d": video_duration,
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
        "sq": 2 + video_duration // 5,
        "t": "video",
        "tp": video_duration,
        "ts": str(ts_start + (video_duration // 5 + 1) * 5000),
        "u": u,
        "uip": "",
        "v": v,
        "v_url": ""
    })

    # 转 JSON
    data = {"heart_data": heart_data}

    # 发包
    try:
        ret = requests.post(url=heartbeat_url, headers=req_headers, cookies=cookies, json=data)
        if ret.status_code == 200:
            print(f"视频 ID: {v} 观看成功")
        else:
            print(f"视频 ID: {v} 返回码: {ret.status_code}，响应: {ret.text[:200]}")
    except Exception as e:
        print(f"发送失败: {str(e)}")
    time.sleep(wait)

print("全部视频观看完成, 可刷新网页查看学习进度")