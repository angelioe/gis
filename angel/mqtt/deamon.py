import time, sqlite3, datetime
from wakeonlan import send_magic_packet
import paho.mqtt.client as mqtt

def split_telegram(telegram):
    telegram_str=str(telegram)
    id,device,function,value = telegram_str.split(",")
    id = id[2:len(id)]
    device = device[2:-1]
    function = function[2:-1]
    value = value[2:-3]
    return(id,device,function,value)

def on_message(client, userdata, message):
    msg_str=str(message.payload.decode("utf-8"))
    print(msg_str)
    device,cs,function,value = msg_str.split(";")
    conn = sqlite3.connect('/angel/FlaskApp/hopeitworks.db')
    try:
        conn.execute('''CREATE TABLE INSTRUCTIONS
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 DATE_TIME TEXT NOT NULL,
                 CONTROLLER TEXT NOT NULL,
                 DEVICE TEXT NOT NULL,
                 FUNCTION TEXT NOT NULL,
                 VALUE TEXT NOT NULL,
                 STATE TEXT NOT NULL);''')
        conn.execute('''CREATE TABLE DATA
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 DATE_TIME TEXT NOT NULL,
                 CONTROLLER TEXT NOT NULL,
                 DEVICE TEXT NOT NULL,
                 FUNCTION TEXT NOT NULL,
                 VALUE TEXT NOT NULL);''')
    except:
        e = "Database already created"
    c = conn.cursor()
    date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())

    c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("mqtt",device,function))
    all_rows = c.fetchall()
    if (str(all_rows) != "[]"):
        if (str(all_rows)[3:-4]!=value):
            conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                            VALUES (?,?,?,?,?)",[date_time,"mqtt",device,function,value]);
            print("Into if"+date_time+device+function+value)
    else:
        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                    VALUES (?,?,?,?,?)",[date_time,"mqtt",device,function,value]);
        print("Into else"+date_time+device+function+value)
    conn.commit()
    conn.close()



if __name__ == "__main__":

    broker_address="192.168.0.100"
    client = mqtt.Client("Deamon") 			#create new instance
    client.on_message=on_message 			#attach function to callback
    client.connect(broker_address) 			#connect to broker
    client.loop_start()                     #start the loop
    client.subscribe("angel/wifi")


    conn = sqlite3.connect('/angel/FlaskApp/hopeitworks.db')
    try:
        conn.execute('''CREATE TABLE INSTRUCTIONS
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 DATE_TIME TEXT NOT NULL,
                 CONTROLLER TEXT NOT NULL,
                 DEVICE TEXT NOT NULL,
                 FUNCTION TEXT NOT NULL,
                 VALUE TEXT NOT NULL,
                 STATE TEXT NOT NULL);''')
        conn.execute('''CREATE TABLE DATA
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 DATE_TIME TEXT NOT NULL,
                 CONTROLLER TEXT NOT NULL,
                 DEVICE TEXT NOT NULL,
                 FUNCTION TEXT NOT NULL,
                 VALUE TEXT NOT NULL);''')
    except:
        e = "Database already created"

    conn.close()

    while True:
        conn = sqlite3.connect('/angel/FlaskApp/hopeitworks.db')
        c = conn.cursor()
        c.execute('SELECT {id},{coi1},{coi2},{coi3} FROM {tn} WHERE {cn}="mqtt" AND {cs}="p" ORDER BY {ord} DESC LIMIT 1'.\
        format(id='ID',coi1='DEVICE', coi2='FUNCTION', coi3='VALUE', tn='INSTRUCTIONS', cn='CONTROLLER', cs='STATE', ord='ID'))
        all_rows = c.fetchall()
        if (str(all_rows) != "[]"):

            id,device,function,value = split_telegram(all_rows)
            msg = device + ";c;" + function + ";" + value
            client.publish("angel/wifi",msg)
            c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
            format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
            conn.commit()
        conn.close()
        time.sleep(0.1)
