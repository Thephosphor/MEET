import pymysql
import time,datetime
import pandas as pd
conn = pymysql.connect(host='106.15.199.220', user='MEET', password='123456', database='meettable', charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute('select * from m_user_thought_relat')
a=cur.fetchall()
cur.execute('select * from m_user_message')
len_uid=len(cur.fetchall())
cur.execute('select * from m_thoughts_message')
len_tid=len(cur.fetchall())
print(len_uid,len_tid)
list2=[]
list1=[]
time_stamp=int(time.time())  #当前时间
print(time_stamp)
for i in range(len_uid):
    list1.append([])
    for j in range(len_tid):
        list1[i].append(0)
for i in range(len(a)):
    if a[i]['user_id'] not in list2:
        list2.append(a[i]['user_id'])
list2.sort()
for i in range(len_uid):
    for j in range(len(a)):
        time_now=a[j]['user_time']
        timeArray = time.strptime(time_now, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        if a[j]['user_id']==list2[i] and (time_stamp-timeStamp)<=31536000 and (time_stamp-timeStamp)>=0:
            print(time_stamp-timeStamp)
        s=int(a[j]['thought_id'])
        list1[i][s-1]=int(a[j]['score'])
list3=[]
for i in range(1,len_tid+1):
    list3.append(i)
test=pd.DataFrame(columns=list3,data=list1)
time_time=time.strftime('%Y%m%d',time.localtime(time.time()))
print(time_time)
test.to_csv('static/data/'+ time_time +'.csv')
print('数据处理完成')
