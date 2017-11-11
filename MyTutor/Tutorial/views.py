from ast import literal_eval
from django.contrib import auth
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, datetime, time, timedelta
from Tutorial.forms import *
import time
from Tutorial.models import *
from decimal import Decimal
from django.template import RequestContext
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.conf import settings
import smtplib
from django.core.mail import send_mail

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from .forms import SearchForm


COMMISION = 1.05
# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)

#####homepage###
def home(request):
    if not request.user.is_authenticated():
        #every function will have this, to make sure guest cannot visit personal account by manipulating url
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user) #fixme if an admin want to go to Tutorial/, he is not a myuser
    return HttpResponseRedirect('/Tutorial/' + str(myuser.id)) #searchTutors/'+str(request.user.id)
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
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    #fixme I do this to make sure you are the person you should be, you cannot be someone else
    #fixme  but I haven't tried how to also relink the url i.e. if id = 2 enter 3/..., the content can be
    #fixme 2's now ,but the url shows 3 still

    all_tutors = Tutor.objects.all()
    private_tutors = PrivateTutor.objects.all()
    zipped = zip(all_tutors, all_tutors)
    params = {"user": myuser, "latest_Tutor_list": all_tutors, "tutors": zipped}
    return render(request, 'searchtutors/index.html', params)


