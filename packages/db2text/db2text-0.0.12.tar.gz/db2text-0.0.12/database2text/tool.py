#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys,os,difflib,jinja2,re,json,datetime

__all__=["db","ckd","dbdata","storidata","stdata"]

def mkdir(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

def quit(errinfo,exitcode=0):
    print(errinfo)
    sys.exit(exitcode)

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        print(obj,type(obj))
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj,bytes):
            return ""
        else:
            return json.JSONEncoder.default(self, obj)

class dblib(object):
    def res1(self,ssql,*args,**kwargs):
        c=self.conn.cursor()
        c.execute(ssql,*args,**kwargs)
        res=c.fetchone()
        c.close()
        if res==None:
            return
        if len(res)==1:
            return res[0]
        else:
            return res
    def exec(self,ssql,*args,**kwargs):
        c=self.conn.cursor()
        c.execute(ssql,*args,**kwargs)
        return c
    def exec2(self,ssql,*args,**kwargs):
        c=self.conn.cursor()
        c.execute(ssql,*args,**kwargs)
        res=[]
        col=c.description
        for item in c.fetchall():
            row={}
            for i in range(len(col)):
                row[col[i][0]]=item[i]
            res.append(row)
        return res

class checkdiff(object):
    def init(self,objtype):
        self.diff=difflib.Differ()
        self.objtype=objtype
        self.datadir=cfgdata["datadir"]
        mkdir(self.datadir)
        self.datadir="%s/%s" %(self.datadir,objtype)
        mkdir(self.datadir)
        self.filelist=[]
        for f in os.listdir(self.datadir):
            self.filelist.append(f)
    def comp(self,objname,objdata):
        fn="%s/%s" %(self.datadir,objname)
        if os.path.isfile(fn):
            data=open(fn).read()
            if data==objdata:
                return
            print("============diff of %s.%s" %(self.objtype,objname))
            print("\n".join(self.diff.compare(data.split("\n"),objdata.split("\n"))))
        else:
            print("============find new: %s.%s" %(self.objtype,objname))
            print(objdata)
        with open(fn,"w") as f:
            f.write(objdata)

class export(object):
    def __init__(self):
        mkdir(stdata["datadir"])
        for objtype,objdata in dbdata["sql"].items():
            datadir=os.path.join(stdata["datadir"],objtype)
            mkdir(datadir)
            for objname,objdesc in objdata.items():
                self.db2file(datadir,objtype,objname,objdesc)
        for objtype in os.listdir(stdata["datadir"]):
            if objtype not in dbdata["sql"]:
                print("%s not exists in database,maybe some error fund, check it! if need delete, do it yourself." %(objtype))
                continue
            datadir=os.path.join(stdata["datadir"],objtype)
            for objname in os.listdir(datadir):
                if objname not in dbdata["sql"][objtype]:
                    fn=os.path.join(datadir,objname)
                    print("delete %s !" %(fn))
                    os.unlink(fn)
    def db2file(self,datadir,objtype,objname,objdesc):
        fn=os.path.join(datadir,objname)
        if os.path.isfile(fn):
            data=open(fn).read()
            if data==objdesc:
                return
            diff=difflib.Differ()
            print("============ diff of %s.%s" %(objtype,objname))
            print("\n".join(diff.compare(data.split("\n"),objdesc.split("\n"))))
        else:
            print("============ find new: %s.%s" %(objtype,objname))
            print(objdesc)
        with open(fn,"w") as f:
            f.write(objdesc)

class render(object):
    def __init__(self):
        for t in dbdata["exp"]["TABLE"]:
            if not "table" in stdata or t["tname"].lower() in stdata["table"].split():
                self.rendertable(t)
    def rendertable(self,t):
        if "help" in stdata and stdata["help"].lower() in ["y","1"]:
            print(json.dumps(t,ensure_ascii=False,skipkeys=False,indent=4,cls=ComplexEncoder))
        tpl=""  #模板
        k=False
        for l in storidata:
            if l.startswith("start="):
                k=True
                continue
            if l.startswith("end="):
                break
            if k:
                tpl=tpl+l
        nt=jinja2.Template(tpl).render(t)  #新的文本
        lnt=nt.split("\n")
        sstart=jinja2.Template(stdata["start"]).render(t)
        send=jinja2.Template(stdata["end"]).render(t)
        if not re.search(sstart,lnt[0]):nt=sstart+"\n"+nt
        if not re.search(send,lnt[-1]):nt=nt+send
        nt=nt+"\n"
        f=open(stdata["file"])
        ft=f.readlines()
        newline=f.newlines
        f.close()
        k=False
        ls,le=-1,-1
        ot=""
        for i in range(len(ft)):
            if ls<0 and re.search(sstart,ft[i]):
                ls=i
            if ls>=0 and re.search(send,ft[i]) and (send!="" or ft[i].strip()==""):
                le=i
                if le>ls:
                    ot=ot+ft[i]
                else:
                    ot=ft[i]
                break
            if ls>=0:
                ot=ot+ft[i]
        if ot==nt:return
        if ot=="":
            ls=len(ft)
        f=open(stdata["file"],"wt")
        f.newline=newline
        for i in range(len(ft)):
            if i==ls:
                f.write(nt)
            if i<ls or i>le:
                f.write(ft[i])
        if ot=="":
            f.write(nt)
        f.close()

db=dblib()
ckd=checkdiff()
dbdata={}       #保存数据库里读到的数据
dbdata["sql"]={}
dbdata["exp"]={}
dbdata["exp"]["TABLE"]=[]
storidata=[]    #执行文件中的原始信息
stdata={}       #执行文件中解析过的信息
