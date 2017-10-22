from django.contrib import auth
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Tutor, PrivateTutor, User, Notification, TutorialSession, Student

# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)

####login####
def login(request):
	if request.user.is_authenticated(): #visitor or client
		return HttpResponseRedirect('/Tutorial/') #searchTutors/'+str(request.user.id)

	username = request.POST.get('username', '')
	password = request.POST.get('password', '')

	user = auth.authenticate(username=username, password=password) #if sucess, should get not none

	if user is not None and user.is_active:
		auth.login(request, user)
		return HttpResponseRedirect('/Tutorial/searchTutors/')
	else:
		return render(request, 'registration/login.html')

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/Tutorial/searchTutors/')
####search tutor####
def index(request):
	"""all_users = User.objects.all()
	list = []
	for user in all_users:
		html = '<p>User {name} has username: {user_name} </b></p>'
		list.append(html.format(name=user.name, user_name = user.user_name))
	output = '<hr>'.join(list)
	return HttpResponse(output)"""
	all_tutors = Tutor.objects.all()
	private_tutors = PrivateTutor.objects.all()
	params = {"latest_Tutor_list": all_tutors}
	return render(request, 'searchtutors/index.html', params)


def tutorpage(request, tutor_id):
	tutor = get_object_or_404(Tutor, pk=tutor_id)
	return render(request, 'searchtutors/tutorpage.html', {'tutor': tutor})

####my account####
def myaccount(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	return render(request, 'myaccount/myaccount.html', {'user':user })

def myprofile(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	return render(request, 'myaccount/myprofile.html', {'user':user })

def mybooking(request, user_id):
	myuser = get_object_or_404(User, pk=user_id)
	mystudent = get_object_or_404(Student,user=myuser)
	booking = TutorialSession.objects.filter(student=mystudent)
	return render(request, 'myaccount/mybooking.html', {'session_list': booking })

"""def selectbooking(request, tutorialSession_id):
	tutorialSession = get_object_or_404(TutorialSession, )"""

def mywallet(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	return render(request, 'myaccount/mywallet.html', {'user':user })

####message####
def message(request, user_id):
	msguser = get_object_or_404(User, pk=user_id)
	messages = Notification.objects.filter(user=msguser)
	return render(request, 'message/message.html', {'user': msguser, 'messages': messages})
