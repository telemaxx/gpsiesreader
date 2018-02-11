# gpsies3.py

### The GPSies Reader Tool
with this tool you can easily download GPS Tracks from GPSies.com  
I made it for Mobile Phones to have a small network footprint  
The first version was running on **Python for Symbian**  
Later i ported it to **QPython on Android**  
For test purposes it can also run on Linux, Windows etc  
On Android, you can select the track you wish to download and enter a username  
On PC, all tracks are downloaded, the username must be set inside the python file  
Only Track which are set to public are reachable  
This Tool require Python2 , Python3, pypy or QPython(Android)  
### HOWTO INSTALL
  * 1st install python 2.7 or python 3 or pypy or 'qpython on android'
  * download gpsies3.py and save it some where
  * create a shortcut on the Desktop. Target:
  `C:\yourepythonprogrammfolder\python.exe C:\thefolderwhereyousavethefile\gpsies3.py`
  * request an API Key from gpsies.com and save it to the correct folder. Description Somewhere below.
  * Edit `C:\yourepythonprogrammfolder\python.exe C:\thefolderwhereyousavethefile\gpsies3.py`
  and set `GPSIES_USER=` to youre GPSies username

### HOWTO USE
##### On PC, just doubleclick the Shortcut
The Files are stored at the location defined in gpsies3.py
```python
# Defining Android PATH:
ANDROID_PATH = os.path.abspath(os.path.join(os.sep,'sdcard','oruxmaps','tracklogs','gpsies'))
# Defining Windows/Linux/Mac Path:
HOME = os.path.expanduser('~')
PCPATH = os.path.join(HOME,'public','gps','gpsies')
```

### HOWTO install the API Key
* at http://www.gpsies.com you can request an API Key:
* create a empty text File with name: `apikey.txt` and copy the 16 Digit Key to.
* copy this File to the PATH defined above, or start the script inside a console an the script tell you where to save the api key file.


