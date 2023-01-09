from tkinter import *
import random
import time
import datetime
from paho.mqtt import client as mqtt_client
import json
from time import strftime
import sqlite3 

broker 		= '7cbd0821e056.sn.mynetname.net'#7cbd0821e056.sn.mynetname.net | 0.tcp.ap.ngrok.io
port 		= 1883
topic 		= "iot/dash"
client_id 	= f'python-mqtt-{random.randint(0, 100)}'

conn = sqlite3.connect('./akuisisiData.sqlite', check_same_thread=False)
cur = conn.cursor()

buat_tabel = '''CREATE TABLE IF NOT EXISTS data_sensor (
                        timestamp TEXT NOT NULL,
                        temp TEXT NOT NULL,
                        humi TEXT NOT NULL,
                        rFanW TEXT NULL,
                        deteksi_gerak TEXT NULL);'''

try:
    cur.execute(buat_tabel)
    conn.commit()
    print("Berhasil Membuat Tabel")
except Exception as e:
    print("Gagal Membuat Tabel:", e)
    conn.rollback()

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set("mqtt", "support")
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

current_time = datetime.datetime.now()

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        _data = json.loads(msg.payload.decode())
        temp = str(_data["temp"])
        humi = str(_data["humi"])
        rFanW = str(_data["rFanW"])
        pir = str(_data["PIR"])

        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        data_sensor_val = (current_time, temp, humi, rFanW, pir)
        cur.execute("INSERT INTO data_sensor (timestamp,temp, humi, rFanW, deteksi_gerak) VALUES(?, ?, ?, ?, ?)",(data_sensor_val))
        conn.commit()

        temp_label = Label(window,
                 text=temp,fg="black", font=("Helvetica", 35),bg="white")
        temp_label.place(x=215, y=380, anchor=CENTER)

        hum_label = Label(window,
                 text=humi,fg="black", font=("Helvetica", 50),bg="white")
        hum_label.place(x=790, y=375, anchor=CENTER)

        rFanW_label = Label(window,
                 text=rFanW,fg="black", font=("Helvetica", 16),bg="white")
        rFanW_label.place(x=210, y=558, anchor=CENTER)

        pir_label = Label(window,
                 text=pir,fg="black", font=("Helvetica", 18),bg="white")
        pir_label.place(x=780, y=558, anchor=CENTER)

        time.sleep(1)
        temp_label.destroy()
        hum_label.destroy()
        rFanW_label.destroy()
        pir_label.destroy()

    client.subscribe(topic)
    client.on_message = on_message


window = Tk()

photo = PhotoImage(file = 'tujuh.png')
window.wm_iconphoto(False, photo)
window.title("Dashboard Monitoring Smart Home")
window.geometry('990x630') # Width, Height
window.resizable(False,False) # Width, Height
#window.config(bg = '#add999')
window.configure(bg='')

# Header image
canvas = Canvas(window, width=990,height=640)
canvas.place(x=0,y=-17)
img = PhotoImage(file="bg.png")
canvas.create_image(0,0,anchor=NW,image=img)

clock_label = Label(window, fg="black", font = ("Times", 15, 'bold'), relief='flat')
clock_label.place(x = 900, y = 2)

def update_label():
    current_time = strftime('%H: %M: %S')
    clock_label.configure(text = current_time)
    clock_label.after(80, update_label)

update_label()
client = connect_mqtt()
subscribe(client)
client.loop_start()
window.mainloop()
client.loop_stop()
