from pywebostv.discovery import *
from pywebostv.connection import *
from pywebostv.controls import *
import time, sqlite3, datetime, time
from wakeonlan import send_magic_packet


store = {}

def split_telegram(telegram):
    """Parse command line arguments and start monitor."""
    telegram_str=str(telegram)
    id,device,function,value = telegram_str.split(",")
    id = id[2:len(id)]
    device = device[2:-1]
    function = function[2:-1]
    value = value[2:-3]
    return(id,device,function,value)

def tv_on(mac):
    for x in range(0,3):
        send_magic_packet(mac)
        x+=1

def tv_off(client):
    system = SystemControl(client)
    system.power_off()

def set_volumen(client,level):
    media = MediaControl(client)
    media.set_volume(level)

def tv_play(client):
    media = MediaControl(client)
    media.play()

def tv_pause(client):
    media = MediaControl(client)
    media.pause()

def tv_stop(client):
    media = MediaControl(client)
    media.stop()

def sys_not(client,msg):
    system = SystemControl(client)
    system.notify(msg)

def app_launch(client,appnumber):
    app = ApplicationControl(client)
    apps = app.list_apps()
    launch_info = app.launch(apps[appnumber])

def tv_source(client,sourcenumber):
    source_control = SourceControl(client)
    sources = source_control.list_sources()
    source_control.set_source(sources[sourcenumber])

if __name__ == "__main__":
    mac_add = 'A0:6F:AA:EA:93:BE'
    client = WebOSClient("192.168.0.11")
    client.connect()
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            result = "Please accept the connect on the TV!"
        elif status == WebOSClient.REGISTERED:
            result = "Registration successful!"

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
    source_control = SourceControl(client)
    sources = source_control.list_sources()
    media = MediaControl(client)
    app = ApplicationControl(client)
    apps = app.list_apps()

    while True:
        conn = sqlite3.connect('/angel/FlaskApp/hopeitworks.db')
        c = conn.cursor()
        c.execute('SELECT {id},{coi1},{coi2},{coi3} FROM {tn} WHERE {cn}="webostv" AND {cs}="p" ORDER BY {ord} DESC LIMIT 1'.\
            format(id='ID',coi1='DEVICE', coi2='FUNCTION', coi3='VALUE', tn='INSTRUCTIONS', cn='CONTROLLER', cs='STATE', ord='ID'))
        all_rows = c.fetchall()

        if (str(all_rows) != "[]"):
            id,device,function,value = split_telegram(all_rows)
            if (function == "power"):
                if (value == "on"):
                    tv_on(mac_add)
                    c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                        format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                    date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                    c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                    all_rows = c.fetchall()
                    if (str(all_rows) != "[]"):
                        if (str(all_rows)[3:-4]!=value):
                            conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                    else:
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                    conn.commit()

                if (value == "off"):
                    tv_off(client)
                    c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                    format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                    date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                    c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                    all_rows = c.fetchall()
                    if (str(all_rows) != "[]"):
                        if (str(all_rows)[3:-4]!=value):
                            conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                            VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                    else:
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                    conn.commit()
            if (function == "vol"):
                if (value == "up"):
                    media.volume_up()
                    c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                        format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                    date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                    c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                    all_rows = c.fetchall()
                    if (str(all_rows) != "[]"):
                        if (str(all_rows)[3:-4]!=value):
                            conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                    else:
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                    conn.commit()

                if (value == "down"):
                    media.volume_down()
                    c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                    format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                    date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                    c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                    all_rows = c.fetchall()
                    if (str(all_rows) != "[]"):
                        if (str(all_rows)[3:-4]!=value):
                            conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                            VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                    else:
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                    conn.commit()
            if (function == "setv"):
                set_volumen(client,int(value))
                c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                all_rows = c.fetchall()
                if (str(all_rows) != "[]"):
                    if (str(all_rows)[3:-4]!=value):
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                else:
                    conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                    VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                conn.commit()
            if (function == "play"):
                tv_play(client)
                c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                all_rows = c.fetchall()
                if (str(all_rows) != "[]"):
                    if (str(all_rows)[3:-4]!=value):
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                else:
                    conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                    VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                conn.commit()
            if (function == "pause"):
                tv_pause(client)
                c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                all_rows = c.fetchall()
                if (str(all_rows) != "[]"):
                    if (str(all_rows)[3:-4]!=value):
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                else:
                    conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                    VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                conn.commit()
            if (function == "stop"):
                tv_stop(client)
                c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                all_rows = c.fetchall()
                if (str(all_rows) != "[]"):
                    if (str(all_rows)[3:-4]!=value):
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                else:
                    conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                    VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                conn.commit()
            if (function == "applaunch"):
                launch_info = app.launch(apps[int(value)])
                c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                all_rows = c.fetchall()
                if (str(all_rows) != "[]"):
                    if (str(all_rows)[3:-4]!=value):
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                else:
                    conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                    VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                conn.commit()
            if (function == "source"):
                print(value)
                print(int(value))
                source_control.set_source(sources[int(value)])
                c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())
                c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("webostv",device,function))
                all_rows = c.fetchall()
                if (str(all_rows) != "[]"):
                    if (str(all_rows)[3:-4]!=value):
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                else:
                    conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                    VALUES (?,?,?,?,?)",[date_time,"webostv",device,function,value]);
                conn.commit()

        conn.close()
        time.sleep(0.1)
