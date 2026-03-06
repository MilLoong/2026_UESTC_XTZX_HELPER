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

# cookies
cookies = {
    '114514': '1919810'
}