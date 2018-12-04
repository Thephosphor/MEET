from fr import AFRTest
from django.http import HttpResponse

def face(request):
    res = AFRTest.checkFace(u'static/facedata/base/cqm.jpg', u'static/facedata/base/cqm.jpg')
    return HttpResponse(res)