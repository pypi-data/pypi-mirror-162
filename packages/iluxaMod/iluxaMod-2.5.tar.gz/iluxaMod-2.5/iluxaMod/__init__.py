import tools


class postgreSQL_connect:
    def __init__(self, user="postgres", password="password", database=None, host="localhost"):
        import psycopg2

        self.db = psycopg2.connect(database=database, user=user, password=password, host=host)
        self.sql = self.db.cursor()
        self.init_DB()

    def init_DB(self, stages=False, sub=False, settings=False, staff=False, balance=False, stdout=True):
        if stages:
            self.sql.execute(f"""CREATE TABLE IF NOT EXISTS stages(
            user_id TEXT PRIMARY KEY,
            stage TEXT
            )""")
            self.db.commit()
            if stdout:
                print(f'[+] Table "stages" init...')
        if settings:
            self.sql.execute(f"""CREATE TABLE IF NOT EXISTS settings(
            setting TEXT PRIMARY KEY,
            status TEXT
            )""")
            self.db.commit()
            if stdout:
                print(f'[+] Table "settings" init...')
        if staff:
            self.sql.execute(f"""CREATE TABLE IF NOT EXISTS staff(
            user_id TEXT PRIMARY KEY,
            status TEXT
            )""")
            self.db.commit()
            if stdout:
                print(f'[+] Table "staff" init...')
        if balance:
            self.sql.execute(f"""CREATE TABLE IF NOT EXISTS balance(
            user_id TEXT PRIMARY KEY,
            balance TEXT
            )""")
            self.db.commit()
            if stdout:
                print(f'[+] Table "balance" init...')
        if sub:
            self.sql.execute(f"""CREATE TABLE IF NOT EXISTS subs(
            user_id TEXT PRIMARY KEY,
            last_update TEXT,
            reg_time TEXT
            )""")
            self.db.commit()
            if stdout:
                print(f'[+] Table "balance" init...')

    def stages(self, user_id, stage=None):
        self.sql.execute(f"SELECT * FROM stages WHERE user_id = '{str(user_id)}'")
        if self.sql.fetchone() is None:
            if stage != None:
                self.sql.execute(f"INSERT INTO stages VALUES('{str(user_id)}', '{stage}')")
                self.db.commit()
                return stage
            else:
                return "None"

        else:
            if stage != None:
                self.sql.execute(f"UPDATE stages SET stage = '{str(stage)}' WHERE user_id = '{str(user_id)}'")
                self.db.commit()
            self.sql.execute(f"SELECT * FROM stages WHERE user_id = '{str(user_id)}'")
            for i in self.sql.fetchall():
                return i[1]

    def settings(self, setting, new=None):
        self.sql.execute(f"SELECT * FROM settings WHERE setting = '{str(setting)}'")
        if self.sql.fetchone() is None:
            if new != None:
                self.sql.execute(f"INSERT INTO settings VALUES('{str(setting)}', '{new}')")
                self.db.commit()
                return new
            else:
                return "None"

        else:
            if new != None:
                self.sql.execute(f"UPDATE settings SET status = '{str(new)}' WHERE setting = '{str(setting)}'")
                self.db.commit()
            self.sql.execute(f"SELECT * FROM settings WHERE setting = '{str(setting)}'")
            for i in self.sql.fetchall():
                return i[1]

    def staff(self, user_id, status=None, remove=False):
        if status == None:
            if remove == False:
                s = None
                self.sql.execute(f"SELECT * FROM staff WHERE user_id = '{str(user_id)}'")
                if self.sql.fetchone() is None:
                    pass
                else:
                    self.sql.execute(f"SELECT * FROM staff WHERE user_id = '{str(user_id)}'")
                    for i in self.sql.fetchall():
                        s = i[1]
                return s
            elif remove == True:
                self.sql.execute(f"SELECT * FROM staff WHERE user_id = '{str(user_id)}'")
                if self.sql.fetchone() is None:
                    pass
                else:
                    self.sql.execute(f"DELETE FROM staff WHERE user_id = '{str(user_id)}'")
                    self.db.commit()
        elif status != None:
            self.sql.execute(f"SELECT * FROM staff WHERE user_id = '{str(user_id)}'")
            if self.sql.fetchone() is None:
                self.sql.execute(f"INSERT INTO staff VALUES('{str(user_id)}','{str(status)}')")
                self.db.commit()
            else:
                self.sql.execute(f"UPDATE staff SET status = '{str(status)}' WHERE user_id = '{str(user_id)}'")
                self.db.commit()

    def balance(self, user_id, new_balance=None):
        self.sql.execute(f"SELECT * FROM balance WHERE user_id = '{str(user_id)}'")
        if self.sql.fetchone() is None:
            if new_balance != None:
                self.sql.execute(f"INSERT INTO balance VALUES('{str(user_id)}', '{str(new_balance)}')")
                self.db.commit()
                return int(new_balance)
            else:
                return 0
        else:
            if new_balance != None:
                self.sql.execute(f"UPDATE balance SET balance = '{str(new_balance)}' WHERE user_id = '{str(user_id)}')")
                self.db.commit()
            self.sql.execute(f"SELECT * FROM balance WHERE user_id = '{str(user_id)}'")
            for i in self.sql.fetchall():
                return int(i[1])

    def sub_update(self, user_id):
        import datetime

        self.sql.execute(f"SELECT * FROM subs WHERE user_id = '{str(user_id)}'")
        if self.sql.fetchone() is None:
            self.sql.execute(f"INSERT INTO subs VALUES('{str(user_id)}', '{str(datetime.datetime.now())}', '{str(datetime.datetime.now())}')")
            self.db.commit()
        else:
            self.sql.execute(f"UPDATE subs SET last_update = '{str(datetime.datetime.now())}' WHERE user_id = '{str(user_id)}'")
            self.db.commit()

    def sub_view(self, user_id):
        import datetime

        self.reg_time = None
        self.last = None
        self.sql.execute(f"SELECT * FROM subs WHERE user_id = '{str(user_id)}'")
        if self.sql.fetchone() is None:
            pass
        else:
            self.sql.execute(f"SELECT * FROM subs WHERE user_id = '{str(user_id)}'")
            for i in self.sql.fetchall():
                self.reg_time = tools().str_to_time(i[2])
                self.last = tools().str_to_time(i[1])

        return {
            "user_id": int(user_id),
            "last_update": self.last,
            "reg_time": self.reg_time
        }

    def drop_table(self, table, stdout=False):
        try:
            self.sql.execute(f"DROP TABLE {str(table)}")
            self.db.commit()
            if stdout:
                print(f'[+] Table "{str(table)}" dropped')
        except:
            if stdout:
                print(f'[-] Error with table "{str(table)}" drop')


