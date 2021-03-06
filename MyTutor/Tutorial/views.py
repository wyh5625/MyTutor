from ast import literal_eval
from django.contrib import auth
from django.template import RequestContext
from django.shortcuts import redirect
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
from django.template import RequestContext
import logging
import re
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
    if not request.user.is_authenticated() or request.user.is_anonymous():
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
    show_tags = []
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    #fixme I do this to make sure you are the person you should be, you cannot be someone else
    #fixme  but I haven't tried how to also relink the url i.e. if id = 2 enter 3/..., the content can be
    #fixme 2's now ,but the url shows 3 still

    all_tutors = Tutor.objects.filter(showProfile=True)
    for tut in all_tutors:
        show_tags.append(tut.tag_set.all())
    private_tutors = PrivateTutor.objects.all()
    courses= Course.objects.all()
    zipped = zip(all_tutors, show_tags)
    params = {"user": myuser, "latest_Tutor_list": all_tutors, "tutors": zipped, 'courses': courses}
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
            logger.error("This is the index" + tutor.myuser.user.username + " " + str(len(timeslot)) + " " + str(weekday * 24 * diff + int (hour_diff * diff) + 24 * diff) + " and " + str(weekday * 48 + hour_diff * 2 + 48))
            logger.error("Finally " + str(weekday * 24 * diff + int (hour_diff * diff) + 24 * diff))
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

                if slot.price != 0:
                    logger.error("This is transaction mytutor")
                    company_user = User.objects.get(username='MyTutor')
                    company = MyUser.objects.get(user=company_user)
                    # company = Tutor.objects.get(myuser=company_user)
                    company.wallet.balance = company.wallet.balance + Decimal(str(slot.price * (COMMISION - 1)))
                    Transaction.objects.create(myuser=company, time=mytime, cashflow=Decimal(str(slot.price * (COMMISION - 1))), information=slot, type=4)
                    company.wallet.save()
                    Transaction.objects.create(myuser=slot.tutor.myuser, time=mytime,
                                               cashflow=slot.price,
                                               information=slot, type=4)
                ## mytutor receives commision fee
    return


def mytutor(request):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
    if request.user.username != 'MyTutor':
        return index(request, company.id)
    company = MyUser.objects.get(user=request.user)
    list = Transaction.objects.filter(myuser=company)
    return render(request, 'mytutor.html', {'user':company, 'list': list})

