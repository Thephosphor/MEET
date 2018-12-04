import pymysql
from django.shortcuts import HttpResponse, render, redirect
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.http import JsonResponse
from qiniu import Auth, put_file, etag
import qiniu.config
import shutil
from django.contrib.auth.models import User
import time
import datetime
import base64
import redis
import jieba
import urllib.request as reqt
import urllib.parse
from PIL import Image
from urllib.request import urlopen
import urllib3
import random
import json
import math
import sys
import pyttsx3
from rongcloud import RongCloud
from PIL import Image
from aip import AipSpeech
import wave
from pyaudio import PyAudio, paInt16
import difflib
import os
import re
import subprocess, numpy as np
from fr import AFRTest
from datetime import datetime

# 情感识别
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
qg_host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=YolDV4vwwFca0xiuZGtgOAR6&client_secret=xRftTq4KsyEOoLecNvG9I4MURHhVjsk1 '
qg_request = reqt.Request(qg_host)
qg_request.add_header('Content-Type', 'application/json; charset=UTF-8')
qg_response = urlopen(qg_request)
qg_content = qg_response.read()
qg_content_str = str(qg_content, encoding="utf-8")
###
qg_content_dir = eval(qg_content_str)
qg_access_token = qg_content_dir['access_token']
qg_http = urllib3.PoolManager()
qg_url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token=" + qg_access_token

# 聊天
app_key = 'z3v5yqkbz1bl0'
app_secret = 'eYPO08LjXqR'
rcloud = RongCloud(app_key, app_secret)

# redis
r = redis.Redis(host='106.15.199.220', port=6379, password=123456, db=5)
r_2 = redis.Redis(host='106.15.199.220', port=6379, password=123456, db=6)
r_t = redis.Redis(host='106.15.199.220', port=6379, password=123456, db=8)

list = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + [str(i) for i in range(10)]  # 大小写+数字

# 短信验证码
access_key = 'dTUG4Js2_j8eHnWoTTa_YpX7r7kWl-DAQ5laGKmL'
secret_key = 'tGvPiKf39om-0wsTnXqaMyCrVF4VBn2wwgf9TSet'
q = Auth(access_key, secret_key)
bucket_name = 'meet'
list_url = []
conn = pymysql.connect(host='106.15.199.220', user='MEET', password='123456', database='meettable', charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)  # 字典形式返回


def Verificationr(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        ver = str(random.randint(100000, 999999))
        keyr = "ver_%s" % phone
        r.setex(keyr, ver, 180)
        textmod = {"sid": "8c599d2fac5be71d8164161a35fe610f", "token": "0925e25422ec206501f868ee2f6e82e9",
                   "appid": "6e5755a1b7df4005af190d0cb6d0b54f", "templateid": "389822", "param": ver,
                   "mobile": phone}
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                       "Content-Type": "application/json"}
        req = reqt.Request(url='https://open.ucpaas.com/ol/sms/sendsms', data=textmod, headers=header_dict)
        res = reqt.urlopen(req)
        res = res.read()
        return HttpResponse(ver)
    else:
        return HttpResponse('验证码获取失败')


def register(request):
    if request.method == "GET":
        cur.execute('select user_phone from m_user_message')
        phone_list = cur.fetchall()
        phone_list1 = []
        for i in phone_list:
            phone_list1.append(i['user_phone'])
        return render(request, 'register.html', {'phone_list': phone_list1})
    else:
        value_1 = request.POST.get('phone')
        value_2 = request.POST.get('email')
        value_3 = request.POST.get('gender')
        value_4 = request.POST.get('birthday')
        value_5 = request.POST.get('pw1')
        user_code = request.POST.get('usercode')
        admin_code = request.POST.get('admincode')
        if value_1 and value_2 and value_3 and value_4 and value_5 and user_code:
            cur.execute('select * from m_user_message where user_phone=%s' % value_1)
            s = cur.fetchone()
            if s:
                return redirect('/register/')
            else:
                user_birth = value_4.split('-')
                user_birth_m = int(user_birth[1])
                user_birth_d = int(user_birth[2])
                if (user_birth_m == 3 and user_birth_d in range(21, 31)) or (
                        user_birth_m == 4 and user_birth_d in range(1, 19)):
                    user_star = "白羊座"
                elif (user_birth_m == 4 and user_birth_d in range(20, 30)) or (
                        user_birth_m == 5 and user_birth_d in range(1, 20)):
                    user_star = "金牛座"
                elif (user_birth_m == 5 and user_birth_d in range(21, 31)) or (
                        user_birth_m == 6 and user_birth_d in range(1, 20)):
                    user_star = "双子座"
                elif (user_birth_m == 6 and user_birth_d in range(21, 30)) or (
                        user_birth_m == 7 and user_birth_d in range(1, 21)):
                    user_star = "巨蟹座"
                elif (user_birth_m == 7 and user_birth_d in range(22, 31)) or (
                        user_birth_m == 8 and user_birth_d in range(1, 22)):
                    user_star = "狮子座"
                elif (user_birth_m == 8 and user_birth_d in range(23, 31)) or (
                        user_birth_m == 9 and user_birth_d in range(1, 22)):
                    user_star = "处女座"
                elif (user_birth_m == 9 and user_birth_d in range(23, 30)) or (
                        user_birth_m == 10 and user_birth_d in range(1, 22)):
                    user_star = "天秤座"
                elif (user_birth_m == 10 and user_birth_d in range(23, 31)) or (
                        user_birth_m == 11 and user_birth_d in range(1, 21)):
                    user_star = "天蝎座"
                elif (user_birth_m == 11 and user_birth_d in range(22, 30)) or (
                        user_birth_m == 12 and user_birth_d in range(1, 21)):
                    user_star = "射手座"
                elif (user_birth_m == 12 and user_birth_d in range(22, 31)) or (
                        user_birth_m == 1 and user_birth_d in range(1, 19)):
                    user_star = "摩羯座"
                elif (user_birth_m == 1 and user_birth_d in range(20, 31)) or (
                        user_birth_m == 2 and user_birth_d in range(1, 18)):
                    user_star = "水瓶座"
                else:
                    user_star = "双鱼座"
                keyr = "ver_%s" % value_1
                _ver = r.get(keyr)
                if _ver:
                    _ver = _ver.decode('utf-8')
                    if user_code == _ver:
                        r.delete(keyr)
                        if admin_code == "111111":
                            state = 1
                            cur.execute(
                                "insert into m_user_message(user_phone,user_email,user_sex,user_birth,user_pass,user_admin,user_star,user_blood) values(%s,%s,%s,%s,%s,%s,%s,%s)",
                                [value_1, value_2, value_3, value_4, value_5, state, user_star, ' '])
                            cur.execute('select user_id from m_user_message where user_phone=%s' % value_1)
                            a = cur.fetchone()['user_id']
                            session_online_time = 0.00
                            cur.execute('insert into m_task_once(user_id) values(%s)', [a])
                            cur.execute('insert into m_task_daily(user_id,task_1,task_2) values(%s,%s,%s)', [a, 1, 1])
                            cur.execute('insert into m_user_online_time(user_id,session_online_time) values(%s,%s)',
                                        [a, session_online_time])
                            if value_3 == '保密':
                                cur.execute(
                                    'insert into m_user_style(user_id,user_head,user_sign,user_label) values(%s,%s,%s,%s)',
                                    [a, 'http://file.g3.xmgc360.com/Head_portrait4.jpg', ' ', ' '])
                            elif value_3 == '女':
                                cur.execute(
                                    'insert into m_user_style(user_id,user_head,user_sign,user_label) values(%s,%s,%s,%s)',
                                    [a, 'http://file.g3.xmgc360.com/Head_portrait25.jpg', ' ', ' '])
                            elif value_3 == '男':
                                cur.execute(
                                    'insert into m_user_style(user_id,user_head,user_sign,user_label) values(%s,%s,%s,%s)',
                                    [a, 'http://file.g3.xmgc360.com/Head_portrait27.jpg', ' ', ' '])
                            conn.commit()
                            rs = rcloud.User.getToken(userId=str(a), name='username',
                                                      portraitUri='http://www.rongcloud.cn/images/logo.png')
                            R = str(rs)
                            R = R.replace("{", "")
                            R = R.replace("}", "")
                            R = R.replace("200", "'200'")
                            R = R.replace(",", "")
                            R = R.replace(":", "")
                            R = R.replace("'", "")
                            lists = R.split(" ")
                            cur.execute('update m_user_style set user_token=%s where user_id=%s', [lists[5], a])
                            numeric_alphabet = "0123456789abcdefghijklmnopqrstuvwxyz_"
                            sessionval = ''.join(str(i) for i in random.sample(numeric_alphabet, 8))
                            request.session['phone'] = str(value_1) + sessionval + user_code
                            session_desc = request.session['phone']
                            session_time_start = time.time()
                            cur.execute(
                                "insert into m_user_online(user_id,session_desc,session_time_start) values ('%s','%s','%s')" % (
                                    a, session_desc, session_time_start))
                            conn.commit()
                        else:
                            cur.execute(
                                "insert into m_user_message(user_phone,user_email,user_sex,user_birth,user_pass,user_star,user_blood) values(%s,%s,%s,%s,%s,%s,%s)",
                                [value_1, value_2, value_3, value_4, value_5, user_star, ' '])
                            cur.execute('select user_id from m_user_message where user_phone=%s' % value_1)
                            a = cur.fetchone()['user_id']
                            session_online_time = 0.00
                            cur.execute('insert into m_task_once(user_id) values(%s)', [a])
                            cur.execute('insert into m_task_daily(user_id,task_1,task_2) values(%s,%s,%s)', [a, 1, 1])
                            cur.execute('insert into m_user_online_time(user_id,session_online_time) values(%s,%s)',
                                        [a, session_online_time])
                            if value_3 == '保密':
                                cur.execute(
                                    'insert into m_user_style(user_id,user_head,user_sign,user_label) values(%s,%s,%s,%s)',
                                    [a, 'http://file.g3.xmgc360.com/Head_portrait4.jpg', ' ', ' '])
                            elif value_3 == '女':
                                cur.execute(
                                    'insert into m_user_style(user_id,user_head,user_sign,user_label) values(%s,%s,%s,%s)',
                                    [a, 'http://file.g3.xmgc360.com/Head_portrait25.jpg', ' ', ' '])
                            elif value_3 == '男':
                                cur.execute(
                                    'insert into m_user_style(user_id,user_head,user_sign,user_label) values(%s,%s,%s,%s)',
                                    [a, 'http://file.g3.xmgc360.com/Head_portrait27.jpg', ' ', ' '])
                            conn.commit()
                            rs = rcloud.User.getToken(userId=str(a), name='username',
                                                      portraitUri='http://www.rongcloud.cn/images/logo.png')
                            R = str(rs)
                            R = R.replace("{", "")
                            R = R.replace("}", "")
                            R = R.replace("200", "'200'")
                            R = R.replace(",", "")
                            R = R.replace(":", "")
                            R = R.replace("'", "")
                            lists = R.split(" ")
                            print(lists[5])
                            cur.execute('update m_user_style set user_token=%s where user_id=%s', [lists[5], a])
                            numeric_alphabet = "0123456789abcdefghijklmnopqrstuvwxyz_"
                            sessionval = ''.join(str(i) for i in random.sample(numeric_alphabet, 8))
                            request.session['phone'] = str(value_1) + sessionval + user_code
                            session_desc = request.session['phone']
                            session_time_start = time.time()
                            cur.execute(
                                "insert into m_user_online(user_id,session_desc,session_time_start) values ('%s','%s','%s')" % (
                                    a, session_desc, session_time_start))
                            conn.commit()
                        return redirect('/cb_ceshi')
        return redirect('/register')


def Verificationl(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        vel = str(random.randint(100000, 999999))
        keyl = "vel_%s" % phone
        r.setex(keyl, vel, 180)
        textmod = {"sid": "8c599d2fac5be71d8164161a35fe610f", "token": "0925e25422ec206501f868ee2f6e82e9",
                   "appid": "6e5755a1b7df4005af190d0cb6d0b54f", "templateid": "389838", "param": vel,
                   "mobile": phone}
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                       "Content-Type": "application/json"}
        req = reqt.Request(url='https://open.ucpaas.com/ol/sms/sendsms', data=textmod, headers=header_dict)
        res = reqt.urlopen(req)
        res = res.read()
        print(res)
        return HttpResponse(vel)
    else:
        return HttpResponse('验证码获取失败')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        phone = request.POST.get('phone')
        password = request.POST.get('pw1')
        user_code = request.POST.get('usercode')
        if phone and password and user_code:
            conn.ping(reconnect=True)
            cur.execute('select * from m_user_message where user_phone=%s', [phone, ])
            data = cur.fetchone()
            user_id = data['user_id']
            if data['user_state'] == 1:
                return redirect('/login/')
            else:
                if data and (phone in data['user_phone'] and password in data['user_pass']):
                    keyl = "vel_%s" % phone
                    _vel = r.get(keyl)
                    if _vel:
                        _vel = _vel.decode('utf-8')
                        if user_code == _vel:
                            r.delete(keyl)
                            numeric_alphabet = "0123456789abcdefghijklmnopqrstuvwxyz_"
                            sessionval = ''.join(str(i) for i in random.sample(numeric_alphabet, 8))
                            request.session['phone'] = str(phone) + sessionval + user_code
                            session_desc = request.session['phone']
                            session_time_start = time.time()
                            cur.execute('update m_user_message set user_online_state=1 where user_id=%s' % user_id)
                            cur.execute(
                                "insert into m_user_online(user_id,session_desc,session_time_start) values ('%s','%s','%s')" % (
                                    user_id, session_desc, session_time_start))
                            conn.commit()
                            return redirect('/fit/')
                        else:
                            return redirect('/login/')
                    else:
                        return redirect('/login/')
                else:
                    return redirect('/login/')
        else:
            return redirect('/login/')


