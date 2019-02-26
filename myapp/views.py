from celery.backends import redis
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.generic import View
from .utils import *
from .tasks import *
from django.db.models import Q
import hashlib
from .models import *
from django.core.cache import caches
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django_redis import get_redis_connection
from alipay import AliPay
from django.conf import settings

cache = caches["confirm"]
cache1 = caches["default"]


# Create your views here.
class ZuceAPI(View):
    def get(self, req):
        return render(req, "user/register.html")

    def post(self, req):
        name = req.POST.get("name")
        pwd = req.POST.get("pwd")
        cpwd = req.POST.get("cpwd")
        email = req.POST.get("email")
        icon = req.FILES.get("icon")
        if len(pwd) > 5 and pwd == cpwd:
            if MyUser.objects.filter(username=name).exists():
                return render(req, "user/register.html", {"errmsg": "用户已存在"})
            else:
                user = MyUser.objects.create_user(
                    username=name,
                    password=pwd,
                    email=email,
                    icon=icon,
                    is_active=False
                )
                url = "http://" + req.get_host() + "/rx/confirm/" + get_uuid()
                print(url)
                send_mail_msg.delay(url, user.id, email)

                return HttpResponse("注册成功，请去邮箱激活")


def confirm(req, uuid_str):
    user_id = cache.get(uuid_str)
    if user_id:
        user = MyUser.objects.get(pk=int(user_id))
        user.is_active = True
        user.save()
        return redirect("/rx/login")
    else:
        return HttpResponse("<h2>链接失效<h2/>")


class LoginAPI(View):
    def get(self, req):
        name = req.session.get("name", "")
        checked = 'checked'

        print(1234)
        print(name)

        if name is None:
            name = ""
            checked = ""

        return render(req, "user/login.html", {"name": name, "checked": checked})

    def post(self, req):
        name = req.POST.get("name")
        pwd = req.POST.get("pwd")
        remember = req.POST.getlist("remember")

        print(12345)

        if not all([name, pwd]):
            return render(req, "user/login.html", {"msg": "用户密码不能为空"})
        user = authenticate(username=name, password=pwd)
        if user is not None:
            if user.is_active:
                login(req, user)
                url = req.GET.get("url", reverse('rx:indenxs'))

                response = redirect(url)
                print(response)

                if remember == ["1"]:
                    req.session["name"] = name
                    print(11111)
                else:
                    req.session["name"] = None

                return response
            else:
                return render(req, "user/login.html", {"errmsg": "用户未激活"})
        else:
            return render(req, "user/login.html", {"errmsg": "用户密码有错误"})


class LogoutAPI(View):
    def get(self, req):
        del req.session["_auth_user_id"]
        del req.session["_auth_user_backend"]
        del req.session["_auth_user_hash"]
        return redirect("rx:indenxs")


def wangji(req):
    if req.method == "GET":
        return render(req, "user/wangjimima.html")
    if req.method == "POST":
        name = req.POST.get("username")

        email = req.POST.get("username")

        print(email)

        if not MyUser.objects.filter(Q(email=email) | Q(username=name)).exists():
            print(123)
            return render(req, "user/wangjimima.html", {"msg": "邮箱或用户名不存在"})
        else:
            user_id = MyUser.objects.filter(Q(email=email) | Q(username=name)).first().id
            print(user_id)
            url = "http://" + req.get_host() + "/rx/setmima/" + get_uuid()
            print(url)
            send_email.delay(url, user_id, email)
            return HttpResponse("OK")


def setmima(req, uuid_str):
    user_id = cache.get(uuid_str)
    if user_id is not None:
        user = MyUser.objects.get(pk=int(user_id))
        if req.method == "GET":
            return render(req, "user/setmima.html", {"uuid_str": uuid_str})
        elif req.method == "POST":
            pwd = req.POST.get("pwd")
            cpwd = req.POST.get("cpwd")
            if len(pwd) > 5 and pwd == cpwd:
                user.password = make_password(pwd)

                print(1234)
                print(user.password)
                user.save()
                return redirect("rx:login")
            else:
                return HttpResponse("密码不一致")
    else:
        return HttpResponse("缓存没数据")


