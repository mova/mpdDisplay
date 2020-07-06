#!/usr/bin/env python
# coding: utf-8

# In[97]:


import os
from mpd import MPDClient
from mpd import CommandError
client = MPDClient()               # create client object
client.timeout = None                # network timeout in seconds (floats allowed), default: None
client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
client.connect("localhost", 6600)  # connect to localhost:6600
existingpl=client.listplaylists()


# In[98]:


musicdir=os.path.expanduser('~/Music')
musicex=(".ogg",".mp3")
plDict={}
for pa, folders, files in os.walk(musicdir):
    if pa.startswith(".") or files==[]:
        continue
    if not  any([x.lower().endswith(musicex) for x in files]):
        continue
    plname= pa.split("/")[4]
    pathprefix="/".join(pa.split("/")[4:])+"/"
    if plname not in plDict:
        plDict[plname]=[]
    plDict[plname]=plDict[plname]+[pathprefix+x for x in files if x.lower().endswith(musicex)]


# In[99]:


for plname in plDict:
    if plname in existingpl:
        print("Clearing {}".format(plname))
        client.playlistclear(plname)
    for fpath in plDict[plname]:
        #print("Adding {} <- {}".format(plname,fpath))
        if not os.path.isfile(musicdir + "/" + fpath):
            raise Exception('Bad Filename Path')
        try:
            client.playlistadd(plname,fpath)
        except CommandError:
            print("Error Adding {} <- {}".format(plname,fpath))


# In[ ]:


client.close()                     # send the close command
client.disconnect()                # disconnect from the server

