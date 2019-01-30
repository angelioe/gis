import sqlite3, datetime


if __name__ == "__main__":
    #####################################################################################################
    ############################### MULTI LAYER PERCEPTRON'S DATA #######################################

    ######### READ DATABASE FROM SERVER AND EXTRACT DEVICES AND FUNCTIONS #########
    conn = sqlite3.connect('hopeitworks.db')
    c = conn.cursor()
    try:
        conn.execute('''CREATE TABLE DATA
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 DATE_TIME TEXT NOT NULL,
                 CONTROLLER TEXT NOT NULL,
                 DEVICE TEXT NOT NULL,
                 FUNCTION TEXT NOT NULL,
                 VALUE TEXT NOT NULL);''')
    except: e = "Database already created"
    c.execute("SELECT DEVICE FROM DATA")
    all_rows = c.fetchall()
    cols = ["year","month","day","weekday","hour","minutes"]
    devices = list(set(all_rows))
    ndev=len(devices)
    for x in range(0,len(devices)):
        devicex=str(devices[x])[2:len(str(devices[x]))-3]
        c.execute('SELECT FUNCTION FROM DATA WHERE DEVICE=?', (devicex,))
        all_funs = c.fetchall()
        functions = list(set(all_funs))
        nfun=len(functions)
        for y in range(0,len(functions)):
            yfun = str(functions[y])[2:len(str(functions[y]))-3]
            devfun =devicex+"_"+yfun
            cols.append(devfun)
            c.execute('SELECT VALUE FROM DATA WHERE DEVICE=? AND FUNCTION=?', (devicex,yfun))
            all_val = c.fetchall()
            vals = list(set(all_val))
            nval=len(vals)
    ######### CREATES FEED DATABASE AND WRITE INFORMATION FROM SERVER DATABASE #########
    connf = sqlite3.connect('feed.db')
    cf = connf.cursor()
    try: connf.execute('''CREATE TABLE MLP(ID INTEGER PRIMARY KEY);''')
    except: e = "Database already created"
    for x in range(0,len(cols)):
        cols[x]=cols[x].replace(" ","")
        cols[x]=cols[x].replace(":","")
        cols[x]=cols[x].replace("_","")
        cols[x]=cols[x].replace("/","")
        cols[x]=cols[x].upper()
        cols[x]="C"+cols[x]
        cf.execute('''ALTER TABLE MLP ADD COLUMN %s TEXT''' % cols[x])
    connf.commit()

    system=[]
    xsys = c.execute("SELECT * FROM DATA")
    for rows in xsys:
        system.append({'ids': rows[0], 'date-times': rows[1], 'controllers': rows[2], 'devices': rows[3], 'functions': rows[4], 'values': rows[5]})

    sqli="INSERT INTO MLP (CYEAR,CMONTH,CDAY,CWEEKDAY,CHOUR,CMINUTES) VALUES (?,?,?,?,?,?)"
    connf.execute(sqli,['0','0','0','0','0','0']);
    for z in cols:
        sqlf="UPDATE MLP SET "+ z +"=? WHERE ID=1"
        connf.execute(sqlf,['0']);

    for x in range(0,len(system)):
        xdate=system[x]['date-times']
        date,time,weekday=xdate.split(" ")
        year,month,day=date.split("-")
        hour,minute,second=time.split(":")
        #################### NORMALIZE DATA ###################################
        year = str(round((int(year)%10)/10,3))
        month = str(round(int(month)/12,3))
        day = str(round(int(day)/31,3))
        weekday = str(round(int(weekday)/7,3))
        hour = str(round(int(hour)/24,3))
        minute = str(round(int(minute)/60,3))
        #######################################################################
        xcol=str(system[x]['devices']+"_"+system[x]['functions']).replace(" ","")
        xcol=xcol.replace(":","")
        xcol=xcol.replace("/","")
        xcol=xcol.replace("_","")
        xcol="C"+xcol.upper()
        xvalues=system[x]['values']
        xvalues=xvalues.replace("off","0")
        xvalues=xvalues.replace("on","1")
        xvalues=xvalues.replace("down","0")
        xvalues=xvalues.replace("up","1")
        sqlt="SELECT ID FROM MLP WHERE CYEAR='"+year+"' AND CMONTH='"+month+"' AND CDAY='"+day+"' AND CHOUR='"+hour+"' AND CMINUTES='"+minute+"' AND CWEEKDAY='"+weekday+"'"
        cf.execute(sqlt);
        all_val = cf.fetchall()
        if (str(all_val) != "[]"):
            sqlt="UPDATE MLP SET "+ xcol +"=? WHERE ID="+str(all_val)[2:-3]
            connf.execute(sqlt,[xvalues]);
        else:
            sql="INSERT INTO MLP (CYEAR,CMONTH,CDAY,CWEEKDAY,CHOUR,CMINUTES,'"+ xcol +"') VALUES (?,?,?,?,?,?,?)"
            connf.execute(sql,[year,month,day,weekday,hour,minute,xvalues]);
    connf.commit()
    #####################################################################################################
    ############################ FILL PREVIOUS STATES AND OPERATE TOGGLE ################################
    cf.execute("SELECT ID FROM MLP ORDER BY ID DESC LIMIT 1");
    all_valid = cf.fetchone()
    num_records=int(str(all_valid)[1:-2])
    for i in range(2,num_records+1):
        for z in cols:
            sqlf="SELECT "+ z +" FROM MLP WHERE ID=?"
            cf.execute(sqlf,[str(i)]);
            all_val = cf.fetchall()
            cf.execute(sqlf,[str(i-1)]);
            all_vala = cf.fetchall()
            if (str(all_val)[2:-3]=='None'):
                if(str(all_vala)[2:-3]=="'0'" or str(all_vala)[2:-3]=="'1'"):
                    sqlu = "UPDATE MLP SET "+ z +"=? WHERE ID=?"
                    cf.execute(sqlu,[int(str(all_vala)[3:-4]),str(i)]);
                if(str(all_vala)[2:-3]=="'x'" or str(all_vala)[2:-3]=="'2'" or str(all_vala)[2:-3]=="'7'"):
                    sqlu = "UPDATE MLP SET "+ z +"=? WHERE ID=?"
                    cf.execute(sqlu,[0,str(i)]);
            if (str(all_val)[2:-3]=="'t'"):
                if(str(all_vala)[2:-3]=="'0'"):
                    sqlu = "UPDATE MLP SET "+ z +"=? WHERE ID=?"
                    cf.execute(sqlu,['1',str(i)]);
                if(str(all_vala)[2:-3]=="'1'"):
                    sqlu = "UPDATE MLP SET "+ z +"=? WHERE ID=?"
                    cf.execute(sqlu,['0',str(i)]);
            connf.commit()
    #####################################################################################################

    #####################################################################################################
    ################################# ELMAN NEURAL NETWORK DATA #########################################

    c.execute("SELECT DEVICE FROM DATA")
    all_rowsr = c.fetchall()
    colsr = ["time","minute","lapse"]
    devicesr = list(set(all_rowsr))
    ndevr=len(devicesr)
    for j in range(0,len(devicesr)):
        devicexr=str(devicesr[j])[2:len(str(devicesr[j]))-3]
        c.execute('SELECT FUNCTION FROM DATA WHERE DEVICE=?', (devicexr,))
        all_funsr = c.fetchall()
        functionsr = list(set(all_funsr))
        nfunr=len(functionsr)
        for k in range(0,len(functionsr)):
            yfunr = str(functionsr[k])[2:len(str(functionsr[k]))-3]
            c.execute('SELECT VALUE FROM DATA WHERE DEVICE=? AND FUNCTION=?', (devicexr,yfunr))
            all_valr = c.fetchall()
            valsr = list(set(all_valr))
            nval=len(valsr)
            for l in range(0,len(valsr)):
                kvalr = str(valsr[l])[2:len(str(valsr[l]))-3]
                devfunvalr =devicexr+"_"+yfunr+"_"+kvalr
                colsr.append(devfunvalr)


    ######### CREATES FEED DATABASE AND WRITE INFORMATION FROM SERVER DATABASE #########
    connf = sqlite3.connect('feed.db')
    cf = connf.cursor()
    try: connf.execute('''CREATE TABLE ENN(ID INTEGER PRIMARY KEY);''')
    except: e = "Database already created"
    for x in range(0,len(colsr)):
        colsr[x]=colsr[x].replace(" ","")
        colsr[x]=colsr[x].replace(":","")
        colsr[x]=colsr[x].replace("_","")
        colsr[x]=colsr[x].replace("/","")
        colsr[x]=colsr[x].upper()
        colsr[x]="C"+colsr[x]
        cf.execute('''ALTER TABLE ENN ADD COLUMN %s TEXT''' % colsr[x])
    connf.commit()

    sqli="INSERT INTO ENN (CTIME,CMINUTE,CLAPSE) VALUES (?,?,?)"
    connf.execute(sqli,['1','0','0']);
    for z in colsr:
        sqlf="UPDATE ENN SET "+ z +"=? WHERE ID=1"
        connf.execute(sqlf,['0']);

    times=[]
    for x in range(0,len(system)):
        xdate=system[x]['date-times']
        date,time,weekday=xdate.split(" ")
        hour,minute,second=time.split(":")
        #################### NORMALIZE DATA ###################################
        minute = str((int(hour)*60)+int(minute))
        lapse = 'x'
        #######################################################################
        xcolr=str(system[x]['devices']+"_"+system[x]['functions']+"_"+system[x]['values']).replace(" ","")
        xcolr=xcolr.replace(":","")
        xcolr=xcolr.replace("/","")
        xcolr=xcolr.replace("_","")
        xcolr="C"+xcolr.upper()
        sqltr="SELECT ID FROM ENN WHERE CMINUTE='"+minute+"' AND CLAPSE='"+lapse+"' AND "+xcolr+"='1'"
        cf.execute(sqltr);
        all_valr = cf.fetchall()
        if (str(all_valr) == "[]"):
            times.append(minute)
            sql="INSERT INTO ENN (CTIME,CMINUTE,CLAPSE,'"+ xcolr +"') VALUES (?,?,?,?)"
            connf.execute(sql,[time,minute,lapse,'1']);
    connf.commit()

    lapses=[]
    for z in range(1,len(times)):
        lapses.append(int(times[z])-int(times[z-1]))
    lapses.append(int(times[0]))
    lapses = list(set(lapses))

    #################### CREATE FINAL RNN TABLE ###################################

    try: connf.execute('''CREATE TABLE RNN(ID INTEGER PRIMARY KEY);''')
    except: e = "Database already created"
    cf.execute('''ALTER TABLE RNN ADD COLUMN CX TEXT''')
    for x in range(0,len(lapses)):
        lapses[x]="C"+str(lapses[x])
        cf.execute('''ALTER TABLE RNN ADD COLUMN %s TEXT''' % lapses[x])
    for x in range(3,len(colsr)):
        cf.execute('''ALTER TABLE RNN ADD COLUMN %s TEXT''' % colsr[x])
    connf.commit()

    sqli="INSERT INTO RNN (CX) VALUES (?)"
    connf.execute(sqli,['1']);
    connf.commit()

    colsr.remove('CTIME')
    colsr.remove('CMINUTE')
    colsr.remove('CLAPSE')
    rnncols=lapses+colsr

    cf.execute("SELECT ID FROM ENN ORDER BY ID DESC LIMIT 1")
    all_rowsrnn = cf.fetchall()

    for w in range(2,int(str(all_rowsrnn)[2:-3])+1):
        cf.execute("SELECT CMINUTE FROM ENN WHERE ID=?",[str(w)])
        all_rowsrnn = cf.fetchall()
        cf.execute("SELECT CMINUTE FROM ENN WHERE ID=?",[str(w-1)])
        all_rowsrnna = cf.fetchall()
        tlapse=int(str(all_rowsrnn)[3:-4])-int(str(all_rowsrnna)[3:-4])
        for p in rnncols:
            if (str(p)==('C'+str(tlapse))):
                sql="INSERT INTO RNN (ID,'"+ p +"') VALUES (?,?)"
                connf.execute(sql,[(w*2-2),'1']);
        firstime = True
        for t in colsr:
            sqltf="SELECT "+ t +" FROM ENN WHERE ID=?"
            cf.execute(sqltf,[str(w)])
            all_rowst = cf.fetchall()
            if (firstime):
                if (str(all_rowst)[3:-4]=='1'):
                    sqlt="INSERT INTO RNN (ID,'"+ t +"') VALUES (?,?)"
                    connf.execute(sqlt,[(w*2-1),str(all_rowst)[3:-4]]);
                    firstime = False
            else:
                if (str(all_rowst)[3:-4]=='1'):
                    sqlt="UPDATE RNN SET "+ t +"=? WHERE ID=?"
                    connf.execute(sqlt,[str(all_rowst)[3:-4],(w*2-1)]);
            connf.commit()
    connf.commit()



    #print(colsr)
