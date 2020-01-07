#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%


from PIL import Image,ImageDraw,ImageFont
#from matplotlib.pyplot import imshow
import sys, os
#import numpy as np
import time

#from songDisplay.waveshare_epd import epd2in7b
#epd = epd2in7b.EPD()  # get the display
# epd.init()  # initialize the display
# epd.Clear()
# height = epd2in7b.EPD_HEIGHT
# width = epd2in7b.EPD_WIDTH

from rpi_epd2in7.epd import EPD
epd = EPD()
epd.init()
height, width = epd.width, epd.height
def newFrame():
    return Image.new('1', (width,height), 255)

def drawFrame(frame):
    #HRedImage = newFrame()
    ## epd.display(epd.getbuffer(frame), epd.getbuffer(HRedImage))
    # epd.displayMono(epd.getbuffer(frame))

    epd.smart_update(frame.transpose(Image.ROTATE_90))

    ### plot with matplotlib
    #imshow(np.asarray(frame))


def lineHeight(number):
    return (5 + number * width / 6.0)


def printToDisplay(playlistName, artistName, titleName):
    HBlackImage = newFrame()
    draw = ImageDraw.Draw(
        HBlackImage
    )  # Create draw object and pass in the image layer we want to work with (HBlackImage)
    font = ImageFont.truetype(
        '/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf', 20)
    symfont = ImageFont.truetype(
        os.path.expanduser('~/.fonts/fa-solid-900.ttf'), 20)

    for i, sym in enumerate([u"\uf0ca", u"\uf028", u"\uf04b", u"\uf04e"]):
        draw.text((5, lineHeight(i)), sym, font=symfont, fill=0)
    draw.text((37, lineHeight(0)), playlistName, font=font, fill=0)
    draw.text((37, lineHeight(1)), "========", font=font, fill=0)
    draw.text((37, lineHeight(2)), artistName, font=font, fill=0)
    draw.text((37, lineHeight(3)), titleName, font=font, fill=0)
    drawFrame(HBlackImage)


def updateDisplay():
    self.client.connect("localhost", 6600)
    songinfo = self.client.currentsong()
    self.client.close()
    self.client.disconnect()
    if (curplaylist, songinfo["artist"], songinfo["title"]) != (
            self.lastinfo["pl"], self.lastinfo["artist"], self.lastinfo["title"]):
        printToDisplay(curplaylist, songinfo["artist"], songinfo["title"])
        (self.lastinfo["pl"], self.lastinfo["artist"],
         self.lastinfo["title"]) = (curplaylist, songinfo["artist"],
                               songinfo["title"])

# %%

class player():
    def __init__(self):
        from mpd import MPDClient
        self.client = MPDClient()
        self.client.timeout = None
        self.client.idletimeout = None
        self.client.connect("localhost", 6600)
        self.client.update()

        self.playlists = [
            x for x in next(os.walk('/home/pi/Music/'))[1]
            if not x.startswith(".") and x != ""
        ]
        self.curplidx = 0
        self.lastinfo = {"pl": "xxx", "artist": "xxx", "title": "xxx"}
        self.nextPlayList()

    def __del__(self):
        self.client.close()
        self.client.disconnect()
        del self.client

    def nextPlayList(self):
        self.curplidx = self.curplidx + 1 % len(self.playlists)

        self.client.clear()
        self.client.add(self.playlists[self.curplidx])
        self.client.shuffle()
        self.client.play(0)

        self.updateDisplay()


    def nextSong(self):
        self.client.next()
        self.updateDisplay()


    def playpause(self):
        self.client.pause()

    def updateDisplay(self):
        songinfo = self.client.currentsong()
        if (self.playlists[self.curplidx], songinfo["artist"], songinfo["title"]) != (
                self.lastinfo["pl"], self.lastinfo["artist"], self.lastinfo["title"]):
            print(songinfo)
            printToDisplay(self.playlists[self.curplidx], songinfo["artist"], songinfo["title"])
            (self.lastinfo["pl"], self.lastinfo["artist"],
            self.lastinfo["title"]) = (self.playlists[self.curplidx], songinfo["artist"],
                                songinfo["title"])
    def incVol(self):
            status=self.client.status()
            print(status)
            curvol = int(status["volume"])
            print("Current vol {}",format(curvol))
            self.client.setvol(curvol+5)
    def decVol(self):
            status=self.client.status()
            print(status)
            curvol = int(status["volume"])
            print("Current vol {}",format(curvol))
            self.client.setvol(curvol-5)



class playerState(object):
    def __init__(self, player):
        self.p=player
        from gpiozero import Button
        self.b1 = Button(5)
        self.b2 = Button(6)
        self.b3 = Button(13)
        self.b4 = Button(19)

        self.b1.when_pressed=self.b1action
        self.b2.when_pressed=self.b2action
        self.b3.when_pressed=self.b3action
        self.b4.when_pressed=self.b4action
        self.state=True
    def b1action(self):
        print("button1Action")
        self.p.nextPlayList()
    def b2action(self):
        print("button2Action")
        self.state=not self.state
    def b3action(self):
        print("button3Action")
        if self.state:
            self.p.playpause()
        else:
            self.p.incVol()
    def b4action(self):
        print("button4Action")
        if self.state:
            self.p.nextSong()
        else:
            self.p.decVol()
# %%
p=player()
state=playerState(p)

# %%
while True:
    time.sleep(2)
    p.updateDisplay()