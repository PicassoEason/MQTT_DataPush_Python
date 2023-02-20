from typing import Self
import paho.mqtt.client as mqtt
import json
import time
import firebase_admin
from numpy import mean
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

MQTT_SERVER = "192.168.168.171"
MQTT_PORT = 1883
MQTT_ALIVE = 60
MQTT_TOPIC = "msg/info"
TempData=[]

HuniData=[]
mqtt_client = mqtt.Client()

# 引用私密金鑰
# path/to/serviceAccount.json 請用自己存放的路徑
cred = credentials.Certificate('serviceAccount.json')

# 初始化firebase，注意不能重複初始化
firebase_admin.initialize_app(cred)

# 初始化firestore
db = firestore.client()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)
# 當伺服器收到訊息要做的動作
def on_message(client, userdata, msg):
    print(f"{msg.topic} - Temp: {json.loads(msg.payload)['Temp']}, Humidity: {json.loads(msg.payload)['Humidity']}")
    temp = float(f"{json.loads(msg.payload)['Temp']}")
    hunidity = float(f"{json.loads(msg.payload)['Humidity']}")
    date = datetime.now().strftime("%Y/%m/%d")
    dtime=datetime.now().strftime("%H:%M")
   #製作時間搓
    Temp_Avg=0
    Huni_Avg=0
    nowTime = time.time()
    TempData.append(temp)
    HuniData.append(hunidity)
    
    if(len(TempData)%5==0 & len(HuniData)%5==0):
        Temp_Avg=mean(TempData)
        Huni_Avg=mean(HuniData)

        print("溫度平均",mean(TempData)," ")
        print("濕度平均",mean(HuniData))
        doc = {
        'temp': Temp_Avg,
        'hunidity': Huni_Avg,
        'date': date,
        'TS': nowTime,
        'time':dtime
        }
        clo_ref = db.collection("Day")
        clo_ref.add(doc)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)
mqtt_client.loop_forever()