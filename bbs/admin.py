from django.contrib import admin

# Register your models here.
from bbs.models import *


admin.site.register(web_user)
admin.site.register(bbs)
admin.site.register(class_list)
admin.site.register(class_course)
admin.site.register(sign_in)
