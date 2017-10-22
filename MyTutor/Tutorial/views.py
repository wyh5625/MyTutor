
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Tutor, PrivateTutor, User, Notification, TutorialSession

# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)

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
	params = {"latest_Tutor_list": all_tutors, "private_Tutor_list" : private_tutors}
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
	booking = TutorialSession.objects.filter(user=myuser)
	return render(request, 'myaccount/mybooking.html', {'session_list': booking })

def mywallet(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	return render(request, 'myaccount/mywallet.html', {'user':user })

####message####
def message(request, user_id):
	msguser = get_object_or_404(User, pk=user_id)
	messages = Notification.objects.filter(user=msguser)
	return render(request, 'message/message.html', {'user': msguser, 'messages': messages})
