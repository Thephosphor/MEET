import pandas as pd
import numpy as np
import pymysql
import redis
conn = pymysql.connect(host='106.15.199.220', user='MEET', password='123456', database='meettable', charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)
r_t = redis.Redis(host='106.15.199.220', port=6379, password=123456, db=8)

a=pd.read_csv("../static/data/test1.csv")
qa=np.linalg.svd(a,full_matrices=0,compute_uv=1)[0]
bp=np.linalg.svd(a,full_matrices=0,compute_uv=1)[2]
qp=np.matmul(qa,bp)
for user_id in range(1,qa.shape[0]+1):
    qp_list=list(qp[user_id])
    list2=[]
    for i in qp_list:
        list2.append(i)
    list2.sort(reverse=True)
    print(list2[0:50])
    list3=[]
    for i in qp_list:
        if i in list2[0:50]:
            list3.append(qp_list.index(i)+1)
    for i in list3:
        key=user_id
        r_t.sadd(key,i)


