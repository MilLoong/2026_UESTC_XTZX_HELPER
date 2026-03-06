from config import *
from bs4 import BeautifulSoup
import requests
import json
import time

data = []

def get_exercise_ids():
    print('正在获取练习题名称...')

    params = (
        ('cid', cid),
        ('sign', sign),
    )

    index_dict = requests.get(index_json_url, headers=headers, cookies=cookies, params=params).json()

    course_chapters = index_dict['data']['course_chapter']
    for chapter in course_chapters:
        chapter_name = chapter['name']
        course_sections = chapter['section_leaf_list'] 
        for section in course_sections:
            if 'leaf_list' in section:
                course_leafs = section['leaf_list']
                for leaf in course_leafs:
                    leaf_name = leaf['name']
                    leaf_id = leaf['id']
                    data.append({"chapter_name": chapter_name, "exercise_name": leaf_name , "leaf_id":leaf_id})
            else:
                leaf_name = section['name']
                leaf_id = section['id']
                data.append({"chapter_name": chapter_name, "exercise_name": leaf_name, "leaf_id": leaf_id})

def get_exercise_leaf_type_ids():
    get_exercise_ids()
    print('正在获取练习题信息...')

    params = (
        ('sign', sign),
    )

    for each in data[:]:
        leafinfo_url = leafinfo_base_url + str(cid) + '/' + str(each['leaf_id']) +'/'
        leafinfo_dict = requests.get(leafinfo_url, headers=headers, cookies=cookies, params=params).json()
        leaf_type_id = leafinfo_dict['data']['content_info']['leaf_type_id']
        if leaf_type_id == None:
            data.remove(each)
            continue
        each['leaf_type_id'] = leaf_type_id

def pre_post_and_get_answers():
    print("正在获取练习题答案...")
    for each in data:
        exercise_url = exercise_list_url + str(each['leaf_type_id']) + '/'
        exercise_dict = requests.get(exercise_url, headers=headers, cookies=cookies).json()
        problems = exercise_dict['data']['problems']
        leaf_id = each['leaf_id']
        classroom_id = int(cid)
        exercise_id = each['leaf_type_id']
        print(f'章节: \"{each["chapter_name"]}\", 练习: \"{each["exercise_name"]}\"')
        with open("answers.txt", "w", encoding='utf-8') as f:
            f.write(f'章节: \"{each["chapter_name"]}\", 练习: \"{each["exercise_name"]}\"\n')
        answers = {}
        for problem in problems:
            problem_id = problem['problem_id']
            count =  str(problem['index'])
            payload = {
                "leaf_id": leaf_id,
                "classroom_id": classroom_id,
                "exercise_id": exercise_id,
                "problem_id": problem_id,
                "sign": sign,
                "answers":{},
                "answer":[]
            }
            problem_type = problem['content']['Type']
            param_to_use = None
            if problem_type == 'SingleChoice':
                payload['answer'] = ['A']
                param_to_use = 'answer'
            elif problem_type == 'FillBlank':
                payload['answers'] = {'1':'1'}
                param_to_use = 'answers'
            elif problem_type == 'Judgement':
                payload['answer'] = ['true']
                param_to_use = 'answer'
            elif problem_type == 'MultipleChoice':
                payload['answer'] = ['A']
                param_to_use = 'answer'
            else:
                raise Exception(f'未知的题目类型: {problem_type}')
            body_html = problem['content']['Body']
            soup = BeautifulSoup(body_html, 'html.parser')
            result = soup.get_text(strip=True)
            print(f'{count}: {result}')
            with open("answers.txt", "w", encoding='utf-8') as f:
                f.write(f'{count}: {result}')
            response = requests.post(problem_apply_url, headers=headers, cookies=cookies, json=payload).json()
            if 'detail' in response:
                if '限速' in response['detail']:
                    print('请求过于频繁, 请调整 wait 的值')
                    with open("answers.txt", "w", encoding='utf-8') as f:
                        f.write('请求过于频繁, 请调整 wait 的值')
                    raise Exception('请求过于频繁')
                else:
                    print(f'提交失败, 错误信息: {response['detail']}')
                    with open("answers.txt", "w", encoding='utf-8') as f:
                        f.write(f'提交失败, 错误信息: {response['detail']}')
                    raise Exception('提交失败')
            answer = None
            if 'error_code' in response:
                if response['error_code'] == 80001:
                    answer = problem['user'][param_to_use]
                    print(f'已做答过, 答案为: {answer}')
                    with open("answers.txt", "w", encoding='utf-8') as f:
                        f.write(f'已做答过, 答案为: {answer}')
                else:
                    print(f'提交失败, 错误信息: {response['msg']}')
                    with open("answers.txt", "w", encoding='utf-8') as f:
                        f.write(f'提交失败, 错误信息: {response['msg']}')
                    raise Exception('提交失败')
            else:
                answer = response['data'][param_to_use]
                print(f'未做答过, 答案为: {answer}')
                with open("answers.txt", "w", encoding='utf-8') as f:
                        f.write(f'未做答过, 答案为: {answer}')
            answers[count] = answer
            time.sleep(wait)
        print()
        each['answers'] = answers

def data2json():
    with open("answers.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ':')))

get_exercise_leaf_type_ids()
pre_post_and_get_answers()
data2json()