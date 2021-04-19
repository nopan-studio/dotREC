import tkinter as tk
import cv2
from PIL import ImageTk, Image
import threading as tr
import os
import imutils
import time
import numpy as np
from pathlib import Path
import threading
#
#   i'm stupid, please don't trash on my coding skills
#   if you see something stupid here, please tell me.ty   
#
# MAIN OPTIONS
method = cv2.TM_CCOEFF_NORMED
PATH = os.getcwd()
fps =5
prev = 0
current = "Nil" # saves the current active trigger
timer = 5
timer_time = 0
# root window
root = tk.Tk()
root.title("dotREC")
root.geometry("402x400")
# opencv frame
lmain = tk.Label(root)
lmain.grid(row=0,column=0)

# opencv -> get camera
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)    

# load triggers/images
entry_1_img = cv2.imread("triggers/entry_1.png",0)#cv2.IMREAD_COLOR)
entry_2_img = cv2.imread("triggers/entry_2.png",0)#cv2.IMREAD_COLOR)

# load trigger/commands
try:
    _ftest = open(PATH+"config.cfg","x").close()
except:
    print("command config is already existing..")

# open config.cfg 
_open = open(PATH+"/config.cfg","r")
_line = _open.readlines()
#get threshold
threshold = _line[0]
#get first command
try:
    entry_1_command = _line[1]
except:
    entry_1_command = ""

#get second command
try:
    entry_2_command = _line[2]
except:
    entry_2_command = ""

# 1st entry thread -> called by template matching
def thread_1(loc1):
    global current
    global timer_time
    for pt in zip(*loc1[::-1]):
            if pt != None and current != "1":
                print("ENTRY 1")
                os.system(entry_1_command)
                current = "1"
                timer_time = 0
            break

# 2nd entry thread -> called by template matching
def thread_2(loc2):
    global current
    global timer_time
    for pt in zip(*loc2[::-1]):
            if pt != None and current != "2":
                print("ENTRY 2")
                os.system(entry_2_command)
                current = "2"
                timer_time = 0
            break

# TEMPLATE MATCHING CORE
def TemplateMatching(frame):
    global current
    global timer_time
    global timer
    global threshold
    temp = threshold.split("\n")
    _threshold = float(temp[0])
    
    min_test1 = cv2.matchTemplate(frame,entry_1_img,method)
    min_test2 = cv2.matchTemplate(frame,entry_2_img,method)
    loc1 = np.where(min_test1 >= _threshold)
    loc2 = np.where(min_test2 >= _threshold)
    tr_1 = threading.Thread(target=thread_1,args=(loc1,))
    tr_2 = threading.Thread(target=thread_2,args=(loc2,))
    tr_1.start()
    tr_2.start()

# SHOW CAMERA VIEW
def menu_camera_view(): # forgot the website i read this from. but opencv to tkinter is what i searched.
    _,frame = cap.read()
    frame_g = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    global prev
    global time
    time_elapsed = time.time() - prev
    if time_elapsed > 1./fps:
        TemplateMatching(frame_g)
        prev = time.time()

    # draw to window
    frame = imutils.resize(frame,width=400,)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(1,menu_camera_view)

# CAPTURE TRIGGER
def menu_camera_capture(entry):
    # read frames
    _,frame = cap.read()

    # capture frame -> save to param:string(entry)
    cv2.imwrite("triggers/"+entry+".png",frame)
    os.system("notify-send \""+entry+" captured\"")

# MAIN MENU
def menu_main():
    # opencv
    menu_camera_view()

    # window frame
    frame = tk.Frame(root)
    frame.grid()

    # config button
    btn_config = tk.Button(frame, text = "CONFIG", command = menu_config)
    btn_config.grid(row=0,column=0)

    btn_exit = tk.Button(frame, text = "EXIT", command = exit)
    btn_exit.grid(row=0,column=2)

# RELOAD
def menu_reload(e1,e2,threshold):
    # save commands
    _open = open(PATH+"/config.cfg","w")
    _open.write(
        threshold+"\n"+
        e1+"&"+"\n"+
        e2+"&"+"\n"
    )
    _open.close()

    while 1:
        # release camera
        cap.release()
        # start new core instance
        os.system("START /B python core.py")
        exit()
        #os.system("notify-send \"SAVING CHANGES & RELOADING\"")
        # kill current instance
        
# CONFIG MENU
def menu_config():
    # config window
    config_window = tk.Tk()
    config_window.title("dotREC:config")
    config_frame = tk.Frame(config_window)
    config_frame.grid()

    # threshold entry
    entry_thresh_l = tk.Label(config_frame,text="THRESHOLD (0.1 -> 1.0)")
    entry_thresh_l.grid(row=0,column=1)
    entry_thresh = tk.Entry(config_frame,width = 10)
    entry_thresh.insert(0,threshold)
    entry_thresh.delete(len(threshold)-1,tk.END)
    entry_thresh.grid(row=1,column=1)

    # entry title
    entry_title = tk.Label(config_frame,text = "COMMANDS")
    entry_title.grid(row=2,column=1)
    
    # entry boxes
    # 1
    entry_label_1 = tk.Label(config_frame,text="#1")
    entry_label_1.grid(row=3,column=0)
    entry_box_1 = tk.Entry(config_frame,width = 20)
    entry_box_1.insert(0,entry_1_command)
    entry_box_1.delete(len(entry_1_command)-2,tk.END)
    entry_box_1.grid(row=3,column=1)
    entry_btn_1 = tk.Button(config_frame, text ="SET TRIGGER", command = lambda temp=".":menu_camera_capture("entry_1"))
    entry_btn_1.grid(row=3,column=2)
    # 2
    entry_label_2 = tk.Label(config_frame,text="#2")
    entry_label_2.grid(row=4,column=0)
    entry_box_2 = tk.Entry(config_frame,width = 20)
    entry_box_2.insert(0,entry_2_command)
    entry_box_2.delete(len(entry_2_command)-2,tk.END)
    entry_box_2.grid(row=4,column=1)
    entry_btn_2 = tk.Button(config_frame, text ="SET TRIGGER", command = lambda temp=".":menu_camera_capture("entry_2"))
    entry_btn_2.grid(row=4,column=2)
   
    # save button
    btn_save = tk.Button(config_frame,text = "SAVE CHANGES",command = lambda temp=".":menu_reload(
        entry_box_1.get(),
        entry_box_2.get(),
        entry_thresh.get()
    ))
    btn_save.grid(row=6,column=1)
    config_window.mainloop()

# AH
if(__name__ == "__main__"):
    # initialize
    menu_main()
    
    # tk loop 
    root.mainloop()