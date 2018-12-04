"""MEET URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views,testFR

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cs', views.cs),
    path('css',views.ceshi),
    path('lo',views.lo),
    path('register/', views.register),               #注册
    path('login/', views.login),                     #登录
    path('fit/', views.fit),                         #匹配
    path('fit/new', views.fit_select),               #筛选
    path('chge_pwd/',views.chge_pwd),                #密码重置
    path('chazhao',views.chazhao),                   #ajax_密码重置
    path('login/chazhaop',views.login_chazhaop),     #ajax_登录手机
    path('login/chazhaom',views.login_chazhaom),     #ajax_登录密码
    path('Verificationr/',views.Verificationr),      #注册验证码生成
    path('Verificationl/',views.Verificationl),      #登录验证码生成
    path('Verificationc/',views.Verificationc),      #密码重置的验证码
    path('Alogout/',views.Alogout),                  #注销登录
    path('',views.shouye),                           #首页
    path('quwei_after', views.quwei_after),          #第二次趣味测试
    path('jifenshop', views.jifenshop),              #积分商城+任务
    path('xiadan', views.xiadan),                    #下单界面
    path('cb_ceshi',views.cb_ceshi),                 #初步测试
    path('sd_ceshi',views.sd_ceshi),                 #深度测试
    path('qw_ceshi_before',views.qw_ceshi_before),   #第一次趣味测试
    path('guangchang',views.guangchang),             #广场_推荐
    path('guangchang_new',views.guangchang_new),     #广场_最新
    path('guangchang_guanzhu',views.guangchang_guanzhu),#广场 关注
    path('select',views.select),                     #搜索心里话
    path('jubao',views.jubao),                       #心里话举报
    path('pinglun_public',views.pinglun_public),     #评论详情
    path('pinglun_person',views.pinglun_person),     #评论详情
    path('pinglun_1_1',views.pinglun_1_1),           #当前用户发送评论
    path('pinglun_1_2',views.pinglun_1_2),           #下面的回复
    path('delpinglun',views.delpinglun),             #删除评论
    path('person_space',views.person_space),         #个人中心
    path('person_space_new',views.person_space_new), #个人中心_收藏
    path('gaitouxiang',views.gaitouxiang),           #更改头像  重定向
    path('gaiqianming',views.gaiqianming),           #更改签名标签血型   重定向
    path('gaidianhua',views.gaidianhua),             #更改电话邮箱   重定向
    path('phone_yzm',views.phone_yzm),               #获取手机验证码  ajax
    path('person_messages',views.person_messages),   #用户信息
    path('person_guanzhu',views.guanzhu),            #用户关注
    path('person_lahei',views.lahei),                #用户拉黑
    path('admin',views.admin),                       #用户管理
    path('admin/fenghao',views.fenghao),             #封号
    path('admin/shanchu',views.shanchu),             #删除
    path('admin/chexiao',views.chexiao),             #撤销
    path('admin/topic',views.topic),                 #主题管理
    path('admin/deltopic',views.deltopic),           #删除主题
    path('guangchang/dzsc',views.guangchang_dzsc),   #点赞收藏
    path('person_space/del',views.person_space_del), #删除心里话
    path('public/topic',views.public_topic),         #主题详情
    path('ls_xiadan',views.ls_xiadan),               #历史下单
    path('del_xiadan',views.del_xiadan),             #删除下单信息
    path('integral_get',views.integral_get),         #积分获取
    path('duihua',views.duihua),                     #聊天界面
    path('liaotian',views.liaotian),                 #存聊天记录
    path('duihua2',views.duihua2),                   #聊天界面
    path('quguan',views.quguan),                     #取关
    path('getface',views.getface),                   #识别人脸
    path('face_login',views.face_login),             #返回人脸登录界面
    path('face_shot',views.face_shot),               #新用户拍照
    path('face_phone',views.face_phone),             #验证手机号码是否等于现在的用户
]