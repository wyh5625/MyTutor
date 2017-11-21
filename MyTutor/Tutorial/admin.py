from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Notification)
admin.site.register(TutorialSession)
admin.site.register(PrivateTutor)
admin.site.register(ContractedTutor)
admin.site.register(Student)
admin.site.register(Tutor)
admin.site.register(MyUser)
admin.site.register(Wallet)
admin.site.register(Tag)
admin.site.register(University)
admin.site.register(Course)


