from instagrapi import Client
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag

from decouple import config
INSTA_USER = config('INSTA_USER')
INSTA_PWD = config('INSTA_PWD')

cl = Client()
cl.login(INSTA_USER, INSTA_PWD)

print("logged in")

post_str = "post#00000"
cl.photo_upload(f"./temp/{post_str}.jpg", "Test Caption")
