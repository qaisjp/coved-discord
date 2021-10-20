import os
import django
import json
import requests
import time
os.environ["DJANGO_SETTINGS_MODULE"] = 'django_project.settings'
django.setup()
from discord_bot.models import Discord_User, Discord_Mention

channel_id = '814686064416915486'
limit = 100
headers = {'Authorization': 'Bot ODE2MDE1NjAzODIyMzYyNjY3.YD0zwA.J3Uzv64I5VUlZURztMi9LDAFvFA'}

def create_user(user_id, username):
    try:
        user = Discord_User.objects.get(user_id=user_id)
        if not user.username == username:
            print(f"Changing username {user.username} to {username}")
            user.username = username
            user.save()
    except Exception:
        u = Discord_User(user_id=user_id, username=username)
        u.save()

def mention_exists(msg_id, author, target):
    try:
        _ = Discord_Mention.objects.get(message_id=msg_id, source_user=author, dest_user=target)
        return True
    except Exception:
        return False


api_base_url = f'https://discord.com/api/v8/channels/{channel_id}/messages?limit={100}'
r = requests.get(api_base_url, headers=headers)
obj = json.loads(r.text)

while (obj != []):
    for o in obj:
        message_id = o['id']
        author_id = o['author']['id']
        author_name = o['author']['username']
        mentions = o['mentions']
        timestamp = o['timestamp']
        try:
            reference = o['message_reference']
            continue
        except:
            timestamp = timestamp[:10] + " " + timestamp[11:19] + "+00"
            mentions_combined = ', '.join([m['id'] + " " + m['username'] for m in mentions])
            if len(mentions) == 0:
                continue
            create_user(author_id, author_name)
            for mention in mentions:
                destination = mention['id']
                destination_name = mention['username']
                create_user(destination, destination_name)

            for mention in mentions:
                author = Discord_User.objects.get(user_id=author_id)
                target = Discord_User.objects.get(user_id=mention['id'])
                if not mention_exists(message_id, author, target):
                    m = Discord_Mention(message_id=message_id, source_user=author, dest_user=target, timestamp=timestamp)
                    print(f"Creating message {author.username} -> {target.username} ({message_id} @ {timestamp})")
                    m.save()
                else:
                    print(f"Skipping message {author} -> {target} ({message_id} @ {timestamp}")

    url = api_base_url + f'&before={message_id}'
    r = requests.get(url, headers=headers)
    obj = json.loads(r.text)
