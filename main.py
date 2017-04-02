#! /usr/bin/env python

import os
import random
import time
import sys
import RPi.GPIO as GPIO
import alsaaudio
import wave
import random
from creds import *
import requests
import json
import re
from memcache import Client

#Settings
button = 18 #GPIO Pin with button connected
P1 = 24
P2 = 25
lights = [P1, P2] # GPIO Pins with LED's conneted
device = "plughw:1" # Name of your microphone/soundcard in arecord -L

#Setup
recorded = False
servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))



def internet_on():
    print "Checking Internet Connection"
    try:
        r =requests.get('https://api.amazon.com/auth/o2/token')
        print "Connection OK"
        return True
    except:
	print "Connection Failed"
    	return False

	
def gettoken():
	token = mc.get("access_token")
	refresh = refresh_token
	if token:
		return token
	elif refresh:
		payload = {"client_id" : Client_ID, "client_secret" : Client_Secret, "refresh_token" : refresh, "grant_type" : "refresh_token", }
		url = "https://api.amazon.com/auth/o2/token"
		r = requests.post(url, data = payload)
		resp = json.loads(r.text)
		mc.set("access_token", resp['access_token'], 3570)
		return resp['access_token']
	else:
		return False
		

def alexa():
	GPIO.output(lights, GPIO.HIGH)
	url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
	headers = {'Authorization' : 'Bearer %s' % gettoken()}
	d = {
   		"messageHeader": {
       		"deviceContext": [
           		{
               		"name": "playbackState",
               		"namespace": "AudioPlayer",
               		"payload": {
                   		"streamId": "",
        			   	"offsetInMilliseconds": "0",
                   		"playerActivity": "IDLE"
               		}
           		}
       		]
		},
   		"messageBody": {
       		"profile": "alexa-close-talk",
       		"locale": "en-us",
       		"format": "audio/L16; rate=16000; channels=1"
   		}
	}
	with open(path+'recording.wav') as inf:
		files = [
				('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
				('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
				]	
		r = requests.post(url, headers=headers, files=files)
	if r.status_code == 200:
		for v in r.headers['content-type'].split(";"):
			if re.match('.*boundary.*', v):
				boundary =  v.split("=")[1]
		data = r.content.split(boundary)
		for d in data:
			if (len(d) >= 1024):
				audio = d.split('\r\n\r\n')[1].rstrip('--')
		with open(path+"response.mp3", 'wb') as f:
			f.write(audio)
		GPIO.output(P2, GPIO.LOW)
		GPIO.output(P1, GPIO.HIGH)
		print "P2 off"
		print "P1 on"
		time.sleep(0.1)
		print "talking"
		#os.system('mpg123 -q {}1sec.mp3 {}response.mp3'.format(path, path))
		os.system('mpg123 -q {}response.mp3'.format(path, path))
		print "talked"
		GPIO.output(P1, GPIO.LOW)
		print "P1 off"
	else:
		print "error"
		GPIO.output(P2, GPIO.LOW)
		print "P2 off"
		time.sleep(2)
		GPIO.output(lights, GPIO.LOW)
		print "P1, P2 off"


def start():
	last = GPIO.input(button)
	inp = None
	recorded=False
	while True:
		val = GPIO.input(button)
		if val != last:
			last = val
			if val == 0 and recorded == True:
				print 'Thinking...'
				rf = open(path+'recording.wav', 'w') 
				rf.write(audio)
				rf.close()
				inp = None
				alexa()
				print "main loop"
			elif val == 1:
				print 'Listening...'
				GPIO.output(P2, GPIO.HIGH)
				print "P2 on"
				inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device)
				inp.setchannels(1)
				inp.setrate(16000)
				inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
				inp.setperiodsize(500)
				audio = ""
				l, data = inp.read()
				if l:
					audio += data
				recorded = True
		elif val == 1 and inp:
			l, data = inp.read()
			if l:
				audio += data
		else:
			time.sleep(0.1)
	
def test():
	i=120
	while i>0:
		i = i -1
		print "test mode: ", GPIO.input(button)
		time.sleep(0.5)


if __name__ == "__main__":
	GPIO.setwarnings(False)
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(lights, GPIO.OUT)
	GPIO.output(lights, GPIO.LOW)
	while internet_on() == False:
		print "."
	token = gettoken()
	
	#os.system('mpg123 -q {}1sec.mp3 {}hello.mp3'.format(path, path))
	if len(sys.argv)>=2 and sys.argv[1]=="test":
		test()
		sys.exit(1)
	start()
