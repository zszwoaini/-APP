from django.conf import settings
from django.core.cache import caches
from django.core.mail import send_mail
from django.template import loader
from celery import task
cache = caches["confirm"]

@task
def send_mail_msg(url,user_id,reciever):
    title = "每日鲜验证连接"
    content = "尊敬的用户欢迎你"

    template = loader.get_template("user/email.html")
    html = template.render({"url":url})
    email_from = settings.DEFAULT_FROM_EMAIL
    send_mail(title,content,email_from,[reciever],html_message=html)
    cache.set(url.split("/")[-1],user_id,settings.VERIFY_CODE_MAX_AGE)
@task
def send_email(url,user_id,reciever):
    title = "密码找回"
    content = ""
    templeate = loader.get_template("user/email.html")
    html = templeate.render({"url":url})
    email_from = settings.DEFAULT_FROM_EMAIL
    send_mail(title, content, email_from, [reciever], html_message=html)
    cache.set(url.split("/")[-1], user_id, settings.VERIFY_CODE_MAX_AGE)
