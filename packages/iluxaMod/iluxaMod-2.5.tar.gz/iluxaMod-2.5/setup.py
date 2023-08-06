from setuptools import setup


version = '2.5'

long_description = """

## How to use?


Importing iluxaModule\n
`import iluxaMod as ilm`\n

PostgreSQL\n

```
# Connect to db
database = ilm.postgreSQL_connect(user="user", password="password", database="database", host="localhost")

# Variables for manual use
db = database.db
sql = database.sql 


# Create tables configured by Iluxa, like: stages, sub, setting, staff, balance...
database.init_DB(stages=False, sub=False, settings=False, staff=False, balance=False, stdout=True)

# User stages [default returns 'None']
database.stages(user_id) # view current user stage.
database.stages(user_id, new) # change user stage.

# App settings
database.settings(setting) # view current setting.
database.settings(setting, new) # change setting.


# Staff manage
database.staff(user_id) # check current user status
database.staff(user_id, status) # change user status
database.staff(user_id, remove=True) # remove user from staff

# Balance
database.balance(user_id) # check current user balance.
database.balance(user_id, new) # set new user balance.

# Subscribers
database.sub_update(user_id) # if user id not in sub-table, it will be added. if exists - updating 'last_update' column
database.sub_view(user_id) # view user's regiser_date and last_update
```

Distance\n
```
# Distance in km
ilm.distance(lat1, lon1, lat2, lon2).get_distance()
```

Telebot\n
```# TGbot init
bot = ilm.tgBot(token, parse_mode='HTML')

# send text message
bot.send(chat_id, msg, reply_markup=None, disable_notification=False)

# Inline Keyboard Markup
bot.kmarkup() # types.InlineKeyboardMarkup() analog

# Back button
bot.back(callback_data) # button with static title "Back"

# Inline Keyboard Buttons
bot.btn("Button", callback_data="Cdata") # callback button
bot.btn("Button", url="https://google.com/") # url button 
```

Arduino\n
```#Arduino init
plate = ilm.arduino(board="COM3")

# digital ports
plate.digital_port(port) # view current status of port
plate.digital_port(port, status) # change status of port

# analog ports
plate.analog_port(port) # view current status of port
plate.analog_port(port, status) # change status of port
```


Barcodes\n
`ilm.barcode(frame).scan() #scan photo/frame`


Pickle
```
# Pick file
ilm.tools().pick(filename, data)

# Unpick file
ilm.tools().unpick(filename)
```


KeysGen
```
ilm.KeysGen().generate(upper=False)
```

Another tools

Importing tools section
```
import iluxaMod.tools as tool
```

Pickle
```
# Init
f = tools.pickle(filename="file")

# Create 
f.pick("New Data")

# Read
data = f.unpick()
print(data)
```
"""



setup(name='iluxaMod',
      version=version,

      author='Lazarev Illya',
      description='Module for simplified work with libraries: TG, PostgreSQL, locations and more...',

      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/LazarevIllya/iluxa_module',
      download_url="https://github.com/LazarevIllya/iluxa_module/archive/v{}.zip".format(version),

      classifiers=['Operating System :: OS Independent',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                   'Programming Language :: Python :: 3.10',
                   'Programming Language :: Python :: Implementation :: PyPy',
                   'Programming Language :: Python :: Implementation :: CPython',


                   ],
      packages=['iluxaMod'],
      install_requires=['geopy', 'psycopg2-binary', 'pyTelegramBotAPI', 'requests', 'pyfirmata', 'Pillow', 'pyzbar', 'qrcode'],
      author_email='lazarevillya031@gmail.com')
