#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys,pymysql
import database2text.tool as dbtt
from database2text.tool import *

class mysql(object):
    def ana_TABLE(otype):
        for oname, in db.exec("show tables"):
            res=db.res1("show create table %s" %(oname))
            odata=res[1]
            oridata=[]
            coldata=[]
            tdesc=db.res1("SELECT TABLE_COMMENT FROM INFORMATION_SCHEMA.TABLES  WHERE TABLE_NAME ='%s' AND TABLE_SCHEMA = '%s'" %(oname,database))
            for i in db.exec2("select * from information_schema.COLUMNS where TABLE_SCHEMA='%s' and table_name='%s'" %(database,oname)):
                oridata.append(i)
            dbdata["sql"]["TABLE"][oname]=odata
            dbdata["exp"]["TABLE"].append({"tname":oname,"tdesc":tdesc,"ori":oridata,"c":coldata})
    def getobjtext(otype,oname):
        _,ssql=db.res1("show create %s %s" %(otype,oname))
        return ssql

def readdata():
    for i in vars(mysql):
        if i.startswith("ana_"):
            otype=i[4:]
            dbdata["sql"][otype]={}
            getattr(mysql,i)(otype)

def connect():
    global database
    database=stdata["database"]
    if "port" in stdata:
        stdata["port"]=int(stdata["port"])
    db.conn=pymysql.connect(**stdata)

def export(stdata,storidata):
    dbtt.export(stdata,storidata,dbdata)

__all__=[]
