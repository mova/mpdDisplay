#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import sys, os
import time
from rpi_epd2in7.epd import EPD

epd = EPD()
epd.init()
height, width = epd.width, epd.height


def newFrame():
    return Image.new("1", (width, height), 255)


def drawFrame(frame, full_refresh):
    if full_refresh:
        epd.display_frame(frame.transpose(Image.ROTATE_90))
    else:
        epd.smart_update(frame.transpose(Image.ROTATE_90))
    # ### for debugging
    # from matplotlib.pyplot import imshow
    # import numpy as np
    # imshow(np.asarray(frame))


def lineHeight(number):
    return 5 + number * width / 6.0


def printToDisplay(state, kwdict, full_refresh):
    HBlackImage = newFrame()
    draw = ImageDraw.Draw(
        HBlackImage
    )  # Create draw object and pass in the image layer we want to work with (HBlackImage)
    font = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf", 20)
    symfont = ImageFont.truetype(os.path.expanduser("~/.fonts/fa-solid-900.ttf"), 20)
    print("Updating display")
    if state == 0:
        for i, sym in enumerate([u"\uf0ca", u"\uf028", u"\uf04b", u"\uf04e"]):
            draw.text((5, lineHeight(i)), sym, font=symfont, fill=0)
        draw.text((37, lineHeight(0)), kwdict["pl"], font=font, fill=0)
        draw.text(
            (37, lineHeight(1)),
            "=" * int(kwdict["volume"] / 100 * 20) + " " + str(kwdict["volume"]),
            font=font,
            fill=0,
        )
        draw.text((37, lineHeight(2)), kwdict["artist"], font=font, fill=0)
        draw.text((37, lineHeight(3)), kwdict["title"], font=font, fill=0)
    if state == 1:
        idx = kwdict["index"]
        plL = kwdict["playlists"]
        for i, sym in enumerate([u"\uf0ca", u"\uf077", u"\uf078", u"\uf078"]):
            draw.text((5, lineHeight(i)), sym, font=symfont, fill=0)
        for row, offset in enumerate([0, -1, 1, 2]):
            draw.text(
                (37, lineHeight(row)),
                str(idx + offset) + ": " + plL[(idx + offset) % len(plL)],
                font=font,
                fill=0,
            )
    if state == 2:
        for i, sym in enumerate([u"\uf0ca", u"\uf028", u"\uf027", u"\uf1f8"]):
            draw.text((5, lineHeight(i)), sym, font=symfont, fill=0)
        draw.text(
            (37, lineHeight(1.5)),
            "=" * int(kwdict["volume"] / 100 * 20) + " " + str(kwdict["volume"]),
            font=font,
            fill=0,
        )
        draw.text((37, lineHeight(3)), "Delete", font=font, fill=0)
    drawFrame(HBlackImage, full_refresh)


# %%


class player:
    def __init__(self):
        from mpd import MPDClient

        self.client = MPDClient()
        self.client.timeout = None
        self.client.idletimeout = None
        self.client.connect("localhost", 6600)
        self.client.update()

        # 0 Display Song
        # 1 Select Playlist
        # 2 Volume
        self.state = 0
        self.lastinfo = (self.state, {})

        self.playlists = [x["playlist"] for x in self.client.listplaylists()]

        self.playPL(self.playlists[0])

    def __del__(self):
        self.client.close()
        self.client.disconnect()
        del self.client

    def playPL(self, PLname):
        self.client.clear()
        self.curplidx = self.playlists.index(PLname)
        self.client.clear()
        self.client.load(PLname)
        self.client.shuffle()
        self.client.play(0)

    def nextPlayList(self):
        self.playPL(self.playlists[self.curplidx + 1 % len(self.playlists)])

    def nextSong(self):
        self.client.next()

    def playpause(self):
        self.client.pause()

    def updateDisplay(self):
        if self.state == 0:
            songinfo = self.client.currentsong()
            curinfo = (
                self.state,
                {
                    "pl": self.playlists[self.curplidx],
                    "artist": songinfo.get(
                        "artist", songinfo.get("albumartist", "Unknown")
                    ),
                    "title": songinfo["title"],
                    "volume": int(self.client.status()["volume"]),
                },
            )
        if self.state == 1:
            curinfo = (
                self.state,
                {"playlists": self.playlists, "index": self.curplidx},
            )
        if self.state == 2:
            curinfo = (
                self.state,
                {"volume": int(self.client.status()["volume"])},
            )

        if self.lastinfo != curinfo:
            if self.lastinfo[0] == curinfo[0]:
                printToDisplay(*curinfo, False)
            else:
                printToDisplay(*curinfo, True)
            self.lastinfo = curinfo
            print(curinfo)

    def incVol(self):
        status = self.client.status()
        curvol = int(status["volume"])
        print("Current vol {}", format(curvol))
        self.client.setvol(curvol + 5)

    def decVol(self):
        status = self.client.status()
        curvol = int(status["volume"])
        print("Current vol {}", format(curvol))
        self.client.setvol(curvol - 5)


class playerState(object):
    def __init__(self, player):
        self.p = player
        from gpiozero import Button

        self.b1 = Button(5)
        self.b2 = Button(6)
        self.b3 = Button(13)
        self.b4 = Button(19)

        self.b1.when_pressed = self.b1action
        self.b2.when_pressed = self.b2action
        self.b3.when_pressed = self.b3action
        self.b4.when_pressed = self.b4action

    def b1action(self):
        self.p.state = (self.p.state + 1) % 3
        print("button1Action" + " State: " + str(self.p.state))

    def b2action(self):
        print("button2Action" + " State: " + str(self.p.state))
        if self.p.state == 0:
            pass
        if self.p.state == 1:
            self.p.playPL(
                self.p.playlists[(self.p.curplidx - 1) % len(self.p.playlists)]
            )
        if self.p.state == 2:
            self.p.incVol()

    def b3action(self):
        print("button3Action" + " State: " + str(self.p.state))
        if self.p.state == 0:
            self.p.playpause()
        if self.p.state == 1:
            self.p.playPL(
                self.p.playlists[(self.p.curplidx + 1) % len(self.p.playlists)]
            )
        if self.p.state == 2:
            self.p.decVol()

    def b4action(self):
        print("button4Action" + " State: " + str(self.p.state))
        if self.p.state == 0:
            self.p.nextSong()
        if self.p.state == 1:
            self.p.playPL(
                self.p.playlists[(self.p.curplidx + 2) % len(self.p.playlists)]
            )
        if self.p.state == 2:
            songinfo = self.p.client.currentsong()
            self.p.client.deleteid(songinfo["id"])
            print("Removing /home/pi/Music/" + songinfo["file"])
            os.remove("/home/pi/Music/" + songinfo["file"])
            self.p.nextSong()


# %%
p = player()
state = playerState(p)

# %%
while True:
    time.sleep(1)
    p.updateDisplay()
