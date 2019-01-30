import broadlink, time, sqlite3, datetime
from wakeonlan import send_magic_packet

def split_telegram(telegram):
    telegram_str=str(telegram)
    id,device,function,value = telegram_str.split(",")
    id = id[2:len(id)]
    device = device[2:-1]
    function = function[2:-1]
    value = value[2:-3]
    return(id,device,function,value)

if __name__ == "__main__":

    devices = broadlink.discover(timeout=15)
    auth = devices[0].auth()
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
        c.execute('SELECT {id},{coi1},{coi2},{coi3} FROM {tn} WHERE {cn}="broad1" AND {cs}="p" ORDER BY {ord} DESC LIMIT 1'.\
        format(id='ID',coi1='DEVICE', coi2='FUNCTION', coi3='VALUE', tn='INSTRUCTIONS', cn='CONTROLLER', cs='STATE', ord='ID'))
        all_rows = c.fetchall()

        if (str(all_rows) != "[]"):

            id,device,function,value = split_telegram(all_rows)
            file_name = "/angel/broadlink/codes/"+device + "_" + function + ".txt"
            try:
                in_file = open(file_name, "rb")
                data = in_file.read()
                in_file.close()
                bool = True
            except:
                bool = False

            if(bool):
                devices[0].send_data(data)
                c.execute('UPDATE {tn} SET {cs}="d" WHERE {ide}=id'.\
                    format(tn='INSTRUCTIONS', cs='STATE', ide='ID'))
                date_time=str(datetime.datetime.now())+" "+str(datetime.datetime.today().weekday())

                c.execute("SELECT VALUE FROM DATA WHERE CONTROLLER=? AND DEVICE=? AND FUNCTION=? ORDER BY ID DESC LIMIT 1",("broad1",device,function))
                all_rows = c.fetchall()
                if (str(all_rows) != "[]"):
                    if (str(all_rows)[3:-4]!=value):
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"broad1",device,function,value]);
                else:
                        conn.execute("INSERT INTO DATA (DATE_TIME,CONTROLLER,DEVICE,FUNCTION,VALUE)\
                                        VALUES (?,?,?,?,?)",[date_time,"broad1",device,function,value]);
                conn.commit()

        conn.close()
        time.sleep(0.1)
