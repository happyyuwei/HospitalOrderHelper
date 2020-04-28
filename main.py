import json
import net_util
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def save_result(path, timestamp, name, result):
        """[summary]
        保存结果
        Arguments:
            path {[type]} -- [description]
            timestamp {[type]} -- [description]
            name {[type]} -- [description]
            result {[type]} -- [description]
        """

        if os.path.exists(path):
            # 读取文件
            with open(path, "r", encoding="utf-8") as f:
                result_list = json.load(f)
        else:
            result_list = []

        # 追加
        result_list.append({
            "time": timestamp,
            "name": name,
            "result": result
        })
        # 生成JSON字符串
        json_str = json.dumps(result_list, ensure_ascii=False, indent=2)
        # 写入文件
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)

def list_to_string(list):
    """
    将列表日期转为字符串
    """
    date= "日, ".join(list)+"日"
    return date.replace("-","月")

def generate_reminder(doctor_name, full_list, new_list, warning_list, accident_list, state_list):
        """[summary]
        生成信息模板
        Arguments:
            doctor_name {[type]} -- [description]
            full_list {[type]} -- [description]
            new_list {[type]} -- [description]
            warning_list {[type]} -- [description]
            accident_list {[type]} -- [description]
            state_list {[type]} -- [description]

        Returns:
            [type] -- [description]
        """        
        full_reminder = None
        new_reminder = None
        accident_reminder = None
        warning_reminder = None


        warning_flag=False

        if len(full_list) > 0:
            full_reminder = "目前已预约满的日期包括："+list_to_string(full_list)
            warning_flag=True
        if len(new_list) > 0:
            new_reminder = "新增可预约日期包括："+list_to_string(new_list)
            warning_flag=True
        if len(accident_list) > 0:
            accident_reminder = "这些日期有人刚刚取消预约，又空出名额，您需要的话尽快预约：" + \
                list_to_string(accident_list)
            warning_flag=True
        if len(warning_list) > 0:
            warning_reminder = "这些日期预约就要满了，预计还剩一个名额，请抓紧时间："+list_to_string(warning_list)
            warning_flag=True

        summary = "近期可预约日程：\n"
        for each in state_list:
            summary = summary+"日期："+each["date"] + \
                "，"+each["week"]+"，"+each["state"]+"\n"

        text=doctor_name+"医生预约提醒\n\n"
        if accident_reminder!=None:
            text=accident_reminder+"\n\n"

        if full_reminder!=None:
            text=text+full_reminder+"\n"

        if new_reminder!=None:
            text=text+new_reminder+"\n"

        if warning_reminder!=None:
            text=text+warning_reminder+"\n"

        text=text+"\n"+summary

        note="注：本信息由就诊预约助手自动发送，请勿回复。详细信息请留意医院官网。"
        text=text+note
        return text, warning_flag



class Schedule:    

    def __init__(self, monitor_info, save_path, email_list):

        # 保存结果的路径
        self.save_path = save_path
        # 邮件通知
        self.email_list=email_list

        # 上一次的查询结果，会和这一次的对比，已表明哪些场次被预约满了
        if os.path.exists(self.save_path):
            # 读取文件
            with open(self.save_path, "r", encoding="utf-8") as f:
                # 读取历史记录
                history = json.load(f)
                # 最后一个历史纪录
                self.last_state_list = history[len(history)-1]["result"]
        else:
            self.last_state_list = []

        
        # monitor list
        self.doctor_name =monitor_info["doctorName"]

        # 获取医生配置文件
        with open("doctors.json", "r", encoding="utf-8") as f:
            self.doctor_list = json.load(f)

        def search_doctor(doctor_name):
            """[summary]
            列表中搜索医生姓名
            Arguments:
                doctor_name {[type]} -- [description]

            Returns:
                [type] -- [description]
            """
            for doctor in self.doctor_list:
                if doctor["doctorName"] == doctor_name:
                    return doctor

            return None
        
        # 搜索医生信息
        doctor_info = search_doctor(self.doctor_name)
        # 获取信息
        self.hos_id = doctor_info["platformHosId"]
        self.dept_id = doctor_info["platformDeptId"]
        self.doctor_id = doctor_info["platformDoctorId"]
        self.his_doct_id = doctor_info["docInfo.hisDoctId"]

    def find_date(self, state_list, date):
        """[summary]
        状态列表中寻找某个具体日期

        Arguments:
            state_list {[type]} -- [description]
            date {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        for state in state_list:
            if state["date"] == date:
                return state

        return None

    def compare(self, current_state_list):
        """[summary]
        比较本次查询状态与上一次查询状态差异，提示部分已预约满，部分新开启，部分已经还剩不多。
        返回四个列表，分别是，已预约满列表，新加列表，剩余不多列表，以及又新增列表（原本已满，中途有人取消预约）
        Arguments:
            current_state_list {[type]} -- [description]
        """

        full_list = []  # 已满列表，原先没满，但现在满了
        new_list = []  # 新增列表，原先没有开启预约
        warning_list = []  # 警告列表，所剩不多列表
        accident_list = []  # 原先满了，有人取消，多余名额

        for current_state in current_state_list:
            date = current_state["date"]
            # 寻找上一次的日期
            last_state = self.find_date(self.last_state_list, date)
            if last_state == None:
                # 没找到说明上次还没开放预约
                new_list.append(date)

            # 如果上次可以预约
            elif last_state["state"] == "预约":
                if current_state["state"] == "余":
                    warning_list.append(date)
                elif current_state["state"] == "已满":
                    full_list.append(date)

            elif last_state["state"] == "已满" and current_state["state"] != "已满":
                accident_list.append(date)

        return full_list, new_list, warning_list, accident_list

    

    def run(self):
            
        # 查询
        result = net_util.query_arrangement(
            self.hos_id, self.dept_id, self.doctor_id, self.his_doct_id)

        # 获取状态
        full_list, new_list, warning_list, accident_list = self.compare(
            result)

        reminder_text, warning_flag= generate_reminder(self.doctor_name, full_list, new_list, warning_list, accident_list, result)

        if warning_flag==True:
            net_util.send_email(reminder_text, self.email_list)
            print(reminder_text)
        
        # 更新状态
        self.last_state_list = result

        # ----------------------------------------------------------
        # 获取时间
        timestamp = time.strftime("%b-%d-%Y-%H:%M:%S", time.localtime())

        # 保存记录
        save_result(self.save_path, timestamp, self.doctor_name, result)
        print("finish epoch, at time {}".format(timestamp))
            


def loop(schedule_config):
    # 读取配置文件
    with open(schedule_config, "r", encoding="utf-8") as f:
        config = json.load(f)

    # parse config
    period = config["period"]
    monitor_list=config["monitorList"]
    email_list=config["emailList"]
    schedule_list=[]

    #初始化任务
    for monitor in monitor_list:
        schedule=Schedule(monitor, "result.json", email_list)
        schedule_list.append(schedule)

    #启动循环任务
    while True:

        for schedule in schedule_list:
            try:
                schedule.run()
            except Exception:
                pass
        
        # 暂停一段时间
        time.sleep(period)


if __name__ == "__main__":
    loop("schedule.json")
