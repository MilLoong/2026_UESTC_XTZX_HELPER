from config_transform import build_runtime_config

'''url, 不用动'''

# base url
base_url = 'https://www.xuetangx.com/'
# api url
api_url = base_url + 'api/v1/lms/'
# heartbeat url
heartbeat_url = base_url + 'video-log/heartbeat/'
# 旧版 url
old_url = base_url + 'learn/'
# 新版 url
new_url = old_url + 'space/'
# 索引 url
index_json_url = api_url + 'learn/course/chapter/'
# 练习信息 url
leafinfo_base_url = api_url + 'learn/leaf_info/'
# 获取练习列表 url
exercise_list_url = api_url + 'exercise/get_exercise_list/'
# 提交问题 url
problem_apply_url = api_url + 'exercise/problem_apply/'

''''以下都是可以改的'''

# sleep 的时间, 越长越好, 不然会被限速
wait = 3

# ========= 新增：推荐只填这 3 个 =========
# 1) 复制「chapter/cid=xxx/sign=xxx」请求的 curl(bash)
curl_bash = r"""
"""

# 2) 复制 heartbeat 请求的 curl(bash)，自动解析 json_data
heartbeat_curl = r"""
"""

# 3) 起始视频 URL（例如：https://www.xuetangx.com/learn/space/xxx/xxx/123/video/987654）
start_video_url = ''

# 4) 结束视频 URL（例如：https://www.xuetangx.com/learn/space/xxx/xxx/123/video/987999）
end_video_url = ''

# ========= 兼容：老参数仍可手填 =========
# 最长的视频长度, 可以大于, 单位 s, 这里默认 50min
d = 3000 
# 用户 ID
u = 114514
# 课程 ID
c = 114514
# 库存量单位 ID
skuid = 114514
# 课程代码
cc = '114514'
# SIGN
sign = '114514'
# CID
cid = '114514'  

# 第一节课 ID
video_start = 114514
# 最后一节课 ID  
video_end = 114514

# 请求头
headers = {
    '114514': '1919810'
}

# cookies（如果只用 curl，会被自动覆盖）
cookies = {}

# 自动转换（当新字段有值时，会覆盖对应老参数）
runtime = build_runtime_config(
    curl_bash_text=curl_bash,
    heartbeat_curl=heartbeat_curl,
    start_video_url=start_video_url,
    end_video_url=end_video_url,
    default_headers=headers,
    default_cookies=cookies,
    default_sign=sign,
    default_cid=cid,
    default_video_start=video_start,
    default_video_end=video_end,
    default_d=d,
    default_u=u,
    default_c=c,
    default_skuid=skuid,
    default_cc=cc,
)

headers = runtime['headers']
cookies = runtime['cookies']
sign = runtime['sign']
cid = runtime['cid']
video_start = runtime['video_start']
video_end = runtime['video_end']
d = runtime['d']
u = runtime['u']
c = runtime['c']
skuid = runtime['skuid']
cc = runtime['cc']
