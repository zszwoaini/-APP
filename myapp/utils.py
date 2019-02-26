import uuid
import hashlib
from django.contrib.auth.decorators import login_required
from django.views.generic.base import View


def get_uuid():
    str_uuid = str(uuid.uuid4()).encode("utf-8")
    md5=hashlib.md5()
    md5.update(str_uuid)
    return md5.hexdigest()

class LoginRequiredView(View):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(view)
class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        # 使用super调用as_view
        view = super().as_view(**initkwargs)

        # 调用login_required装饰器函数
        return login_required(view)
def get_summoney(cart_items):
    sum_money = 0
    cart_items = cart_items.filter(
        is_selected = True
    )
    for i in cart_items:
        sum_money = i.goods.price * i.num + sum_money
    return sum_money