class distance:
    def __init__(self, lat1, lon1, lat2, lon2):
        self.lat1 = lat1
        self.lon1 = lon1
        self.lat2 = lat2
        self.lon2 = lon2

    def get_distance(self):
        from geopy.distance import great_circle

        locationA = (self.lat1, self.lon1)
        locationB = (self.lat2, self.lon2)
        return round(great_circle.geodesic(locationA, locationB).km, 3)


class tgBot:

    def __init__(self, token):
        import telebot
        self.token = token
        self.bot = telebot.TeleBot(self.token)

    def send(self, chat_id, msg, reply_markup=None, disable_notification=False):
        self.bot.send_message(chat_id, msg, reply_markup=reply_markup, disable_notification=disable_notification,
                         parse_mode='HTML')

    def kmarkup(self):
        from telebot import types

        return types.InlineKeyboardMarkup()

    def back(self, callback_data, bname="Back"):
        from telebot import types

        return types.InlineKeyboardButton(bname, callback_data=callback_data)

    def btn(self, button_id, callback_data=None, url=None):
        from telebot import types

        return types.InlineKeyboardButton(button_id, callback_data=callback_data, url=url)


class arduino:

    def __init__(self, board):
        from pyfirmata import Arduino, util
        self.board = Arduino(board)
        it = util.Iterator(board)
        it.start()

    def digital_port(self, port, status=None):
        if status == None:
            return self.board.digital[port].read()
        elif status in ['True', True, "on", 1]:
            return self.board.digital[port].write(1)
        else:
            return self.board.digital[port].write(0)

    def analog_port(self, port, status=None, enable_reporting=False):
        if enable_reporting:
            self.board.analog[port].enable_reporting()
        if status == None:
            return self.board.analog[port].read()
        elif status != None:
            return self.board.analog[port].write(status)


class barcode:
    def __init__(self, frame):
        from PIL import Image
        self.frame = frame
        self.source_img = Image.open(frame)

    def scan(self):
        from pyzbar.pyzbar import decode
        self.decoded = decode(self.source_img)
        return self.decoded[0].data.decode('utf-8')


class qr:
    def __init__(self, data):
        self.data = data

    def create(self, filename="qr_code.jpg", version=4, border=2):
        import qrcode
        qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=version, border=border,)
        qr.add_data(self.data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="green", back_color="black")
        img.save(filename, "JPEG")


class KeysGen:
    def __init__(self, upper=False):
        self.lst = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if upper:
            self.lst = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def generate(self):
        from random import choice as cho

        def prgf():
            return cho(self.lst) + cho(self.lst) + cho(self.lst) + cho(self.lst) + cho(self.lst) + cho(self.lst)

        return str(f"{prgf()}-{prgf()}-{prgf()}-{prgf()}-{prgf()}-{prgf()}")







