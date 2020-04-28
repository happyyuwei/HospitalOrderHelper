import itchat
import time

itchat.auto_login(hotReload=True)# 扫码自动登陆

# itchat.send("你好，文件传输助手","filehelper")

for i in range(5):
    itchat.send("你好，文件传输助手","filehelper")
    time.sleep(10)