import urllib, time, json, os, thread
from subprocess import Popen, PIPE
from shutil import move
from communication import send_mail, call_number
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('switch')
def switch(data):
    global isRunning
    text = data['message'].encode('ascii', 'ignore')
    if text == 'off':
	isRunning = False
    if text == 'on':
	isRunning = True
	thread.start_new_thread(mainLoop, ())
    socketio.emit('echo', {'echo' : str(isRunning)})

PROTOCOL = 'http://'
PORT = '8081'
CAMS = ['cam0.local','cam1.local']
MAILS = ['abc@abc.com']
NUMBERS = ['+491234567890']
PASSED_SECONDS = 300
ALARM_SOUND = 'alarm.mp3'
DARKNET_BINARY_PATH = ''
DARKNET_THRESHOLD = '0.5'

index = 0
oldtime = 0
isRunning = True

def getNextImageName(cam):
    try:
        json_url = PROTOCOL + cam + ':' + PORT + '/get-images'
	response = urllib.urlopen(json_url)
	data = json.loads(response.read())
	return data[0]
    except:
        #print('error getting next image name')   
	return '0'

def downloadImage(cam, name):
    if name == '0':
        return 0
    try:
	img_url = PROTOCOL + cam + ':' + PORT + '/get-images/' + name
	img_downloader = urllib.URLopener()
	img_downloader.retrieve(img_url, name)
        return 1
    except:
        print('error downloading image')
        return 0

def downloadNextImage():
    global index
    global CAMS
    name = getNextImageName(CAMS[index])
    return_code = 0
    if name != '0':
        return_code = downloadImage(CAMS[index], name)
    if index + 1 < len(CAMS):
	index += 1
    else:
	index = 0
    if return_code == 0:
        return 'fail'
    else:
        return name

def checkForDetectedImages():
    global oldtime
    while isRunning:
	time.sleep(2)
        for file in os.listdir('.'):
	    if isRunning == False:
		return
            if file.endswith(".png"):
                print("Person detected")
	        move(file, 'detected/' + file)
		file_split = file.split('.')
		orig_file = file_split[0] + '.' + file_split[1]
		move(orig_file, 'detected/' + orig_file)
		if time.time() - oldtime >= PASSED_SECONDS or oldtime == 0:
		    oldtime = time.time()
		    call_number(NUMBERS)
		    Popen(['mpg321', '-q', ALARM_SOUND])
		    print('called')
		send_mail(MAILS, 'Person detected!', 'Pictures sent as attachment.', ['detected/' + orig_file, 'detected/' + file])

def deleteAll(cam):
    data = 'fail'
    while data is 'fail':
        try:
            json_url = PROTOCOL + cam + ':' + PORT + '/delete-all'
	    response = urllib.urlopen(json_url)
	    data = response.read()
	    print data
        except:
            #print('error deleting images')   
	    data = 'fail'
	    print data

def mainLoop():
    for cam in CAMS:
        deleteAll(cam)
    print('finished deleting')
    thread.start_new_thread(checkForDetectedImages, ())
    p = Popen(DARKNET_BINARY_PATH + ' detect cfg/yolo.cfg yolo.weights -thresh ' + DARKNET_THRESHOLD, shell=True, stdin = PIPE, bufsize = 1)
    print('started')
    time.sleep(10)
    while isRunning:
        name = downloadNextImage()
        if name != 'fail':
            print name
            p.stdin.write(name + '\n')
            while(os.path.isfile("lock")):
	        pass
    p.kill()

if __name__ == "__main__":
    thread.start_new_thread(mainLoop, ())
    socketio.run(app, '0.0.0.0', 8080)

