from django.contrib import admin
from .models import *

# Register your models here.
class TypegoodsAdmin(admin.ModelAdmin):
    list_display = ["id","name","images"]
class GoodsAdmin(admin.ModelAdmin):
    list_display = ["id","type","goodname","goodimage","price",
                    "unit","stock","brief","sales","detail"]

admin.site.register(Typegoods,TypegoodsAdmin)
admin.site.register(Goods,GoodsAdmin)