import re


def remove_same(list):

    result = []
    for each in list:
        if each not in result:
            result.append(each)

    return result


with open("1.html", "r", encoding="utf-8") as f:
    html = f.read()
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