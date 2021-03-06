from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
# //, UserImageForm, UserForm2
from .forms import UserRegisterForm, CommitteeForm, UserImageForm, UserForm2
from django.template.loader import get_template
from django.template import Context
from django.utils import timezone

from .models import Delegate, Event, Committee
from django.contrib.auth.models import User

# INDEX


def index(request):
    all_events = Event.objects.all().order_by('-date')
    D = []
    myEvents = []


    ## Last Logged in users

    #count = Delegate.objects.count()
    all_users = User.objects.all()

    user_list=[]
    check = timezone.now() + timezone.timedelta(minutes=-15)

    for user in all_users:
        if user.last_login is None:
            user.last_login = timezone.now()
        
        if (user.last_login >= check) and (user.is_authenticated) :
            user_list.append(user)


    for i in all_events:
        organizer = i.core_organizer
        event = i.event
        organization = i.organization
        date = i.date
        venue = i.venue
        price = i.price
        if date < timezone.now():  # removes events that occurred in past
            continue
        if str(organizer) == str(request.user):
            myEvents.append(event)
        L = (event, organization, date, venue, price, organizer)
        D.append(L)

    throw_to_frontend = {
        'events': D,
        'myEvents': myEvents,
        'users': user_list
    }
    return render(request, 'user/index.html', throw_to_frontend)


# event registration saving in database

def save_event(request):
    print(request.POST)
    # getting current logged in username
    username = request.user.get_username()
    # getting id of currently logged in username
    # id used in creating new Event object
    id = Delegate.objects.only('id').get(name=username).id
    event = request.POST.get('event')
    organization = request.POST.get('org')
    date = request.POST.get('date')
    venue = request.POST.get('venue')
    price = request.POST.get('price')
    numberOfCommittees = request.POST.get('noOfCommittees')
    description = request.POST.get('description')
    
    created_event = Event.objects.create(core_organizer_id=id, event=event, organization=organization, date=date, venue=venue, price=price, numberOfCommittees=numberOfCommittees,description=description)

    temp = []
    integercount = int(numberOfCommittees)
    for i in range(integercount):
        temp.append(i+1)
    event_iddd = created_event.id
    print(event_iddd)
    #print(event_id)
    L = [event_iddd, event, price, numberOfCommittees, temp]
    committeeForm = CommitteeForm()
    throw_to_frontend = {
        'info': L,
        'committeeForm': committeeForm
    }
    return render(request, 'user/create_committee.html', throw_to_frontend)
    #return redirect(index)  # redirects for index view to run


# REGISTER HERE

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone_no')
            Fname = form.cleaned_data.get('first_name')
            Lname = form.cleaned_data.get('last_name')

            ######################### mail system ####################################

            htmly = get_template('user/Email.html')
            d = {'username': username}
            subject, from_email, to = 'welcome', 'your_email@gmail.com', email
            html_content = htmly.render(d)
            # msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            #msg.attach_alternative(html_content, "text/html")
            # msg.send()
            ###############
            messages.success(
                request, f'Your account has been created ! You are now able to log in')
            newUser = Delegate(name=username, rating=0, join_date=timezone.now(
            ), first_name=Fname, last_name=Lname, acheivement="none")
            newUser.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form, 'title': 'register here'})

# login forms


def Login(request):
    if request.method == 'POST':

        # AuthenticationForm_can_also_be_used__

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            ##url = 'user/' + username

            return redirect('/')
        else:
            messages.info(request, f'Account does not exist. Please try again')
    form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form, 'title': 'log in'})


# NEW LOGGED IN FUNCTION WHICH SENDS TO PROFILE PAGE OF THE USER

def loggedin(request, username):
    login = str(request.user)
    if username != login:
        canedit = 0
    else:
        canedit = 1

    d = get_object_or_404(Delegate, name=username)
    rating = d.rating
    date_joined = d.join_date
    acheivements = d.acheivement
    fname = d.first_name
    lname = d.last_name
    name = fname + ' ' + lname

    imageForm = UserImageForm()
    userEditForm = UserForm2(data={'first_name': request.user.first_name, 'last_name': request.user.last_name, 'acheivement': acheivements})

    throw_to_frontend = {
        'title': 'Profile',
        'rating': rating,
        'name': name,
        'username': username,
        'join_date': date_joined,
        'acheivement': acheivements,
        'profile_pic': d.profile_pic,
        'edit':  canedit,
        'imageform': imageForm,
        'userform': userEditForm,
    }
    return render(request, 'user/profile.html', throw_to_frontend)


def committee(request, username):
    context = {}

    form = CommitteeForm(request.POST or None, request.FILES or None)

    #event_id = Event.objects.last().id
    #event_id += 1
    if form.is_valid():
        form.save()
    #context['nei'] = event_id
    context['form'] = form
    return render(request, 'user/create_event.html', context)


#   COMMITTEE SAVING IN DATABASE

def save_committee(request, event_id):
    if request.method == 'POST':
        committee_info_form = CommitteeForm(data=request.POST, instance=request.user)

        if committee_info_form.is_valid():

            name = committee_info_form.cleaned_data['name']
            registrations = committee_info_form.cleaned_data['numberOfRegistrations']
            committee_description = committee_info_form.cleaned_data['committee_description']
            link_to_BG = committee_info_form.cleaned_data['linkToBackgroundGuide']

            event_instance = Event.objects.get(pk=event_id)
            Committee.objects.create(event=event_instance, name=name, numberOfRegistrations=registrations, committee_description=committee_description, linkToBackgroundGuide=link_to_BG)


        else:
            print(update_user_form.errors)
    
    return redirect(f"/user/{request.user.username}")


# EDITING USER PROFILE PICTURE

def edit_profile(request):
    temp = str(request.user)
    user_profile = Delegate.objects.get(name=temp)
    
    if request.method == 'POST':
        #update_user_form = UserForm2(data=request.POST, instance=request.user)
        imageForm = UserImageForm(data=request.POST, instance=user_profile)

        if imageForm.is_valid():
            #user = update_user_form.save()
            #profile = imageForm.save(commit=False)
            #profile.user = user
            
            if 'profile_pic' in request.FILES:
                #userob = request.user
                user_profile.profile_pic = request.FILES['profile_pic']
            
            user_profile.save()

        else:
            print(imageForm.errors)

    # return redirect(loggedin(request, request.user))
    return redirect(f"/user/{request.user.username}")


# EDITING USER INFORMATION
def edit_user_info(request):
    temp = str(request.user)
    user_profile = Delegate.objects.get(name=temp)

    if request.method == 'POST':
        update_user_form = UserForm2(data=request.POST, instance=request.user)

        if update_user_form.is_valid():
            user_profile.first_name = update_user_form.cleaned_data['first_name']
            user_profile.last_name = update_user_form.cleaned_data['last_name']
            user_profile.acheivement = update_user_form.cleaned_data['acheivement']
        
            user_profile.save()
    
        else:
            print(update_user_form.errors)
    return redirect(f"/user/{request.user.username}")

# Returning create_event page

def create_event(request, username):
    return render(request, 'user/create_event.html', {'title': 'Create event'})

# Returning password change page


def password_change(request):
    return render(request, 'user/change_password.html', {'title': 'MUnite'})


def show_event(request, event_name):
    # id = Event.objects.only('id').get(event=event_name).id

    e = get_object_or_404(Event, event=event_name)
    D = [e.event, e.organization, e.date, e.venue, e.price, e.description]
    stuff_for_frontend = {
        'event': D
    }

    return render(request, 'user/event_description.html', stuff_for_frontend)
