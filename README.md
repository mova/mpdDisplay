# mpdDisplay

![ExamplePicutre](Example.jpg)

Use your waveshare 2.7 E-ink to display song infos and control mpd!
`foldersToMPDPlaylists.py` sets up the folders in the music directory as mpd playlists.


### Requirements
- ![python-mpd2](https://python-mpd2.readthedocs.io/en/latest/index.html)
- ![rpi_epd2in7](https://github.com/elad661/rpi_epd2in7)
- ![pillow](https://pillow.readthedocs.io/en/latest/installation.html#basic-installation)
- ![fontawesome free font](https://fontawesome.com/download) 

### Paths:
`/home/pi/Music` as the Music directory.
`/home/pi/mpdDisplay` for this repo.

### Setup mpdDisplay as a service:
~~~
mkdir -p ~/.config/systemd/user/
ln -s mpdDisplay.service ~/.config/systemd/user/
systemctl --user enable mpdDisplay
~~~