class AddressAPI(LoginRequiredView, View):

    def get(self, req):
        user = req.user
        temp = []
        all_adress = Saddress.objects.filter(user_id=user.id)
        for i in all_adress:
            temp.append(i)
        default_adrress = Saddress.objects.get(user=user, is_default=True)
        content = {
            "address": default_adrress,
            'have_address': temp
        }
        return render(req, "user/user_center_site.html", content)

    def post(self, req):
        receiver = req.POST.get("receiver")
        address = req.POST.get("direction")
        mail_code = req.POST.get("mail_code")
        phone = req.POST.get("phone")
        is_default = req.POST.getlist("is_default")[0]
        print(is_default)
        # 参数校检
        if not all([receiver, phone, address]):
            return render(req, "user/user_center_site.html", {"errmsg": "参数不完整"})
        user = req.user
        # 默认地址
        address_obj = Saddress.objects.filter(user=user, is_default=True)
        if address_obj.exists():
            address_obj.update(is_default=False)

        Saddress.objects.create(
            reciver=receiver,
            saddress=address,
            youbian=mail_code,
            phone=phone,
            is_default=is_default,
            user_id=user.id

        )
        return redirect("rx:addadress")


class UserinfoAPI(LoginRequiredView, View):
    def get(self, req):
        user = req.user
        address = Saddress.objects.filter(user=user, is_default=True).first()
        conn = get_redis_connection("default")
        # 设置KEY
        history_key = 'history_%d' % user.id
        goods_id = conn.lrange(history_key, 0, 4)
        goods = []
        for i in goods_id:
            good = Goods.objects.get(pk=int(i))
            goods.append(good)

        return render(req, "user/user_center_info.html", {'user': user, "address": address,"goods":goods})

class IndexAPI(View):
    def get(self, req):
        context = cache.get("data")
        print(123)
        print(context)
        if context is None:


            types = Typegoods.objects.all()
            good01 = types[0].goods_set.order_by("-id")[0:4]
            good02 = types[1].goods_set.order_by("-id")[0:4]
            good03 = types[2].goods_set.order_by("-id")[0:4]
            good04 = types[3].goods_set.order_by("-id")[0:4]
            good05 = types[4].goods_set.order_by("-id")[0:4]
            good06 = types[5].goods_set.order_by("-id")[0:4]
            content = {
                "good01": good01,
                "types": types,
                "good02": good02,
                "good03": good03,
                "good04": good04,
                "good05": good05,
                "good06": good06,


            }

            res = cache.set('data', content, 3600)








        return render(req, "goods/index.html", context)
def type_list(req):
    categroy = Typegoods.objects.all()

    return render(req,"goods/base_detail_list.html",{"types":categroy})

class ListgoodAPI(View):
    def get(self,req,type_id,page):
        try:
            categroy = Typegoods.objects.get(pk=int(type_id))
        except Typegoods.DoesNotExist:
            return redirect("rx:indenxs")
        newsgood = categroy.goods_set.order_by("-create_time")[0:2]
        sort = req.GET.get("sort")
        good_list= []

        if sort == "sales":
            good_list = categroy.goods_set.order_by("sales")
        elif sort == "price":
            good_list =  categroy.goods_set.order_by("price")
        else:
            # 按照默认顺序来排序
            sort = 'default'
            good_list = categroy.goods_set.order_by('-id')



        paginator = Paginator(good_list, 2)
        pages = paginator.page(int(page))
        data = {
            "page":pages ,
            "paginator":paginator,
            "sort":sort,
            "newsgood":newsgood,
            "categroy":categroy
        }
        return render(req,"goods/list.html",data)
class GooddetailAPI(View):
    def get(self,req,good_id):
        try:
            good = Goods.objects.get(pk=int(good_id))
        except Goods.DoesNotExist:
            # 商品不存在，则直接跳回首页
            return redirect(reverse('rx:indenxs'))
        good.gclick = good.gclick+1
        good.save()
        newgood = good.type.goods_set.order_by("-create_time")[0:2]
        conn = get_redis_connection("default")
        history_key = 'history_%d'% req.user.id
        conn.lrem(history_key,0,good_id)
        conn.lpush(history_key,good_id)
        res = conn.ltrim(history_key,0,4)
        print(123)
        print(res)

        data = {
            "good":good,
            "newgood":newgood

        }

        return render(req,"goods/detail.html",data)
