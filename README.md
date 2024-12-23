# VLC based webradio with lcd touch display


![picture of webradio touch](/docs/assets/touch_lcd_radio.jpg "picture of my webradio")

A few months ago I started the [first webradio project](https://github.com/chess-levin/esp32webradio) based on an ESP32 (Arduino API). I changed the project platform to a Rasberry Pi for several reasons:
* The wifi streaming performance of the ESP32 (Arduino platform) is not as good as expected 
* It is not possible to use Wifi and Bluetooth in parallel. 
* It was not possible to find a way to automatically (re)connect an already paired Bluetoothspeaker

All this issues working like a charm with the raspi.

My motivation to choose this platform was to dive deeper into Python and GUI-development for touch displays. 

There is a [Python wrapper for VLC](https://pypi.org/project/python-vlc/), which does all the streaming work in this project.

I found [CustomTKinter](https://customtkinter.tomschimansky.com/) by Tom Schimansky and gave it try. It's a good looking and easy to use addition to [Tkinter](https://docs.python.org/3/library/tkinter.html).


## Parts

* Rasberry 4B running Bookworm 64-bit
* [Waveshare 7.9" Touch LCD](https://www.waveshare.com/7.9inch-hdmi-lcd.htm)
* [WAVESHARE 7.9" DSI LCD & RPI 4B ENCLOSURE](https://cults3d.com/en/3d-model/gadget/waveshare-7-9-dsi-lcd-rpi-4b-enclosure)
* Bluetooth Speaker


## Config

Run `py3 main_oop.py kiosk` to start in fullscreen kiosk mode.

## Python

Show installed packages: `pip list`


## VLC

In case there are errors like these on startup of the python app

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

execute the following command on an admin shell:

```
c:\programme\videolan\vlc\vlc-cache-gen.exe c:\programme\videolan\vlc\plugins\
```


## Resources

### Python

* [pip requirements](https://learnpython.com/blog/python-requirements-file/)
* [Call function every x seconds](https://pythonassets.com/posts/executing-code-every-certain-time/)

### Waveshare Touch LCD 
* https://www.youtube.com/watch?v=mVA42vosU3w

### TKinter
* https://www.youtube.com/watch?v=WE1IuPOICxE
* [Scrollable Frames](https://www.youtube.com/watch?v=Envp9yHb2Ho)
* https://www.youtube.com/watch?v=A48414Lz7NM 
* [Switch Frames](https://www.geeksforgeeks.org/tkinter-application-to-switch-between-different-page-frames/)
* [MVC with Tkinter](https://nazmul-ahsan.medium.com/how-to-organize-multi-frame-tkinter-application-with-mvc-pattern-79247efbb02b)
* [Professional GUI with TKinter inkl. Switch frames](https://medium.com/@mohit444123/sleek-and-professional-gui-with-tkinter-a-step-by-step-guide-4e9f82486380)
* [Using images in tkinter](https://www.youtube.com/watch?v=VnwDPa9biwc)

### Rasberry Pi
* [Shortcuts](https://raspberrytips.com/desktop-shortcuts-on-raspberry-pi/)
* [Create Icon](https://www.youtube.com/watch?v=aWg_9VZjf1c)
* [Add Icon to Launcher](https://forums.raspberrypi.com/viewtopic.php?t=358648)
* [Bookworm vs. Bullseye](https://github.com/thagrol/Guides/blob/main/bookworm.pdf)
* [Assign Icon](https://www.youtube.com/watch?v=Y9_3DlFqc1Q)
* [GPIO](https://hackaday.com/2022/02/01/did-you-know-that-the-raspberry-pi-4-has-more-spi-i2c-uart-ports/#:~:text=We've%20gotten%20used%20to,on%20its%2040%2Dpin%20header.)
* [Raspberry Pi Power Switch Button - Safe Shutdown / Start Up](https://www.youtube.com/watch?v=WrPbVWwCOqc)
* [1/0 Switch](https://blog.gc2.at/post/pi-herunterfahren/)


### VLC

* [VLC Module](https://www.geeksforgeeks.org/vlc-module-in-python-an-introduction/)
* [Play Podcast in VLC](https://www.youtube.com/watch?v=5ztCJvfl9Aw)


## Assembly

![enclosure assembly](/docs/assets/enclosure_assembly_1.jpg  "enclosure assembly")
![enclosure assembly](/docs/assets/enclosure_assembly_2.jpg  "enclosure assembly")
![enclosure assembly](/docs/assets/enclosure_assembly_3.jpg  "enclosure assembly")
![enclosure assembly](/docs/assets/enclosure_assembly_4.jpg  "enclosure assembly")
![enclosure assembly](/docs/assets/enclosure_assembly_5.jpg  "enclosure assembly")
