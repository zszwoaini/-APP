# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-01-12 18:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_goods_gclick'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('num', models.IntegerField(default=1)),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Goods')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '购物车',
                'verbose_name': '购物车',
                'db_table': 'rx_cart',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('status', models.IntegerField(choices=[(2, '微信支付'), (1, '支付宝支付')], default=1, verbose_name='支付方式')),
                ('transit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='订单运费')),
                ('sum_money', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='商品总价')),
                ('num', models.IntegerField(default=1, verbose_name='商品数量')),
                ('ordercard', models.CharField(max_length=200, primary_key=True, serialize=False, verbose_name='订单编号')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Saddress', verbose_name='收货地址')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '订单',
                'verbose_name': '订单',
                'db_table': 'rx_order',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('pay_status', models.IntegerField(choices=[(2, '待支付'), (1, '已支付')], verbose_name='支付状态')),
                ('content', models.TextField(verbose_name='商品评论')),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Goods')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Order')),
            ],
            options={
                'verbose_name_plural': '订单详情',
                'verbose_name': '订单详情',
                'db_table': 'df_orderitem',
            },
        ),
        migrations.RemoveField(
            model_name='indextypegoodsbanner',
            name='category',
        ),
        migrations.RemoveField(
            model_name='indextypegoodsbanner',
            name='goods',
        ),
        migrations.DeleteModel(
            name='IndexTypeGoodsBanner',
        ),
    ]