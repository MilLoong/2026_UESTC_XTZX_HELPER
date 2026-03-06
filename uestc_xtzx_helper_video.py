from config import *
import requests
import time

for video_offset in range(video_end - video_start + 1):
    # 更新 headers
    v = video_start + video_offset
    d += 1

    headers['Referer'] = new_url + f'/{sign}/{sign}/{cid}/video/{v}'

    # 生成发出的 JSON
    heart_data = []
    for i in range(d // 5):
        # 构造 heartbeat 数据
        heart_data.append({
            "c": c,
            "cards_id": 0,
            "cc": cc,
            "classroomid": cid,
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
        "classroomid": cid,
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
        ret = requests.post(url=heartbeat_url, headers=headers, cookies=cookies, json=data)
        if ret.status_code == 200:
            print(f"视频 ID: {v} 观看成功")
    except Exception as e:
        print(f"发送失败: {str(e)}")
    time.sleep(wait)

print("全部视频观看完成, 可刷新网页查看学习进度")