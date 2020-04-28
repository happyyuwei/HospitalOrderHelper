import requests
url = "https://yuyue.shdc.org.cn/ajaxSearchOrderNumInfoForComment.action"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Content-Length": "94",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # "Cookie": "name=value; JSESSIONID=1373B065038C8FEFD1153E7B68AF2933; usid=112E3972C4B84049810E52A2710F5196,",
    "Host": "yuyue.shdc.org.cn",
    "Origin": "https://yuyue.shdc.org.cn",
    "Referer": "https://yuyue.shdc.org.cn/forwardDocInfo.action",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "XMLHttpRequest"
}
data = {
    "platformHosId": "25",
    "platformDeptId": "83",
    "platformDoctorId": "28107",
    "docInfo.hisDoctId": "2322",
    "nextNumInfo": "0"
}
res = requests.post(url=url, data=data, headers=headers)
html=res.text
# x=html.split("\n")[0]
# print(x.encode("utf-8"))

html=html.replace("\r\n","").replace(" ","").replace("\t","")
# print(html)
# with open("1.html", "w", encoding="utf-8") as f:
#     f.write(html)

import re


def remove_same(list):

    result = []
    for each in list:
        if each not in result:
            result.append(each)

    return result


# 把头截掉
# 从 doctime_middle div开始寻找
html = html.split("doctime_middle")[1]

# 日期
pattern = re.compile('[0-1][0-9]-[0-3][0-9]')
date = pattern.findall(html)
date = remove_same(date)

# 星期
pattern = re.compile('星期.')
week = pattern.findall(html)

# 名额
# 日期
pattern = re.compile('已满|预约|余|停诊')
state = pattern.findall(html)

result = []
for i in range(len(date)):
    result.append({
        "date": date[i],
        "week": week[i],
        "state": state[i]
    })

for each in result:
    print(each)