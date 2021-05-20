import cv2 as cv
from werkzeug.utils import secure_filename
from scipy.spatial import distance
from playsound import playsound
from flask import Flask,render_template,request,url_for,Response,stream_with_context,session,flash,make_response
app = Flask(__name__, instance_relative_config=True, template_folder='template')
app.secret_key="hello"
filenames=""
message=""
capacity=0
capacity1=0
@app.route('/hellos')
def hellos():
    return render_template('home.html')
@app.route('/through_image')
def through_image():
    return render_template('image.html')
def gen1(image,capacity):
    out_img=cv.cvtColor(image,cv.COLOR_RGB2GRAY)
    face_cascade=cv.CascadeClassifier(cv.data.haarcascades+'haarcascade_frontalface_alt2.xml')
    faces=face_cascade.detectMultiScale(out_img,scaleFactor=1.1,minNeighbors=5)
    i=0
    MIN_DISTANCE = 130
    for (x,y,w,h) in faces:
        rectangle=cv.rectangle(out_img,(x,y),(x+w,y+h),(0,0,255),1)
        if len(faces)>=2:
            label = [0 for i in range(len(faces))]
            for i in range(len(faces)-1):
                for j in range(i+1, len(faces)):
                    dist = distance.euclidean(faces[i][:2],faces[j][:2])
                    if dist<MIN_DISTANCE:
                        label[i] = 1
                        label[j] = 1
            new_img = cv.cvtColor(out_img, cv.COLOR_RGB2BGR) #colored output image
            for i in range(len(faces)):
                (x,y,w,h) = faces[i]
                if label[i]==1:
                    rectangle=cv.rectangle(new_img,(x,y),(x+w,y+h),(255,0,0),1)
                else:
                    rectangle=cv.rectangle(new_img,(x,y),(x+w,y+h),(0,255,0),1)
    imjpeg=cv.imencode('.jpg',rectangle)[1].tobytes()
    yield(b'--frame\r\n'+b'Content-Type: image/jpeg\r\n\r\n' + imjpeg + b'\r\n\r\n')
@app.route('/through_images',methods=['GET','POST'])
def through_images():
    if request.method=='POST':
        f=request.files['image[]']
        global filenames
        filenames=""
        global capacity1
        capacity1=0
        f1=request.form['Capacity']
        capacity1=int(f1)
        l=0
        filenames+=secure_filename(f.filename)
        l=len(filenames)
        f.save('/Users/saikscbs/Documents/project2/venuproj/Upload_Folder/'+secure_filename(f.filename))
    return render_template('imageoutput.html')
@app.route('/through_imagess')
def through_imagess():
    img=cv.imread('/Users/saikscbs/Documents/project2/venuproj/Upload_Folder/'+filenames) 
    return Response(stream_with_context(gen1(img,capacity1)),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/through_video')
def through_video():
    return render_template('video.html')   
@app.route('/through_videos',methods=['GET','POST'])
def through_videos():
    global capacity
    if request.method=="POST":
        f=request.form['text']
        f=int(f)
        capacity=f
    return render_template('outputvideo.html',capacity=f)
def gen():
    global capacity
    global message
    face_cascade=cv.CascadeClassifier(cv.data.haarcascades+'haarcascade_frontalface_default.xml')
    eyes_cascade=cv.CascadeClassifier(cv.data.haarcascades+'haarcascade_eye.xml')
    cap=cv.VideoCapture(0)
    '''d=cap.isOpened()
    if d==1:
        pass
    else:
        cap.Open()'''
    cap=cv.VideoCapture(1)
    count_img=0
    while (cap.isOpened() and count_img<=100):
        ret,img =cap.read()
        count_img+=1
        img = cv.resize(img, (0,0), fx=0.5, fy=0.5) 
        faces=face_cascade.detectMultiScale(img,scaleFactor=1.1,minNeighbors=5)
        i=0                   
        for(x,y,w,h) in faces:
            rectangle=cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            i=i+1
            if i<=capacity:
                rectangle=cv.putText(rectangle,'face num'+str(i),(x-10,y-10),cv.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            else:
                rectangle=cv.putText(rectangle,'exceeded',(50,50),cv.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                playsound("/Users/saikscbs/Documents/project2/proj3/sai.mp3")            
            jpegs = cv.imencode('.jpg', rectangle)[1].tobytes()
            yield (b'--frame\r\n'+b'Content-Type: image/jpeg\r\n\r\n' + jpegs + b'\r\n\r\n')
            if(cv.waitKey(1) & 0xFF ==ord('q')):
                break
    cap.release()
    cv.destroyAllWindows()
@app.route('/detecting')
def detecting():
    return Response(stream_with_context(gen()),mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__=='__main__':
    app.run(debug="True")