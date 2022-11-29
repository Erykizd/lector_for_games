import time
import pyscreenshot
import pytesseract
import os
import pyttsx3
import keyboard
import PySimpleGUI as sg
import threading
import json
import multiprocessing

def takeScreenshot(bbox, fileName):
    im = pyscreenshot.grab(bbox)
    im.save(fileName)

def OCR(fileName, lang):
    text = pytesseract.image_to_string(fileName, lang=lang)
    text = ''.join(ch for ch in text if isOk(ch))
    return text

def isOk(ch):
    goodChars = ['ą','ć','ę','ł','ń','ó','ś','ź','ż',' ']
    if ch.isalnum():
        return True
    for goodChar in goodChars:
        if goodChar == ch:
            return True
    return False

def TTS(text, voiceId, speed):
    tts = pyttsx3.init()
    voices = tts.getProperty('voices')
    tts.setProperty('voice', voices[voiceId].id)
    tts.setProperty('rate', speed)
    tts.say(text)
    tts.runAndWait()

def deleteFiles(fileNames):
    for fileName in fileNames:
        os.remove(fileName)

def mainLogic():
    global pause, stop, bbox, timeout, speed
    pause = True
    stop = False
    quitButton = '.'
    pauseButton = ','
    playButton = "/"
    textOld = ""

    time.sleep(2)
    while stop == False:
        if keyboard.is_pressed(playButton):
            pause = False
            thread2 = Process(target=TTS, args=["Włączono lektora", voiceId, speed])
            thread2.start()

        if pause == False:
            takeScreenshot(bbox, fileName)
            text = OCR(fileName, lang)
            if text != textOld:
                print(text)
                thread3 = threading.Thread(target=TTS, args=[text, voiceId, speed])
                thread3.start()
            startTime = time.time()
            while True:
                if keyboard.is_pressed(quitButton):
                    stop = True
                    thread2 = threading.Thread(target=TTS, args=["Wyłączono lektora", voiceId, speed])
                    thread2.start()
                    deleteFiles(fileNames)
                    break
                elif keyboard.is_pressed(pauseButton):
                    pause = True
                    thread2 = threading.Thread(target=TTS, args=["Zatrzymano lektora", voiceId, speed])
                    thread2.start()
                    break
                elif time.time() - startTime > timeout:
                    break
            textOld = text


def createGUI():
    global x1, x2, y1, y2, bbox, stop, pause, voiceId, speed, fileName, fileNames
    stop = False
    pause = True

    label1 = [sg.Text("OCR lector", background_color='gray', text_color="black")]
    btn1 = [sg.Button("Play")]
    btn2 = [sg.Button("Pause")]
    btn3 = [sg.Button("Refresh")]
    label2 = [sg.Text("This lector for games reads subtitles\n from part of screenshot.", background_color='gray', text_color="black")]
    label3 = [sg.Text("Manual: \n pause = , \n play = / ", background_color='gray', text_color="black")]
    x1Input = [sg.Text('x1', size =(10, 1)), sg.InputText(default_text=x1)]
    x2Input = [sg.Text('x2', size =(10, 1)), sg.InputText(default_text=x2)]
    y1Input = [sg.Text('y1', size =(10, 1)), sg.InputText(default_text=y1)]
    y2Input = [sg.Text('y2', size =(10, 1)), sg.InputText(default_text=y2)]
    exampleInput = [sg.Text('To release input fields -> ', size =(20, 1)), sg.InputText(size =(10, 1))]

    picture = [sg.Image(source="screenshot.png", key="-IMAGE-")]

    layout = [label1, label2, label3, x1Input, x2Input, y1Input, y2Input, exampleInput, btn1, btn2, btn3, picture]
    window = sg.Window("Lector for games", layout, size=(round(w/1.25), round(h/1.25)), location=(round(x/1.25), round(y/1.25)), alpha_channel=0.8, background_color='green')

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            thread2 = threading.Thread(target=TTS, args=["Zamknięto okno", voiceId, speed])
            thread2.start()
            time.sleep(1)
            stop = True
            break
        if event == "Play":
            thread2 = threading.Thread(target=TTS, args=["Włączono lektora", voiceId, speed])
            thread2.start()
            time.sleep(1)
            stop = False
            pause = False
        if event == "Pause":
            thread2 = threading.Thread(target=TTS, args=["Zatrzymano lektora", voiceId, speed])
            thread2.start()
            time.sleep(1)
            pause = True
        if event == "Stop":
            stop = True
        if event == "Refresh":
            thread2 = threading.Thread(target=TTS, args=["Odświerzono podgląd wycinka", voiceId, speed])
            thread2.start()
            window["-IMAGE-"].update("screenshot.png")
        if(values[0].isnumeric()):
            x1 = int(float(values[0]))
        if(values[1].isnumeric()):
            x2 = int(float(values[1]))
        if(values[2].isnumeric()):
            y1 = int(float(values[2]))
        if(values[3].isnumeric()):
            y2 = int(float(values[3]))
        bbox = (x1, y1, x2, y2)
    window.close()

def readConfigFile():
    global x1, x2, y1, y2, bbox, voiceId, speed, lang, timeout, fileName, fileNames

    configPath = 'config.json'
    try:
        if (os.path.isfile(configPath)):
            configFile = open(configPath)
            data = json.load(configFile)
            configFile.close()
            if (data['x1'] >= 0):
                x1 = int(data['x1'])
            if (data['x2'] > x1):
                x2 = int(data['x2'])
            if (data['y1'] >= 0):
                y1 = int(data['y1'])
            if (data['y2'] > y1):
                y2 = int(data['y2'])
            bbox = (x1, y1, x2, y2)
            if (data['voiceId'] >= 0):
                voiceId = data['voiceId']
            if (data['speed'] > 0):
                speed = data['speed']
            if (data['lang'] != ""):
                lang = data['lang']
            if (data['timeout'] > 0):
                timeout = float(data['timeout'])
            if (data['filename'] != ""):
                fileName = data['filename']
                fileNames = [fileName]
    except:
        print("config.json file is incorrectly")

pytesseract.pytesseract.tesseract_cmd = r'D:\programy\Tesseract-OCR\tesseract.exe'

global x1, x2, y1, y2, bbox, voiceId, speed, lang, timeout, fileName, fileNames

fileName = "screenshot.png"
fileNames = [fileName]
x1 = 400
y1 = 970
x2 = 1520
y2 = 998
bbox = (x1,y1,x2,y2) #(x1,y1,x2,y2)
voiceId = 0
lang = "pol"
speed = 100
timeout = 0.01
textOld = ""

x = 300
y = 200
w = 1500
h = 600

multiprocessing.freeze_support()
readConfigFile()

thread = threading.Thread(target=mainLogic)
thread.start()

createGUI()
