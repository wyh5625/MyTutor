from django.contrib import admin

# Register your models here.
from .models import Notification, PrivateTutor, ContractedTutor, Student, Tutor, User, Wallet

admin.site.register(Notification)
admin.site.register(PrivateTutor)
admin.site.register(ContractedTutor)
admin.site.register(Student)
admin.site.register(Tutor)
admin.site.register(User)
admin.site.register(Wallet)

