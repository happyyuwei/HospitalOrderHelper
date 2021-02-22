import requests
import json
import os
from lxml import etree
import time
import logging
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def get_page():

    cookie = "_sid_=161399210491820178067168; _e_m=1613992105183; _ipgeo=province%3A%E5%85%A8%E5%9B%BD%7Ccity%3A%E4%B8%8D%E9%99%90; searchHistory=%E4%B9%9D%E9%99%A2%2C%7C%2Cclear; Hm_lvt_3a79c3f192d291eafbe9735053af3f82=1613992107,1613993826,1613993833; _hsid_d_=qg+4ks39Ogiy0l7EWXMUpUz13MlGjYM/nvRnVpjiqhagsKLxJ1ruNVG4uCbNu4ll; _sh_ssid_=1613996701615; JSESSIONID=node014fhcvuiil5j912im63maclgfb4523.node0; __rf__=wNBc8vR7lY27qdFga6T4BYvTK7VC5gcFAkBQdiWn+mgi8z20+aNYubfyBKH5H5cglM0FizGTyvEGYVEw0NRLNExKUUlptV7mKm2fBfCbDnz8COpWykUzob9GT52QjMPi; _ci_=9/KGBQwx06HlLzodJZZuTME7xT8iI5BctItOoXZeU6dkoapk+q+d+f3UGnu0Lgo8; _exp_=m/GOuji1V94EaJL6zOLbfCvdYZqAX4OFx/OO9/FsYSU=; __wyt__=!PVNMi75S6K6aqmJT6qcAq3liKW56G0M517S64udDvS5mdnYvQKyQ4puEAVXVA2CNXHmXV4f5_M2YY4RYyJ2l0hYhO_1pPiSWik1WOhDrlgDXxXUMJG-6ChkCHOE2AKqRBSOk5oyopfCIQoID98ZL-f7KwcFGvS2W18lrP-NovWbnI; Hm_lpvt_3a79c3f192d291eafbe9735053af3f82=1613997700; _fmdata=dF1%2FHF5bnD3JBLXg4OMLmX8yY5wOjqNGMNAorPaUv9F6v0QjEMI22myaL52WiqR5yfYLvvko3jXvMIEntCK36sk5hDa8VnKf9mdaTZwVmBg%3D; _fm_code=eyJ2IjoiL01SWGxaaG5ibWdwcGVqR1IyWThGajJNV29oT01wand1Qkt4YytJSEs3TmQ0RkFkSnFJRGJLYURPY1hPQTRQaSIsIm9zIjoid2ViIiwiaXQiOjk3MSwidCI6InFBZkd5VkxiZzlObWVKa3dyQ1VRMHFEWStUejlyaEhjQkx6OURhZnFZS3luN1BTNnBISytZeXA2U2FRcjBNR1ZmNWIveUdYRkwyblRESjA0L1kzZlNBPT0ifQ%3D%3D"

    cookie_dict = {}
    cookie = cookie.split(";")

    for each in cookie:
        elements = each.strip().split("=")
        cookie_dict[elements[0]] = elements[1]

    response = requests.get(
        "https://www.guahao.com/department/138181401416908000?isStd=", cookies=cookie_dict)
    html = response.content.decode("utf-8")

    # with open("x.html", "w", encoding="utf-8") as f:
    #     f.writelines([html])

    return html


def get_time(info_list):
    for info in info_list:
        if "出诊时间" in info:
            return info

    return ""


def parse_page(html: str):
    html = etree.HTML(html)

    elements = html.xpath("//table/tbody/tr/td/span/a")

    doctor_time_dict = {}

    for element in elements:
        # print(etree.tostring(element,encoding='utf-8',method='html').decode("utf-8"))
        info_list = element.get("data-tips").split("</p><p>")
        # print(etree.tostring(etree.SubElement(element, "span"), encoding='utf-8',method='html').decode("utf-8"))

        doctor_time_str = get_time(info_list)
        details = doctor_time_str.split("：")

        doctor_time_dict[details[1]] = element.xpath("string()").strip()

    return doctor_time_dict


def send_email(text, to_list, sender):

    # 我也不知道合在一起写为什么不行，要分开来发
    for to_email in to_list:
        with SMTP_SSL(host="smtp.qq.com") as smtp:
            smtp.login(user=sender, password="vunfvcqpssxfbafj")

            msg = MIMEText(text, _charset="utf8")
            msg["Subject"] = "医院预约日程提醒"
            msg["from"] = sender
            msg["to"] = to_email

            smtp.sendmail(from_addr=sender,
                          to_addrs=to_email, msg=msg.as_string())
            print("send email done："+to_email)


def watch():
    doctor_time_dict = parse_page(get_page())
    history = {}

    if os.path.exists("history.json") == True:
        with open("history.json", "r", encoding="utf-8") as f:
            history = json.load(f)

    diff = {}
    for date in doctor_time_dict:
        if date in history:
            if doctor_time_dict[date] != "已满":
                diff[date] = doctor_time_dict[date]
        else:
            diff[date] = doctor_time_dict[date]

    history.update(doctor_time_dict)

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False)

    logging.info("Watching...")
    if len(diff) == 0:
        logging.info("No chaning...")
    else:
        text = "上海第九人民医院——牙体牙髓炎科\r\n预约已更新：\r\n\r\n"
        for each in diff:
            text = text+"    {}： {}\r\n".format(each, diff[each])

        message = text+"\r\n注：本信息由就诊预约助手自动发送，请勿回复。详细信息请留意医院官网。\r\n开发：@变蝙蝠侠"

        send_email(message,
                   [
                       "happyyuwei1994@qq.com",
                       "1257064323@qq.com",
                       "1932143535@qq.com"
                   ],
                   "happyyuwei1994@qq.com"
                   )
        print(text)


def main():

    while True:
        watch()
        # watching every 60 seconds
        localtime = time.localtime(time.time())
        if localtime.tm_hour >= 7 and localtime.tm_hour <= 8:
            sleep_time = 10+int(random.random()*5)
        else:
            sleep_time = 60+int(random.random()*10)
        logging.info("Sleeping...Await in {} seconds".format(sleep_time))
        time.sleep(sleep_time)


main()