def tutorpage(request, myuser_id, tutor_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    return render(request, 'searchtutors/tutorpage.html', {'user':myuser, 'tutor': tutor})

####my account####
def myaccount(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    return render(request, 'myaccount/myaccount.html', {'user':myuser })

def myprofile(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    return render(request, 'myaccount/myprofile.html', {'user':myuser })

def mybooking(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    mystudent = Student.objects.filter(myuser=myuser)
    mytutor = Tutor.objects.filter(myuser=myuser)
    #booking is the record as a student, booked is the record as a tutor
    if mystudent:
        mystudent = Student.objects.get(myuser = myuser)
        booking = TutorialSession.objects.filter(student=mystudent)
    else:
        booking=""
    if mytutor:
        mytutor = Tutor.objects.get(myuser=myuser)
        booked = TutorialSession.objects.filter(tutor=mytutor)
    else:
        booked=""
        #TODO template should have if clause so if not student, do not display anything of record
    return render(request, 'myaccount/mybooking.html', {'user': myuser , 'session_list': booking, "booked_list": booked })

def selectbooking(request, myuser_id, tutor_id ):	#receive data: starttime (yyyymmddhhmm string)
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user) #myuser = MyUser.objects.get(pk=myuser_id)

    begintime = request.POST['starttime']
    student = Student.objects.filter(myuser=myuser)
    tutor = Tutor.objects.get(pk=tutor_id)
    if not student:
        return render(request, 'searchtutors/tutorpage.html',
                      {'fail': "Only a student can book session", 'tutor': tutor, 'user': myuser, 'begintime': begintime})
    student = Student.objects.get(myuser=myuser)
    if tutor.myuser == myuser:
        return render(request, 'searchtutors/tutorpage.html',
                      {'fail': "You cannot book your own session", 'tutor': tutor, 'user': myuser, 'begintime': begintime})

    tutorial_session = tutor.tutorialsession_set.filter(starttime=begintime)

    if tutorial_session: #if it is not empty, you cannot make this session
        session = tutor.tutorialsession_set.get(starttime=begintime)
        if session.status != 3:
            return render(request, 'searchtutors/tutorpage.html',
                      {'fail': "This session has been booked", 'tutor': tutor, 'user': myuser, 'begintime': begintime})


    #check if two bookings on the same day
    timeformat = '%Y%m%d%H%M'
    bookingtime = time.mktime(datetime.strptime(begintime, timeformat).timetuple())
    now = datetime.now()
    showingtime = time.mktime(datetime(now.year, now.month, now.day, 0, 0).timetuple())
    nowbooking = datetime.strptime(begintime, timeformat) #this is the yy mm dd format for what student wants to book
    for slot in tutor.tutorialsession_set.filter(student=student): #for this tutor's session, for student is this student , for loop
        slottime = datetime.strptime(slot.starttime, timeformat)
        if nowbooking.year == slottime.year and nowbooking.month == slottime.month and nowbooking.day == slottime.day:
            if slot.status != 3: #if equals three, then even the booking record exists, it has been canceled
                return render(request, 'searchtutors/tutorpage.html',
                          {'fail': "You have already booked a session on that day", 'tutor': tutor, 'user': myuser,
                           'begintime': begintime})
    wallet = myuser.wallet
    if wallet.balance < tutor.hourly_rate * COMMISION: #if not enough money, failed of course
        return render(request, 'searchtutors/tutorpage.html',
                      {'fail': "Your wallet does not have enough money", 'tutor': tutor, 'user': myuser, 'begintime': begintime})# fixme should report that not enough money

    #later on with beginAllSessions, we update the available string for every tutor each week at the end
    #day difference is because the 14-day long string starts from this Sunday, the first day of the week
    half_hour_diff = int(bookingtime - showingtime) / 1800 #only consider private tutor
    hour_diff = int(half_hour_diff / 2)
    weekday = (1 + now.weekday()) % 7 #Monday is 0 ... Sunday is 6, but Sunday is the first day of the week, transform to 0
    # modify timeslot string
    timeslot = list(tutor.timeslot)
    timeslot[weekday * 24 + hour_diff] = '2' #meaning I book the session, 0 only means tutor doesn't want this session to be booked
    tutor.timeslot = "".join(timeslot)
    tutor.myuser.wallet.balance = tutor.myuser.wallet.balance + tutor.hourly_rate
    tutor.myuser.wallet.save()
    content = "System notification [ " + str(datetime(now.year, now.month, now.day, now.hour,
                                                      now.minute)) + " ]: You have been booked on " + str(
        datetime.strptime(begintime,
                          timeformat)) + " with student " + student.myuser.user.username + " ,with wallet balance added by " + str(
        tutor.hourly_rate) + " to " + str(tutor.myuser.wallet.balance)
    notification = Notification(content=content, myuser=tutor.myuser)
    notification.save()

    #this is to send email through sendgrid
    #if tutor.myuser.user.email:
        #send_mail('Booking Notification', content, settings.EMAIL_HOST_USER, [tutor.myuser.user.email], fail_silently=False)

    tutor.save()
    tutor.tutorialsession_set.create(starttime=begintime, status=0, tutor=tutor, student=student)
    #wallet deduction
    wallet.balance = wallet.balance - Decimal.from_float(
        tutor.hourly_rate * COMMISION)  # fixme didn't add money to tutor account
    wallet.save()
    # message delivering
    content = "System notification [ " + str(datetime(now.year, now.month, now.day, now.hour,
                                                      now.minute)) + " ]: You have booked a session on " + str(
        datetime.strptime(begintime,
                          timeformat)) + " with tutor " + tutor.myuser.user.username + " ,with wallet balance deduced by " + str(
        tutor.hourly_rate * COMMISION) + " to " + str(wallet.balance)
    notification = Notification(content=content, myuser=myuser)
    notification.save()


    return render(request, 'searchtutors/tutorpage.html', {'success': "aa", 'tutor': tutor, 'user': myuser})



def cancelbooking(request, myuser_id, tutorial_sessions_id): #, student_id, tutor_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    #begintime = request.POST['starttime']
    tutorial_session =get_object_or_404(TutorialSession, pk=tutorial_sessions_id)
    tutor = tutorial_session.tutor
    #student = tutorial_session.student
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    mystudent = get_object_or_404(Student, myuser=myuser)
    booking = TutorialSession.objects.filter(student=mystudent)
    timeformat = '%Y%m%d%H%M'
    bookingtime = time.mktime(datetime.strptime(tutorial_session.starttime, timeformat).timetuple())
    now = datetime.now()
    showingtime = time.mktime(datetime(now.year, now.month, now.day, 0, 0).timetuple())
    half_hour_diff = int(bookingtime - showingtime) / 1800
    hour_diff = int(half_hour_diff / 2)
    weekday = (1 + now.weekday()) % 7 #Monday is 0 ... Sunday is 6, but Sunday is the first day of the week, transform to 0
    # modify timeslot string
    timeslot = list(tutor.timeslot)
    timeslot[weekday * 24 + hour_diff] = '1'
    tutor.timeslot = "".join(timeslot)
    tutor.myuser.wallet.balance = tutor.myuser.wallet.balance - tutor.hourly_rate
    tutor.myuser.wallet.save()
    tutor.save()
    tutorial_session.status = 3
    tutorial_session.save()
    content = "System notification [ " + str(
        datetime(now.year, now.month, now.day, now.hour, now.minute)) + " ]: Your following tutoring session has been cancelled:" + str(
        datetime.strptime(tutorial_session.starttime,
                          timeformat)) + " with student " + mystudent.myuser.user.username + " ,with wallet deduced by " \
              + str(tutor.hourly_rate) + " to " + str(tutor.myuser.wallet.balance)
    notification = Notification(content=content, myuser=tutor.myuser)
    notification.save()

    #this is to send email through sendgrid
    #if tutor.myuser.user.email:
        #send_mail('Booking Cancel Notification', content, settings.EMAIL_HOST_USER, [tutor.myuser.user.email], fail_silently=False)

    #wallet repaying
    wallet = mystudent.myuser.wallet
    wallet.balance = wallet.balance + Decimal.from_float(
        tutor.hourly_rate * COMMISION)  # fixme didn't add money to tutor account
    wallet.save()
    # message delivering
    content = "System notification [ " + str(
        datetime(now.year, now.month, now.day, now.hour, now.minute)) + " ]: You have cancelled the session on " + str(
        datetime.strptime(tutorial_session.starttime, timeformat)) + " with tutor " + tutor.myuser.user.username + " ,with wallet repaid by " + str(tutor.hourly_rate * COMMISION) + " to " + str(wallet.balance)
    notification = Notification(content=content, myuser=myuser)
    notification.save()

    return render(request, 'myaccount/mybooking.html', {'myuser': myuser, 'session_list':booking})

def mywallet(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    student_list = ""
    tutor_list = ""
    if Student.objects.filter(myuser=myuser):
        mystudent = Student.objects.get(myuser=myuser)
        student_list = TutorialSession.objects.filter(student=mystudent)
    if Tutor.objects.filter(myuser=myuser):
        mytutor = Tutor.objects.get(myuser=myuser)
        tutor_list = TutorialSession.objects.filter(tutor=mytutor)
    return render(request, 'myaccount/mywallet.html', {'user':myuser, 'student_list':student_list, 'tutor_list':tutor_list })

#def forget_password(request, myuser_id):

####message####
def message(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    messages = Notification.objects.filter(myuser=myuser)
    return render(request, 'message/message.html', {'user': myuser, 'messages': messages})


def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                last_name = form.cleaned_data['last_name'],
                first_name = form.cleaned_data['first_name']
            )
            wallet = Wallet.objects.create()
            myuser = MyUser.objects.create(user=user, wallet=wallet)
            identity = form.cleaned_data['identity']
            if identity == 'Student':
                student = Student.objects.create(myuser=myuser)
            elif identity == 'Private Tutor':
                tutor = Tutor.objects.create(myuser=myuser)
                privateTutor = PrivateTutor.objects.create(tutor=tutor)
            else:   # contracted tutor
                tutor = Tutor.objects.create(myuser=myuser)
                setattr(tutor,'timeslot','111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111')
                tutor.save()
                contractedTutor = ContractedTutor.objects.create(tutor=tutor)
            #return render(request, 'home.html')
    else:
        form = RegistrationForm()
    variables = {
        'form': form
    }
    return render_to_response(
        'registration/register.html',
        variables, RequestContext(request)
    )

#def forget_password(request):



"""class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 0.5 # every half minte

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'    # a unique code

    CRON_CLASSES = [
        "my_app.cron.MyCronJob"
    ]

    def do(self):
        user = User.objects.get(username='plus')
        myuser = MyUser.objects.get(user=user)
        myuser.wallet.balance = myuser.wallet.balance + 10"""


def search_tutor_name(request,myuser_id ):
    tutors = []
    tutors=Tutor.objects.all()
    show_results = False
    if 'givenName' in request.GET:
        show_results = True
        query = request.GET['givenName'].strip()
        if query:
            tutors = tutors.filter(myuser__user__first_name__contains=query)
    if 'familyName' in request.GET:
        show_results = True
        query = request.GET['familyName'].strip()
        if query:
            tutors = tutors.filter(myuser__user__last_name__contains=query)
    variables = {
        "tutors": tutors
    }
    return render(request, 'searchtutors/index.html', variables)


def search_tutor_tag(request,myuser_id ):
    tag = []
    tutors = []
    tutor_set = []
    query = []
    show_tags = []
    tag_of_tutor = []
    if 'tags' in request.GET:
        logger.error("has tag")
        query = request.GET['tags']
        if query:
            tagset = query.split(',')
            for tag_name in tagset:
                tag = Tag.objects.filter(name=tag_name)
                if tag:
                    tutors = tag[0].tutors.all()
                    for tut in tutors:
                        if tut not in tutor_set:
                            tutor_set.append(tut)
                            tag_of_tutor = []
                            tag_of_tutor.append(tag[0].name)
                            show_tags.append(tag_of_tutor)
                        else:
                            i = tutor_set.index(tut)
                            show_tags[i].append(tag[0].name)

    logger.error(tutor_set)
    logger.error(show_tags)
    zipped = zip(tutor_set, show_tags)
    variables = {
        "tutors": zipped
    }
    return render(request, 'searchtutors/index.html', variables)

