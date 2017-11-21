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
import operator
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
from django.contrib.auth import views as auth_views

from django.conf import settings
import smtplib
from django.core.mail import send_mail
import operator
import logging
from decimal import Decimal

# Get an instance of a logger
logger = logging.getLogger(__name__)

from .forms import SearchForm


COMMISION = 1.05
# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)

class SearchedTutor(object):
    tutor = ""
    hourly_rate = 0
    tags = []
    teachCourse = []
    def __init__(self, tutor, hourly_rate, tags, teachCourse):
        self.tutor = tutor
        self.hourly_rate = hourly_rate
        self.tags = tags
        self.teachCourse = teachCourse

#####homepage###
def home(request):
    if not request.user.is_authenticated():
        #every function will have this, to make sure guest cannot visit personal account by manipulating url
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #fixme if an admin want to go to Tutorial/, he is not a myuser
    return HttpResponseRedirect('/Tutorial/' + str(myuser.id)) #searchTutors/'+str(request.user.id)
####login####
def login(request):
    if request.user.is_authenticated(): #visitor or client
        if not MyUser.objects.filter(user=request.user):
            return HttpResponseRedirect('/Tutorial/admin/') # Assume all tutors share a same page, so noneed for user.id+ str(user.id))
        myuser = MyUser.objects.get(user=request.user)
        return HttpResponseRedirect('/Tutorial/' + str(myuser.id)) #searchTutors/'+str(request.user.id)

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(username=username, password=password) #if sucess, should get not none

    if user is not None and user.is_active:
        auth.login(request, user)
        if not MyUser.objects.filter(user=request.user):
            return HttpResponseRedirect('/Tutorial/admin/') # Assume all tutors share a same page, so noneed for user.id+ str(user.id))
        myuser = MyUser.objects.get(user=request.user)
        return HttpResponseRedirect('/Tutorial/' + str(myuser.id))
    else:
        return render(request, 'registration/login.html')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/Tutorial/')
"""def password_reset(request):
    return render( 'registration/password_reset_form.html')

def password_reset_done(request):
    return render('/registration/password_reset_done.html')

def password_reset_confirm(requst):
    return HttpResponseRedirect('/Tutorial/')

def password_reset_complete(request):
    return HttpResponseRedirect('/Tutorial/')"""


