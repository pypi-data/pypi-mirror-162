#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys,cx_Oracle,json
import database2text.tool as dbtt
from database2text.tool import *

class oracle(object):
    def ana_TABLE(otype):
        for oname, in db.exec("select object_name from user_objects where object_type=:ot",ot=otype):
            odata="create table %s\n(\n" %(oname)
            coldata=[]  #记录列数据，包括type类型，name列名，desc注释信息，size长度，ns名称+长度如name[5]这样
            maxcsize=db.res1("select max(length(column_name)) from all_tab_cols where owner='%s' and table_name='%s'" %(owner,oname))
            tdesc=db.res1("select comments from user_tab_comments where table_name=:1",[oname])
            oridata=[]
            for col in db.exec2("select * from all_tab_cols where owner='%s' and table_name='%s' order by column_id" %(owner,oname)):
                col["COLUMN_COMMENT"]=db.res1("select comments from user_col_comments where table_name=:n and column_name=:cn",n=oname,cn=col["COLUMN_NAME"])
                if col["DATA_DEFAULT"]!=None:
                    col["DATA_DEFAULT"]=col["DATA_DEFAULT"].strip()
                oridata.append(col)
            for column_name,data_type,char_length,data_precision,data_scale,nullable,default_length,data_default in db.exec("select column_name,data_type,char_length,data_precision,data_scale,nullable,default_length,data_default from all_tab_cols where owner='%s' and table_name='%s' order by column_id" %(owner,oname)):
                odata=odata+"  %s%*s" %(column_name,maxcsize-len(column_name)+1," ")
                ctype="char"
                cns="%s[%d]" %(column_name,char_length+1)
                desc=db.res1("select comments from user_col_comments where table_name=:n and column_name=:cn",n=oname,cn=column_name)
                if not desc:desc=""
                if data_type=="NUMBER":
                    if data_precision is not None and data_scale is not None:
                        if data_scale==0:
                            if data_precision<8:ctype="int"
                            else:ctype="long"
                            odata=odata+"NUMBER(%d)" %(data_precision)
                        else:
                            ctype="double"
                            odata=odata+"NUMBER(%d,%d)" %(data_precision,data_scale)
                    elif data_precision is None and data_scale==0:
                        ctype="long"
                        odata=odata+"INTEGER"
                    elif char_length==0:
                        ctype="long"
                        odata=odata+"NUMBER"
                    else:
                        print("table %s column %s type %s length %s %s %s" %(oname,column_name,data_type,char_length,data_precision,data_scale))
                        sys.exit(-1)
                    cns=column_name
                elif data_type in ("VARCHAR2","VARCHAR","CHAR","NVARCHAR2","NVARCHAR"):
                    if char_length==1:cns=column_name
                    odata=odata+"%s(%d)" %(data_type,char_length)
                elif data_type.startswith("TIMESTAMP"):
                    cns="%s[20]" %(column_name)
                    odata=odata+"%s" %(data_type)
                elif data_type in("DATE"):
                    cns="%s[20]" %(column_name)
                    odata=odata+"%s" %(data_type)
                elif data_type in("CLOB","BLOB","NCLOB"):
                    cns="%s[2000]" %(column_name)
                    odata=odata+"%s" %(data_type)
                elif data_type in ("FLOAT"):
                    ctype="double"
                    odata=odata+"FLOAT(%d)" %(data_precision)
                else:
                    print("table %s column %s type %s length %s %s %s" %(oname,column_name,data_type,char_length,data_precision,data_scale))
                    sys.exit(-1)
                if default_length:
                    odata=odata+" default %s" %(data_default.strip())
                if nullable=="N":
                    odata=odata+" not null"
                odata=odata+",\n"
                coldata.append({"type":ctype,"name":column_name,"ns":cns,"desc":desc})
            odata=odata[:-2]
            odata=odata+"\n);"
            dbdata["sql"]["TABLE"][oname]=odata
            dbdata["exp"]["TABLE"].append({"tname":oname,"tdesc":tdesc,"ori":oridata,"c":coldata})

    def ana_VIEW(otype):
        for oname, in db.exec("select object_name from user_objects where object_type=:ot",ot=otype):
            dbdata["sql"][otype][oname]=oracle.getobjtext(otype,oname)

    def getobjtext(otype,oname):
        c=db.conn.cursor()
        c.callproc('DBMS_METADATA.SET_TRANSFORM_PARAM',(-1, 'TABLESPACE',False))
        c.callproc("DBMS_METADATA.SET_TRANSFORM_PARAM",(-1,'STORAGE',False))
        c.callproc("DBMS_METADATA.SET_TRANSFORM_PARAM",(-1,'SEGMENT_ATTRIBUTES',False))
        c.callproc("DBMS_METADATA.SET_TRANSFORM_PARAM",(-1,'PRETTY',False))
        ssql=db.res1("SELECT dbms_metadata.get_ddl(:otype,:oname) FROM DUAL",otype=otype,oname=oname).read()
        return ssql

def readdata():
    for i in vars(oracle):
        if i.startswith("ana_"):
            otype=i[4:]
            dbdata["sql"][otype]={}
            getattr(oracle,i)(otype)

def connect():
    global owner
    owner=stdata["loginname"].upper()
    try:
        db.conn=cx_Oracle.connect(stdata["loginname"],stdata["password"],stdata["dbserver"])
    except:
        dbtt.quit("connect error!")

__all__=[]
