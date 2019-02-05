import wxpy
import json
import sqlite3
import ntplib
import time


class User(object):
    def __init__(self):
        self.bot = wxpy.Bot(cache_path='cache.pkl', qr_path='qr.png')
        self.bot.enable_puid(path='puid.pkl')
        print('登录结束')

    def __del__(self):
        self.bot.logout()

    def get_all_friend_data(self):
        db = sqlite3.connect("friends.db")
        cursor = db.cursor()
        for item in self.bot.friends():
            puid = str(item.puid)
            remarkname = str(item.remark_name)
            sex = int(item.sex)
            province = str(item.province)
            city = str(item.city)

            if sex == 1:
                sex = '男'
            else:
                sex = '女'
            if remarkname is None:
                remarkname = "Unknow"

            cursor.execute("INSERT INTO Friends(RemarkName, Sex, Province, City, Puid) "
                           "VALUES ('%s', '%s', '%s', '%s', '%s')" % (remarkname, sex, province, city, puid))
            db.commit()
        cursor.close()
        db.close()

    def check_time(self):
        c = ntplib.NTPClient()
        try:
            response = c.request('120.25.108.11')
        except ntplib.NTPException:
            response = c.request('203.107.6.88')
        ts = response.tx_time

        del c, response

        # 新年时间戳 1549296000.0
        if ts >= 1549296000.0 :
            print("时间到！新年快乐！启动发送！")
            return 1
        else:
            return 0

    def wait_time(self):
        while True:
            if self.check_time() == 0:
                time.sleep(0.08)
                continue
            else:
                time.sleep(0.8)
                self.start_send()
                break

    def start_send(self):
        with open("message.json", "r", encoding='utf-8') as f:
            msg_json = json.load(f)
            f.close()
        msg_arr = msg_json['message']

        msg = GetSerializedMsg(msg_arr)

        while True:
            m = msg.get()
            if m == 2:
                break
            else:
                self.send(m['rname'], m['send'])

        print("发送结束")

    def send(self, remark_name: str, msg: str):
        try:
            fr_list = self.bot.friends().search(remark_name)
            fr = wxpy.ensure_one(fr_list)
            fr.send(msg)
        except Exception:
            print("!!!发送遇到问题!!!请检查 %s 的消息发送是否成功" % remark_name)
            pass
        local_time = str(time.asctime(time.localtime(time.time())))
        print("%s , 成功向 %s 发送消息 ：%s " % (local_time, remark_name, msg))


class GetSerializedMsg(object):
    def __init__(self, msg_arr):
        self.msg_arr = msg_arr
        self.now_sn = 0
        self.num = len(msg_arr)

        self.max_sn = 0
        for item in self.msg_arr:
            if self.max_sn < item['sn']:
                self.max_sn = item['sn']

    def get(self):
        for item in self.msg_arr:
            if self.now_sn + 1 == item['sn']:
                self.now_sn = self.now_sn + 1
                return item
        return 2


if __name__ == '__main__':
    user = User()
    user.wait_time()
    del user
    print("全部结束！")

