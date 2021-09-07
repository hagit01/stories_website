import feedparser

NewFeed = feedparser.parse("http://feeds.feedburner.com/bedtimeshortstories/LYCF")
entry = NewFeed.entries[1]
print(entry.keys())
print('Title :', entry.title)
print('Link :', entry.link)
print('Author :', entry.author)