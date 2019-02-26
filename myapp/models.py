#coding=UTF-8
from django.contrib.auth.models import AbstractUser
from django.db import models
from tinymce.models import HTMLField

# Create your models here.
class BaseModel(models.Model):
    """抽象模型基类"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')

    class Meta:
        # 指定这个类是一个抽象模型类
        abstract = True
class MyUser(AbstractUser,BaseModel):
    '''
    用户模型类
    '''
    uphone = models.CharField(
        max_length=11
    )
    uaddress = models.CharField(
        max_length=255
    )
    uyoubian = models.CharField(
        max_length=6,
        verbose_name="邮编"
    )
    icon = models.ImageField(
        upload_to="icons",
        null=True
    )


    class Meta:
        db_table = "rx_user"
        verbose_name = '用户'
        verbose_name_plural = verbose_name
class Saddress(models.Model):
    user = models.ForeignKey(
        MyUser
    )
    saddress = models.CharField(
        max_length=100
    )
    youbian = models.CharField(
        max_length=6,
        default=False
    )
    reciver = models.CharField(
        max_length=10,
        default=False,
        verbose_name="收件人"
    )
    phone = models.CharField(
        max_length=11,
        default=False

    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="是否默认"
    )
    class Meta:
        db_table = 'rx_saddress'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
class Typegoods(BaseModel):
    name = models.CharField(
        max_length=20,

    )
    images = models.ImageField(
        upload_to='type_icon',
        verbose_name="商品类型图片"
    )
    class Meta:
        db_table = "rx_typegoods"
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name
class Goods(BaseModel):
    type = models.ForeignKey(
        Typegoods
    )
    goodname = models.CharField(
        max_length=30
    )
    goodimage = models.ImageField(
        upload_to= "goods_icons",
        verbose_name="商品图片"
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    unit = models.CharField(
        max_length=20,
        default="500g",
        verbose_name="单位"
    )
    stock = models.IntegerField(
        default=1,
        verbose_name="库存"
    )
    brief = models.CharField(
        max_length=100,
        verbose_name="商品简介"
    )
    sales = models.IntegerField(
        default=0,
        verbose_name="销量"
    )
    gclick = models.IntegerField(
        default=1,
        verbose_name="点击量"
    )
    detail = HTMLField(blank=True, verbose_name='商品详情')
    class Meta:
        db_table = "rx_goods"
        verbose_name = "商品"
        verbose_name_plural =verbose_name
class Cart(BaseModel):
    user = models.ForeignKey(
        MyUser
    )
    goods = models.ForeignKey(
        Goods
    )
    num = models.IntegerField(
        default=1
    )
    is_selected = models.BooleanField(
        default=True
    )
    class Meta:
        db_table = "rx_cart"
        verbose_name = "购物车"
        verbose_name_plural = verbose_name
class Order(BaseModel):
    ORDER_STATUS = (
        (1, "支付宝支付"),
        (2, "微信支付")
    )


    status = models.IntegerField(
        choices=ORDER_STATUS,
        default=1,
        verbose_name="支付方式"
    )
    address = models.ForeignKey(
        Saddress,
        verbose_name="收货地址"
    )
    user = models.ForeignKey(
        MyUser
    )
    transit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='订单运费'
    )
    sum_money = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="商品总价"
    )
    num = models.IntegerField(
        default=1,
        verbose_name="商品数量"

    )
    ordercard = models.CharField(
        max_length=200,
        primary_key=True,
        verbose_name="订单编号"

    )

    class Meta:
        db_table = 'rx_order'
        verbose_name = '订单'
        verbose_name_plural = verbose_name
class OrderInfo(BaseModel):
    STATUS = {
        (1,"待支付"),
        (2,"已支付")
    }

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    goods = models.ForeignKey(
        Goods
    )
    pay_status = models.IntegerField(
        choices=STATUS,
        default=1,
        verbose_name="支付状态"
    )
    content = models.TextField(
        default="",
        verbose_name="评论"


    )

    class Meta:
        db_table = 'df_orderitem'
        verbose_name = '订单详情'
        verbose_name_plural = verbose_name


















