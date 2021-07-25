"""
$env:FLASK_ENV = "development"
$env:APP_NAME = "app.py"
"""

from flask import Flask,request, render_template
from flask_mail import Mail, Message
from flask_mysqldb import MySQL 

app = Flask(__name__)

app.config['MYSQL_USER'] = 'sql6416074'
app.config['MYSQL_PASSWORD'] = 'ycHm8YvETw'
app.config['MYSQL_HOST'] = 'sql6.freemysqlhosting.net'
app.config['MYSQL_DB'] = 'sql6416074'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

global flag 
flag=0

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/',methods=['POST'])
def authenticate():
    username = request.form['email']
    password = request.form['pass']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE username='"+username+"' AND password='"+password+"'")
    data=cur.fetchone()
    if data is None:
        return "Username or Password is wrong"
    else:
        # return "Logged in successfully"
        global flag
        flag=1
        return render_template('index.html')

@app.route('/index')
def index():
    if flag==1:
        return render_template('index.html')
    else:
        return render_template('login.html')

@app.route('/ContactUs')
def ContactUs():
    return render_template('ContactUs.html')

# @app.route('/login')
# def Login():
#     return render_template('login.html')

@app.route('/fall')
def Fall():
    return render_template('fall.html')

@app.route('/VehicleCrash')
def VehicleCrash():
    return render_template('VehicleCrash.html')

@app.route('/SocialDistancing')
def SocialDistancing():
    return render_template('SocialDistancing.html')
    

@app.route('/ObjectDetection')
def ObjectDetection():
    return render_template('ObjectDetection.html')

@app.route('/Survilliance')
def Survilliance():
    # importing required libraries
    import numpy as np
    import cv2

    #reading input video frame by frame by opencv
    cap = cv2.VideoCapture('video1.avi')

    #saving first frame of the video as background image
    _, BG= cap.read()
    BG=cv2.cvtColor(BG,cv2.COLOR_BGR2GRAY)            #changing backgroung image to gray scale
    cv2.equalizeHist(BG)                              #increasing contrast of the image
    BG=cv2.GaussianBlur(BG,(7,7),0)                   #bluring the edges of the image 
    cv2.imshow('BG', BG)
    #circular dictionary initiaization which has frame no. as key and list centroids of blobs as value 
    fgcnts={}
    frameno=0
    flag=0
    while (cap.isOpened()):
        # reading frame from video one by one
        ret, frame = cap.read()
    
        if ret==0:                    #break the if it is last frame
            break
        
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)        #change frame to gray scale
        cv2.equalizeHist(gray)                             # increasing cntrast of frame
        gray=cv2.GaussianBlur(gray,(7,7),0)                #bluring the edges 
    
        # taking absolute difference of background image with current frame
        fgmask=cv2.absdiff(gray.astype(np.uint8), BG.astype(np.uint8))
    
        #applying threshold on subtacted image
        rt,fgmask=cv2.threshold(fgmask.astype(np.uint8), 25, 255, cv2.THRESH_BINARY)
  
        #applying mrphological operation both erosion and dilation  
        kernel2 = np.ones((8,8),np.uint8)   #higher the kernel, eg (10,10), more will be eroded or dilated
        thresh2 = cv2.morphologyEx(fgmask,cv2.MORPH_CLOSE, kernel2,iterations=3)
        #applying edge detector after morphological operation 
        edged = cv2.Canny(thresh2, 30,50)
    
        #finding boundaries of all blobs of the frame
        contours, hierarchy = cv2.findContours(edged,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
        #initialising list of centroids of blobs
        fgcnts[frameno%1000]=[]
        for contour in contours:
            #finding the centroid of each blob
             M = cv2.moments(contour)
             if not M['m00'] == 0: 
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                centre=(cx,cy) 
                #appending the centroid to list
                fgcnts[frameno%1000].append(centre)
           
            #checking for unattended object
                if frameno>200:
                    if cv2.contourArea(contour) in range(200,15000) and centre in fgcnts[(frameno-190)%1000] and fgcnts[(frameno-100)%1000] and fgcnts[(frameno-50)%1000]:
                        flag=1
                        (x,y,w,h) = cv2.boundingRect(contour)
                        cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 0, 255), 2)
                        cv2.putText(frame,'Alert', (x,y-10),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2) 
        
        #background update: to remove the wrong prediction press key 'a'    
        if(cv2.waitKey(1) & 0xFF == ord('a')):
            BG[y:y+h, x:x+w]=gray[y:y+h, x:x+w] 
        
        frameno+=1
        #cv2.imshow('result', edged  )
        frame=cv2.resize(frame, (1500,720))          #final frame is resized to a value
        cv2.imshow('original',frame)                #final frame is shown

    #to
        if(cv2.waitKey(1) & 0xFF == ord('q')):
            break
    #when everything is done, release cap
    cap.release()
    cv2.destroyAllWindows()
    if(flag==1):
        mail = Mail(app) # instantiate the mail class
   
        # configuration of mail
        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = 'capstone.ivs@gmail.com'
        app.config['MAIL_PASSWORD'] = 'capstone123'
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True
        mail = Mail(app)
   
        # message object mapped to a particular URL ‘/’
        msg = Message(
                    'ALERT',
                    sender ="capstone.ivs@gmail.com",
                    recipients = ["shivamrawat2000@gmail.com","siddhant.zyx@gmail.com","ayushiawesome10@gmail.com","aakashbali24@gmail.com"]
                    )
        msg.body = "Suspicious Object Detected"
        mail.send(msg)
        print('Sent')
        
        return render_template('alert.html')
    else:
        return render_template('normal.html')  

if __name__ == '__main__':

    app.run(host='127.0.0.1', port=8000, debug=True)
