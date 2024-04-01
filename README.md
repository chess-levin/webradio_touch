# VLC based webradio with lcd touch display


![picture of my webradio](/docs/touch_lcd_radio.jpg "picture of my webradio")

## Parts

* Rasberry 4B running Bookworm 64-bit
* [Waveshare 7.9" Touch LCD](https://www.waveshare.com/7.9inch-hdmi-lcd.htm)
* [WAVESHARE 7.9" DSI LCD & RPI 4B ENCLOSURE](https://cults3d.com/en/3d-model/gadget/waveshare-7-9-dsi-lcd-rpi-4b-enclosure)
* Bluetooth Speaker

## Config

Run `py3 main_oop.py kiosk` to start in fullscreen kiosk mode.


## VLC

In case there are errors like these on startup

``` 
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_concat_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_imem_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_mms_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_realrtsp_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_srt_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_wasapi_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libattachment_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libcdda_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libdcp_plugin.dll
[000002635638b9b0] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libdshow_plugin.dll
```

execute as admin

```
c:\programme\videolan\vlc\vlc-cache-gen.exe c:\programme\videolan\vlc\plugins\
```


## Resources

### Python

* [pip requirements](https://learnpython.com/blog/python-requirements-file/)

### Waveshare Touch LCD 
* https://www.youtube.com/watch?v=mVA42vosU3w

### TKinter
* https://www.youtube.com/watch?v=WE1IuPOICxE
* [Scrollable Frames](https://www.youtube.com/watch?v=Envp9yHb2Ho)
* https://www.youtube.com/watch?v=A48414Lz7NM 
* [Switch Frames](https://www.geeksforgeeks.org/tkinter-application-to-switch-between-different-page-frames/)
* [MVC with Tkinter](https://nazmul-ahsan.medium.com/how-to-organize-multi-frame-tkinter-application-with-mvc-pattern-79247efbb02b)
* [Professional GUI with TKinter inkl. Switch frames](https://medium.com/@mohit444123/sleek-and-professional-gui-with-tkinter-a-step-by-step-guide-4e9f82486380)

### Rasberry Pi
* [Shortcuts](https://raspberrytips.com/desktop-shortcuts-on-raspberry-pi/)
* [Create Icon](https://www.youtube.com/watch?v=aWg_9VZjf1c)
* [Add Icon to Launcher](https://forums.raspberrypi.com/viewtopic.php?t=358648)
* [Bookworm vs. Bullseye](https://github.com/thagrol/Guides/blob/main/bookworm.pdf)
* [Assign Icon](https://www.youtube.com/watch?v=Y9_3DlFqc1Q)


### VLC

* [Play Podcast in VLC](https://www.youtube.com/watch?v=5ztCJvfl9Aw)
