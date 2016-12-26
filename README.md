#Darknet Person Detection

I limited darknet only to person detection for use with my raspberry security night cams.

The server.py is a flask server checking the cams for new images. If it recognizes a person, it calls you using twilio and sends mails with relevant pictures.

It's just a temporary solution and not very useful expect for me, because many things are hardcoded. In the near future, I am going to write a new solution using TensorFlow for the recognition part.

###Note

Link to weights file http://pjreddie.com/media/files/yolo.weights