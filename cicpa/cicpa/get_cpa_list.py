import requests
from datetime import datetime
import ddddocr
import re


def get_now_timestamp():
    return int(datetime.now().timestamp()*1000)

def get_captcha_url():
    now_timestamp = get_now_timestamp()
    return f'http://acc.mof.gov.cn/login_achieve/getImage?t={now_timestamp}'

def captcha_ocr(content):
    ocr = ddddocr.DdddOcr(show_ad=False)
    text = ocr.classification(content)
#     print(text)
    text = text.replace('加','+').replace('减','-').replace('乘','*').replace('除','/')
    try:
        return eval(''.join(re.findall(r'[0-9]+|\+|\-|\*|\\', text)))
    except:
        return 1

def get_captcha_img():
    url = get_captcha_url()
    r = requests.get(url)
    captcha_result = captcha_ocr(r.content)
    cookies = r.headers['Set-Cookie']
    return captcha_result, cookies

def query_cpa_list(currentPage=1, pageSize=1000000):
    captcha_result, cookies = get_captcha_img()
#     print(captcha_result)
    q_url = 'http://acc.mof.gov.cn/searchBfLogin/searchCpaAcct'
    data = {
        'currentPage': currentPage,
        'pageSize': pageSize,
        'division_province': '',
        'cpaCno': '',
        'cpaName': '',
        'cpafName': '事务所',
        'cpaStatus': '',
        'pic_code': captcha_result,
        }
    headers = {'Cookie':cookies}
    r = requests.post(q_url, data=data, headers=headers)
    return r.json()

def get_cpa_list():
    data = query_cpa_list()
    while data['message'] == '验证码输入错误!':
        data = query_cpa_list()
    return data