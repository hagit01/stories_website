import datetime
from datetime import date
from django.shortcuts import render, redirect
from .models import Category, Story, Contact, User, UserProfileInfo
from django.http import HttpResponse
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import FormContact, UserForm, UserProfileInfoForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json

import feedparser

from MyNews.settings import EMAIL_HOST_USER
# from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

from rest_framework import viewsets
from rest_framework import permissions

from stories.serializers import StorySerializer

now = datetime.datetime.now()
today = date.today()


def index(request):
    value = 1
    if request.COOKIES.get('visits'):
        value = int(request.COOKIES.get('visits'))

    last_visit = request.session.get('last_visit', now.strftime('%B %d, %Y %I:%M %p'))
    request.session['last_visit'] = now.strftime('%B %d, %Y %I:%M %p')

    young_children = Story.objects.filter(category=1).order_by("-id")
    older_children = Story.objects.filter(category=2).order_by("-id")

    context = {'young': young_children, 'older': older_children,
               'visits': value, 'last_visit': last_visit}
    response = render(request, "stories/index.html", context)

    if value != 1:
        response.set_cookie('visits', value+1)
    else:
        response.set_cookie('visits', value)

    return response
    

def category(request, pk):
    story_list = Story.objects.filter(category=pk).order_by("-id")

    for story in story_list:
        story.content = re.sub('<[^<]+?>', '', story.content)

    page = request.GET.get('page', 1)  # trang bắt đầu

    paginator = Paginator(story_list, 3)  # số story/trang

    try:
        stories = paginator.page(page)
    except PageNotAnInteger:
        stories = paginator.page(1)
    except EmptyPage:
        stories = paginator.page(paginator.num_pages)

    context = {'stories': stories, 'pk': pk}
    return render(request, "stories/category.html", context)


def story(request, pk):
    story_select = Story.objects.get(pk=pk)
    other_story = Story.objects.all().exclude(id=pk)

    context = {'today': now, 'story': story_select, 'other_story': other_story}
    return render(request, "stories/story.html", context)


def search(request):
    global search_str

    stories = []
    if request.method == 'GET':
        if request.GET.get('name'):
            search_str = request.GET.get('name')
        else:
            search_str = ''

        if search_str != '':
            stories = Story.objects.filter(Q(name__contains=search_str)|Q(content__contains=search_str)).order_by("-id")
    for story in stories:
        story.content = re.sub('<[^<]*?>', '', story.content)
    numbers = len(stories)
    context = {'numbers': numbers, 'search_str': search_str, 'stories': stories}
    return render(request, 'stories/search.html', context)


def contact(request):
    result = ""
    form = FormContact()
    if request.method == 'POST':
        form = FormContact(request.POST, Contact)
        if form.is_valid():
            request.POST._mutable = True
            post = form.save(commit=False)
            post.name = form.cleaned_data['name']
            post.phone_number = form.cleaned_data['phone_number']
            post.email = form.cleaned_data['email']
            post.subject = form.cleaned_data['subject']
            post.message = form.cleaned_data['message']
            post.save()

            result = '''
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                Your message has successfully sent.
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            '''

    context = {'form': form, 'result': result}

    return render(request, 'stories/contact.html', context)


def register(request):
    registered = False
    register_msg = ''
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            if user_form.cleaned_data['password'] == user_form.cleaned_data['confirm']:
                user = user_form.save()
                print(user)
                user.set_password(user.password)
                user.save()

                profile = profile_form.save(commit=False)
                profile.user = user
                if 'image' in request.FILES:
                    profile.image = request.FILES['image']
                profile.save()
                registered = True
                register_msg = '''
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        Successfully register! <a href="/login.html" class="alert-link">Login here.</a>
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                '''
                user_form = UserForm()
                profile_form = UserProfileInfoForm()
        else:
            register_msg = '''
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    Register Fail!
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
            '''
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    context = {'user_form': user_form, 'profile_form': profile_form,
               'registered': registered, 'register_msg': register_msg}

    return render(request, 'stories/register.html', context)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            result = "Hello " + username
            request.session['username'] = username
            username = request.session.get('username', 0)
            return redirect('/')
        else:
            print("You can't login.")
            print("Username: {} and password: {}".format(username, password))
            login_result = "Username or password is incorrect!"
            return render(request, 'stories/login.html', {'login_result': login_result})
    else:
        return render(request, 'stories/login.html')


@login_required
def user_logout(request):
    logout(request)
    result = "You're logged out. You can login again."
    context = {'logout_result': result,}
    return redirect('/')
    return render(request, 'stories/login.html', context)


def subscribe(request):
    now = datetime.datetime.now()
    last_visit = request.session.get('last_visit', False)
    username = request.session.get('username', 0)
    if request.method == 'POST':
        email_address = request.POST.get('email')
        subject = 'Welcome to Stories for Children website'
        message = 'Hope you\'re enjoy the reading journey'
        recipient = str(email_address)

        http_content = '<h2 style="color:blue"><i>Dear Reader,</i></h2>'\
                        + '<p>Welcome to <strong>Stories for Children</strong> website.</p>'\
                        + '<h4 style="color:red">' + message + '</h4>'

        msg = EmailMultiAlternatives(subject, message, EMAIL_HOST_USER, [recipient])
        msg.attach_alternative(http_content, 'text/html')
        msg.send()
        result = 'Thank you, our email was sent to your mail box.'

        return render(request, 'stories/base.html', {'username': username, 'result': result})

    return render(request, 'stories/base.html', {'username': username})


def read_feeds(request):
    news_feed = feedparser.parse('http://feeds.feedburner.com/bedtimeshortstories/LYCF')
    entry = news_feed.entries

    username = request.session.get('last_visit', False)
    return render(request, 'stories/feeds.html', {'username': username, 'feeds': entry})


def stories_service(request):
    stories = Story.objects.order_by('-id')
    result_list = list(stories.values('category', 'name', 'author', 'url', 'public_day', 'image', 'content'))
    return HttpResponse(json.dumps(result_list, indent=4, sort_keys=True, default=str).encode('utf8'))


class StoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed stories (or edited)
    """
    queryset = Story.objects.all().order_by('-id')
    serializer_class = StorySerializer
    # Cấp quyền cho người dùng
    # permission_classes = [permissions.IsAdminUser] # đọc/ ghi
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # chỉ đọc