class CartAPI(View):
    def get(self,req):
        user = req.user
        if not user.is_authenticated():
            data = {
                "code": 1,
                "msg": "请先登录",
                "data": "/rx/login"

            }
            return JsonResponse(data)
        cart_items = Cart.objects.filter(user_id=user.id)

        sum_money = get_summoney(cart_items)
        if cart_items.exists() and not cart_items.filter(is_selected=False).exists():
            is_all_select = True
        else:
            is_all_select = False
        count = 0
        for i in cart_items:
            count += i.num

        result = {
            "sum_money":sum_money,
            "cart_items":cart_items,
            "is_all_select": is_all_select,

            "total_count":count,

        }
        return  render(req,"cart/cart.html",result)




class CartitemAPI(View):
    def post(self,req):
        user = req.user
        if not isinstance(user,MyUser):
            data = {
                "code":1,
                "msg":"请先登录",
                "data":"/rx/login"

            }
        return  JsonResponse(data)
        op_type = req.POST.get("op_type")
        g_id = req.POST.get("g_id")
        goods = Goods.objects.get(pk=int(g_id))
        if op_type == "add":
            goods_num = 1
            if goods.stock > 1:
                cart_goods = Cart.objects.create(
                    user=user,
                    goods=goods
                )
                if cart_goods.exists():
                    cart_item = cart_goods.first()
                    print(cart_item)
                    cart_item.num += 1
                    cart_item.save

                    print(cart_item.num)
                    goods_num = cart_item.num
                else:
                    Cart.objects.create(
                        user=user,
                        goods=goods
                    )
                data = {
                    "code": 1,
                    "msg": "ok",
                    "data": goods_num
                }
                return JsonResponse(data)

            else:
                data = {
                    "code":2,
                    "msg":"库存不足"
                }
                return JsonResponse(data)
        elif op_type == "sub":
            goods_num = 0
            cart_item = Cart.objects.get(user=user,
                                            goods=goods
                                            )
            cart_item.num -= 1
            cart_item.save()
            if cart_item.num == 0:
                cart_item.delete()
            else:
                goods_num = cart_item.num
            data = {
                "code":1,
                "msg":"ok",
                "data":goods_num
            }
            return JsonResponse(data)

class CartstatusAPI(View):
    def patch(self,req):
        par = QueryDict(req.body)
        g_id = int(par.get("g_id"))
        user = req.user
        cart_item = Cart.objects.filter(user_id=user.id)
        cart_goods = cart_item.get(id=g_id)
        cart_goods.is_selected = not cart_goods.is_selected
        cart_item.save()
        sum_money = get_summoney(cart_item)
        if cart_item.filter(is_selected=False).exists():
            is_all_selected = False
        else:
            is_all_selected = True
        result = {
            "code": 1,
            "msg": "ok",
            "data": {

                "total_amount": sum_money,
                "status": cart_goods.is_selected
            }
        }
        return JsonResponse(result)
class CartallstatusAPI(View):
    def put(self,req):

        user = req.user
        cart_item = Cart.objects.filter(user_id=user.id)
        is_all_selected =False
        if cart_item.exists() and cart_item.filter(is_selected=False).exists():
            is_all_selected = True
            cart_item.filter(is_selected=False).update(is_selected=True)
            sum_money = get_summoney(cart_item)
        else:
            cart_item.update(is_selected=False)
            sum_money = 0
        result = {
            "code":1,
            "msg":"ok",
            "data":{
                "total_amount":sum_money
            }
        }
        return JsonResponse(result)
class CartbusAPI(View):
    def get(self,req):
        user = req.user
        g_id = req.POST.get("sku_id")


        cart_item = Cart.objects.filter(pk=int(g_id))
        if cart_item.goods.stock < 1:
            data = {
                "code": 2,
                "msg": "库存不足",
                "data": ""
            }
            return JsonResponse(data)
        cart_item.num += 1
        cart_item.save()
        cart_items = Cart.objects.filter(
            user_id=user.id,
            is_selected=True
        )
        sum_money = get_summoney(cart_items)
        data = {
            "code": 1,
            "msg": "ok",
            "data": {
                "total_count": cart_item.num,
                "total_amount": sum_money
            }
        }
        return JsonResponse(data)
    def delete(self,req):
        user = req.user
        g_id = QueryDict(req.body)
        cart_item = Cart.objects.filter(pk=int(g_id))
        cart_item.num -= 1
        cart_item.save()
        if cart_item.num == 0:
            goods_num = 0
            cart_item.delete()
        else:
            goods_num = cart_item.num
        cart_items = Cart.objects.filter(
            user=user,
            is_selected=True
        )
        sum_money = get_summoney(cart_items)
        data = {
            "code": 1,
            "msg": "ok",
            "data": {
                "num": goods_num,
                "sum_money": sum_money
            }
        }
        return JsonResponse(data)
