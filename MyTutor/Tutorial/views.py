from ast import literal_eval
from django.contrib import auth
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Tutor, PrivateTutor, MyUser, Notification, TutorialSession, Student, Tutor
from django.contrib.auth.models import User
from datetime import date, datetime, time, timedelta

# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)
#####homepage###
def home(request):
	return render(request, 'home.html')
####login####
def login(request):
	if request.user.is_authenticated(): #visitor or client
		myuser = MyUser.objects.get(user=request.user)
		return HttpResponseRedirect('/Tutorial/' + str(myuser.id)) #searchTutors/'+str(request.user.id)

	username = request.POST.get('username', '')
	password = request.POST.get('password', '')

	user = auth.authenticate(username=username, password=password) #if sucess, should get not none

	if user is not None and user.is_active:
		auth.login(request, user)
		myuser = MyUser.objects.get(user=request.user)
		return HttpResponseRedirect('/Tutorial/' + str(myuser.id))
	else:
		return render(request, 'registration/login.html')

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/Tutorial/')
####search tutor####
def index(request, myuser_id):
	"""all_users = User.objects.all()
	list = []
	for user in all_users:
		html = '<p>User {name} has username: {user_name} </b></p>'
		list.append(html.format(name=user.name, user_name = user.user_name))
	output = '<hr>'.join(list)
	return HttpResponse(output)"""
	all_tutors = Tutor.objects.all()
	private_tutors = PrivateTutor.objects.all()
	myuser = get_object_or_404(MyUser, pk=myuser_id)
	student = get_object_or_404(Student, myuser=myuser)
	params = {"user": myuser, "latest_Tutor_list": all_tutors, 'student': student}
	return render(request, 'searchtutors/index.html', params)


def tutorpage(request, myuser_id, tutor_id):
	tutor = get_object_or_404(Tutor, pk=tutor_id)
	myuser = get_object_or_404(MyUser, pk=myuser_id)
	student = get_object_or_404(Student, myuser=myuser)
	return render(request, 'searchtutors/tutorpage.html', {'user':myuser, 'tutor': tutor, 'student':student})

####my account####
def myaccount(request, myuser_id):
	myuser = get_object_or_404(MyUser, pk=myuser_id)
	return render(request, 'myaccount/myaccount.html', {'user':myuser })

def myprofile(request, myuser_id):
	myuser = get_object_or_404(MyUser, pk=myuser_id)
	return render(request, 'myaccount/myprofile.html', {'user':myuser })

def mybooking(request, myuser_id):
	myuser = get_object_or_404(MyUser, pk=myuser_id)
	mystudent = get_object_or_404(Student,myuser=myuser)
	booking = TutorialSession.objects.filter(student=mystudent)
	return render(request, 'myaccount/mybooking.html', {'user':myuser, 'session_list': booking })

def selectbooking(request, student_id, tutor_id ):	#receive data: starttime (yyyymmddhhmm string)
	begintime = request.POST['starttime']
	tutor = get_object_or_404(Tutor, pk=tutor_id)
	student = get_object_or_404(Student, pk=student_id)
	tutorial_session = tutor.tutorialsession_set.filter(starttime=begintime)

	if tutorial_session: #if it is not empty, you cannot make this session
		return render(request, 'searchtutors/tutorpage.html',
					  {'fail': tutorial_session, 'tutor': tutor, 'student': student, 'begintime': begintime})
	else:
		# time solving
		"""timeformat = '%Y%m%d%H%M'  # fixme currently I don't care about exceed 14 days, or illegal booking ,only check availability
		bookingtime = time.mktime(datetime.strptime(begintime, timeformat).timetuple())
		today = date.today()
		showingtime = time.mktime(datetime(today.year, today.month, today.day, 0, 0).timetuple())
		half_hour_diff = int(showingtime - bookingtime) / 1800
		hour_diff = half_hour_diff / 2
		timeslot = list(tutor.timeslot)
		timeslot[hour_diff] = '1'
		tutor.timeslot = "".join(timeslot)"""
		tutor.tutorialsession_set.create(starttime=begintime, status="Occupied", tutor=tutor, student=student)
		return render(request, 'searchtutors/tutorpage.html', {'success': tutorial_session, 'tutor': tutor, 'student': student})

"""
def cancelbooking(request, student_id, tutor_id, tutorial_sessions_id): #, student_id, tutor_id):
	#begintime = request.POST['starttime']
	tutorial_session =get_object_or_404(TutorialSession, pk=tutorial_sessions_id)
	tutor = get_object_or_404(Tutor, pk=tutor_id)
	student = get_object_or_404(Student, pk=student_id)
	if tutorial_session:
		tutor.tutorialsession_set.create(begintime, "Occupied", tutor, student)
		return render(request, 'searchtutors/tutorpage.html', {'success': tutorial_session, 'tutor': tutor})
	else:
		return render(request, 'searchtutors/tutorpage.html', {'fail': tutorial_session, 'tutor': tutor})
"""
def mywallet(request, myuser_id):
	myuser = get_object_or_404(MyUser, pk=myuser_id)
	return render(request, 'myaccount/mywallet.html', {'user':myuser })

####message####
def message(request, myuser_id):
	myuser = get_object_or_404(MyUser, pk=myuser_id)
	messages = Notification.objects.filter(myuser=myuser)
	return render(request, 'message/message.html', {'user': myuser, 'messages': messages})
