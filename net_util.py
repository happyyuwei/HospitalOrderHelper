"""
查询某个医生的预约情况，并返回预约列表
"""

import requests
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import datetime
import time

import password

# 预约 url
order_url = "https://yuyue.shdc.org.cn/ajaxSearchOrderNumInfoForComment.action"


def query_arrangement(hos_id, dept_id, doctor_id, his_doct_id, next_num_info="0", cookie=None):
    """[summary]
    查询某个医生的预约安排

    Arguments:
        hos_id {[string]} -- [医院代号]
        dept_id {[string]} -- [科室代号]
        doctor_id {[string]} -- [医生代号]
        his_doct_id {[string]} -- [尚不清楚]

    Keyword Arguments:
        next_num_info {int} -- [尚不清楚] (default: {"0"})
        cookie {[type]} -- [请求头cookie，包含用户身份] (default: {None})

    Returns:
        [list] -- [查询列表，每个元素为一个对象，包含三个信息，data, week, state]

    """

    # 生成请求头
    post_body = {
        "platformHosId": hos_id,
        "platformDeptId": dept_id,
        "platformDoctorId": doctor_id,
        "docInfo.hisDoctId": his_doct_id,
        "nextNumInfo": next_num_info
    }
    # 转换成 x-www-form-urlencoded 格式
    body_str_list = []
    for key in post_body:
        body_str_list.append(key+"="+post_body[key])
    # 计算长度
    body_length = len("&".join(body_str_list))

    # 创建请求头
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Length": str(body_length),
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "yuyue.shdc.org.cn",
        "Origin": "https://yuyue.shdc.org.cn",
        "Referer": "https://yuyue.shdc.org.cn/forwardDocInfo.action",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest"
    }
    # 添加cookie
    if cookie != None:
        headers["Cookie"] = cookie

    # 请求url
    res = requests.post(url=order_url, data=post_body, headers=headers)
    # 获取html内容
    html = res.text
    # 去除多余字符，方便解析
    html = html.replace("\r\n", "").replace(" ", "").replace("\t", "")

    def remove_same(list):
        """[summary]
        移除数组中相同的元素，输出元素按原顺序排序
        Arguments:
            list {[list]} -- [输入数组]

        Returns:
            [list] -- [移除相同元素后的数组]
        """

        result = []
        for each in list:
            if each not in result:
                result.append(each)

        return result

    """
    由于该html内容非常乱，因此本人并不打算解析html内容，直接按顺序获取日期，星期以及预约量
    """
    # 把头截掉
    # 从 doctime_middle所在的 div开始寻找
    html = html.split("doctime_middle", 1)
    if len(html) >= 2:
        html = html[1]

    # 解析日期
    pattern = re.compile('[0-1][0-9]-[0-3][0-9]')
    date = pattern.findall(html)
    date = remove_same(date)

    # 解析星期
    pattern = re.compile('星期.')
    week = pattern.findall(html)

    # 解析名额
    pattern = re.compile('已满|预约|余|停诊')
    state = pattern.findall(html)

    result = []
    for i in range(len(date)):

        # 自动补充，若余则认为剩一张
        if state[i] == "余":
            state[i] = "余 1"

        elif state[i] == "预约":
            state[i] = "可预约"

        result.append({
            "date": date[i],
            "week": week[i],
            "state": state[i]
        })

    def parse_date(element):
        date = element["date"]
        date = datetime.datetime.strptime(date, "%m-%d").date()
        return date

    result.sort(key=parse_date)

    return result

# query_arrangement("25", "83", "28107", "2322")


def send_email(text, to_list):

    #我也不知道合在一起写为什么不行，要分开来发
    for to_email in to_list:
        with SMTP_SSL(host="smtp.qq.com") as smtp:
            smtp.login(user=password.email, password=password.password)

            msg = MIMEText(text, _charset="utf8")
            msg["Subject"] = "医院预约日程提醒"
            msg["from"] = password.email
            msg["to"] = to_email

            smtp.sendmail(from_addr="happyyuwei1994@qq.com",
                        to_addrs=to_email, msg=msg.as_string())
            print("send email done："+to_email)

# date = datetime.datetime.strptime("05-01", "%m-%d").date()

def send_wechat(text):
    import itchat
    itchat.auto_login(hotReload=False)# 扫码自动登陆

    author = itchat.search_chatrooms(name='home')[0]
    author.send(text)
    print("send wechat done.")
    time.sleep(5)
    itchat.logout()
    