"""autoOps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin

from asset import asset_urls
from capability import capability_urls
from batch_exec import batch_urls
from tasklog import tasklog_urls
from asset import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^asset/', include(asset_urls)),
    url(r'^capability/', include(capability_urls)),
    url(r'^batch_exec/', include(batch_urls)),
    url(r'^tasklog/', include(tasklog_urls)),
    url(r'^login/', views.acc_login, name='login'),
    url(r'^$', views.index, name='index'),

    url(r'^logout/', views.acc_logout,name='logout'),

]
