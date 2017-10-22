from django.contrib import admin

# Register your models here.
from .models import Notification, PrivateTutor, Student, Tutor, User, Wallet, Tutor2

admin.site.register(Notification)
admin.site.register(PrivateTutor)
admin.site.register(Tutor2)
admin.site.register(Student)
admin.site.register(Tutor)
admin.site.register(User)
admin.site.register(Wallet)

