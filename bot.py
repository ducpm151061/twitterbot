#!/usr/bin/env python
import tweepy
import time
import datetime
import os
import requests
# NOTE: I put my keys in the keys.py to separate them
# from this main file.
# Please refer to keys_format.py to see the format.
from keys_format import *

# NOTE: flush=True is just for running this script
# with PythonAnywhere's always-on task.
# More info: https://help.pythonanywhere.com/pages/AlwaysOnTasks/
print('this is my twitter bot', flush=True)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

FILE_NAME = '/home/pi/Code/Python/pi/last_seen_id.txt'
class Data:
    def __init__(self,data):
        self.data=data
    def data(self):
        return self.__init__
    def result(self):
        data_win=self.data['radiant_win']
        if data_win:
            win= 'Radiant'
        else:
            win= 'Dire'
        data_side=self.data['player_slot']
        if int(data_side) in range(0,128):
            side= 'Radiant'
        else:
            side= 'Dire'
        if win==side:
            return 'Win'
        else:
            return 'Lose'
    def duration(self):
        return str(int(int(self.data['duration'])/60))
    def hero(self):
        return list_hero_id[self.data['hero_id']]
    def kda(self):
        return '{}/{}/{}'.format(self.data['kills'],self.data['deaths'],self.data['assists'])
    def time(self):
        return datetime.datetime.fromtimestamp(int(self.data['start_time'])).strftime('%H:%M:%S %d/%m/%Y')
    

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    # DEV NOTE: use 1060651988453654528 for testing.
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(
                        last_seen_id,
                        tweet_mode='extended')
    direct_messages =api.list_direct_messages()
    sender_id=direct_messages[0].message_create['sender_id']
    message=direct_messages[0].message_create['message_data']['text']
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        recipient_id=mention.in_reply_to_user_id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if '#temp' in mention.full_text.lower():
            print('found #temp!', flush=True)
            print('responding back...', flush=True)
            cmd = 'vcgencmd measure_temp'
            line = os.popen(cmd).readline().strip()
            temp = line.split('=')[1].split("'")[0]
            update=' Temperature of raspberry pi 4: ' +temp + ' °C'
            #api.update_status(update, mention.id)
            api.send_direct_message(recipient_id,update)
        if '#dota' in mention.full_text.lower():
            print('found #dota!', flush=True)
            print('responding back..', flush=True)    
            res= requests.get('https://api.opendota.com/api/players/{}/recentMatches'.format(account_id))
            if res.status_code==200:
                data_send=''
                for i in res.json():
                    data=Data(i)
                    update=('{} {} in {} ({}) within {} minutes\n'.format(data.time(),data.result(),data.hero(),data.kda(),data.duration()))
                    data_send+=update
                #api.update_status(data_send , mention.id)
                api.send_direct_message(recipient_id,data_send)
        if '/dota' in message.lower():
            print('found /dota!', flush=True)
            print('responding back..', flush=True)    
            res= requests.get('https://api.opendota.com/api/players/{}/recentMatches'.format(account_id))
            if res.status_code==200:
                update=''
                for i in res.json():
                    data=Data(i)
                    update+=('{} {} in {} ({}) within {} minutes\n'.format(data.time(),data.result(),data.hero(),data.kda(),data.duration()))
            api.send_direct_message(sender_id,update)
            time.sleep(45)

        if '/temp' in message.lower():
            print('found /temp!', flush=True)
            print('responding back...', flush=True)
            cmd = 'vcgencmd measure_temp'
            line = os.popen(cmd).readline().strip()
            temp = line.split('=')[1].split("'")[0]
            update_temp=' Temperature of raspberrypi 4: ' + temp + ' °C'
            api.send_direct_message(sender_id,update_temp)
            time.sleep(45)
while True:
    reply_to_tweets()
    time.sleep(15)
