from django.shortcuts import render


def to_dashboard(request):
    """
    主界面
    """
    param = {"page": "b9b101e"}
    return render(request, "html/dashboard.html", param)


def to_share(request):
    """
    分享页面
    """
    param = {"page": "share"}
    return render(request, "html/dashboard.html", param)


def to_star(request):
    """
    收藏页面
    """
    param = {"page": "star"}
    return render(request, "html/dashboard.html", param)


def to_recycle(request):
    """
    回收站
    """
    param = {"page": "recycle"}
    return render(request, "html/dashboard.html", param)


def to_detail(request):
    """
    详情页面
    """
    param = {'id': request.GET.get('id')}
    return render(request, "html/detail.html", param)


def share_to_detail(request):
    """
    详情页面
    """
    param = {'h': request.GET.get('h'), 'u': request.GET.get('u')}
    return render(request, "html/detail.html", param)