def tutorpage(request, myuser_id, tutor_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    sessions = filter(
        lambda session: session.status == 4 and session.comment != "",
        TutorialSession.objects.filter(tutor=tutor))
    return render(request, 'searchtutors/tutorpage.html', {'user':myuser, 'tutor': tutor, 'sessions': sessions})

####my account####
####my account####
def myaccount(request, myuser_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    isstudent = "0"
    istutor = "0"
    if Student.objects.filter(myuser=myuser):
       isstudent = "1"
    if Tutor.objects.filter(myuser=myuser):
        istutor = "1"
        mytutor = Tutor.objects.get(myuser=myuser)
        return render(request, 'myaccount/myaccount.html',{'user': myuser, 'isstudent': isstudent, 'istutor': istutor, 'tutor': mytutor})
    return render(request, 'myaccount/myaccount.html', {'user':myuser, 'isstudent': isstudent, 'istutor': istutor})


def myprofile(request, myuser_id):
    logger.error("------render profile")
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return HttpResponseRedirect('/Tutorial/login/')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    edit = False
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    student = Student.objects.filter(myuser=myuser)
    tutor = Tutor.objects.filter(myuser=myuser)
    hourly_rate = 0
    activated = False
    t = None
    show_tags = []
    if tutor:
        hourly_rate = tutor[0].hourly_rate
        activated = tutor[0].showProfile
        show_tags = tutor[0].tag_set.all()
        t = tutor[0]
    privateTutor = PrivateTutor.objects.filter(tutor=tutor)
    if privateTutor:
        form = PrivateTutorProfileForm(initial = {'last_name': myuser.user.last_name, 'first_name': myuser.user.first_name, 'email': myuser.user.email, 'phone': myuser.phone, 'content': myuser.profile_content, 'hourly_rate': hourly_rate})
    else:
        form = ProfileForm(initial = {'last_name': myuser.user.last_name, 'first_name': myuser.user.first_name, 'email': myuser.user.email, 'phone': myuser.phone, 'content': myuser.profile_content})
    if request.method == "GET":
        logger.error("get method")
        if 'show_or_not' in request.GET:
            show_or_not = request.GET['show_or_not']
            if show_or_not == '1':
                tutor[0].showProfile = True
                activated = True
            else:
                tutor[0].showProfile = False
                activated = False
            tutor[0].save()
            logger.error("get show value")
            logger.error(tutor[0].showProfile)
        if 'edit' in request.GET:
            edit_or_not = request.GET['edit']
            logger.error("get edit value")
            logger.error(edit_or_not)
            if edit_or_not == '1':
                edit = True
            else:
                edit = False
        return render(request, 'myaccount/myprofile.html', {'user':myuser, 'form': form, 'edit': edit, 'tutor': tutor, 'privateTutor': privateTutor, 'hourly_rate': hourly_rate, 'profileActivated': activated, 'tutor': t, 'tags': show_tags})
    else:   # POST
        logger.error("get post request")
        if 'changePassWord' in request.POST:
            resetPassword = True
            passWordForm = ResetPasswordForm(request.POST, user=myuser)
            if passWordForm.is_valid():
                myuser.user.set_password(passWordForm.cleaned_data['new_password1'])
                myuser.user.save()
                edit = False

                return render(request, 'myaccount/myprofile.html',
                              {'user': myuser, 'form': passWordForm, 'edit': edit, 'tutor': tutor,
                               'privateTutor': privateTutor,
                               'hourly_rate': hourly_rate, 'profileActivated': activated, 'tutor': t, 'tags': show_tags})
            else:
                if 'newForm' in request.POST:
                    passWordForm = ResetPasswordForm(user=myuser)
            edit = True
            return render(request, 'myaccount/myprofile.html',
                          {'user': myuser, 'form': passWordForm, 'edit': edit, 'resetPassword': resetPassword,
                           'tutor': tutor, 'privateTutor': privateTutor, 'hourly_rate': hourly_rate,
                           'profileActivated': activated, 'tutor': t, 'tags': show_tags})
        if 'tags' in request.POST:
            query = request.POST['tags']
            tagset = query.split(',')
            if 'deleteTags' in request.POST:
                delete_query = request.POST['deleteTags']
                delete_tagset = delete_query.split(',')
                ret_list = []
                for item in tagset:
                    if item not in delete_tagset:
                        ret_list.append(item)
            else:
                ret_list = tagset
            if ret_list != ['']:
                for tag_name in ret_list:
                    if re.match(r'^\s+$',tag_name) == None and tag_name != "":
                        tag = Tag.objects.filter(name=tag_name)
                        if tag:
                            tag[0].tutors.add(tutor[0])
                            tag[0].save()
                        else:
                            newTag = Tag.objects.create(name=tag_name)
                            newTag.tutors.add(tutor[0])
                            newTag.save()
        if 'deleteTags' in request.POST:
            delete_query = request.POST['deleteTags']
            deletetagset = delete_query.split(',')
            logger.error("deletetagset")
            logger.error(deletetagset)
            if deletetagset != ['']:
                for tag_name in deletetagset:
                    tag = Tag.objects.filter(name=tag_name)
                    if tag:
                        tag[0].tutors.remove(tutor[0])
                        tag[0].save()
        if privateTutor:
            form = PrivateTutorProfileForm(request.POST, request.FILES)
        else:
            form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            firstName = form.cleaned_data['first_name']
            lastName = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            profile_content = form.cleaned_data['content']
            image = '0'
            if len(request.FILES) != 0:
                image = request.FILES['image_file']
            if privateTutor:
                tutor[0].hourly_rate = form.cleaned_data['hourly_rate']
                tutor[0].save()
                hourly_rate = tutor[0].hourly_rate
            myuser.user.first_name = firstName
            myuser.user.last_name = lastName
            myuser.phone = phone
            myuser.user.email = email
            myuser.profile_content = profile_content
            if image != '0':
                myuser.image = image
            myuser.save()
            myuser.user.save()
            edit = False
        else:
            edit = True
        return render(request, 'myaccount/myprofile.html', {'user':myuser, 'form': form, 'edit': edit, 'tutor': tutor, 'privateTutor': privateTutor, 'hourly_rate': hourly_rate, 'profileActivated': activated, 'tutor':t, 'tags': show_tags})

def mybooking(request, myuser_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return HttpResponseRedirect('/Tutorial/login/')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    isstudent = "0"
    istutor = "0"
    #booking is the record as a student, booked is the record as a tutor
    if Student.objects.filter(myuser=myuser):
        mystudent = Student.objects.get(myuser = myuser)
        booking = TutorialSession.objects.filter(student=mystudent)
        isstudent = "1"
    else:
        booking= ""
    if Tutor.objects.filter(myuser=myuser):
        mytutor = Tutor.objects.get(myuser=myuser)
        booked = TutorialSession.objects.filter(tutor=mytutor)
        istutor = "1"
        return render(request, 'myaccount/mybooking.html',{'user': myuser, 'session_list': booking, "booked_list": booked, 'isstudent': isstudent,'istutor': istutor, 'tutor': mytutor})
    else:
        booked=""
    return render(request, 'myaccount/mybooking.html', {'user': myuser , 'session_list': booking, "booked_list": booked, 'isstudent': isstudent, 'istutor': istutor })

def selectbooking(request, myuser_id, tutor_id ):	#receive data: starttime (yyyymmddhhmm string)
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
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
    sessions = filter(
        lambda session: session.status == 4 and session.comment != "",
        TutorialSession.objects.filter(tutor=tutor))
    courses = Course.objects.all()
    return render(request, 'searchtutors/tutorpage.html', {'success': "aa", 'tutor': tutor, 'user': myuser,'sessions': sessions, 'courses': courses})



def cancelbooking(request, myuser_id, tutorial_sessions_id): #, student_id, tutor_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        return HttpResponseRedirect('/Tutorial/admin/')
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
                       'istutor': istutor, 'tutor': mytutor})

def evaluate(request, myuser_id, tutorial_sessions_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')

    score = request.POST['score']
    logger.error(score)

    comment = request.POST['comment']
    logger.error(comment)
    anonymous = request.POST['anonymous']
    logger.error(str(anonymous) + " this is anonymous value")
    comment = comment.replace('^space^', ' ')
    logger.error(comment)
    if len(comment) > 200:
        msg = 'Exceeds limit 200 characters, the left characters will not be stored'
        comment = comment[:200]
    logger.error("check it")
    session = TutorialSession.objects.get(pk=tutorial_sessions_id)
    score = int (float (score))
    session.score = score
    session.comment = comment
    session.showname  = anonymous
    session.status = 4
    session.save()
    tutor = session.tutor
    #only if a tutor is evaluated, will this be executed, but NOT directly after booking
    tutor.average = (tutor.average * tutor.reviewed_times + score) / (tutor.reviewed_times + 1)
    tutor.reviewed_times = tutor.reviewed_times + 1
    tutor.save()
    return mybooking(request, myuser_id)


def mywallet(request, myuser_id): #TODO filter thirty days!
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    student_list = ""
    tutor_list = ""
    mytutor = None
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
    return render(request, 'myaccount/mywallet.html', {'user':myuser, 'student_list':student_list, 'tutor_list':tutor_list, 'msg': "", 'isstudent': isstudent, 'istutor': istutor , 'tutor':mytutor})
#def forget_password(request, myuser_id):

####mytransaction#####
def mytransaction(request, myuser_id): #TODO filter thirty days!
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        home(request) #return render(request, 'home.html')
    #if request.user == AnonymousUser:
    #    logger.error("I am anonymous!")
    #    return HttpResponseRedirect('/Tutorial/login/')auth
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    student_list = ""
    tutor_list = ""
    isstudent = "0"
    istutor = "0"
    timeformat = '%Y%m%d%H%M'
    now = datetime.now()
    nowtime = time.mktime(now.timetuple())
    refdelta = int(60 * 60 * 24 * 29 + now.hour * 3600 + now.minute * 60 + now.second) #The last 29 days + today
    if Student.objects.filter(myuser=myuser):
        mystudent = Student.objects.get(myuser=myuser)
        isstudent = "1"

        #for each session in transaction, calculate the time now and the time that transaction happen, if it happens 30 days ago, lambda function returns false
    list = filter(
        lambda session: nowtime - time.mktime(datetime.strptime(session.time, timeformat).timetuple()) <= refdelta and session.cashflow != 0,
        Transaction.objects.filter(myuser=myuser))
    if Tutor.objects.filter(myuser=myuser):
        mytutor = Tutor.objects.get(myuser=myuser)
        istutor = "1"
        return render(request, 'myaccount/mytransaction.html',{'user': myuser, 'list': list, 'isstudent': isstudent, 'istutor': istutor, 'tutor':mytutor})
    return render(request, 'myaccount/mytransaction.html', {'user':myuser, 'list': list, 'isstudent': isstudent, 'istutor': istutor })

####message####
def message(request, myuser_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    messages = Notification.objects.filter(myuser=myuser)
    return render(request, 'message/message.html', {'user': myuser, 'messages': messages})

def withdraw(request, myuser_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    student_list = ""
    tutor_list = ""
    messages = ""
    if Student.objects.filter(myuser=myuser):
        mystudent = Student.objects.get(myuser=myuser)
        student_list = TutorialSession.objects.filter(student=mystudent)
    if Tutor.objects.filter(myuser=myuser):
        mytutor = Tutor.objects.get(myuser=myuser)
        tutor_list = TutorialSession.objects.filter(tutor=mytutor)
        #return render(request, 'myaccount/mywallet.html',{'user': myuser, 'student_list': student_list, 'tutor_list': tutor_list, 'msg': messages, 'tutor':mytutor})
    #filter1: not tutor
    if not Tutor.objects.filter(myuser=myuser): #mytutor can use withdraw
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


def tutorwithdraw(request):
    logger.error("It is tutorwithdraw")
    if not request.user.is_authenticated(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user)  # myuser = get_object_or_404(MyUser, pk=myuser_id)
    amount = request.POST.get('withdraw', False)
    #filter2: not number
    try:
        cashflow = Decimal(amount)
    except Exception as e:
        messages = "Please enter a valid number"
        logger.error("I am Mytutor")
        list = Transaction.objects.filter(myuser=myuser)
        return render(request, 'mytutor.html', {'user': myuser, 'list': list, 'msg': messages})
    #filter3: not possitive
    logger.error("It is tutorwithdraw1")
    if cashflow <= 0:
        messages = "Please enter a positive number"
        logger.error("I am Mytutor")
        list = Transaction.objects.filter(myuser=myuser)
        return render(request, 'mytutor.html', {'user': myuser, 'list': list, 'msg': messages})
    #filter4: not enough moneyD
    logger.error("It is tutorwithdraw2")
    if cashflow > myuser.wallet.balance:
        messages = "You don't have enough money in your account"
        logger.error("I am Mytutor")
        list = Transaction.objects.filter(myuser=myuser)
        request.POST['withdraw'] = 0
        return render(request, 'mytutor.html', {'user': myuser, 'list': list, 'msg': messages})
    logger.error("It is tutorwithdraw4")

    myuser.wallet.balance = myuser.wallet.balance - cashflow
    myuser.wallet.save()
    messages = "Withdrawal success!" #TODO: remember that tutorialsession should keep track of hourly rate, and it records depost & withdraw
    Transaction.objects.create(myuser=myuser, time=datetime.now().strftime("%Y%m%d%H%M"),
                               cashflow=cashflow * (-1), type=1)

    logger.error("I am Mytutor")
    list = Transaction.objects.filter(myuser=myuser)
    return render(request, 'mytutor.html', {'user': myuser, 'list': list, 'msg': messages})


def deposit(request, myuser_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
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
                tutor = Tutor.objects.create(myuser=myuser, hourly_rate = 100)
                privateTutor = PrivateTutor.objects.create(tutor=tutor)
            elif identity == 'Student and Contracted Tutor':
                student = Student.objects.create(myuser=myuser)
                tutor = Tutor.objects.create(myuser=myuser)
                setattr(tutor, 'timeslot',
                        '111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111')
                tutor.save()
                contractedTutor = ContractedTutor.objects.create(tutor=tutor)
            elif identity == 'Student and Private Tutor':
                student = Student.objects.create(myuser=myuser)
                tutor = Tutor.objects.create(myuser=myuser, hourly_rate = 100)
                privateTutor = PrivateTutor.objects.create(tutor=tutor)
            else:   # contracted tutor
                tutor = Tutor.objects.create(myuser=myuser)
                setattr(tutor,'timeslot','111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111')
                tutor.save()
                contractedTutor = ContractedTutor.objects.create(tutor=tutor)
            return redirect('../login')
    else:
        form = RegistrationForm()
    variables = {
        'form': form
    }
    return render_to_response(
        'registration/register.html',
        variables, RequestContext(request)
    )

def search_tutor_name(request,myuser_id ): #TODO don't know what should admin be able to see lol
    tutors=Tutor.objects.filter(showProfile=True)
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
    show_tag = []
    for tut in tutors:
        tags = tut.tag_set.all()
        show_tag.append(tags)
    zipped = zip(tutors, show_tag)
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

    # only activated profile tutors
    selectAllTutors(request, tutor_set)
    
    logger.error(tutor_set)
    tagFilter(request, tutor_set)
    logger.error("---tag filtered---")
    logger.error(tutor_set)
    
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
    courses = Course.objects.all()
    variables = {
        "tutors": zipped,
        'courses':courses
    }
    return render(request, 'searchtutors/index.html', variables)

def selectAllTutors(request, tutor_set):
    tutors = Tutor.objects.filter(showProfile=True)
    logger.error("select all shown tutor")
    logger.error(tutors)
    for tut in tutors:
        if tut.showProfile:
            tutor_set.append(tut)

def tagFilter(request, tutor_set):
    result_tutors = []
    logger.error("-----tags-----")
    if 'tags' in request.GET:
        query = request.GET['tags']
        logger.error(query)
        tagset = query.split(',')
        if 'deleteTags' in request.GET:
            delete_query = request.GET['deleteTags']
            delete_tagset = delete_query.split(',')
            ret_list = []
            for item in tagset:
                if item not in delete_tagset:
                    ret_list.append(item)
        else:
            ret_list = tagset
        logger.error("ret_list ----")
        logger.error(ret_list)
        if ret_list and ret_list != ['']:
            for tag_name in ret_list:
                tag = Tag.objects.filter(name=tag_name)
                if tag:
                    for tut in tutor_set:
                        tags = tut.tag_set.all()
                        for tag in tags:
                            if tag.name != "" and tag.name in ret_list and tut not in result_tutors:
                                result_tutors.append(tut)
                                break
        else:
            logger.error("Chen Zihao is a cat!!")
            for ele in tutor_set:
                result_tutors.append(ele)
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
        if premin != "" and re.match(r'^[0-9]*$',premin) != None:
            min = int(request.GET['lowPrice'])
        else:
            min = 0
        if premax != "" and re.match(r'^[0-9]*$',premax) != None:
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
            elif order == "Rate high to low":
                tutor_set.sort(key=operator.attrgetter('hourly_rate'))
            else: #tutor sorted by avg
                tutor_set.sort(key=operator.attrgetter('average'), reverse=True)
    else:
        tutor_set.sort(key=operator.attrgetter('hourly_rate'))

def deleteTag(tutor, tag):
    tutor.tag_set.remove(tag=tag)
    tutor.save()

def addTag(tutor, tag_name):
    tags = Tag.objects.filter(name = tag_name)
    if tags:
        tags[0].tutors.add(tutor)
        tags[0].save()
    else:
        tag = Tag.objects.create(name=tag_name)
        tag.tutors.add(tutor)
        tag.save()
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

def tutorTimeslot(request, myuser_id, tutor_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    mytutor = get_object_or_404(Tutor, pk=tutor_id)
    return render(request, 'myaccount/tutorTimeslot.html', {'user':myuser, 'tutor': mytutor})

def tutorTimeslotSelecting(request, myuser_id, tutor_id):
    if not request.user.is_authenticated() or request.user.is_anonymous(): #visitor or client
        return render(request, 'home.html')
    if not MyUser.objects.filter(user=request.user):
        HttpResponseRedirect('/Tutorial/admin/')
    myuser = MyUser.objects.get(user=request.user) #myuser = get_object_or_404(MyUser, pk=myuser_id)
    mytutor = get_object_or_404(Tutor, pk=tutor_id)
    if 'newList' in request.POST:
        timeslot =  request.POST['newList'] # get new timeslot string
        mytutor.timeslot = timeslot
    if 'checked' in request.POST:
        checked = request.POST['checked']
    mytutor.save()
    return render(request, 'myaccount/tutorTimeslot.html', {'user':myuser, 'tutor': mytutor, 'check':checked })

