import time
from random import randint
import socket
import os
import smtplib
from email import encoders
from flask import Flask, render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from platform import python_version
from translate import Translator
import pygame
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from setuptools import setup


#Module info
version = '0.0.2'
long_description = '''Python module for Two It 2022 project.'''

setup(
    name='mcom',
    version=version,

    author='Two It 2022 (Vagif Babayev)',
    author_email='strangerstrog@gmail.com',

    description=(
        u'Python module for Two It project.'
    ),
    long_description=long_description,
    #long_description_content_type='text/markdown',

    packages=['mcom'],

)


def FileDialog(type):
    if type == "save_as":
        file_path = filedialog.asksaveasfile()
        return file_path
    elif type == "open":
        file_path = filedialog.askopenfile()
        return file_path


def fileRemove(file):
    os.remove(file)
    com = f"File {file} removed successfully"
    return com 


def PlayAudio(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()



def printS(text, sleepTime):
    time.sleep(sleepTime)
    print(text)

def loadText(txt, sleepTime):
    for k in txt:
        time.sleep(sleepTime) 
        print(k, end='')
    print()

def loadSs(style, Sss, timeSleep):
    if style == "square":
        for i in range(Sss):
            print("███", end="")
            time.sleep(timeSleep / 2)
    elif style == "line":
        for i in range(Sss):
            print("―", end="")
            time.sleep(timeSleep / 2)
    elif style == "circle":
        for i in range(Sss):
            print("◯", end="")
            time.sleep(timeSleep / 2)

    def LetterEdit(txt, style):
        if style == "up":
            up_letter = txt.upper()
            return up_letter
        elif style == "down":
            down_letter = txt.lower()
            return down_letter

def file_system_Read(file):
    f = open(file, "r", encoding="UTF-8")
    data = f.read()
    f.close()
    return data

def fileRead(name):
    read = file_system_Read(name)
    return read

def fileWrite(file, text):
    global f
    f = open(file, "w", encoding="UTF-8")
    data = f.write(text)
    f.close()
    return data


def fileCreate(name):
    my_file = open(name, "w+")
    sub = f"Created file {name}!"
    return sub



def fileRename(oldName, newName):
    os.rename(oldName, newName)
    syb = f"Renamed file {oldName} to {newName}!"
    return syb


def mailReg(userR, passwordR):
        
    global user
    global password
        
    user = userR
    password = passwordR


def sendToGmail(to, message):
        
        
    server = 'smtp.gmail.com'

    recipients = [to]
    sender = user
    subject = 'Python More Commands'
    text = message
    html = '<html><head></head><body><p>' + text + '</p></body></html>'


    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'Python script <' + sender + '>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender
    msg['X-Mailer'] = 'Python/' + (python_version())

    part_text = MIMEText(text, 'plain')
    part_html = MIMEText(html, 'html')

    msg.attach(part_text)
    msg.attach(part_html)

    mail = smtplib.SMTP_SSL(server)
    mail.login(user, password)
    mail.sendmail(sender, recipients, msg.as_string())
    mail.quit()


def sendToMail(to, message):
        
        
    server = 'smtp.mail.ru'

    recipients = [to]
    sender = user
    subject = 'Python More Commands'
    text = message
    html = '<html><head></head><body><p>' + text + '</p></body></html>'


    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'Python script <' + sender + '>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender
    msg['X-Mailer'] = 'Python/' + (python_version())

    part_text = MIMEText(text, 'plain')
    part_html = MIMEText(html, 'html')

    msg.attach(part_text)
    msg.attach(part_html)

    mail = smtplib.SMTP_SSL(server)
    mail.login(user, password)
    mail.sendmail(sender, recipients, msg.as_string())
    mail.quit()


def Translate(fromL, toL, text):

    translator = Translator(from_lang=fromL, to_lang=toL)
    translation = translator.translate(text)
    return translation



def System(typeS):
    if typeS == "DISPLAY" or typeS == "display":
        display = socket.gethostname()
        return display
    elif typeS == "IP-ADDRESS" or typeS == "ip-address" or typeS == "IP-address" or typeS == "IP-Address":
        ip = socket.gethostbyname(socket.gethostname())
        return ip


def MessageWindow(type, title, message):
    if type == "info":
        messagebox.showinfo(title, message)
    elif type == "warning":
        messagebox.showwarning(title, message)
    elif type == "error":
        messagebox.showerror(title, message)
    elif type == "ask":
        messagebox.askquestion(title, message)
    elif type == "ask_ok_cancel":
        messagebox.askokcancel(title, message)
    elif type == "ask_retry":
        messagebox.askretrycancel(title, message)


def timer(type, count):
    if type == "m":
        time.sleep(count * 60)

    elif type == "s":
        time.sleep(count)
    
    elif type == "h":
        time.sleep(count * 3600)


def start_server():
    global app
    app = Flask(__name__)

    if __name__ == "__main__":
        app.run()


def create_room(address, name, text):
    @app.route(address)
    def index():
        return text
    if __name__ == "__main__":
        app.run()
    print(app.run())


def connect(address, name, server_name):
    @app.route(address)
    def index():
        return render_template(server_name)
    if __name__ == "__main__":
        app.run()
    print(app.run())


