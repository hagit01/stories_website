from django.db import models
import datetime
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Story(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=250, unique=True)
    author = models.CharField(max_length=250)
    url = models.URLField(null=True)
    content = RichTextUploadingField()
    public_day = models.DateField(default=datetime.date.today)
    image = models.ImageField(upload_to="stories/images", default="stories/images/default.jpg")

    def __str__(self):
        return str(self.id) + " " + self.name + " " + str(self.category.id)


class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, null=True)
    subject = models.CharField(max_length=400)
    message = models.TextField()
    submit_day = models.DateTimeField(default=datetime.datetime.now)
    
    def __str__(self):
        return self.name + ". " + self.subject


class UserProfileInfo(models.Model):
    # Create relationship from this class to User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any more attribute you want
    portfolio = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to="stories/images/", default="stories/images/people_default.png", null=True)

    def __str__(self):
        return self.user.username