def Verificationc(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        vec = str(random.randint(100000, 999999))
        keyc = "vec_%s" % phone
        r.setex(keyc, vec, 180)
        textmod = {"sid": "8c599d2fac5be71d8164161a35fe610f", "token": "0925e25422ec206501f868ee2f6e82e9",
                   "appid": "6e5755a1b7df4005af190d0cb6d0b54f", "templateid": "389839", "param": vec,
                   "mobile": phone}
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                       "Content-Type": "application/json"}
        req = reqt.Request(url='https://open.ucpaas.com/ol/sms/sendsms', data=textmod, headers=header_dict)
        res = reqt.urlopen(req)
        res = res.read()
        print(res)
        return HttpResponse(vec)
    else:
        return HttpResponse('验证码获取失败')


def chazhao(request):
    phone = request.POST.get('phone')
    conn.ping(reconnect=True)
    cur.execute('select * from m_user_message where user_phone=%s' % phone)
    p = cur.fetchone()
    if p != None:
        return HttpResponse('true')
    else:
        return HttpResponse('false')


def login_chazhaop(request):
    phone = request.POST.get('phone')
    conn.ping(reconnect=True)
    cur.execute('select * from m_user_message where user_phone=%s' % phone)
    p = cur.fetchone()
    if p != None:  # 是否注册
        cur.execute('select * from m_user_style where user_id=%s'%(p['user_id']))
        a=cur.fetchone()
        if p['user_state'] == 1:
            return JsonResponse({'foo': 'fenghao'})
        elif p['user_online_state'] == 1:
            return JsonResponse({'foo': 'online'})
        elif p['user_online_state'] == 0:
            # return JsonResponse({'foo': 'noonline'})
            if a['user_face']==1:
                return JsonResponse({'foo': 'face'})
            elif a['user_face']==0:
                return JsonResponse({'foo': 'noface'})
    else:  # 未注册
        return JsonResponse({'foo': 'noregister'})


def login_chazhaom(request):
    phone = request.POST.get('phone')
    pasw = request.POST.get('pasw')
    if pasw and phone:
        conn.ping(reconnect=True)
        cur.execute('select user_pass from m_user_message where user_phone=%s' % phone)
        p = cur.fetchone()['user_pass']
        if p == pasw:  # 密码正确
            return HttpResponse('true')
        else:
            return HttpResponse('false')


def chge_pwd(request):
    if request.method == 'GET':
        conn.ping(reconnect=True)
        cur.execute('select user_phone from m_user_message')
        phone_list = cur.fetchall()
        phone_list1 = []
        for i in phone_list:
            phone_list1.append(i['user_phone'])
        return render(request, 'chge_pwd.html', {'phone_list': phone_list1})
    else:
        phone = request.POST.get('phone')
        pw = request.POST.get('userpass')
        user_code = request.POST.get('usercode')
        if phone and pw and user_code:
            conn.ping(reconnect=True)
            cur.execute('select user_phone,user_pass from m_user_message where user_phone=%s', [phone, ])
            data = cur.fetchone()
            if data and phone in data['user_phone']:
                keyc = "vec_%s" % phone
                _vec = r.get(keyc)
                if _vec:
                    _vec = _vec.decode('utf-8')
                    if user_code == _vec:
                        r.delete(keyc)
                        cur.execute('update m_user_message set user_pass=%s where user_phone=%s', [pw, phone])
                        conn.commit()
                        return redirect('/login/')
                    else:
                        return redirect('/chge_pwd/')
                else:
                    return redirect('/chge_pwd/')
            else:
                return redirect('/chge_pwd/')
        else:
            return redirect('/chge_pwd/')