class OrderAPI(View):
    def get(self,req):
        user = req.user
        address = Saddress.objects.filter(user_id=user.id)

        cart_items = Cart.objects.filter(user_id=user.id)
        transit_price = 10
        num = 0
        money = 0
        sku_ids = []
        for i in cart_items:
            sku_ids.append(str(i.goods.id))
            num += i.num
            money += i.goods.price * i.num



        sum_money = transit_price + money
        data = {
            "address":address,
            "cart_items":cart_items,
            "num":num,
            "sum_money":sum_money,
            "transit_price":transit_price,
            "sku_ids":','.join(sku_ids)

        }
        return render(req,"order/place_order.html",data)
class OrderitemAPI(View):
    def post(self,req):
        ORDER_STATUS = {
            "微信支付": 1,
            "支付宝支付": 2
        }
        user = req.user
        addr_id = req.POST.get("addr_id")
        print(addr_id)
        status = int(req.POST.get("status"))
        print(status)
        sku_ids = req.POST.get("sku_ids")
        print(sku_ids)
        sku_id = sku_ids.split(",")
        print(sku_id)
        if not all([addr_id,sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
        try :
            addr = Saddress.objects.get(pk=int(addr_id))
        except Saddress.DoesNotExist:
            return JsonResponse({"res":1,"errmsg":"地址不正确"})

        if status not in list(ORDER_STATUS.values()):
            return JsonResponse({'res': 3, 'errmsg': '非法的支付方式'})
        from datetime import datetime
        ordercard = datetime.now().strftime("%Y%m%d%H%S") + str(user.id)
        transit_price = 10
        cart_items = Cart.objects.filter(user_id=user.id,is_selected=True)
        num = 0
        money = 0
        transit_price = 10

        for i in cart_items:
            num += i.num
            money += i.goods.price * i.num

        sum_money = transit_price + money
        order = Order.objects.create(
            ordercard=ordercard,
            transit_price=transit_price,
            num=num,
            sum_money=sum_money,
            user=user,
            address=addr,
            status=status

        )

        print(order)

        for sku in sku_id:

            goods = Goods.objects.get(id=int(sku))

            # num = cart.num
            # money = cart.num * cart.goods.price



            OrderInfo.objects.create(
                goods=goods,
                order = order,
                pay_status=1,
                content=""
            )
            cart = Cart.objects.get(goods=goods)
            num = int(cart.num)
            goods.stock -= int(num)
            goods.sales += int(num)
            goods.save()
            cart.delete()
            print(cart)

        return JsonResponse({'res': 5, 'errmsg': '订单创建成功'})
class PayorderAPI(LoginRequiredView,View):
    def get(self,req):
        user = req.user
        orderinfo = OrderInfo.objects.all()
        data = {
            "user":user,
            "orderinfo":orderinfo
        }
        return render(req,"user/pay_order.html",data)
class OrderPayView(View):
    """订单支付"""
    def post(self, request):
        # 登录验证
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 参数校验
        if not all([order_id]):
            return JsonResponse({'res': 1, 'errmsg': '缺少参数'})

        # 校验订单id
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          order_status=1, # 待支付
                                          pay_method=3, # 支付宝支付
                                          )
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '无效订单id'})

        # 业务处理: 调用支付宝python SDK中的api_alipay_trade_page_pay函数
        # 初始化
        ali_pay = AliPay(
            appid=settings.ALIPAY_APP_ID,  # 应用APPID
            app_notify_url=settings.ALIPAY_APP_NOTIFY_URL,  # 默认回调url
            app_private_key_path=settings.APP_PRIVATE_KEY_PATH,  # 应用私钥文件路径
            # 支付宝的公钥文件，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False，False代表线上环境，True代表沙箱环境
        )


        total_pay = order.total_price + order.transit_price # Decimal
        order_string = ali_pay.api_alipay_trade_page_pay(
            out_trade_no=order_id, # 订单id
            total_amount=str(total_pay), # 订单实付款
            subject='每日鲜%s' % order_id, # 订单标题
            return_url='http://127.0.0.1:8000/order/check',
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        pay_url = settings.ALIPAY_GATEWAY_URL + order_string
        # print(pay_url)
        return JsonResponse({'res': 3, 'pay_url': pay_url, 'errmsg': 'OK'})


















































