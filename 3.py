import itchat
import time

itchat.auto_login(hotReload=False)# 扫码自动登陆

# itchat.send("你好，文件传输助手","filehelper")

# for i in range(3):
#     itchat.send("你好，程序调试中 "+str(i),"home")
#     time.sleep(10)

for i in range(3):
    author = itchat.search_chatrooms(name='home')[0]
    author.send("你好，程序调试中 "+str(i))
    time.sleep(10)