def fit(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_user_deepth_state')
        list1 = cur.fetchall()
        list10 = []
        if list1:
            cur.execute('select user_id from m_tests_result where test_deepth_state=1')
            list7 = cur.fetchall()
            list8 = []
            for i in list7:
                list8.append(i['user_id'])
            for i in range(len(list1)):
                if list1[i]['user_id'] in list8:
                    list10.append(list1[i])
        cur.execute('select * from m_user_deepth_state where user_id=%s' % user_id)
        asd = cur.fetchone()
        list4 = []
        list5 = []
        list6 = []
        b = 0
        if list1 and asd:
            for i in range(len(list10)):
                for j in range(1, 27):
                    s = (list10[i]['test_' + str(j)] - asd['test_' + str(j)]) ** 2
                    list4.append(s)
                    b += int(s)
                c = math.sqrt(b / 26)
                d = 0.5 + (1 - c) * 0.5
                list5.append(d)
                list1[i]['pipei'] = d
                list4 = []
                b = 0
            for i in range(len(list5)):
                a = list5.index(max(list5))
                list6.append(list10[a])
                list5.remove(list5[a])
                list10.remove(list10[a])
                if i == 12:
                    break
        cur.execute('select * from m_tests_result where user_id=%s' % user_id)
        a = cur.fetchone()['test_result_before']
        cur.execute('select * from m_tests_result where test_result_before=%s', [a])
        users_list0 = cur.fetchall()
        users_list = []
        for i in range(len(users_list0)):
            users_list.append(users_list0[i])
            if i == 12:
                break
        cur.execute('select user_lh_id from m_user_lh where user_id=%s' % user_id)
        pl = cur.fetchall()
        state = 0
        users_list3 = []
        users_list2 = []
        if list6:
            state = 1
        if pl:
            loa = []
            for i in pl:
                loa.append(i['user_lh_id'])
            for i in range(len(users_list)):
                if users_list[i]['user_id'] not in loa:
                    users_list2.append(users_list[i])
            users_list = users_list2
        elif pl and list6:
            loa = []
            for i in pl:
                loa.append(i['user_lh_id'])
            for i in range(len(list6)):
                if list6[i]['user_id'] not in loa:
                    users_list3.append(list6[i])
            list6 = users_list3
        return render(request, 'fit.html',
                      {'style_list': style_list, 'user_id': user_id, 'user_list': user_list, 'users_list': users_list,
                       'list6': list6, 'state': state})
    else:
        return redirect('/login/')


def fit_select(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        sx1 = request.POST.get('sx11')
        sx2 = request.POST.get('sx21')
        sx3 = request.POST.get('sx31')
        sx4 = request.POST.get('sx41')
        user_list1, user_list2, user_list3, user_list4 = [], [], [], []
        if sx1:  # 在线
            cur.execute('select * from m_user_message where user_online_state=1')
            user_list1 = cur.fetchall()
        if sx2:  # 性别
            cur.execute('select * from m_user_message where user_sex="%s"' % sx2)
            user_list2 = cur.fetchall()
        if sx3:  # 年龄
            t = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            t = t.split('-')
            tt = int(t[0]) * 365 + int(t[0]) * 30 + int(t[0])
            cur.execute('select * from m_user_message')
            y = cur.fetchall()
            if sx3 == '18-24':
                for i in y:
                    yy = i['user_birth'].split('-')
                    ys = int(yy[0]) * 365 + int(yy[0]) * 30 + int(yy[0])
                    if (tt - ys) >= 6570 and (tt - ys) < 8760:
                        user_list3.append(i)
            elif sx3 == '24-35':
                for i in y:
                    yy = i['user_birth'].split('-')
                    ys = int(yy[0]) * 365 + int(yy[0]) * 30 + int(yy[0])
                    if (tt - ys) >= 8760 and (tt - ys) < 12775:
                        user_list3.append(i)
            elif sx3 == '其他':
                for i in y:
                    yy = i['user_birth'].split('-')
                    ys = int(yy[0]) * 365 + int(yy[0]) * 30 + int(yy[0])
                    if (tt - ys) < 6570 or (tt - ys) >= 12775:
                        user_list3.append(i)
        if sx4:  # 星座
            cur.execute('select * from m_user_message where user_star="%s"' % sx4)
            user_list4 = cur.fetchall()
        users_list = []
        if user_list1 != [] and user_list2 == [] and user_list3 == [] and user_list4 == []:  # 1000
            users_list = user_list1
        if user_list1 == [] and user_list2 != [] and user_list3 == [] and user_list4 == []:  # 0100
            users_list = user_list2
        if user_list1 == [] and user_list2 == [] and user_list3 != [] and user_list4 == []:  # 0010
            users_list = user_list3
        if user_list1 == [] and user_list2 == [] and user_list3 == [] and user_list4 != []:  # 0001
            users_list = user_list4
        if user_list1 != [] and user_list2 != [] and user_list3 == [] and user_list4 == []:  # 1100
            for i in user_list1:
                if i in user_list2:
                    users_list.append(i)
        if user_list1 != [] and user_list2 == [] and user_list3 != [] and user_list4 == []:  # 1010
            for i in user_list1:
                if i in user_list3:
                    users_list.append(i)
        if user_list1 != [] and user_list2 == [] and user_list3 == [] and user_list4 != []:  # 1001
            for i in user_list1:
                if i in user_list4:
                    users_list.append(i)
        if user_list1 == [] and user_list2 != [] and user_list3 != [] and user_list4 == []:  # 0110
            for i in user_list3:
                if i in user_list2:
                    users_list.append(i)
        if user_list1 == [] and user_list2 != [] and user_list3 == [] and user_list4 != []:  # 0101
            for i in user_list4:
                if i in user_list2:
                    users_list.append(i)
        if user_list1 == [] and user_list2 == [] and user_list3 != [] and user_list4 != []:  # 0011
            for i in user_list3:
                if i in user_list2:
                    users_list.append(i)
        if user_list1 != [] and user_list2 != [] and user_list3 != [] and user_list4 == []:  # 1110
            for i in user_list1:
                if i in user_list2 and i in user_list3:
                    users_list.append(i)
        if user_list1 != [] and user_list2 != [] and user_list3 == [] and user_list4 != []:  # 1101
            for i in user_list1:
                if i in user_list2 and i in user_list4:
                    users_list.append(i)
        if user_list1 != [] and user_list2 == [] and user_list3 != [] and user_list4 != []:  # 1011
            for i in user_list1:
                if i in user_list4 and i in user_list3:
                    users_list.append(i)
        if user_list1 == [] and user_list2 != [] and user_list3 != [] and user_list4 != []:  # 0111
            for i in user_list4:
                if i in user_list2 and i in user_list3:
                    users_list.append(i)
        if user_list1 != [] and user_list2 != [] and user_list3 != [] and user_list4 != []:  # 1111
            for i in user_list1:
                if i in user_list2 and i in user_list3 and i in user_list4:
                    users_list.append(i)
        return render(request, 'fit_select.html',
                      {'style_list': style_list, 'user_id': user_id, 'user_list': user_list, 'users_list': users_list,
                       'sx_1': sx1, 'sx_2': sx2, 'sx_3': sx3, 'sx_4': sx4})
    else:
        return redirect('/login/')


def Alogout(request):
    if request.method == "POST":
        state = request.POST.get('state')
        if state == "1":
            var = request.session.get('phone')
            conn.ping(reconnect=True)
            cur.execute("select session_time_start from m_user_online where session_desc=%s", [var, ])
            data = cur.fetchone()
            session_time_start = data['session_time_start']
            cur.execute("select user_id from m_user_online where session_desc=%s", [var, ])
            data = cur.fetchone()
            user_id = data['user_id']
            cur.execute("update m_user_message set user_online_state=%s where user_id=%s", [0, user_id])
            conn.commit()
            del request.session['phone']
            session_time_end = time.time()
            session_time_once = float(session_time_end) - float(session_time_start)
            cur.execute("select session_online_time from m_user_online_time where user_id=%s", [user_id, ])
            get_session_online_time = cur.fetchone()
            session_online_time_zs = 0.00
            session_online_time = float(get_session_online_time['session_online_time']) + session_time_once
            cur.execute(
                "update m_user_online_time set session_online_time=%s,session_online_time_zs=%s where user_id=%s",
                [session_online_time, session_online_time_zs, user_id])
            conn.commit()
            cur.execute("update m_user_online set session_time_end=%s,session_time_once=%s where session_desc=%s",
                        [session_time_end, session_time_once, var])
            conn.commit()
            return redirect('/login/')
    else:
        var = request.session.get('phone')
        conn.ping(reconnect=True)
        cur.execute("select session_time_start from m_user_online where session_desc=%s", [var, ])
        data = cur.fetchone()
        session_time_start = data['session_time_start']
        cur.execute("select user_id from m_user_online where session_desc=%s", [var, ])
        data = cur.fetchone()
        user_id = data['user_id']
        user_online_state = 0
        cur.execute("update m_user_message set user_online_state=%s where user_id=%s", [user_online_state, user_id])
        conn.commit()
        session_time_end = time.time()
        session_time_once = float(session_time_end) - float(session_time_start)
        cur.execute("select session_online_time from m_user_online_time where user_id=%s", [user_id, ])
        get_session_online_time = cur.fetchone()
        session_online_time_zs = 0.00
        session_online_time = float(get_session_online_time['session_online_time']) + session_time_once
        cur.execute("update m_user_online_time set session_online_time=%s,session_online_time_zs=%s where user_id=%s",
                    [session_online_time, session_online_time_zs, user_id])
        conn.commit()
        cur.execute("update m_user_online set session_time_end=%s,session_time_once=%s where session_desc=%s",
                    [session_time_end, session_time_once, var])
        conn.commit()
        del request.session['phone']
        return redirect('/login/')


def cs(request):
    return render(request, '3211.html')


def css(request):
    x = request.POST.get('x')
    response = JsonResponse({'foo': 'bar'})
    return response


def shouye(request):
    return render(request, 'shouye.html')


def quwei_after(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        id = request.GET.get('test_subject_id', '317')
        cur.execute('select * from m_test_interest_after')
        cs_list = cur.fetchall()
        cur.execute('select * from m_test_interest_after where test_subject_id=%s', [id])
        cs_list1 = cur.fetchone()
        # cs_list是列表形式，cs_list1无列表
        return render(request, 'quweiceshi_after.html',
                      {'cs_list': cs_list, 'cs_list1': cs_list1, 'user_id': user_id, 'style_list': style_list,
                       'user_list': user_list})
    else:
        return redirect('/login/')


def jifenshop(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute("select session_time_start from m_user_online where session_desc=%s", [char, ])
        start_time = cur.fetchone()
        new_time = time.time()
        cur.execute("select session_online_time from m_user_online_time where user_id=%s", [user_id, ])
        get_session_online_time = cur.fetchone()
        session_online_time_zs = float(new_time) - float(start_time['session_time_start'])
        cur.execute("update m_user_online_time set session_online_time_zs=%s where user_id=%s",
                    [session_online_time_zs, user_id])
        conn.commit()
        session_online_time = float(get_session_online_time['session_online_time']) + session_online_time_zs
        state = 1
        cur.execute("select * from m_task_once where user_id=%s", [user_id, ])
        task_list_state = cur.fetchone()
        task_state_5 = task_list_state['task_5']
        if task_state_5 == 0:
            if session_online_time > 36000 and session_online_time < 108000:
                cur.execute("update m_task_once set task_5=%s where user_id=%s", [state, user_id])
                conn.commit()
        task_state_6 = task_list_state['task_6']
        if task_state_6 == 0:
            if session_online_time > 108000 and session_online_time < 180000:
                cur.execute("update m_task_once set task_6=%s where user_id=%s", [state, user_id])
                conn.commit()
        task_state_7 = task_list_state['task_7']
        if task_state_7 == 0:
            if session_online_time > 180000 and session_online_time < 356400:
                cur.execute("update m_task_once set task_7=%s where user_id=%s", [state, user_id])
                conn.commit()
        task_state_8 = task_list_state['task_8']
        if task_state_8 == 0:
            if session_online_time > 356400:
                cur.execute("update m_task_once set task_8=%s where user_id=%s", [state, user_id])
                conn.commit()
        cur.execute("select count(*) from m_user_guanzhu where follow_id=%s" % user_id)
        follow_id_list = cur.fetchone()
        sa = follow_id_list['count(*)']
        task_state_4 = task_list_state['task_4']
        if task_state_4 == 0:
            if sa >= 100:
                cur.execute("update m_task_once set task_4=%s where user_id=%s", [state, user_id])
                conn.commit()
        cur.execute("select * from m_thoughts_message where user_id=%s", [user_id, ])
        thoughts_mes_list = cur.fetchall()
        len_thonght = len(thoughts_mes_list)
        task_state_3 = task_list_state['task_3']
        if task_state_3 == 0:
            if len_thonght >= 100:
                cur.execute("update m_task_once set task_3=%s where user_id=%s", [state, user_id])
                conn.commit()
        tt = datetime.now().timetuple()
        unix_ts = time.mktime(tt)
        time_chat_start = unix_ts - tt.tm_hour * 60 * 60 - tt.tm_min * 60 - tt.tm_sec  # 获取今天零点时间戳
        time_chat_end = time_chat_start + 60 * 60 * 24  # 获取明天零点时间戳
        cur.execute("select * from m_chatroom where user_sent_id=%s", [user_id, ])
        chat_list = cur.fetchall()
        if chat_list:
            chat_list_count = []
            for row in chat_list:
                time_chat = row['chat_time']
                timeArray = time.strptime(time_chat, "%Y-%m-%d %H:%M:%S")  # 转换格式
                timeStamp = int(time.mktime(timeArray))
                if timeStamp > time_chat_start and timeStamp < time_chat_end:
                    chat_list_count.append(timeStamp)
            if len(chat_list_count) >= 50:
                task_state_2 = 1
                cur.execute("update m_task_daily set task_2=%s where user_id=%s", [task_state_2, user_id])
                conn.commit()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        cur.execute('select * from m_task_message')
        task_list = cur.fetchall()
        cur.execute('select * from m_integral_shop')
        shop_list = cur.fetchall()
        cur.execute("select * from m_task_daily where user_id=%s", [user_id, ])
        task_list_daily = cur.fetchone()
        cur.execute("select * from m_task_once where user_id=%s", [user_id, ])
        task_list_once = cur.fetchone()
        return render(request, 'jifenshop.html',
                      {"task_list": task_list, 'shop_list': shop_list, 'user_id': user_id, 'style_list': style_list,
                       'user_list': user_list, 'task_list_daily': task_list_daily, 'task_list_once': task_list_once})
    else:
        return redirect('/login/')


def integral_get(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        integral_get_id = request.GET.get('task_id')
        integral_get_val = request.GET.get('task_integral')
        cur.execute("select user_integral from m_user_message where user_id=%s", [user_id, ])
        user_integral_data = cur.fetchone()
        user_core = user_integral_data['user_integral']
        user_integral = user_core + int(integral_get_val)
        cur.execute("update m_user_message set user_integral=%s where user_id=%s", [user_integral, user_id])
        conn.commit()
        task_state = 0
        task_state_once = 2
        if integral_get_id == '1':
            cur.execute("update m_task_daily set task_1=%s where user_id=%s", [task_state, user_id])
            conn.commit()
        elif integral_get_id == '2':
            cur.execute("update m_task_daily set task_2=%s where user_id=%s", [task_state, user_id])
            conn.commit()
        elif integral_get_id == '3':
            cur.execute("update m_task_once set task_3=%s where user_id=%s", [task_state_once, user_id])
            conn.commit()
        elif integral_get_id == '4':
            cur.execute("update m_task_once set task_4=%s where user_id=%s", [task_state_once, user_id])
            conn.commit()
        elif integral_get_id == '5':
            cur.execute("update m_task_once set task_5=%s where user_id=%s", [task_state_once, user_id])
            conn.commit()
        elif integral_get_id == '6':
            cur.execute("update m_task_once set task_6=%s where user_id=%s", [task_state_once, user_id])
            conn.commit()
        elif integral_get_id == '7':
            cur.execute("update m_task_once set task_7=%s where user_id=%s", [task_state_once, user_id])
            conn.commit()
        return redirect('/jifenshop')


def ls_xiadan(request):
    if request.method == "GET":
        char = request.session.get('phone')
        if char:
            conn.ping(reconnect=True)
            cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
            data = cur.fetchone()
            user_id = data['user_id']
            cur.execute('select * from m_shop_already where user_id=%s', [user_id, ])
            commodity_list = cur.fetchall()
            cur.execute('select * from m_integral_shop')
            commodity_mes_list = cur.fetchall()
            cur.execute('select * from m_user_style')
            style_list = cur.fetchall()
            cur.execute('select * from m_user_message where user_id=%s' % user_id)
            user_list = cur.fetchone()
            return render(request, 'ls_xiadan.html',
                          {'commodity_list': commodity_list, 'user_id': user_id, 'style_list': style_list,
                           'user_list': user_list, 'commodity_mes_list': commodity_mes_list})


def del_xiadan(request):
    id = request.GET.get('id')
    cur.execute('delete from m_shop_already where id=%s', [id, ])
    conn.commit()
    return redirect('/ls_xiadan')


def xiadan(request):
    if request.method == 'GET':
        char = request.session.get('phone')
        if char:
            conn.ping(reconnect=True)
            cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
            data = cur.fetchone()
            user_id = data['user_id']
            id = request.GET.get('commodity_id')
            cur.execute('select * from m_user_style')
            style_list = cur.fetchall()
            cur.execute('select * from m_user_message where user_id=%s' % user_id)
            user_list = cur.fetchone()
            cur.execute('select * from m_integral_shop where commodity_id=%s', [id])
            shop_list = cur.fetchone()
            cur.execute('select user_name,user_addr,user_addr_phone from m_user_addr where user_id=%s' % user_id)
            user_addr_list = cur.fetchone()
            return render(request, 'xiadan.html',
                          {"shop_list": shop_list, 'user_id': user_id, 'style_list': style_list, 'user_list': user_list,
                           'user_addr_list': user_addr_list})
        else:
            return render(request, 'login.html')
    else:
        char = request.session.get('phone')
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        commodity_id = request.POST.get('commodityid')
        cur.execute("insert into m_shop_already(user_id,commodity_id) values(%s,%s)", [user_id, commodity_id])
        conn.commit()
        user_name = request.POST.get('addrname')
        user_addr = request.POST.get('addraddr')
        user_addr_phone = request.POST.get('addrphone')
        user_name_new = request.POST.get('addrnamenew')
        user_addr_new = request.POST.get('addraddrnew')
        user_addr_phone_new = request.POST.get('addrphonenew')
        if user_name == '':
            cur.execute(
                "INSERT INTO m_user_addr(user_id,user_name,user_addr,user_addr_phone)VALUES('%s','%s','%s','%s')" % (
                    user_id, user_name_new, user_addr_new, user_addr_phone_new))
            conn.commit()
        else:
            if user_name_new == '':
                cur.execute('update m_user_addr set user_name=%s,user_addr=%s,user_addr_phone=%s where user_id=%s',
                            [user_name, user_addr, user_addr_phone, user_id])
                conn.commit()
            else:
                cur.execute('update m_user_addr set user_name=%s,user_addr=%s,user_addr_phone=%s where user_id=%s',
                            [user_name_new, user_addr_new, user_addr_phone_new, user_id])
                conn.commit()
        cur.execute("select * from m_user_message where user_id=%s", [user_id, ])
        user_mes_list = cur.fetchone()
        user_integral_val = user_mes_list['user_integral']
        cur.execute("select * from m_integral_shop where commodity_id=%s", [commodity_id, ])
        commodity_mes_list = cur.fetchone()
        commodity_cost_val = commodity_mes_list['commodity_cost']
        user_integral = float(user_integral_val) - float(commodity_cost_val)
        cur.execute("update m_user_message set user_integral=%s where user_id=%s", [user_integral, user_id])
        conn.commit()
        return redirect('/ls_xiadan')


def cb_ceshi(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        skip_id = request.GET.get('skip_id', '0')
        if int(skip_id) <= 12:
            cur.execute('select * from m_test_before where test_subject_id=%s', [skip_id])
            cs_list = cur.fetchone()
            return render(request, 'cb_ceshi.html',
                          {'cs_list': cs_list, 'user_id': user_id, 'style_list': style_list, 'user_list': user_list})
        else:
            cur.execute('select * from m_test_before where test_subject_id=%s', [skip_id])
            cs_list = cur.fetchone()
            cur.execute('update m_user_message set user_online_state=1 where user_id=%s' % user_id)
            cur.execute('insert into m_tests_result(user_id,test_result_before,test_result) values("%s","%s","%s")' % (
                user_id, cs_list["test_subject"], cs_list["test_subject"]))
            conn.commit()
            return render(request, 'cb_ceshi_jieguo.html',
                          {'cs_list': cs_list, 'user_id': user_id, 'style_list': style_list, 'user_list': user_list})
    else:
        return redirect('/login/')


def sd_ceshi(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_tests_result where user_id=%s' % user_id)
        deepth_state = cur.fetchone()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        skip_id = request.GET.get('skip_id', '0')
        if deepth_state['test_deepth_state'] == 0:
            cur.execute('select * from m_user_deepth_state where user_id=%s' % user_id)
            s = cur.fetchone()
            if not s:
                cur.execute('insert into m_user_deepth_state(user_id) values("%s")' % user_id)
                conn.commit()
            if int(skip_id) <= 25:
                cur.execute('select * from m_test_deepth where test_subject_id=%s', [skip_id])
                cs_list = cur.fetchone()
                ans = request.GET.get('ans')
                if ans:
                    sa = int(skip_id) + 1
                    lis = 'test_' + str(sa)
                    if ans == '1':
                        cur.execute('update m_user_deepth_state set %s=1 where user_id=%s' % (lis, user_id))
                    elif ans == '-1':
                        cur.execute('update m_user_deepth_state set %s=-1 where user_id=%s' % (lis, user_id))
                    conn.commit()
                return render(request, 'sd_ceshi.html',
                              {'cs_list': cs_list, 'user_id': user_id, 'style_list': style_list, 'user_list': user_list,
                               'deepth_state': deepth_state})
            else:
                cur.execute('select * from m_test_deepth where test_subject_id=%s', [skip_id])
                cs_list = cur.fetchone()
                a = cs_list["test_subject"]
                cur.execute('update m_tests_result set test_result_deepth=%s,test_deepth_state=%s where user_id=%s',
                            [a, 1, user_id])
                conn.commit()
                return render(request, 'sd_ceshi_jieguo.html',
                              {'cs_list': cs_list, 'user_id': user_id, 'style_list': style_list,
                               'user_list': user_list})
        else:
            cur.execute('select test_result_deepth from m_tests_result where user_id=%s' % user_id)
            lia = cur.fetchone()['test_result_deepth']
            cur.execute('select * from m_test_deepth where test_subject="%s"' % (lia,))
            cs_list = cur.fetchone()
            return render(request, 'sd_ceshi_already.html',
                          {'user_id': user_id, 'style_list': style_list, 'user_list': user_list, 'cs_list': cs_list})
    else:
        return redirect('/login/')


def qw_ceshi_before(request):
    skip_id = request.GET.get('skip_id', '0')
    conn.ping(reconnect=True)
    if int(skip_id) <= 14:
        cur.execute('select * from m_test_interest_before where test_subject_id=%s', [skip_id])
        cs_list = cur.fetchone()
        return render(request, 'qw_ceshi_before.html', {'cs_list': cs_list})
    else:
        cur.execute('select * from m_test_interest_before where test_subject_id=%s', [skip_id])
        cs_list = cur.fetchone()
        return render(request, 'qw_ceshi_jieguo_before.html', {'cs_list': cs_list})


# 广场发布图片存在时
def image_yes(image, text, t, dw_list, dwstate, user_id, result):
    image1 = Image.open(image)
    image1.save('123.png')
    x = random.sample(list, 25)
    if x not in list_url:
        list_url.append(x)
        value = ''.join(x)
        key = str(value)
        url = 'http://file.g3.xmgc360.com/' + key
        localfile = r"123.png"
        token = q.upload_token(bucket_name, key)
        ret, info = put_file(token, key, localfile)
        if dwstate == '1':
            if result == '0':  # 消极
                cur.execute(
                    "INSERT INTO m_thoughts_message(user_id,thought_content,thought_image,thought_addr,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s','%s','%s')" % (
                        user_id, text, url, dw_list, t, 0))
            elif result == '1':  # 中间
                cur.execute(
                    "INSERT INTO m_thoughts_message(user_id,thought_content,thought_image,thought_addr,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s','%s')" % (
                        user_id, text, url, dw_list, t, 1))
            elif result == '2':  # 积极
                cur.execute(
                    "INSERT INTO m_thoughts_message(user_id,thought_content,thought_image,thought_addr,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s')" % (
                        user_id, text, url, dw_list, t, 2))
            conn.commit()
            datas = jieba.cut(text)
            last_id = cur.lastrowid
            for word in datas:
                key = word
                r_2.sadd(key, last_id)
        else:
            if result == '0':  # 消极
                cur.execute(
                    "INSERT INTO m_thoughts_message(user_id,thought_content,thought_image,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s')" % (
                        user_id, text, url, t, 0))
            elif result == '1':  # 中间
                cur.execute(
                    "INSERT INTO m_thoughts_message(user_id,thought_content,thought_image,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s')" % (
                        user_id, text, url, t, 1))
            elif result == '2':  # 积极
                cur.execute(
                    "INSERT INTO m_thoughts_message(user_id,thought_content,thought_image,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s')" % (
                        user_id, text, url, t, 2))
            conn.commit()
            datas = jieba.cut(text)
            last_id = cur.lastrowid
            for word in datas:
                key = word
                r_2.sadd(key, last_id)


# 广场发布图片不存在时
def image_no(text, t, dw_list, dwstate, user_id, result):
    if dwstate == '1':
        if result == '0':  # 消极
            cur.execute(
                "INSERT INTO m_thoughts_message(user_id,thought_content,thought_addr,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s')" % (
                    user_id, text, dw_list, t, 0))
        elif result == '1':  # 中间
            cur.execute(
                "INSERT INTO m_thoughts_message(user_id,thought_content,thought_addr,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s')" % (
                    user_id, text, dw_list, t, 1))
        elif result == '2':  # 积极
            cur.execute(
                "INSERT INTO m_thoughts_message(user_id,thought_content,thought_addr,thought_time,qinggan)VALUES('%s','%s','%s','%s','%s')" % (
                    user_id, text, dw_list, t, 2))
        conn.commit()
        datas = jieba.cut(text)
        last_id = cur.lastrowid
        for word in datas:
            key = word
            r_2.sadd(key, last_id)
    else:
        if result == '0':  # 消极
            cur.execute(
                "INSERT INTO m_thoughts_message(user_id,thought_content,thought_time,qinggan)VALUES('%s','%s','%s','%s')" % (
                    user_id, text, t, 0))
        elif result == '1':  # 中间
            cur.execute(
                "INSERT INTO m_thoughts_message(user_id,thought_content,thought_time,qinggan)VALUES('%s','%s','%s','%s')" % (
                    user_id, text, t, 1))
        elif result == '2':  # 积极
            cur.execute(
                "INSERT INTO m_thoughts_message(user_id,thought_content,thought_time,qinggan)VALUES('%s','%s','%s','%s')" % (
                    user_id, text, t, 2))
        conn.commit()
        datas = jieba.cut(text)
        last_id = cur.lastrowid
        for word in datas:
            key = word
            r_2.sadd(key, last_id)


# 获取定位信息
def dingwei():
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87'
    referer = 'https://www.opengps.cn/'
    post_data = {'q': '0.09711989818817401'}  # 此处将POST的数据定义为一个字典
    headers = {'User-Agent': user_agent, 'Referer': referer,
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}  # Headers属性初始化
    post_data_encode = urllib.parse.urlencode(post_data)  # 将POST的数据进行编码
    # UTF-8编码
    # 否则会报错：POST data should be bytes or an iterable of bytes. It cannot be of type str.
    post_data_encode = post_data_encode.encode(encoding='UTF-8')
    request_url = 'https://www.opengps.cn/Data/IP/LocHiAcc.ashx'  # 需要请求的URL地址
    # 使用Request来设置Headers
    request1 = urllib.request.Request(request_url, post_data_encode, headers)
    response = urllib.request.urlopen(request1)
    page_source = response.read().decode("utf-8")
    page_source = page_source.replace('true', '"true"')
    page_source = page_source.replace('{', '')
    page_source = page_source.replace('[', '')
    page_source = page_source.replace(':', '')
    page_source = page_source.replace(']', '')
    page_source = page_source.replace('}', '')
    page_source = page_source.replace(',', '')
    return (page_source.split('""')[12])


def guangchang1(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s', [user_id])
        user_list = cur.fetchone()
        # 获取定位信息
        dw_list = dingwei()
        # 获取当前时间
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if request.method == 'POST':
            text = request.POST.get('text')
            dwstate = request.POST.get('dwstate')
            # 图片处理
            image = request.FILES.get('file')
            datas = {"text": text}
            encode_data = json.dumps(datas).encode('GBK')
            requests = qg_http.request('POST',
                                       qg_url,
                                       body=encode_data,
                                       headers={'Content-Type': 'application/json'}
                                       )
            result = str(requests.data, 'GBK')
            if image:
                image_yes(image, text, t, dw_list, dwstate, user_id, result[-4])
                cur.execute('select thought_id from m_thoughts_message order by thought_id desc limit 1')
                user = cur.fetchone()['thought_id']
                cur.execute('select * from m_topics_message')
                tname = cur.fetchall()
                for i in tname:
                    if i['topic_name'] in text:
                        cur.execute('insert into m_topics_list(user_id,topic_id,thought_id) values(%s,%s,%s)',
                                    [user_id, i['topic_id'], user])
                        conn.commit()
            else:
                image_no(text, t, dw_list, dwstate, user_id, result[-4])
                cur.execute('select thought_id from m_thoughts_message order by thought_id desc limit 1')
                user = cur.fetchone()['thought_id']
                cur.execute('select * from m_topics_message')
                tname = cur.fetchall()
                for i in tname:
                    if i['topic_name'] in text:
                        cur.execute('insert into m_topics_list(user_id,topic_id,thought_id) values(%s,%s,%s)',
                                    [user_id, i['topic_id'], user])
                        conn.commit()
            # 数据库分页
            page = ''
            if page:
                a = (int(page) - 1) * 6
            else:
                a = 0
            # 一次获取多少条数据
            cur.execute('select * from m_thoughts_message limit ' + str(a) + ',6')
            thought_list = cur.fetchall()
            cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
            dz_list = cur.fetchall()
            cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
            sc_list = cur.fetchall()
            for key in thought_list:
                for dz in dz_list:
                    if dz['thought_id'] == key['thought_id']:
                        key['dz_state'] = 1
                        break
                    else:
                        key['dz_state'] = 0
            for key in thought_list:
                for sc in sc_list:
                    if sc['thought_id'] == key['thought_id']:
                        key['sc_state'] = 1
                        break
                    else:
                        key['sc_state'] = 0
            # 为了page才加的
            cur.execute('select * from m_thoughts_message')
            thought = cur.fetchall()
            cur.execute('select * from m_user_style')
            style_list = cur.fetchall()
            cur.execute('select * from m_topics_message')
            topic_list = cur.fetchall()
            cur.execute('select * from m_user_music where music_type=%s' % (int(result[-4])))
            music_list = cur.fetchone()
            paginator = Paginator(thought, 6)
            print(result[-4])
            # Paginator(thought,6,5)   写在里面的5没有效果，自动删除了少于6的page
            try:
                page_list = paginator.page(page)
            except PageNotAnInteger:
                page_list = paginator.page(1)
            except EmptyPage:
                page_list = paginator.page(paginator.count)
            return render(request, 'guangchang.html',
                          {'thought_list': thought_list, 'page_list': page_list,
                           'style_list': style_list, 'dw_list': dw_list, 'time': t, 'user_list': user_list,
                           'user_id': user_id, 'topic_list': topic_list, 'dz_list': dz_list, 'sc_list': sc_list,
                           'music': result[-4], 'music_list': music_list})

        # 数据库分页
        page = request.GET.get('page')
        if page:
            a = (int(page) - 1) * 6
        else:
            a = 0
        # 一次获取多少条数据
        cur.execute('select * from m_thoughts_message limit ' + str(a) + ',6')
        thought_list = cur.fetchall()
        cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
        dz_list = cur.fetchall()
        cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
        sc_list = cur.fetchall()
        for key in thought_list:
            for dz in dz_list:
                if dz['thought_id'] == key['thought_id']:
                    key['dz_state'] = 1
                    break
                else:
                    key['dz_state'] = 0
        for key in thought_list:
            for sc in sc_list:
                if sc['thought_id'] == key['thought_id']:
                    key['sc_state'] = 1
                    break
                else:
                    key['sc_state'] = 0
        # 为了page才加的
        cur.execute('select * from m_thoughts_message')
        thought = cur.fetchall()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_topics_message')
        topic_list = cur.fetchall()
        cur.execute('select * from m_thoughts_message where user_id=%s order by thought_id desc limit 1' % user_id)
        music = str(cur.fetchone()['qinggan'])
        cur.execute('select * from m_user_music where music_type=%s' % (int(music)))
        music_list = cur.fetchone()
        paginator = Paginator(thought, 6)
        # Paginator(thought,6,5)   写在里面的5没有效果，自动删除了少于6的page
        try:
            page_list = paginator.page(page)
        except PageNotAnInteger:
            page_list = paginator.page(1)
        except EmptyPage:
            page_list = paginator.page(paginator.count)
        return render(request, 'guangchang.html',
                      {'thought_list': thought_list, 'page_list': page_list,
                       'style_list': style_list, 'dw_list': dw_list, 'time': t, 'user_list': user_list,
                       'user_id': user_id, 'topic_list': topic_list, 'dz_list': dz_list, 'sc_list': sc_list,
                       'music': music, 'music_list': music_list})
    else:
        return redirect('/login/')


def guangchang(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s', [user_id])
        user_list = cur.fetchone()
        # 获取定位信息
        dw_list = dingwei()
        # 获取当前时间
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if request.method == 'POST':
            text = request.POST.get('text')
            dwstate = request.POST.get('dwstate')
            # 图片处理
            image = request.FILES.get('file')
            datas = {"text": text}
            encode_data = json.dumps(datas).encode('GBK')
            requests = qg_http.request('POST',
                                       qg_url,
                                       body=encode_data,
                                       headers={'Content-Type': 'application/json'}
                                       )
            result = str(requests.data, 'GBK')
            if image:
                image_yes(image, text, t, dw_list, dwstate, user_id, result[-4])
                cur.execute('select thought_id from m_thoughts_message order by thought_id desc limit 1')
                user = cur.fetchone()['thought_id']
                cur.execute('select * from m_topics_message')
                tname = cur.fetchall()
                for i in tname:
                    if i['topic_name'] in text:
                        cur.execute('insert into m_topics_list(user_id,topic_id,thought_id) values(%s,%s,%s)',
                                    [user_id, i['topic_id'], user])
                        conn.commit()
            else:
                image_no(text, t, dw_list, dwstate, user_id, result[-4])
                cur.execute('select thought_id from m_thoughts_message order by thought_id desc limit 1')
                user = cur.fetchone()['thought_id']
                cur.execute('select * from m_topics_message')
                tname = cur.fetchall()
                for i in tname:
                    if i['topic_name'] in text:
                        cur.execute('insert into m_topics_list(user_id,topic_id,thought_id) values(%s,%s,%s)',
                                    [user_id, i['topic_id'], user])
                        conn.commit()
            # 数据库分页
            page = ''
            if page:
                a = (int(page) - 1) * 6
            else:
                a = 0
            # 一次获取多少条数据
            bbb = r_t.smembers(user_id)
            if bbb:
                aaa = []
                for i in bbb:
                    j = i.decode('utf-8')
                    intj = int(j)
                    aaa.append(intj)
                cur.execute('select * from m_thoughts_message')
                thought_list1 = cur.fetchall()
                thought_list = []
                for i in thought_list1:
                    if i['thought_id'] in aaa:
                        thought_list.append(i)
            else:
                cur.execute('select test_result_before from m_tests_result where user_id=%s' % user_id)
                pl = cur.fetchone()['test_result_before']
                cur.execute('select * from m_tests_result where test_result_before="%s"' % pl)
                ps = cur.fetchall()
                pa = []
                for i in ps:
                    if i['user_id'] != user_id:
                        pa.append(i['user_id'])
                cur.execute('select * from m_thoughts_message')
                pp = cur.fetchall()
                thought_list = []
                for i in pp:
                    if i['user_id'] in pa:
                        thought_list.append(i)
            cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
            dz_list = cur.fetchall()
            cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
            sc_list = cur.fetchall()
            for key in thought_list:
                for dz in dz_list:
                    if dz['thought_id'] == key['thought_id']:
                        key['dz_state'] = 1
                        break
                    else:
                        key['dz_state'] = 0
            for key in thought_list:
                for sc in sc_list:
                    if sc['thought_id'] == key['thought_id']:
                        key['sc_state'] = 1
                        break
                    else:
                        key['sc_state'] = 0
            # 为了page才加的
            cur.execute('select * from m_user_style')
            style_list = cur.fetchall()
            cur.execute('select * from m_topics_message')
            topic_list = cur.fetchall()
            cur.execute('select * from m_user_music where music_type=%s' % (int(result[-4])))
            music_list = cur.fetchone()
            paginator = Paginator(thought_list, 6)
            print(result[-4])
            # Paginator(thought,6,5)   写在里面的5没有效果，自动删除了少于6的page
            try:
                page_list = paginator.page(page)
            except PageNotAnInteger:
                page_list = paginator.page(1)
            except EmptyPage:
                page_list = paginator.page(paginator.count)
            thought_list = thought_list[a:a + 6]
            return render(request, 'guangchang.html',
                          {'thought_list': thought_list, 'page_list': page_list,
                           'style_list': style_list, 'dw_list': dw_list, 'time': t, 'user_list': user_list,
                           'user_id': user_id, 'topic_list': topic_list, 'dz_list': dz_list, 'sc_list': sc_list,
                           'music': result[-4], 'music_list': music_list})

        # 数据库分页
        page = request.GET.get('page')
        if page:
            a = (int(page) - 1) * 6
        else:
            a = 0
        # 一次获取多少条数据
        bbb = r_t.smembers(user_id)
        if bbb:
            aaa = []
            for i in bbb:
                j = i.decode('utf-8')
                intj = int(j)
                aaa.append(intj)
            cur.execute('select * from m_thoughts_message')
            thought_list1 = cur.fetchall()
            thought_list = []
            for i in thought_list1:
                if i['thought_id'] in aaa:
                    thought_list.append(i)
        else:
            cur.execute('select test_result_before from m_tests_result where user_id=%s' % user_id)
            pl = cur.fetchone()['test_result_before']
            cur.execute('select * from m_tests_result where test_result_before="%s"' % pl)
            ps = cur.fetchall()
            pa = []
            for i in ps:
                if i['user_id'] != user_id:
                    pa.append(i['user_id'])
            cur.execute('select * from m_thoughts_message')
            pp = cur.fetchall()
            thought_list = []
            for i in pp:
                if i['user_id'] in pa:
                    thought_list.append(i)
        cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
        dz_list = cur.fetchall()
        cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
        sc_list = cur.fetchall()
        for key in thought_list:
            for dz in dz_list:
                if dz['thought_id'] == key['thought_id']:
                    key['dz_state'] = 1
                    break
                else:
                    key['dz_state'] = 0
        for key in thought_list:
            for sc in sc_list:
                if sc['thought_id'] == key['thought_id']:
                    key['sc_state'] = 1
                    break
                else:
                    key['sc_state'] = 0
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_topics_message')
        topic_list = cur.fetchall()
        cur.execute('select * from m_thoughts_message where user_id=%s order by thought_id desc limit 1' % user_id)
        music = cur.fetchone()
        if music:
            music = str(music['qinggan'])
            cur.execute('select * from m_user_music where music_type=%s' % (int(music)))
            music_list = cur.fetchone()
        else:
            cur.execute('select * from m_user_music where music_type=1')
            music_list = cur.fetchone()
            music = '1'
        paginator = Paginator(thought_list, 6)
        # Paginator(thought,6,5)   写在里面的5没有效果，自动删除了少于6的page
        try:
            page_list = paginator.page(page)
        except PageNotAnInteger:
            page_list = paginator.page(1)
        except EmptyPage:
            page_list = paginator.page(paginator.count)
        thought_list = thought_list[a:a + 6]
        return render(request, 'guangchang.html',
                      {'thought_list': thought_list, 'page_list': page_list,
                       'style_list': style_list, 'dw_list': dw_list, 'time': t, 'user_list': user_list,
                       'user_id': user_id, 'topic_list': topic_list, 'dz_list': dz_list, 'sc_list': sc_list,
                       'music': music, 'music_list': music_list})
    else:
        return redirect('/login/')


def guangchang_new(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s', [user_id])
        user_list = cur.fetchone()
        # 获取定位信息
        dw_list = dingwei()
        # 获取当前时间
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if request.method == 'POST':
            text = request.POST.get('text')
            dwstate = request.POST.get('dwstate')
            # 图片处理
            image = request.FILES.get('file')
            if image:
                image_yes(image, text, t, dw_list, dwstate, user_id)
                cur.execute('select thought_id from m_thoughts_message order by thought_id desc limit 1')
                user = cur.fetchone()['thought_id']
                cur.execute('select * from m_topics_message')
                tname = cur.fetchall()
                for i in tname:
                    if i['topic_name'] in text:
                        cur.execute('insert into m_topics_list(user_id,topic_id,thought_id) values(%s,%s,%s)',
                                    [user_id, i['topic_id'], user])
                        conn.commit()
            else:
                image_no(text, t, dw_list, dwstate, user_id)
                cur.execute('select thought_id from m_thoughts_message order by thought_id desc limit 1')
                user = cur.fetchone()['thought_id']
                cur.execute('select * from m_topics_message')
                tname = cur.fetchall()
                for i in tname:
                    if i['topic_name'] in text:
                        cur.execute('insert into m_topics_list(user_id,topic_id,thought_id) values(%s,%s,%s)',
                                    [user_id, i['topic_id'], user])
                        conn.commit()
            # 数据库分页
            page = ''
            if page:
                a = (int(page) - 1) * 6
            else:
                a = 0
            # 一次获取多少条数据
            cur.execute('select * from m_thoughts_message order by thought_id desc limit ' + str(a) + ',6')
            thought_list = cur.fetchall()
            cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
            dz_list = cur.fetchall()
            cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
            sc_list = cur.fetchall()
            for key in thought_list:
                for dz in dz_list:
                    if dz['thought_id'] == key['thought_id']:
                        key['dz_state'] = 1
                        break
                    else:
                        key['dz_state'] = 0
            for key in thought_list:
                for sc in sc_list:
                    if sc['thought_id'] == key['thought_id']:
                        key['sc_state'] = 1
                        break
                    else:
                        key['sc_state'] = 0
            # 为了page才加的
            cur.execute('select * from m_thoughts_message order by thought_id desc')
            thought = cur.fetchall()
            cur.execute('select * from m_topics_message')
            topic_list = cur.fetchall()
            cur.execute('select * from m_user_style')
            style_list = cur.fetchall()
            paginator = Paginator(thought, 6)
            # Paginator(thought,6,5)   写在里面的5没有效果，自动删除了少于6的page
            try:
                page_list = paginator.page(page)
            except PageNotAnInteger:
                page_list = paginator.page(1)
            except EmptyPage:
                page_list = paginator.page(paginator.count)
            return render(request, 'guangchang_new.html',
                          {'thought_list': thought_list, 'page_list': page_list,
                           'style_list': style_list, 'dw_list': dw_list, 'time': t, 'user_list': user_list,
                           'user_id': user_id, 'topic_list': topic_list, 'dz_list': dz_list, 'sc_list': sc_list})

        # 数据库分页
        page = request.GET.get('page')
        if page:
            a = (int(page) - 1) * 6
        else:
            a = 0
        # 一次获取多少条数据
        cur.execute('select * from m_thoughts_message order by thought_id desc limit ' + str(a) + ',6')
        thought_list = cur.fetchall()
        cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
        dz_list = cur.fetchall()
        cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
        sc_list = cur.fetchall()
        for key in thought_list:
            for dz in dz_list:
                if dz['thought_id'] == key['thought_id']:
                    key['dz_state'] = 1
                    break
                else:
                    key['dz_state'] = 0
        for key in thought_list:
            for sc in sc_list:
                if sc['thought_id'] == key['thought_id']:
                    key['sc_state'] = 1
                    break
                else:
                    key['sc_state'] = 0
        # 为了page才加的
        cur.execute('select * from m_thoughts_message order by thought_id desc')
        thought = cur.fetchall()
        cur.execute('select * from m_topics_message')
        topic_list = cur.fetchall()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        paginator = Paginator(thought, 6)
        # Paginator(thought,6,5)   写在里面的5没有效果，自动删除了少于6的page
        try:
            page_list = paginator.page(page)
        except PageNotAnInteger:
            page_list = paginator.page(1)
        except EmptyPage:
            page_list = paginator.page(paginator.count)
        return render(request, 'guangchang_new.html',
                      {'thought_list': thought_list, 'page_list': page_list,
                       'style_list': style_list, 'dw_list': dw_list, 'time': t, 'user_list': user_list,
                       'user_id': user_id, 'topic_list': topic_list, 'dz_list': dz_list, 'sc_list': sc_list})
    else:
        return redirect('/login/')


def guangchang_guanzhu(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s', [user_id])
        user_list = cur.fetchone()
        # 获取定位信息
        dw_list = dingwei()
        # 获取当前时间
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if request.method == 'POST':
            text = request.POST.get('text')
            dwstate = request.POST.get('dwstate')
            # 图片处理
            image = request.FILES.get('file')
            if image:
                image_yes(image, text, t, dw_list, dwstate, user_id)
                cur.execute('select thought_id from m_thoughts_message order by thought_id desc limit 1')
                user = cur.fetchone()['thought_id']
                cur.execute('select * from m_topics_message')
                tname = cur.fetchall()
                for i in tname:
                    if i['topic_name'] in text:
                        cur.execute('insert into m_topics_list(user_id,topic_id,thought_id) values(%s,%s,%s)',
                                    [user_id, i['topic_id'], user])
                        conn.commit()
            else:
                image_no(text, t, dw_list, dwstate, user_id)
                cur.execute('select thought_id from m_thoughts_message order by thought_id desc limit 1')
                user = cur.fetchone()['thought_id']
                cur.execute('select * from m_topics_message')
                tname = cur.fetchall()
                for i in tname:
                    if i['topic_name'] in text:
                        cur.execute('insert into m_topics_list(user_id,topic_id,thought_id) values(%s,%s,%s)',
                                    [user_id, i['topic_id'], user])
                        conn.commit()
            # 数据库分页
            page = ''
            if page:
                abs = (int(page) - 1) * 6
            else:
                abs = 0
            # 一次获取多少条数据
            cur.execute('select * from m_user_guanzhu where follow_id=%s' % user_id)
            f_list = cur.fetchall()
            thought_list = []
            for i in f_list:
                cur.execute('select * from m_thoughts_message where user_id=%s' % (i['befollow_id']))
                a = cur.fetchone()
                if a != None:
                    thought_list.append(a)
            cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
            dz_list = cur.fetchall()
            cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
            sc_list = cur.fetchall()
            for key in thought_list:
                for dz in dz_list:
                    if dz['thought_id'] == key['thought_id']:
                        key['dz_state'] = 1
                        break
                    else:
                        key['dz_state'] = 0
            for key in thought_list:
                for sc in sc_list:
                    if sc['thought_id'] == key['thought_id']:
                        key['sc_state'] = 1
                        break
                    else:
                        key['sc_state'] = 0
            paginator = Paginator(thought_list, 6)
            try:
                contacts = paginator.page(page)
            except PageNotAnInteger:
                contacts = paginator.page(1)
            except EmptyPage:
                contacts = paginator.page(paginator.num_pages)
            thought_list = thought_list[abs:abs + 6]
            cur.execute('select * from m_topics_message')
            topic_list = cur.fetchall()
            cur.execute('select * from m_user_style')
            style_list = cur.fetchall()
            return render(request, 'guangchang_guanzhu.html',
                          {'thought_list': thought_list,
                           'style_list': style_list, 'dw_list': dw_list, 'time': t, 'user_list': user_list,
                           'user_id': user_id, 'topic_list': topic_list, 'dz_list': dz_list, 'sc_list': sc_list})

        # 数据库分页
        page = request.GET.get('page')
        if page:
            abs = (int(page) - 1) * 6
        else:
            abs = 0
        # 一次获取多少条数据
        cur.execute('select * from m_user_guanzhu where follow_id=%s' % user_id)
        f_list = cur.fetchall()
        list2 = []
        for i in f_list:
            list2.append(i['befollow_id'])
        thought_list = []
        cur.execute('select * from m_thoughts_message')
        lis = cur.fetchall()
        for i in lis:
            if i['user_id'] in list2:
                thought_list.append(i)
        cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
        dz_list = cur.fetchall()
        cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
        sc_list = cur.fetchall()
        for key in thought_list:
            for dz in dz_list:
                if dz['thought_id'] == key['thought_id']:
                    key['dz_state'] = 1
                    break
                else:
                    key['dz_state'] = 0
        for key in thought_list:
            for sc in sc_list:
                if sc['thought_id'] == key['thought_id']:
                    key['sc_state'] = 1
                    break
                else:
                    key['sc_state'] = 0
        paginator = Paginator(thought_list, 6)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)
        thought_list = thought_list[abs:abs + 6]
        cur.execute('select * from m_topics_message')
        topic_list = cur.fetchall()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        return render(request, 'guangchang_guanzhu.html',
                      {'contacts': contacts, 'thought_list': thought_list,
                       'style_list': style_list, 'dw_list': dw_list, 'time': t, 'user_list': user_list,
                       'user_id': user_id, 'topic_list': topic_list, 'dz_list': dz_list, 'sc_list': sc_list})
    else:
        return redirect('/login/')


def jubao(request):
    text = request.POST.get('text')
    sentid = request.POST.get('sent')
    getid = request.POST.get('get')
    thoughtid = request.POST.get('thought')
    image = request.FILES.get('file')
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    if thoughtid:
        conn.ping(reconnect=True)
        cur.execute('select * from m_user_thought_relat where user_id=%s and thought_id=%s' % (sentid, thoughtid))
        relat = cur.fetchone()
        if relat:
            cur.execute(
                'update m_user_thought_relat set score=score-5,user_time="%s" where user_id=%s and thought_id=%s' % (
                    t, sentid, thoughtid))
        else:
            cur.execute(
                'insert into m_user_thought_relat(user_id,thought_id,score,user_time) values("%s","%s","%s","%s")' % (
                    sentid, thoughtid, -5, t))
        if image:
            image1 = Image.open(image)
            image1.save('123.png')
            x = random.sample(list, 25)
            value = ''.join(x)
            key = str(value)
            url = 'http://file.g3.xmgc360.com/' + key
            localfile = r"123.png"
            token = q.upload_token(bucket_name, key)
            ret, info = put_file(token, key, localfile)
            cur.execute(
                "INSERT INTO m_report_user(report_sent_id,report_get_id,report_content,report_image,thought_id)VALUES('%s','%s','%s','%s','%s')" % (
                    sentid, getid, text, url, thoughtid))
            conn.commit()
            return redirect('/guangchang')
        else:
            cur.execute(
                "INSERT INTO m_report_user(report_sent_id,report_get_id,report_content,thought_id)VALUES('%s','%s','%s','%s')" % (
                    sentid, getid, text, thoughtid))
            conn.commit()
            return redirect('/guangchang')
    else:
        if image:
            image1 = Image.open(image)
            image1.save('123.png')
            x = random.sample(list, 25)
            value = ''.join(x)
            key = str(value)
            url = 'http://file.g3.xmgc360.com/' + key
            localfile = r"123.png"
            token = q.upload_token(bucket_name, key)
            ret, info = put_file(token, key, localfile)
            cur.execute(
                "INSERT INTO m_report_user(report_sent_id,report_get_id,report_content,report_image)VALUES('%s','%s','%s','%s')" % (
                    sentid, getid, text, url))
            conn.commit()
            return redirect('/duihua2?id=' + str(getid))
        else:
            cur.execute(
                "INSERT INTO m_report_user(report_sent_id,report_get_id,report_content)VALUES('%s','%s','%s')" % (
                    sentid, getid, text))
            conn.commit()
            return redirect('/duihua2?id=' + str(getid))


def lo(request):
    return render(request, '1.html')


def person_space(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        if request.method == 'POST':
            shouji = request.POST.get('shouji')
            youxiang = request.POST.get('youxiang')
            syzm = request.POST.get('syzm')
            keyr = "ver_%s" % shouji
            _ver = r.get(keyr).decode('utf-8')
            if syzm:
                if syzm == _ver:
                    cur.execute('update m_user_message set user_phone=%s,user_email=%s where user_id=%s',
                                [shouji, youxiang, user_id])
                    conn.commit()
                    return redirect('/person_space')
                else:
                    return render(request, 'person_space.html')
        else:
            page = request.GET.get('page')
            if page:
                a = (int(page) - 1) * 6
            else:
                a = 0
            # 获取个人信息
            cur.execute('select * from m_user_message where user_id=%s' % user_id)
            user_list = cur.fetchone()
            # 一次获取多少条数据
            cur.execute('select * from m_thoughts_message where user_id=%s limit ' + str(a) + ',6', [user_id])
            thought_list = cur.fetchall()
            cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
            dz_list = cur.fetchall()
            cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
            sc_list = cur.fetchall()
            for key in thought_list:
                for dz in dz_list:
                    if dz['thought_id'] == key['thought_id']:
                        # key['dz_state']='1'+str(key['thought_id'])
                        key['dz_state'] = 1
                        break
                    else:
                        key['dz_state'] = 0
            for key in thought_list:
                for sc in sc_list:
                    if sc['thought_id'] == key['thought_id']:
                        key['sc_state'] = 1
                        break
                    else:
                        key['sc_state'] = 0
            # 为了page才加的
            cur.execute('select * from m_thoughts_message where user_id=%s' % user_id)
            thought = cur.fetchall()
            cur.execute('select * from m_user_style where user_id=%s' % user_id)
            style_list = cur.fetchone()
            paginator = Paginator(thought, 6)
            # Paginator(thought,6,5)   写在里面的5没有效果，自动删除了少于6的page
            try:
                page_list = paginator.page(page)
            except PageNotAnInteger:
                page_list = paginator.page(1)
            except EmptyPage:
                page_list = paginator.page(paginator.count)
            return render(request, 'person_space.html',
                          {'thought_list': thought_list, 'page_list': page_list,
                           'style_list': style_list, 'user_list': user_list, 'user_id': user_id, 'dz_list': dz_list,
                           'sc_list': sc_list})
    else:
        return redirect('/login/')


def person_space_new(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        if request.method == 'POST':
            shouji = request.POST.get('shouji')
            youxiang = request.POST.get('youxiang')
            syzm = request.POST.get('syzm')
            keyr = "ver_%s" % shouji
            _ver = r.get(keyr).decode('utf-8')
            if syzm:
                if syzm == _ver:
                    cur.execute('update m_user_message set user_phone=%s,user_email=%s where user_id=%s',
                                [shouji, youxiang, user_id])
                    conn.commit()
                    return redirect('/person_space_new')
                else:
                    return render(request, 'person_space_new.html')
        else:
            # 获取个人信息
            cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
            sc_list = cur.fetchall()
            cur.execute('select * from m_user_message where user_id=%s' % user_id)
            user_list = cur.fetchone()
            cur.execute('select * from m_thoughts_message')
            thought_list = cur.fetchall()
            cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
            dz_list = cur.fetchall()
            for key in thought_list:
                for dz in dz_list:
                    if dz['thought_id'] == key['thought_id']:
                        key['dz_state'] = 1
                        break
                    else:
                        key['dz_state'] = 0
            for key in thought_list:
                for sc in sc_list:
                    if sc['thought_id'] == key['thought_id']:
                        key['sc_state'] = 1
                        break
                    else:
                        key['sc_state'] = 0
            cur.execute('select * from m_user_style where user_id=%s' % user_id)
            style_list = cur.fetchone()
            cur.execute('select * from m_user_style')
            style_list1 = cur.fetchall()
            cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
            shoucang_list = cur.fetchall()
            return render(request, 'person_space_new.html',
                          {'thought_list': thought_list,
                           'style_list': style_list, 'user_list': user_list, 'user_id': user_id, 'dz_list': dz_list,
                           'sc_list': sc_list, 'shoucang_list': shoucang_list, 'style_list1': style_list1})
    else:
        return redirect('/login/')


# 改头像
def gaitouxiang(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        src = request.GET.get('gtouxiang')
        cur.execute('update m_user_style set user_head=%s where user_id=%s', [src, user_id])
        conn.commit()
        return redirect('/person_space')
    else:
        return redirect('/login/')


# 改签名
def gaiqianming(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        qianming = request.GET.get('qianming')
        biaoqian = request.GET.get('biaoqian')
        xuexing = request.GET.get('xuexing')
        if len(qianming) > 34:
            return redirect('/person_space')
        else:
            cur.execute('update m_user_style set user_label=%s,user_sign=%s where user_id=%s',
                        [biaoqian, qianming, user_id])
            cur.execute('update m_user_message set user_blood=%s where user_id=%s', [xuexing, user_id])
            conn.commit()
            return redirect('/person_space')
    else:
        return redirect('/login/')


# 改电话/邮箱
def gaidianhua(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        shouji = request.GET.get('shouji')
        youxiang = request.GET.get('youxiang')
        syzm = request.GET.get('syzm')
        keyr = "ver_%s" % shouji
        _ver = r.get(keyr)
        if shouji and syzm:
            if syzm == _ver:
                cur.execute('update m_user_message set user_phone=%s,user_emali=%s where user_id=%s',
                            [shouji, youxiang, user_id])
                conn.commit()
                return redirect('/person_space')
            else:
                return render(request, 'person_space.html')
    else:
        return redirect('/login/')


# 手机验证码
def phone_yzm(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        ver = str(random.randint(100000, 999999))
        keyr = "ver_%s" % phone
        r.setex(keyr, ver, 180)
        textmod = {"sid": "8c599d2fac5be71d8164161a35fe610f", "token": "0925e25422ec206501f868ee2f6e82e9",
                       "appid": "6e5755a1b7df4005af190d0cb6d0b54f", "templateid": "391221", "param": ver,
                       "mobile": phone}
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                           "Content-Type": "application/json"}
        req = reqt.Request(url='https://open.ucpaas.com/ol/sms/sendsms', data=textmod, headers=header_dict)
        res = reqt.urlopen(req)
        print(ver)
        return HttpResponse('1')


def person_messages(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        page = request.GET.get('page')
        if page:
            a = (int(page) - 1) * 6
        else:
            a = 0
        # 获取个人信息
        id = request.GET.get('id')
        cur.execute('select * from m_user_message where user_id=%s', [id])
        user_list = cur.fetchone()
        # 一次获取多少条数据
        cur.execute('select * from m_thoughts_message where user_id=%s limit ' + str(a) + ',6', [id])
        thought_list = cur.fetchall()
        # 为了page才加的
        cur.execute('select * from m_thoughts_message where user_id=%s', [id])
        thought = cur.fetchall()
        cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
        dz_list = cur.fetchall()
        cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
        sc_list = cur.fetchall()
        for key in thought_list:
            for dz in dz_list:
                if dz['thought_id'] == key['thought_id']:
                    # key['dz_state']='1'+str(key['thought_id'])
                    key['dz_state'] = 1
                    break
                else:
                    key['dz_state'] = 0
        for key in thought_list:
            for sc in sc_list:
                if sc['thought_id'] == key['thought_id']:
                    key['sc_state'] = 1
                    break
                else:
                    key['sc_state'] = 0
        cur.execute('select * from m_user_style where user_id=%s' % id)
        style_list = cur.fetchone()
        cur.execute('select * from m_user_style where user_id=%s' % user_id)
        style_list2 = cur.fetchone()
        cur.execute(
            'select * from m_user_guanzhu where follow_id={} and befollow_id={}'.format(user_id, user_list['user_id']))
        guanzhu = cur.fetchone()
        cur.execute('select * from m_user_lh where user_id={} and user_lh_id={}'.format(user_id, user_list['user_id']))
        lahei = cur.fetchone()
        paginator = Paginator(thought, 6)
        # Paginator(thought,6,5)   写在里面的5没有效果，自动删除了少于6的page
        try:
            page_list = paginator.page(page)
        except PageNotAnInteger:
            page_list = paginator.page(1)
        except EmptyPage:
            page_list = paginator.page(paginator.count)
        return render(request, 'person_messages.html',
                      {'thought_list': thought_list, 'page_list': page_list,
                       'style_list': style_list, 'user_list': user_list, 'user_id': user_id,
                       'style_list2': style_list2, 'guanzhu': guanzhu, 'lahei': lahei, 'dz_list': dz_list,
                       'sc_list': sc_list})
    else:
        return redirect('/login/')


def guanzhu(request):
    uid = request.POST.get('uid')
    fid = request.POST.get('fid')
    conn.ping(reconnect=True)
    cur.execute('select * from m_user_guanzhu where follow_id=%s and befollow_id=%s', [uid, fid])
    gz = cur.fetchone()
    if gz:  # 已关注
        cur.execute('delete from m_user_guanzhu where follow_id=%s and befollow_id=%s', [uid, fid])
        conn.commit()
        return HttpResponse('true')
    else:  # 未关注
        cur.execute('insert into m_user_guanzhu(follow_id,befollow_id) values(%s,%s)', [uid, fid])
        conn.commit()
        return HttpResponse('false')


def lahei(request):
    uid = request.POST.get('uid')
    fid = request.POST.get('fid')
    conn.ping(reconnect=True)
    cur.execute('select * from m_user_lh where user_id=%s and user_lh_id=%s', [uid, fid])
    lh = cur.fetchone()
    if lh:  # 已拉黑
        cur.execute('delete from m_user_lh where user_id=%s and user_lh_id=%s', [uid, fid])
        conn.commit()
        return HttpResponse('true')
    else:  # 未拉黑
        cur.execute('insert into m_user_lh(user_id,user_lh_id) values(%s,%s)', [uid, fid])
        conn.commit()
        return HttpResponse('false')


def pinglun_public(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        id = request.GET.get('id')
        cur.execute('select * from m_user_message where user_id=%s', [user_id])
        user_list = cur.fetchone()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_thoughts_message where thought_id=%s', [id])
        thought_list = cur.fetchone()
        cur.execute('select * from m_thoughts_comment where thought_id=%s', [id])
        comment_list = cur.fetchall()
        cur.execute('select * from m_topics_message')
        topic_list = cur.fetchall()
        cur.execute('select * from m_user_thought_relat where user_id=%s and thought_id=%s' % (user_id, id))
        relat = cur.fetchone()
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if relat:
            cur.execute(
                "update m_user_thought_relat set score=score+1 where user_id=%s and thought_id=%s" % (user_id, id))
        else:
            cur.execute(
                "insert into m_user_thought_relat(user_id,thought_id,score,user_time) values('%s','%s','%s','%s')" % (
                    user_id, id, 1, t))
        conn.commit()
        return render(request, 'pinglun_public.html', {
            'user_list': user_list, 'style_list': style_list, 'thought_list': thought_list,
            'comment_list': comment_list, 'user_id': user_id, 'topic_list': topic_list})
    else:
        return redirect('/login/')


def pinglun_1_1(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        # 获取当前时间
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        content = request.POST.get('text')  # 评论内容
        getid = request.POST.get('getid')
        id = request.POST.get('thoughtid')  # 心里话id
        datas = {"text": content}
        encode_data = json.dumps(datas).encode('GBK')
        requests = qg_http.request('POST',
                                   qg_url,
                                   body=encode_data,
                                   headers={'Content-Type': 'application/json'}
                                   )
        result = str(requests.data, 'GBK')
        cur.execute('select * from m_user_thought_relat where user_id=%s and thought_id=%s' % (user_id, id))
        relat = cur.fetchone()
        if relat:
            if result[-4] == '0':
                cur.execute(
                    "update m_user_thought_relat set score=score-5,user_time='%s' where user_id=%s and thought_id=%s" % (
                        t, user_id, id))
            else:
                cur.execute(
                    "update m_user_thought_relat set score=score+3,user_time='%s' where user_id=%s and thought_id=%s" % (
                        t, user_id, id))
        else:
            if result[-4] == '0':
                cur.execute(
                    "insert into m_user_thought_relat(user_id,thought_id,score,user_time) values('%s','%s','%s','%s')" % (
                        user_id, id, -5, t))
            else:
                cur.execute(
                    "insert into m_user_thought_relat(user_id,thought_id,score,user_time) values('%s','%s','%s','%s')" % (
                        user_id, id, 3, t))
        cur.execute(
            "INSERT INTO m_thoughts_comment(thought_id,comment_sent_id,comment_get_id,comment_content,comment_time) VALUES('%s','%s','%s','%s','%s')" % (
                id, user_id, getid, content, t))
        cur.execute('update m_thoughts_message set comment_num=comment_num+1')
        conn.commit()
        return redirect('/pinglun_public?id=%s' % id)
    else:
        return redirect('/login/')


def pinglun_1_2(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        # 获取当前时间
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        text = request.POST.get('text')
        content = request.POST.get(text)  # 评论内容
        getid = request.POST.get('getid')
        id = request.POST.get('thoughtid')  # 心里话id
        datas = {"text": content}
        encode_data = json.dumps(datas).encode('GBK')
        requests = qg_http.request('POST',
                                   qg_url,
                                   body=encode_data,
                                   headers={'Content-Type': 'application/json'}
                                   )
        result = str(requests.data, 'GBK')
        cur.execute('select * from m_user_thought_relat where user_id=%s and thought_id=%s' % (user_id, id))
        relat = cur.fetchone()
        if relat:
            if result[-4] == '0':
                cur.execute(
                    "update m_user_thought_relat set score=score-5,user_time='%s' where user_id=%s and thought_id=%s" % (
                        t, user_id, id))
            else:
                cur.execute(
                    "update m_user_thought_relat set score=score+3,user_time='%s' where user_id=%s and thought_id=%s" % (
                        t, user_id, id))
        else:
            if result[-4] == '0':
                cur.execute(
                    "insert into m_user_thought_relat(user_id,thought_id,score,user_time) values('%s','%s','%s','%s')" % (
                        user_id, id, -5, t))
            else:
                cur.execute(
                    "insert into m_user_thought_relat(user_id,thought_id,score,user_time) values('%s','%s','%s','%s')" % (
                        user_id, id, 3, t))
        cur.execute(
            "INSERT INTO m_thoughts_comment(thought_id,comment_sent_id,comment_get_id,comment_content,comment_time) VALUES('%s','%s','%s','%s','%s')" % (
                id, user_id, getid, content, t))
        cur.execute('update m_thoughts_message set comment_num=comment_num+1')
        conn.commit()
        return redirect('/pinglun_public?id=%s' % id)
    else:
        return redirect('/login/')


def pinglun_person(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        id = request.GET.get('id')
        cur.execute('select * from m_user_message where user_id=%s', [user_id])
        user_list = cur.fetchone()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_thoughts_message where thought_id=%s', [id])
        thought_list = cur.fetchone()
        cur.execute('select * from m_thoughts_comment where thought_id=%s', [id])
        comment_list = cur.fetchall()
        cur.execute('select * from m_user_thought_relat where user_id=%s and thought_id=%s' % (user_id, id))
        relat = cur.fetchone()
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if relat:
            cur.execute(
                'update m_user_thought_relat set score=score+1,user_time="%s" where user_id=%s and thought_id=%s' % (
                    t, user_id, id))
        else:
            cur.execute(
                "insert into m_user_thought_relat(user_id,thought_id,score,user_time) values('%s','%s','%s','%s')" % (
                    user_id, id, 1, t))
        conn.commit()
        return render(request, 'pinglun_person.html', {
            'user_list': user_list, 'style_list': style_list, 'thought_list': thought_list,
            'comment_list': comment_list, 'user_id': user_id})
    else:
        return redirect('/login/')


def delpinglun(request):
    id = request.GET.get('id')
    tid = request.GET.get('tid')
    cur.execute('delete from m_thoughts_comment where comment_id=%s', [id])
    conn.commit()
    return redirect('/pinglun_person?id=%s' % tid)


def admin(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_report_user')
        report_list = cur.fetchall()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        cur.execute('select * from m_thoughts_message')
        thought_list = cur.fetchall()
        return render(request, 'admin.html',
                      {'report_list': report_list, 'thought_list': thought_list, 'user_id': user_id,
                       'user_list': user_list, 'style_list': style_list})
    else:
        return redirect('/login/')


def fenghao(request):
    id = request.GET.get('id')
    rid = request.GET.get('rid')
    cur.execute('update m_user_message set user_state=1 where user_id=%s', [id])
    cur.execute('delete from m_report_user where report_id=%s', [rid])
    conn.commit()
    return redirect('/admin')


def shanchu(request):
    id = request.GET.get('id')
    rid = request.GET.get('rid')
    cur.execute('delete from m_thoughts_message where thought_id=%s', [id])
    cur.execute('delete from m_report_user where report_id=%s', [rid])
    conn.commit()
    return redirect('/admin')


def chexiao(request):
    rid = request.GET.get('id')
    cur.execute('delete from m_report_user where report_id=%s', [rid])
    conn.commit()
    return redirect('/admin')


def topic(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        if request.method == 'POST':
            t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            text = request.POST.get('text')
            print(text)
            cur.execute("insert into m_topics_message(user_id,topic_name,topic_time) values(%s,%s,%s)",
                        [user_id, text, t])
            conn.commit()
            return redirect('/admin/topic')
        cur.execute('select * from m_topics_message')
        topic_list = cur.fetchall()
        return render(request, 'topic.html',
                      {'topic_list': topic_list, 'user_id': user_id, 'user_list': user_list, 'style_list': style_list})
    else:
        return redirect('/login/')


def deltopic(request):
    id = request.POST.get('id')
    cur.execute('delete from m_topics_message where topic_id=%s' % id)
    conn.commit()
    return HttpResponse('true')


def guangchang_dzsc(request):
    uid = request.POST.get('uid')
    tid = request.POST.get('tid')
    state = request.POST.get('state')
    print(uid, tid, state)
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    conn.ping(reconnect=True)
    cur.execute('select * from m_user_thought_relat where user_id=%s and thought_id=%s' % (uid, tid))
    relat = cur.fetchone()
    if state == '1':
        cur.execute('select * from m_thought_dz where user_id=%s and thought_id=%s' % (uid, tid))
        s = cur.fetchone()
        if s:  # 取消点赞
            cur.execute('delete from m_thought_dz where user_id=%s and thought_id=%s' % (uid, tid))
            cur.execute('update m_thoughts_message set dz_num=dz_num-1 where thought_id=%s' % tid)
            if relat:
                cur.execute(
                    'update m_user_thought_relat set score=score-2,user_time="%s" where user_id=%s and thought_id=%s' % (
                        t, uid, tid))
            else:
                cur.execute(
                    'insert into m_user_thought_relat(user_id,thought_id,score,user_time) values("%s","%s","%s","%s")' %
                    (uid, tid, -2, t))
            conn.commit()
            return HttpResponse('true')
        else:  # 点赞
            cur.execute('insert into m_thought_dz(user_id,thought_id) values("%s","%s")' % (uid, tid))
            cur.execute('update m_thoughts_message set dz_num=dz_num+1 where thought_id=%s' % tid)
            if relat:
                cur.execute(
                    'update m_user_thought_relat set score=score+2,user_time="%s" where user_id=%s and thought_id=%s' % (
                        t, uid, tid))
            else:
                cur.execute(
                    'insert into m_user_thought_relat(user_id,thought_id,score,user_time) values("%s","%s","%s","%s")' % (
                        uid, tid, 2, t))
            conn.commit()
            return HttpResponse('false')
    elif state == '2':
        cur.execute('select * from m_thought_sc where user_id=%s and thought_id=%s' % (uid, tid))
        s = cur.fetchone()
        if s:  # 取消收藏
            cur.execute('delete from m_thought_sc where user_id=%s and thought_id=%s' % (uid, tid))
            cur.execute('update m_thoughts_message set sc_num=sc_num-1 where thought_id=%s' % tid)
            if relat:
                cur.execute(
                    'update m_user_thought_relat set score=score-3,user_time="%s" where user_id=%s and thought_id=%s' % (
                        t, uid, tid))
            else:
                cur.execute(
                    'insert into m_user_thought_relat(user_id,thought_id,score,user_time) values("%s","%s","%s","%s")' %
                    (uid, tid, 3, t))
            conn.commit()
            return HttpResponse('true')
        else:  # 收藏
            cur.execute('insert into m_thought_sc(user_id,thought_id) values("%s","%s")' % (uid, tid))
            cur.execute('update m_thoughts_message set sc_num=sc_num+1 where thought_id=%s' % tid)
            if relat:
                cur.execute(
                    'update m_user_thought_relat set score=score+3,user_time="%s" where user_id=%s and thought_id=%s' % (
                        t, uid, tid))
            else:
                cur.execute(
                    'insert into m_user_thought_relat(user_id,thought_id,score,user_time) values("%s","%s","%s","%s")' % (
                        uid, tid, 3, t))
            conn.commit()
            return HttpResponse('false')


def person_space_del(request):
    tid = request.POST.get('tid')
    uid = request.POST.get('uid')
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    conn.ping(reconnect=True)
    cur.execute('select * from m_user_thought_relat where user_id=%s and thought_id=%s' % (uid, tid))
    relat = cur.fetchone()
    if relat:
        cur.execute(
            'update m_user_thought_relat set score=score-3,user_time="%s" where user_id=%s and thought_id=%s' % (
                t, uid, tid))
    else:
        cur.execute('insert into m_user_thought_relat(user_id,thought_id,score,user_time) values("%s","%s","%s","%s")' %
                    (uid, tid, -3, t))
    cur.execute('delete from m_thoughts_message where thought_id=%s' % tid)
    conn.commit()
    return HttpResponse('true')


def public_topic(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        topic = request.GET.get('id')
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
        dz_list = cur.fetchall()
        cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
        sc_list = cur.fetchall()
        cur.execute('select * from m_topics_list where topic_id=%s' % topic)
        topic_list = cur.fetchall()
        cur.execute('select * from m_topics_message')
        topic_list1 = cur.fetchall()
        cur.execute('select * from m_thoughts_message')
        thought_list = cur.fetchall()
        for key in thought_list:
            for dz in dz_list:
                if dz['thought_id'] == key['thought_id']:
                    key['dz_state'] = 1
                    break
                else:
                    key['dz_state'] = 0
        for key in thought_list:
            for sc in sc_list:
                if sc['thought_id'] == key['thought_id']:
                    key['sc_state'] = 1
                    break
                else:
                    key['sc_state'] = 0
        return render(request, 'public_topic.html',
                      {'topic_list': topic_list, 'user_id': user_id, 'user_list': user_list, 'style_list': style_list,
                       'thought_list': thought_list, 'topic_list1': topic_list1, 'dz_list': dz_list,
                       'sc_list': sc_list})
    else:
        return redirect('/login/')


def select(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        cur.execute('select * from m_user_message where user_id=%s' % user_id)
        user_list = cur.fetchone()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_topics_message')
        topic_list = cur.fetchall()
        cur.execute('select * from m_thoughts_message')
        thought_list = cur.fetchall()
        cur.execute('select thought_id from m_thought_dz where user_id=%s' % user_id)
        dz_list = cur.fetchall()
        cur.execute('select * from m_thought_sc where user_id=%s' % user_id)
        sc_list = cur.fetchall()
        for key in thought_list:
            for dz in dz_list:
                if dz['thought_id'] == key['thought_id']:
                    key['dz_state'] = 1
                    break
                else:
                    key['dz_state'] = 0
        for key in thought_list:
            for sc in sc_list:
                if sc['thought_id'] == key['thought_id']:
                    key['sc_state'] = 1
                    break
                else:
                    key['sc_state'] = 0
        content = request.POST.get('content')
        list1 = []
        inter_list = []
        asd = r_2.keys()
        for i in asd:
            a = i.decode('utf-8')
            if a in content:
                list1.append(a)
        if list1:
            inter = r_2.sinter(list1)
            for i in inter:
                inter_list.append(int(i.decode('utf-8')))
        return render(request, 'select.html',
                      {'topic_list': topic_list, 'user_id': user_id, 'user_list': user_list, 'style_list': style_list,
                       'thought_list': thought_list, 'inter_list': inter_list, 'dz_list': dz_list, 'sc_list': sc_list})
    else:
        return redirect('/login/')


def duihua(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        lt_id = request.GET.get('lt_id')
        if lt_id:
            lt_id=int(lt_id)
        else:
            lt_id=''
        cur.execute('select * from m_user_message where user_id=%s', [user_id])
        user_list = cur.fetchone()
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_user_guanzhu where follow_id=%s' % user_id)
        gz_list = cur.fetchall()
        cur.execute('select * from m_thoughts_message where user_id=%s order by thought_id desc limit 1' % user_id)
        music = cur.fetchone()
        if music:
            music = str(music['qinggan'])
            cur.execute('select * from m_user_music where music_type=%s' % (int(music)))
            music_list = cur.fetchone()
        else:
            cur.execute('select * from m_user_music where music_type=1')
            music_list = cur.fetchone()
            music = '1'
        return render(request, 'duihua.html',
                      {'style_list': style_list, 'user_list': user_list, 'user_id': user_id, 'gz_list': gz_list,
                       'lt_id': lt_id, 'music': music, 'music_list': music_list})
    else:
        return redirect('/login/')

def liaotian(request):
    uid=request.POST.get('uid')
    lt_id=request.POST.get('lt_id')
    news=request.POST.get('news')
    print(uid,lt_id,news)
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    cur.execute('insert into m_chatroom(user_sent_id,user_get_id,chat_info,chat_time) values(%s,%s,%s,%s)',
                [uid, lt_id, news, t])
    conn.commit()
    return HttpResponse(1)

def duihua2(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        id = int(request.GET.get('id'))  # 聊天人的id
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        if request.method == 'POST':
            text = request.POST.get('text')
            if text:
                sent_id = request.POST.get('sent_id')
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                cur.execute('insert into m_chatroom(user_sent_id,user_get_id,chat_info,chat_time) values(%s,%s,%s,%s)',
                            [sent_id, id, text, t])
                conn.commit()
                return redirect('/duihua2?id=' + str(id))
            else:
                return redirect('/duihua2?id=' + str(id))
        cur.execute(
            'select * from m_chatroom where (user_sent_id=%s and user_get_id=%s) or ( user_get_id=%s and user_sent_id=%s)',
            [user_id, id, user_id, id])
        chat_list = cur.fetchall()
        cur.execute('select * from m_user_message where user_id=%s', [user_id])
        user_list = cur.fetchone()
        cur.execute('select * from m_thoughts_message where user_id=%s order by thought_id desc limit 1' % user_id)
        music = cur.fetchone()
        if music:
            music = str(music['qinggan'])
            cur.execute('select * from m_user_music where music_type=%s' % (int(music)))
            music_list = cur.fetchone()
        else:
            cur.execute('select * from m_user_music where music_type=1')
            music_list = cur.fetchone()
            music = '1'
        cur.execute('select * from m_user_style')
        style_list = cur.fetchall()
        cur.execute('select * from m_user_guanzhu where follow_id=%s' % user_id)
        gz_list = cur.fetchall()
        return render(request, 'duihua2.html',
                      {'style_list': style_list, 'user_list': user_list, 'user_id': user_id, 'gz_list': gz_list,
                       'lt_id': id, 'chat_list': chat_list,'music':music,'music_list':music_list})
    else:
        return redirect('/login/')


def quguan(request):
    char = request.session.get('phone')
    if char:
        conn.ping(reconnect=True)
        cur.execute("select user_id from m_user_online where session_desc=%s", [char, ])
        data = cur.fetchone()
        user_id = data['user_id']
        id = request.GET.get('id')
        lt_id = request.GET.get('lid')
        cur.execute('delete from m_user_guanzhu where follow_id=%s and befollow_id=%s', [user_id, id])
        conn.commit()
        return redirect('/duihua?lt_id=' + str(lt_id))


def save_wave_file(filename, data):
    framerate = 8000
    NUM_SAMPLES = 2000
    channels = 1
    sampwidth = 1
    TIME = 2
    '''save the date to the wavfile'''
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()


def ceshi(request):
    audio = request.FILES.get('audioData')
    save_wave_file('01.pcm', audio)
    APP_ID = '14718541'
    API_KEY = 'bTUGd4hHZipP23jZxqYcoDxL'
    SECRET_KEY = 'Fee8xeVGlukUPKpxdFYmI6iiGzGY3MGR'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    # 读取文件
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    # 识别本地文件
    result = client.asr(get_file_content('01.pcm'), 'pcm', 8000, {'dev_pid': 1536, })
    print(result)
    if len(result) != 3:
        return HttpResponse(result['result'][0])
    else:
        return HttpResponse('识别错误')


def getface(request):
    if request.POST:
        times = datetime.now().strftime('%Y%m%d&%H%M%S')
        strs = request.POST['message']
        phone_num=request.POST['phone']
        conn.ping(reconnect=True)
        cur.execute('select * from m_user_message where user_phone=%s'%phone_num)
        user_id=cur.fetchone()['user_id']
        imgdata = base64.b64decode(strs)
        try:
            file = open(u'static/face/facedata/confirm/' + times + '.jpg', 'wb')
            file.write(imgdata)
            file.close()
        except:
            print('as')
        res = AFRTest.checkFace(u'static/face/facedata/base/user' + phone_num + '.jpg',
                                        u'static/face/facedata/confirm/' + times + '.jpg')
        if res >= 0.6:
            numeric_alphabet = "0123456789abcdefghijklmnopqrstuvwxyz_"
            sessionval = ''.join(str(i) for i in random.sample(numeric_alphabet, 14))
            request.session['phone'] = str(phone_num) + sessionval
            session_desc = request.session['phone']
            session_time_start = time.time()
            cur.execute('update m_user_message set user_online_state=1 where user_id=%s' % user_id)
            cur.execute(
                                "insert into m_user_online(user_id,session_desc,session_time_start) values ('%s','%s','%s')" % (
                                    user_id, session_desc, session_time_start))
            conn.commit()
            shutil.rmtree(u'static/face/facedata/confirm')
            os.mkdir(u'static/face/facedata/confirm')
            return JsonResponse({'foo':phone_num,'los':'fit/'})
        else:
            return HttpResponse('no')
    else:
        return HttpResponse('no')


def face_login(request):
    phone=request.GET.get('phone')
    return render(request, "face_login.html",{'phone':phone})

def face_phone(request):
    phone_nums=request.POST.get('phone_nums')
    user_id=request.POST.get('user_id')
    conn.ping(reconnect=True)
    cur.execute('select * from m_user_message where user_id=%s'%user_id)
    a=cur.fetchone()['user_phone']
    if a==phone_nums:
        return HttpResponse('true')
    else:
        return HttpResponse('false')

def face_shot(request):
    if request.method == 'POST':
        phone_num = request.POST.get('phone_num')
        conn.ping(reconnect=True)
        cur.execute('select * from m_user_message where user_phone=%s'%phone_num)
        user_id=cur.fetchone()['user_id']
        strs = request.POST.get('message')
        strs = strs.split(',')[1]
        imgdata = base64.b64decode(strs)
        try:
            file = open(u'static/face/facedata/base/user' + phone_num + '.jpg', 'wb')
            file.write(imgdata)
            file.close()
            cur.execute('update m_user_style set user_face=1 where user_id=%s'%user_id)
            conn.commit()
            return JsonResponse({'foo':'OK','los':'person_space'})
        except:
            print('as')
            return JsonResponse({'foo':'error'})
    else:
        phone_num = request.GET.get('phone_num')
        return render(request, 'face_shot.html', {'phone_num': phone_num})
