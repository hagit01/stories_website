from datetime import date
import datetime
from .models import Story

now = datetime.datetime.now()
today = date.today()
d1 = today.strftime("%b. %d,%Y")

story_list = Story.objects.order_by("-id")
newest = story_list[0]
next_4_newest = story_list[1:5]
newest_4 = story_list[0:4]
most_viewed_stories = story_list[3:6]


def stories_processor(request):
    return {
        'now': now,
        'today': now,
        'd1': d1,
        'story_list': story_list,
        'newest': newest,
        'next_4_newest': next_4_newest,
        'newest_4': newest_4,
        'most_viewed_stories': most_viewed_stories,

    }