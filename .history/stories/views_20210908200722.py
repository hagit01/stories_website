import datetime
from datetime import date
from django.shortcuts import render, redirect
from .models import Category, Story, Contact
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
d1 = today.strftime("%b. %d,%Y")


def index(request):
        value = 1
        if request.COOKIES.get('visits'):
            value = int(request.COOKIES.get('visits'))

        last_visit = request.session.get('last_visit', now.strftime('%B %d, %Y %I:%M %p'))
        request.session['last_visit'] = now.strftime('%B %d, %Y %I:%M %p')

        story_list = Story.objects.order_by("-id")
        newest = story_list[0]
        next_4_newest = story_list[1:5]
        newest_stories = story_list[0:4]
        most_viewed_stories = story_list[3:6]

        young_children = Story.objects.filter(category=1).order_by("-id")
        older_children = Story.objects.filter(category=2).order_by("-id")

        context = {'today': now, 'd1': d1, 'newest': newest, 'next_4_newest': next_4_newest,
                   'newest_stories': newest_stories, 'young': young_children,
                   'older': older_children, 'most_viewed_stories': most_viewed_stories,
                   'visits': value, 'last_visit': last_visit}
        response = render(request, "stories/index.html", context)

        if value != 1:
            response.set_cookie('visits', value+1)
        else:
            response.set_cookie('visits', value)

        # response.delete_cookie('visits')
        return response
    else:
        return redirect('/login.html')


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

    newest = Story.objects.filter(category=pk).order_by("-id")[0]
    newest_stories = Story.objects.order_by("-id")[0:4]
    most_viewed_stories = Story.objects.order_by("-id")[3:6]
    context = {'today': now, 'stories': stories, 'newest': newest, 'pk': pk,
               'newest_stories': newest_stories, 'most_viewed_stories': most_viewed_stories}
    return render(request, "stories/category.html", context)


def story(request, pk):
    story_select = Story.objects.get(pk=pk)
    stories = Story.objects.filter(category=story_select.category).order_by("-id")
    newest = Story.objects.order_by("-id")[0]
    newest_stories = Story.objects.order_by("-id")[0:4]
    most_viewed_stories = Story.objects.order_by("-id")[3:6]
    context = {'today': now, 'story': story_select, 'stories': stories, 'newest': newest,
               'newest_stories': newest_stories, 'most_viewed_stories': most_viewed_stories}
    return render(request, "stories/story.html", context)


# def contact(request):
#     newest = Story.objects.order_by("-id")[0]
#     newest_stories = Story.objects.order_by("-id")[0:4]
#     most_viewed_stories = Story.objects.order_by("-id")[3:6]
#     context = {'today':now, 'newest': newest, 'newest_stories': newest_stories,
#               'most_viewed_stories': most_viewed_stories}
#     return render(request, "stories/contact.html", context)
    

def search(request):
    global search_str
    latest = Story.objects.order_by("-id")[0]
    newest_4 = Story.objects.order_by("-id")[0:4]
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
    context = {'today': now, 'latest': latest, 'stories': stories, 'newest_4': newest_4, 'numbers': numbers, 'search_str': search_str}
    return render(request, 'stories/search.html', context)


def contact(request):
    result = '...'
    newest = Story.objects.order_by("-id")[0]
    newest_stories = Story.objects.order_by("-id")[0:4]
    most_viewed_stories = Story.objects.order_by("-id")[3:6]
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
            result = "Thank you for your contact. We will answer you soon"
    else:
        form = FormContact()

    context = {'today': now, 'newest': newest, 'newest_stories': newest_stories, 'most_viewed_stories': most_viewed_stories,
               'form': form, 'result': result}

    return render(request, 'stories/contact.html', context)


def register(request):
    newest = Story.objects.order_by("-id")[0]
    registered = False
    if request.method == "POST":
        form_user = UserForm(data=request.POST)
        form_por = UserProfileInfoForm(data=request.POST)
        if form_user.is_valid() and form_por.is_valid() and form_user.cleaned_data['password'] == form_user.cleaned_data['confirm']:
            user = form_user.save()
            user.set_password(user.password)
            user.save()
            profile = form_por.save(commit=False)
            profile.user = user
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            registered = True
        if form_user.cleaned_data['password'] != form_user.cleaned_data['confirm']:
            form_user.add_error('confirm', 'The passwords do not match')
            print(form_user.error, form_por.errors)
    else:
        form_user = UserForm()
        form_por = UserProfileInfoForm()
    context = {'user_form': form_user, 'profile_form': form_por, 'newest': newest, 'registered': registered, 'today': now}
    return render(request, 'stories/register.html', context)


def user_login(request):
    now = datetime.datetime.now()
    newest = Story.objects.order_by("-id")[0]
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            result = "Hello " + username
            request.session['username'] = username
            username = request.session.get('username', 0)
            return render(request, 'stories/login.html', {'login_result': result,
                                                          'username': username, 'today': now, 'newest': newest})
        else:
            print("You can't login.")
            print("Username: {} and password: {}".format(username, password))
            login_result = "Username or password is incorrect!"
            return render(request, 'stories/login.html', {'login_result': login_result, 'today': now, 'newest': newest})
    else:
        return render(request, 'stories/login.html', {'today': now, 'newest': newest})


@login_required
def user_logout(request):
    now = datetime.datetime.now()
    newest = Story.objects.order_by("-id")[0]
    logout(request)
    result = "You're logged out. You can login again."
    context = {'logout_result': result, 'today': now, 'newest': newest}
    return render(request, 'stories/login.html', context)
    pass


# @login_required
# def subscribe(request):
#     now = datetime.datetime.now()
#     username = request.session.get('username', 0)
#     if request.method == 'POST':
#         email_address = request.POST.get('email')
#         subject = 'Welcome to Stories for Children website'
#         message = 'Hope you are enjoying your stories!'
#         recepient = str(email_address)
#         send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
#         result = 'Our email was sent to your mail box. Thank you. '
#
#         return render(request, 'stories/base.html', {'today': now, 'username': username, 'result': result})
#
#     return render(request, 'stories/base.html', {'today': now, 'username': username})


@login_required
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

        return render(request, 'stories/base.html', {'today': now, 'username': username, 'result': result})

    return render(request, 'stories/base.html', {'today': now, 'username': username})


def read_feeds(request):
    news_feed = feedparser.parse('http://feeds.feedburner.com/bedtimeshortstories/LYCF')
    entry = news_feed.entries

    now = datetime.datetime.now()
    username = request.session.get('last_visit', False)
    return render(request, 'stories/feeds.html', {'today': now, 'username': username, 'feeds': entry})


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