from turtle import left
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import time
import schedule
from tkinter import *
from tkinter import messagebox
import matplotlib.pyplot as plt
from twilio.rest import Client
from PIL import ImageTk, Image
import tkinter as tk


def save_info():
    Name = name.get()
    Totalmins = totalmins.get()
    print(Name, Totalmins, Warning)
    with open("User Name", "w") as d:
        d.write(Name)
    with open("Total minutes", "w") as f:
        f.write(str(Totalmins))


def save_info():
    Name = name.get()
    Totalmins = totalmins.get()
    print(Name, Totalmins, Warning)
    with open("User Name", "w") as d:
        d.write(Name)
    with open("Total minutes", "w") as f:
        f.write(str(Totalmins))


app = Tk()
app.geometry("500x500")
app.title("Eye Care - Protects your vision")
heading = Label(text="Eye Care - Protects your vision",
                fg="black", bg="lightskyblue2", width="500", height="3", font="10")
heading.pack()


bg = ImageTk.PhotoImage(file="image.jpeg")

# Create a Canvas
canvas = Canvas(app, width=700, height=3500)
canvas.pack(fill=BOTH, expand=True)

# Add Image inside the Canvas
canvas.create_image(0, 0, image=bg, anchor='nw')

# Function to resize the window


def resize_image(e):
    global image, resized, image2
    # open image to resize it
    image = Image.open("image.jpeg")
    # resize the image with width and height of root
    resized = image.resize((e.width, e.height), Image.ANTIALIAS)

    image2 = ImageTk.PhotoImage(resized)
    canvas.create_image(0, 0, image=image2, anchor='nw')


# Bind the function to configure the parent window
app.bind("<Configure>", resize_image)

name = Label(text="Enter your name :")
totalmins = Label(text="Enter the numbers of minutes to check :")


name.place(x=565, y=80)
totalmins.place(x=565, y=140)

name = StringVar()
totalmins = StringVar()

first_name_entry = Entry(textvariable=name, width="30")
last_name_entry = Entry(textvariable=totalmins, width="30")


first_name_entry.place(x=565, y=110)
last_name_entry.place(x=565, y=180)
button = Button(app, text="Save Data", command=save_info,
                width="30", height="2", bg="DodgerBlue2")
button.place(x=565, y=220)
mainloop()

# It captures the video frames from the webcam
cap = cv2.VideoCapture(0)

detector = FaceMeshDetector(maxFaces=1)
# It is a built in feature for open cv module that detects the facial structure
# And assigns points on the face

plotY = LivePlot(640, 360, [20.6, 31.6], invert=True)
# It belongs to the matplotlib module that shows the live ploting of the ratio of the horizontal distance and vertical distance

idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
# These are the selected points from the mesh which indicates the assigned points around the eye lids

ratioList = []
blinkCounter = 0
counter = 0
color = (255, 0, 255)
start = time.time()
# It will start counting the time when the program executes


with open("Total minutes", "r") as f:
    t = int(f.read())

with open("User Name", "r") as username:
    name = username.read()

t = t*60+5
print(t)


def refresh():
    global blinkCounter
    print("Refreshing: ", blinkCounter)

# It is the threshold time limit after which the warning pops up
    if(blinkCounter <= 8):
        # account_sid = < copy the code from the twilio account >
        # auth_token = < copy the code from the twilio account >
        # client = Client(account_sid, auth_token)
        # client.messages.create(from_=<Enter the given number>,
                               # body=f"Warning Message!! \n{name}\nYour eyes are getting strained !!\n Please move away from the screen and give some rest to your eyes.",
                               # to="+91 **********")
        # Enter your registered phone number above
        messagebox.showwarning("ALERT", "Please give some rest to your eyes")
        
    blinkCounter = 0


def eye_border(img, leftUp, leftDown, leftLeft, leftRight):
    cv2.line(img, leftUp, leftDown, (0, 200, 0), 3)
    cv2.line(img, leftLeft, leftRight, (0, 200, 0), 3)


# It is the scheduler which automatically refreshes the blink Counter after 30 seconds
schedule.every(30).seconds.do(refresh)

# Here the real counting of the time starts lets say t = 15 minutes, then the program will stop runnning after 15 minutes

while time.time() < start+t:
    # This function will run the scheduled task at the schedule time. Here the scheduled task is counting the blinks
    schedule.run_pending()

    # The below lines will place the cursor at the starting position of the frames.
    # In a video there are a series of frames
    # Example: In a 1 minute video takes in 30 fps then total number of frames are: 30 x 60 = 1800 frames
    # CAP_PROP_FRAME_COUNT gives the number of frames i.e. 1800 for the above example:
    # CAP_PROP_POS_FRAMES gives the current frame:
    # set(cv2.CAP_PROP_POS_FRAMES, 0) places the cursor to the starting of the video or the first frame

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # It reads the video
    success, img = cap.read()

    # We are resizing it to the desired dimensions
    img = cv2.resize(img, (1280, 720))

    # image contains the frame and faces contain the detected face mesh
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        # The below lines draw a lines around the left eye
        face = faces[0]
        for id in idList:
            cv2.circle(img, face[id], 5, color, cv2.FILLED)
        # Assigning 4 points on the eye, each point is assigned from each direction
        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]
        # Finding the vertical and horizontal distance of the 4 points
        lengthVer, _ = detector.findDistance(leftUp, leftDown)
        lengthHor, _ = detector.findDistance(leftLeft, leftRight)
        # creates a line for the distances
        eye_border(img, leftUp, leftDown, leftLeft, leftRight)
        # We are taking the ratio because if we move away from the camera, the distance decreases automatically and if we take ratio,
        # it normalizes the total distance and it will remain constant while not blinking and changes as the person blinks
        ratio = (lengthVer / lengthHor) * 100
        ratioList.append(ratio)

        if len(ratioList) > 3:
            ratioList.pop(0)
        ratioAvg = sum(ratioList)/len(ratioList)
        # Taking the average of the ratios to create a threshold i.e. if the Average ratio goes
        # below the assigned threshold which we took as 25 then a blink is counted

        if ratioAvg < 25.5 and counter == 0:
            blinkCounter += 1
            color = (0, 200, 0)
            counter = 1

        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0
                color = (255, 0, 255)
        # It puts text on the open CV window showing the blink counter
        cvzone.putTextRect(
            img, f"Number of Blinks : {blinkCounter}", (50, 100), colorR=color)
        # It plots the live ploting on the side of the video
        imgPlot = plotY.update(round(ratioAvg, 1), color)
        # It again resizes the image to decrease the video size of the output or else it will lag the program
        img = cv2.resize(img, (640, 360))
        # stackImages() helps to stack 2 or more images in a single window
        imgStack = cvzone.stackImages([img, imgPlot], 2, 1)

    cv2.imshow("Image", imgStack)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # If we want to stop the program in between then we should press q to terminate