####search tutor####
def index(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    #fixme I do this to make sure you are the person you should be, you cannot be someone else
    #fixme  but I haven't tried how to also relink the url i.e. if id = 2 enter 3/..., the content can be
    #fixme 2's now ,but the url shows 3 still

    all_tutors = Tutor.objects.all()
    private_tutors = PrivateTutor.objects.all()
    zipped = zip(all_tutors, all_tutors)
    params = {"user": myuser, "latest_Tutor_list": all_tutors, "tutors": zipped}
    return render(request, 'searchtutors/index.html', params)

def adminpage(request):
    return render(request, 'admin.html')

def triggersession(request):
    time = request.POST['time']
    timeformat = '%Y%m%d%H%M'
    try:
        bookingtime = datetime.strptime(time, timeformat)
    except Exception as e:
        return render(request, 'admin.html', {"msg": "Please enter format: YYYYmmddHHMM"})
    logger.error("trigger time wanted at" + time)
    if bookingtime.minute != 0 and bookingtime.minute != 30:
        return render(request, 'admin.html', {"msg": "Minutes is not 00 or 30, so no effect"})
    locksession(time)

    endsession(time)
    return render(request, 'admin.html', {"msg": "Setting success"})

def locksession(mytime):
    timeformat = '%Y%m%d%H%M'
    reftime = datetime.strptime(mytime, timeformat)
    if reftime.weekday() == 6 and reftime.hour == 0 and reftime.minute == 0:
        ## update the week of timeslot, if it is Sunday 00:00, then the timeslot should switch to a new week
        for tutor in Tutor.objects.all():
            if tutor.hourly_rate == 0:
                trigger = 2
            else: trigger = 1 #this is to distinguish between the two kinds
            slotlist = tutor.timeslot
            mid = 168 * trigger
            first_half = slotlist[mid: ] #the first half should be the second half of previous slot, next week has become the current week
            second_half = '1' * mid
            tutor.timeslot = first_half + second_half
            tutor.save()

    for slot in TutorialSession.objects.all(): #for this tutor's session, for student is this student , for loop
        ## begin tutorial
        if slot.starttime == mytime:
            if slot.status == 0 or slot.status == 1: #meaning that this session is upcoming but not canceled
                slot.status = 5 #set to in progress
                slot.save()
        else:
        ## lock cancel
            nowbooking = datetime.strptime(slot.starttime,timeformat)  # this is the yy mm dd format for what student wants to book
            bookingtime = time.mktime(nowbooking.timetuple())  # transfrom nowbooking into time format, should expect this to be later
            bookingreftime = time.mktime(reftime.timetuple()) # transform the reftime into time format
            logger.error("This is slot's time " + str(bookingtime) + " and this is now time " + str(bookingreftime) + " and this is the time delta " + str((bookingtime - bookingreftime) / 3600))
            if (slot.status == 0 and (bookingtime - bookingreftime) / 3600 <= 24): #if it is upcoming, make it cannot be canceled
                slot.status = 1
                slot.save()

    ## close booking

    now = reftime #only test for within one week!!
    #now = datetime.now()
    showingtime = time.mktime(datetime(now.year, now.month, now.day, 0, 0).timetuple())
    bookingtime = time.mktime(now.timetuple()) #transfrom nowbooking into time format
    #later on with beginAllSessions, we update the available string for every tutor each week at the end
    #day difference is because the 14-day long string starts from this Sunday, the first day of the week
    hour_diff = (bookingtime - showingtime) / 3600
    weekday = (1 + now.weekday()) % 7  # Monday is 0 ... Sunday is 6, but Sunday is the first day of the week, transform to 0
    if reftime.minute == 0:
        for tutor in Tutor.objects.all():

            if tutor.hourly_rate == 0:
                diff = 2
            else: diff = 1

            # modify timeslot string
            timeslot = list(tutor.timeslot)
            logger.error("This is the index" + str(weekday * 24 * diff + int (hour_diff * diff) + 24 * diff) + " and " + str(weekday * 48 + hour_diff * 2 + 48))
            timeslot[weekday * 24 * diff + int (hour_diff * diff) + 24 * diff] = '3' #meaning this session has passed the state to be modified
            #weekday * 24 * diff is how many 24 hours has passed
            #int (hour_diff * diff) means starting from today to 'now', hong long has passed
            #24 * diff means 24 hours passed
            #this function works when we are in the first week in timeslot string, because it should be updated every Saturday night, why now
            #I pretend today is next Wednesday and it fails is because it change the time of the current week, but in practical the next week
            #should be the reall current week, so it works well
            tutor.timeslot = "".join(timeslot)
            tutor.save()
    else: #then only contracted tutor needed in this case, but currently now working because no interface for half an hour yet
        half_hour_diff = int((bookingtime - showingtime) / 1800)
        weekday = (1 + now.weekday()) % 7  # Monday is 0 ... Sunday is 6, but Sunday is the first day of the week, transform to 0
        for tutor in Tutor.objects.filter(hourly_rate=0):

            # modify timeslot string
            timeslot = list(tutor.timeslot) 
            timeslot[weekday * 48 + half_hour_diff + 48] = '3' #meaning I book the session, 0 only means tutor doesn't want this session to be booked
            logger.error(
                "This is the index" + str(weekday * 48 + half_hour_diff + 48))

            tutor.timeslot = "".join(timeslot)
            tutor.save()

        #TODO they should be two times, but curently not, so byebye

    return

def endsession(mytime):
    timeformat = '%Y%m%d%H%M'
    reftime = datetime.strptime(mytime, timeformat)
    bookingreftime = time.mktime(reftime.timetuple())
    now = datetime.now()

    for slot in TutorialSession.objects.all(): #for this tutor's session, for student is this student , for loop

        starttime = time.mktime(datetime.strptime(slot.starttime, timeformat).timetuple())
        if ((slot.tutor.hourly_rate > 0 and (int(bookingreftime - starttime) == 3600)) or (slot.tutor.hourly_rate == 0 and (int(bookingreftime - starttime) == 1800))):
            #private tutor and start for one hour, or contracted tutor and start for half an hour
            if slot.status == 0 or slot.status == 1 or slot.status == 5: #meaning that this session is not cancelled, so will be asked to review
                ## end tutorial
                slot.status = 2 #set to in progress
                slot.save()

                ## transaction
                slot.tutor.myuser.wallet.balance = slot.tutor.myuser.wallet.balance + slot.price
                slot.tutor.myuser.wallet.save()
                now = datetime.now()
                content = "System notification [ " + str(datetime(now.year, now.month, now.day, now.hour,
                                                                  now.minute)) + " ]: You have completed the tutorial starting from " + str(
                    datetime.strptime(slot.starttime, timeformat)) + " to " + str(reftime) + " with student " + slot.student.myuser.user.username + ", tuition fee " + str(slot.price) + " has been transfered to your wallet"
                notification = Notification(content=content, myuser=slot.tutor.myuser)
                notification.save()

                ## review
                content = "System notification [ " + str(datetime(now.year, now.month, now.day, now.hour,
                                                                  now.minute)) + " ]: You have completed the tutorial starting from " + str(
                    datetime.strptime(slot.starttime,
                                      timeformat)) + " to " + str(reftime) + " with tutor " + slot.tutor.myuser.user.username + ", please evalute his/her performance!"
                notification = Notification(content=content, myuser=slot.student.myuser)
                notification.save()

                Transaction.objects.create(myuser=slot.tutor.myuser, time=mytime,
                                           cashflow=slot.price,
                                           information=slot, type=4)


                ## mytutor receives commision fee
    return




def tutorpage(request, myuser_id, tutor_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    return render(request, 'searchtutors/tutorpage.html', {'user':myuser, 'tutor': tutor})

####my account####
####my account####
def myaccount(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    isstudent = "0"
    istutor = "0"
    if Student.objects.filter(myuser=myuser):
       isstudent = "1"
    if Tutor.objects.filter(myuser=myuser):
        istutor = "1"
    return render(request, 'myaccount/myaccount.html', {'user':myuser, 'isstudent': isstudent, 'istutor': istutor})

def myprofile(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    form = ProfileForm(initial = {'last_name': myuser.user.last_name, 'first_name': myuser.user.first_name, 'email': myuser.user.email, 'phone': myuser.phone, 'content': myuser.profile_content})
    edit = False
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    isstudent = "0"
    istutor = "0"
    if Student.objects.filter(myuser=myuser):
        isstudent = "1"
    if Tutor.objects.filter(myuser=myuser):
        istutor = "1"
    if request.method == "GET":
        if 'edit' in request.GET:
            edit_or_not = request.GET['edit']
            logger.error("get edit value")
            logger.error(edit_or_not)
            if edit_or_not == '1':
                edit = True
            else:
                edit = False

        return render(request, 'myaccount/myprofile.html', {'user':myuser, 'form': form, 'edit': edit, 'isstudent': isstudent, 'istutor': istutor})
    else:   # POST
        logger.error("get post request")
        form = ProfileForm(request.POST)
        if form.is_valid():
            firstName = form.cleaned_data['first_name']
            lastName = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            profile_content = form.cleaned_data['content']
            myuser.user.first_name = firstName
            myuser.user.last_name = lastName
            myuser.phone = phone
            myuser.user.email = email
            myuser.profile_content = profile_content
            myuser.save()
            myuser.user.save()
        edit = False
        return render(request, 'myaccount/myprofile.html', {'user': myuser, 'form': form, 'edit': edit, 'isstudent': isstudent, 'istutor': istutor})

def mybooking(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    mystudent = Student.objects.filter(myuser=myuser)
    mytutor = Tutor.objects.filter(myuser=myuser)
    isstudent = "0"
    istutor = "0"
    #booking is the record as a student, booked is the record as a tutor
    if mystudent:
        mystudent = Student.objects.get(myuser = myuser)
        booking = TutorialSession.objects.filter(student=mystudent)
        isstudent = "1"
    else:
        booking= ""
    if mytutor:
        mytutor = Tutor.objects.get(myuser=myuser)
        booked = TutorialSession.objects.filter(tutor=mytutor)
        istutor = "1"
    else:
        booked=""
    return render(request, 'myaccount/mybooking.html', {'user': myuser , 'session_list': booking, "booked_list": booked, 'isstudent': isstudent, 'istutor': istutor })

def selectbooking(request, myuser_id, tutor_id ):	#receive data: starttime (yyyymmddhhmm string)
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = MyUser.objects.get(pk=myuser_id)

    begintime = request.POST['starttime']
    logger.error("Start time is " + str(begintime))
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

    now = datetime.now()
    showingtime = time.mktime(datetime(now.year, now.month, now.day, 0, 0).timetuple())
    nowbooking = datetime.strptime(begintime, timeformat) #this is the yy mm dd format for what student wants to book
    logger.error("This is after formatting " + str(nowbooking))
    bookingtime = time.mktime(nowbooking.timetuple()) #transfrom nowbooking into time format
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
                      {'fail': "Your wallet does not have enough money", 'tutor': tutor, 'user': myuser, 'begintime': begintime})

    #later on with beginAllSessions, we update the available string for every tutor each week at the end
    #day difference is because the 14-day long string starts from this Sunday, the first day of the week
    half_hour_diff = int((bookingtime - showingtime) / 1800) #only consider private tutor
    hour_diff = int(half_hour_diff / 2)
    weekday = (1 + now.weekday()) % 7 #Monday is 0 ... Sunday is 6, but Sunday is the first day of the week, transform to 0
    # modify timeslot string
    timeslot = list(tutor.timeslot)
    if tutor.hourly_rate == 0:
        timeslot[weekday * 48 + half_hour_diff] = '2' #meaning I book the session, 0 only means tutor doesn't want this session to be booked
    else :
        timeslot[weekday * 24 + hour_diff] = '2' #meaning I book the session, 0 only means tutor doesn't want this session to be booked
    tutor.timeslot = "".join(timeslot)
    #tutor.myuser.wallet.balance = tutor.myuser.wallet.balance + tutor.hourly_rate
    tutor.myuser.wallet.save()
    content = "System notification [ " + str(datetime(now.year, now.month, now.day, now.hour,
                                                      now.minute)) + " ]: You have been booked on " + str(
        datetime.strptime(begintime,
                          timeformat)) + " with student " + student.myuser.user.username
    notification = Notification(content=content, myuser=tutor.myuser)
    notification.save()

    #this is to send email through sendgrid
    #if tutor.myuser.user.email:
        #logger.error("I try to send the following email: " + content)
        #send_mail('Booking Notification', content, settings.EMAIL_HOST_USER, [tutor.myuser.user.email], fail_silently=False)

    tutor.save()
    newSession = tutor.tutorialsession_set.create(starttime=begintime, status=0, tutor=tutor, student=student, price=tutor.hourly_rate)
    #wallet deduction
    wallet.balance = wallet.balance - Decimal.from_float(
        tutor.hourly_rate * COMMISION)
    wallet.save()
    # message delivering
    content = "System notification [ " + str(datetime(now.year, now.month, now.day, now.hour,
                                                      now.minute)) + " ]: You have booked a session on " + str(
        datetime.strptime(begintime,
                          timeformat)) + " with tutor " + tutor.myuser.user.username + " ,with wallet balance deduced by " + str(
        tutor.hourly_rate * COMMISION) + " to " + str(wallet.balance)
    notification = Notification(content=content, myuser=myuser)
    notification.save()


    Transaction.objects.create(myuser=myuser, time=now.strftime(timeformat), cashflow=tutor.hourly_rate * COMMISION * (-1), information = newSession, type = 3)

    return render(request, 'searchtutors/tutorpage.html', {'success': "aa", 'tutor': tutor, 'user': myuser})



def cancelbooking(request, myuser_id, tutorial_sessions_id): #, student_id, tutor_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
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
    half_hour_diff = int((bookingtime - showingtime) / 1800)
    hour_diff = int(half_hour_diff / 2)
    weekday = (1 + now.weekday()) % 7 #Monday is 0 ... Sunday is 6, but Sunday is the first day of the week, transform to 0
    # modify timeslot string
    timeslot = list(tutor.timeslot)
    if tutor.hourly_rate == 0:
        timeslot[weekday * 48 + half_hour_diff] = '1'
    else:
        timeslot[weekday * 24 + hour_diff] = '1'
    tutor.timeslot = "".join(timeslot)
    #tutor.myuser.wallet.balance = tutor.myuser.wallet.balance - tutor.hourly_rate
    #tutor.myuser.wallet.save()
    tutor.save()
    tutorial_session.status = 3
    tutorial_session.save()
    content = "System notification [ " + str(
        datetime(now.year, now.month, now.day, now.hour, now.minute)) + " ]: Your following tutoring session has been cancelled:" + str(
        datetime.strptime(tutorial_session.starttime,
                          timeformat)) + " with student " + mystudent.myuser.user.username
    notification = Notification(content=content, myuser=tutor.myuser)
    notification.save()

    #this is to send email through sendgrid
    #if tutor.myuser.user.email:
        #send_mail('Booking Cancel Notification', content, settings.EMAIL_HOST_USER, [tutor.myuser.user.email], fail_silently=False)

    #wallet repaying
    wallet = mystudent.myuser.wallet
    wallet.balance = wallet.balance + Decimal.from_float(
        tutorial_session.price * COMMISION)
    wallet.save()
    # message delivering
    content = "System notification [ " + str(
        datetime(now.year, now.month, now.day, now.hour, now.minute)) + " ]: You have cancelled the session on " + str(
        datetime.strptime(tutorial_session.starttime, timeformat)) + " with tutor " + tutor.myuser.user.username + " ,with wallet repaid by " + str(tutorial_session.price * COMMISION) + " to " + str(wallet.balance)
    notification = Notification(content=content, myuser=myuser)
    notification.save()

    Transaction.objects.create(myuser=myuser, time=now.strftime(timeformat),
                               cashflow=tutorial_session.price * COMMISION, information=tutorial_session, type=2)

    mytutor = Tutor.objects.filter(myuser=myuser)
    if mytutor:
        mytutor = Tutor.objects.get(myuser=myuser)
        booked = TutorialSession.objects.filter(tutor=mytutor)
        istutor = "1"
    else:
        booked=""
        istutor = "0"
    return render(request, 'myaccount/mybooking.html',
                      {'user': myuser, 'session_list': booking, "booked_list": booked, 'isstudent': "1",
                       'istutor': istutor})

def evaluate(request, myuser_id, tutorial_sessions_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')

    score = request.POST['score']
    comment = request.POST['comment']
    comment = comment.replace('^space^', ' ')
    logger.error(comment)
    if len(comment) > 200:
        msg = 'Exceeds limit 200 characters, the left characters will not be stored'
        comment = comment[:200]
    logger.error("check it")
    session = TutorialSession.objects.get(pk=tutorial_sessions_id)
    session.score = score
    session.comment = comment
    session.status = 4
    session.save()
    return mybooking(request, myuser_id)


def mywallet(request, myuser_id): #TODO filter thirty days!
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    student_list = ""
    tutor_list = ""
    if Student.objects.filter(myuser=myuser):
        mystudent = Student.objects.get(myuser=myuser)
        student_list = TutorialSession.objects.filter(student=mystudent)
    if Tutor.objects.filter(myuser=myuser):
        mytutor = Tutor.objects.get(myuser=myuser)
        tutor_list = TutorialSession.objects.filter(tutor=mytutor)
    isstudent = "0"
    istutor = "0"
    if Student.objects.filter(myuser=myuser):
        isstudent = "1"
    if Tutor.objects.filter(myuser=myuser):
        istutor = "1"
    return render(request, 'myaccount/mywallet.html', {'user':myuser, 'student_list':student_list, 'tutor_list':tutor_list, 'msg': "", 'isstudent': isstudent, 'istutor': istutor })
#def forget_password(request, myuser_id):

####mytransaction#####
def mytransaction(request, myuser_id): #TODO filter thirty days!
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    student_list = ""
    tutor_list = ""
    if Student.objects.filter(myuser=myuser):
        mystudent = Student.objects.get(myuser=myuser)
        student_list = TutorialSession.objects.filter(student=mystudent)
    if Tutor.objects.filter(myuser=myuser):
        mytutor = Tutor.objects.get(myuser=myuser)
        tutor_list = TutorialSession.objects.filter(tutor=mytutor)
    isstudent = "0"
    istutor = "0"
    if Student.objects.filter(myuser=myuser):
        isstudent = "1"
    if Tutor.objects.filter(myuser=myuser):
        istutor = "1"
    return render(request, 'myaccount/mytransaction.html', {'user':myuser, 'student_list':student_list, 'tutor_list':tutor_list, 'msg': "", 'isstudent': isstudent, 'istutor': istutor })

####message####
def message(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    messages = Notification.objects.filter(myuser=myuser)
    return render(request, 'message/message.html', {'user': myuser, 'messages': messages})

def withdraw(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    student_list = ""
    tutor_list = ""
    if Student.objects.filter(myuser=myuser):
        mystudent = Student.objects.get(myuser=myuser)
        student_list = TutorialSession.objects.filter(student=mystudent)
    if Tutor.objects.filter(myuser=myuser):
        mytutor = Tutor.objects.get(myuser=myuser)
        tutor_list = TutorialSession.objects.filter(tutor=mytutor)
    #filter1: not tutor
    if not Tutor.objects.filter(myuser=myuser):
        messages = "Only a tutor can withdraw money from wallet"
        return render(request, 'myaccount/mywallet.html',
                      {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})
    amount = request.POST['withdraw']
    #filter2: not number
    try:
        cashflow = Decimal(amount)
    except Exception as e:
        messages = "Please enter a valid number"
        return render(request, 'myaccount/mywallet.html',
                      {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})
    #filter3: not possitive
    if cashflow <= 0:
        messages = "Please enter a positive number"
        return render(request, 'myaccount/mywallet.html',
                      {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})
    #filter4: not enough moneyD
    if cashflow > myuser.wallet.balance:
        messages = "You don't have enough money in your account"
        return render(request, 'myaccount/mywallet.html',
                      {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})
    myuser.wallet.balance = myuser.wallet.balance - cashflow
    myuser.wallet.save()
    messages = "Withdrawal success!" #TODO: remember that tutorialsession should keep track of hourly rate, and it records depost & withdraw

    Transaction.objects.create(myuser=myuser, time=datetime.now().strftime("%Y%m%d%H%M"),
                               cashflow=cashflow * (-1), type=1)
    return render(request, 'myaccount/mywallet.html',
                  {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})


def deposit(request, myuser_id):
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    student_list = ""
    tutor_list = ""
    if Student.objects.filter(myuser=myuser):
        mystudent = Student.objects.get(myuser=myuser)
        student_list = TutorialSession.objects.filter(student=mystudent)
    if Tutor.objects.filter(myuser=myuser):
        mytutor = Tutor.objects.get(myuser=myuser)
        tutor_list = TutorialSession.objects.filter(tutor=mytutor)
    #filter1: only tutor can withdraw
    if not Student.objects.filter(myuser=myuser):
        messages = "Only a student can deposit money from wallet"
        return render(request, 'myaccount/mywallet.html',
                      {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})
    amount = request.POST['deposit']
    #filter2: not number
    try:
        cashflow = Decimal(amount)
    except Exception as e:
        messages = "Please enter a valid number"
        return render(request, 'myaccount/mywallet.html',
                      {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})
    #filter3: not positive
    if cashflow <= 0:
        messages = "Please enter a positive number"
        return render(request, 'myaccount/mywallet.html',
                      {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})
    myuser.wallet.balance = myuser.wallet.balance + cashflow
    myuser.wallet.save()
    messages = "Deposit success!" #TODO: remember that tutorialsession should keep track of hourly rate, and it records depost & withdraw

    Transaction.objects.create(myuser=myuser, time=datetime.now().strftime("%Y%m%d%H%M"),
                               cashflow=cashflow, type=0)
    return render(request, 'myaccount/mywallet.html',
                  {'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages})

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




def search_tutor_name(request,myuser_id ): #TODO don't know what should admin be able to see lol
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
    zipped = zip(tutors, tutors)
    variables = {
        "tutors": zipped
    }
    return render(request, 'searchtutors/index.html', variables)


def search_tutor_tag(request,myuser_id ):
    show_tags = []
    tutor_set = []
    #option = request.GET["option"]
    course = object()
    # first filter
    tag_query = request.GET['tags']
    course_query = request.GET['course']

    selectAllTutors(request, tutor_set)

    tagFilter(request, tutor_set)

    courseFilter(request, tutor_set)

    #university filter
    universityFilter(request, tutor_set)


    # third filter
    typeFilter(request, tutor_set)


    # fourth filer
    priceFilter(request, tutor_set)


    #fifth filter
    showOptionFilter(request, tutor_set)


    orderFilter(request, tutor_set)

    for tut in tutor_set:
        show_tags.append(tut.tag_set.all())

    logger.error(show_tags)

    #logger.error(t_set)
    zipped = zip(tutor_set,show_tags)
    variables = {
        "tutors": zipped
    }
    return render(request, 'searchtutors/index.html', variables)
def selectAllTutors(request, tutor_set):
    tutors = Tutor.objects.all()
    for tut in tutors:
        tutor_set.append(tut)

def tagFilter(request, tutor_set):
    result_tutors = []
    logger.error("-----tags-----")
    if 'tags' in request.GET:
        query = request.GET['tags']
        tagset = query.split(',')
        if tagset != ['']:
            for tag_name in tagset:
                tag = Tag.objects.filter(name=tag_name)
                if tag:
                    tutors = tag[0].tutors.all()
                    for tut in tutor_set:
                        tags = tut.tag_set.all()
                        for tag in tags:
                            if tag.name in tagset:
                                result_tutors.append(tut)
                                break
            tutor_set.clear()
            for ele in result_tutors:
                tutor_set.append(ele)

# tutor_set, show_tags and course is one-to-one set
def courseFilter(request, tutor_set):
    result_tutors = []
    if 'course' in request.GET and request.GET['course'] != "":
        query = request.GET['course']
        course_name = query
        for tut in tutor_set:
            courses = tut.course_set.all()
            for course in courses:
                if course.course_code == course_name:
                    result_tutors.append(tut)
                    break
        tutor_set.clear()
        for ele in result_tutors:
            tutor_set.append(ele)

def typeFilter(request, tutor_set):
    search_private = False
    search_contracted = False
    privateTutor = []
    PT = PrivateTutor.objects.all()
    for t in PT:
        privateTutor.append(t.tutor)
    if 'type' in request.GET:
        type = request.GET["type"]
        if type == "PrivateTutor":
            search_private = True
        elif type == "ContractedTutor":
            search_contracted = True
    result_tutor = []
    if search_contracted and not search_private:
        logger.error("contracted tutor")
        for tut in tutor_set:
            if tut not in privateTutor:
                result_tutor.append(tut)
        tutor_set.clear()
        for ele in result_tutor:
            tutor_set.append(ele)
    elif not search_contracted and search_private:
        for tut in tutor_set:
            if tut in privateTutor:
                result_tutor.append(tut)
        tutor_set.clear()
        for ele in result_tutor:
            tutor_set.append(ele)

def priceFilter(request, tutor_set):
    new_tutor_set = []
    if 'lowPrice' in request.GET and 'highPrice' in request.GET:
        premin = request.GET['lowPrice']
        premax = request.GET['highPrice']
        if premin != "":
            min = int(request.GET['lowPrice'])
        else:
            min = 0
        if premax != "":
            max = int(request.GET['highPrice'])
        else:
            max = 500000
        for tut in tutor_set:
            if tut.hourly_rate >= min and tut.hourly_rate <= max:
                new_tutor_set.append(tut)
        tutor_set.clear()
        for ele in new_tutor_set:
            tutor_set.append(ele)


def showOptionFilter(request, tutor_set):
    new_tutor_set = []
    if 'option' in request.GET:
        option = request.GET['option']
        if option == "TutorWithin7Days":
            for tut in tutor_set:
                available = tut.timeslot
                length = len(available)
                weekslot = available[0:int(length/2)]
                logger.error("check timeslot")
                logger.error(weekslot)
                if '1' in weekslot:
                    new_tutor_set.append(tut)
            tutor_set.clear()
            for ele in new_tutor_set:
                tutor_set.append(ele)

def universityFilter(request, tutor_set):
    new_tutor_set = []
    university = ""
    # university filter
    if 'university' in request.GET:
        university = request.GET['university']
        if university != "":
            uni = University.objects.filter(name=university)
            for tut in tutor_set:
                logger.error(tut.university)
                if tut.university == uni[0]:
                    new_tutor_set.append(tut)
            logger.error("-----inside")
            logger.error(new_tutor_set)
            tutor_set.clear()
            for ele in new_tutor_set:
                tutor_set.append(ele)

def orderFilter(request, tutor_set):
    result_tutor = []
    if 'order' in request.GET:
        order = request.GET['order']
        if order != "RandomOrder":
            if order == "Rate high to low":
                tutor_set.sort(key=operator.attrgetter('hourly_rate'), reverse=True)
            else:
                tutor_set.sort(key=operator.attrgetter('hourly_rate'))
    else:
        tutor_set.sort(key=operator.attrgetter('hourly_rate'))
'''
def editProfile(request):
    user = request.GET['user']
    form = UserProfileForm(user)
    context = {
        "edit": True,
        "form": form
    }
    return render(request, myaccount/myprofile(request, user.id), context)
'''
'''
def saveProfile(request):
    '''