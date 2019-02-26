from django.conf.urls import url
from .views import *
from django.contrib.auth.decorators import login_require

urlpatterns = [

    url(r"^zuce/",ZuceAPI.as_view(),name="zuce"),
    url(r"^login/",LoginAPI.as_view(),name="login"),
    url(r"^confirm/(.*)",confirm),
    url(r"^indenxs/",IndexAPI.as_view(),name="indenxs"),
    url(r"^logout/",LogoutAPI.as_view(),name="logout"),
    url(r"^wangji/",wangji,name="wangji"),
    url(r"^setmima/(.*)",setmima,name="setmima"),
    url(r"^addadress/",AddressAPI.as_view(),name="addadress"),
    url(r"^userinfo/",UserinfoAPI.as_view(),name="userinfo"),
    url(r"^listgood/(\d+)/(\d+)$",ListgoodAPI.as_view(),name="listgood"),
    url(r"^typelist/",type_list,name="typelist"),
    url(r"^detail/(\d+)$",GooddetailAPI.as_view(),name="detail"),
    url(r"^cart/",CartAPI.as_view(),name="cart"),
    url(r"^cartitem/",CartitemAPI.as_view(),name="cartitem"),
    url(r"^cartstaus/",CartstatusAPI.as_view(),name="cartstatus"),
    url(r"^cartallstatus/",CartallstatusAPI.as_view(),name="cartallstatus"),
    url(r"cartbus/",CartbusAPI.as_view(),name="cartbus"),
    url(r"^order/",OrderAPI.as_view(),name="order"),
    url(r"^orderitem$",OrderitemAPI.as_view(),name="orderitem"),
    url(r"^orderinfo/",PayorderAPI.as_view(),name="orderinfo")



]