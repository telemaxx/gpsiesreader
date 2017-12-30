#qpy:console
#qpy:2

""" GPSIES Downloader
With this Script you can download tracks of a specified GPSIES User.
The Tracks must be set to public, private tracks are not accessible

return codes:
0 = ok
1 = no APIKEY File found
2 = APIKEY File wrong file length

History:
0.4 :runs on python2 and python3, module sl4a is now in androidhelper
0.41 : support for different formats: GPX track, TCX Track, KML Google Earth
0.43 : api key is now in an external file. MANY Code cleanup 4 going github
"""

__version__ = '0.43'
__author__ = 'telemaxx'

import time
import os.path
import sys
import re
import xml.dom.minidom

#try to detect android
ROA = True
try: #check if android and import gui tools
	import androidhelper.sl4a as sl4a
except: #otherwise its not android
	ROA = None

python3 = True
try: # for python3
	from urllib.request import urlopen, Request
except ImportError: # or python2
	from urllib2 import urlopen, Request, HTTPError
	python3 = False

GPSIES_USER='telamaxx'
BASEURL = 'http://www.gpsies.com/api.do?'
FILEFORMATS = ['gpxTrk', 'tcx', 'kml']
FILEFORMATS_EXT = ['gpx', 'tcx', 'kml']
DEBUG = 1 # Debug output [0,1]
DEFAUL_ALL_SELECTED = 0 #in tracklist default all items selected? [0,1]
PS=os.sep

# Defining Android PATH:
ANDROID_PATH = os.path.abspath(os.path.join(os.sep,'sdcard','oruxmaps','tracklogs','gpsies'))
# Defining Windows/Linux/Mac Path:
HOME = os.path.expanduser('~')
PCPATH = os.path.join(HOME,'public','gps','gpsies')

# ROA = 1
if ROA:
	PATH = ANDROID_PATH #if is Android, then set Patheseperator and the path to Oruxmaps.
	droid = sl4a.Android()
else:
	PATH = PCPATH
GPSIES_XML_FILE_PATH = os.path.join(PATH,'GPSies.xml')
APIKEY_FILE_PATH = os.path.join(PATH, 'apikey.txt')
GPSIES_TRACKS_PATH = os.path.join(PATH,'tracks')

if not os.path.exists(PATH):
	os.makedirs(PATH)
if not os.path.exists(GPSIES_TRACKS_PATH):
	os.makedirs(GPSIES_TRACKS_PATH)

errorcode = None
errorstring = ''
if os.path.isfile(APIKEY_FILE_PATH):
	with open(APIKEY_FILE_PATH, 'r') as f:
		apikey = f.readline().strip()
	if len(apikey) != 16:
		errorcode = 2
		errorstring = 'filelength not 16 chr'
		print(errorstring)
else:
	errorstring = '%s not found' % (APIKEY_FILE_PATH)
	print(errorstring)
	errorcode = 1

if ROA and errorcode:
	droid.dialogDismiss()
	title='Problem with API Key'
	summary = '%s %s' % (APIKEY_FILE_PATH, errorstring)
	droid.dialogCreateAlert(title, summary)
	droid.dialogSetPositiveButtonText('OK')
	droid.dialogShow()
	dummy = droid.dialogGetResponse().result
	sys.exit(errorcode)
elif not ROA and errorcode:
	sys.exit(errorcode)

def main():
	global GPSIES_USER
	selected_Items = 0 # default for non ROA
	filetype = FILEFORMATS[selected_Items]
	file_ext = FILEFORMATS_EXT[selected_Items]
	download = 1
	status_user_cancel = 0
	print(GPSIES_USER)
	Dprint('PATH: %s' % (PATH))
	if ROA:
		Dprint('Android (qpython) detectet')
		#query GPSIES Username
		message = 'cancel to quit'
		gpsies_user_temp = droid.dialogGetInput('GPSIES Username?',message,GPSIES_USER).result
		if gpsies_user_temp:
			GPSIES_USER = gpsies_user_temp
		else:
			status_user_cancel = 1
		Dprint('username is: %s' % (GPSIES_USER))

		title = 'select format'
		droid.dialogCreateAlert(title)
		droid.dialogSetSingleChoiceItems(FILEFORMATS)
		droid.dialogSetPositiveButtonText('OK')
		droid.dialogShow()
		response = droid.dialogGetResponse().result
		selected_Items = droid.dialogGetSelectedItems().result
		Dprint(selected_Items)
		filetype = FILEFORMATS[selected_Items[0]]
		file_ext = FILEFORMATS_EXT[selected_Items[0]]
		Dprint('selected Format is %s' % (filetype))
	else:
		Dprint('Android (qpython) not detectet')

	if not status_user_cancel:
		#trying to get xml File vie rest api, containing the tracks. filetype=tcx or filetype=gpxTrk
		URL = BASEURL+'key='+apikey+'&username='+GPSIES_USER+'&limit=100&filetype='+filetype
		try:
			#response = urllib.request.urlopen(URL)
			response = urlopen(URL)
			got_xml = 1
		except:
			print('Problem with Internet or nothing found')
			got_xml = 0
			
		Dprint ('xmlpath %s' % (GPSIES_XML_FILE_PATH))

		if got_xml:
			xml_ok = 1
			#storing the received XML File
			gpsies_xml_file = open(GPSIES_XML_FILE_PATH,'wb')
			gpsies_xml_file.write(response.read())
			gpsies_xml_file.close()

			gpsies_xml_file = open(GPSIES_XML_FILE_PATH,'r')
			gpsies_xml_file_data = gpsies_xml_file.read()
			#close file because we dont need it anymore:
			gpsies_xml_file.close()
			
			try:
				# parsing the xml File
				dom = xml.dom.minidom.parseString(gpsies_xml_file_data)
			except:
				print('Server send us bad Data, try again later','error')
				xml_ok = 0

			if xml_ok:
				tracks = dom.getElementsByTagName('track')
				n = 0
				# storing the Filename url etc in array 'mytrack'
				mytracks = []
				for track in tracks:
					km = float((getText(track.getElementsByTagName('trackLengthM')[0].childNodes)))/1000
					tps = int ((getText(track.getElementsByTagName('countTrackpoints')[0].childNodes)))
					trackname = getText(track.getElementsByTagName('title')[0].childNodes)
					link =		getText(track.getElementsByTagName('downloadLink')[0].childNodes)
					hm =   int((getText(track.getElementsByTagName('totalAscentM')[0].childNodes)))
					###Dprint ('Trackname: %s with length: %.1f ' % (trackname,km))

					# replace spec chars with underline
					filename = re.compile('[^a-zA-Z0-9_-]').subn('_', trackname)[0]+'.'+file_ext
					Dprint('Filename: %s' % (filename))
					mytracks.append([trackname,filename,link,km,tps,hm])
					n += 1


				if n > 1:
					if ROA:
						my_name_list=[]
						my_select_list=[]
						my_counter=0
						for mytrack in mytracks:
							my_name_list.append(mytrack[0]+'('+str(mytrack[5])+'hm)')
							Dprint(mytrack[1]+'('+str(mytrack[5])+'hm)')
							# optionaly mark all items in the list:
							if DEFAUL_ALL_SELECTED:
								my_select_list.append(my_counter) # 7 intend
								my_counter+=1
						Dprint('downloadlist: %s' % (my_name_list))
						if n == 100:
							title = 'I got a list with 100 Files'
							message = 'There could be more,but unreachable for me'
							droid.dialogCreateAlert(title, message)
							droid.dialogSetPositiveButtonText('Continue')
							droid.dialogShow()
							response = droid.dialogGetResponse().result
						# Create Downloadlist Dialog:
						title = 'Found %d Files' % (n)
						droid.dialogCreateAlert(title)
						droid.dialogSetMultiChoiceItems(my_name_list, my_select_list)
						droid.dialogSetPositiveButtonText('get selected')
						droid.dialogSetNegativeButtonText('get all')
						droid.dialogSetNeutralButtonText('Cancel')
						droid.dialogShow()
						response = droid.dialogGetResponse().result
						selected_Items = droid.dialogGetSelectedItems().result
						Dprint('response: %s #selected: %s laenge: %d' % (response,selected_Items,len(selected_Items)))
						if response['which'] == 'positive':
							# if selected Items is selected create a new list with the selected Items
							Dprint('getselected')
							download = 1
							download_list=[]
							if len(selected_Items) > 0:
								for Item in selected_Items:
									download_list.append(mytracks[Item]) # 8 intend
							else:
								download = 0
								droid.makeToast('nothing selected')
							mytracks = download_list
							Dprint('download_list %s' % (download_list))
							#n = len(download_list)
							#Dprint('DL_list count %d' % n)
						elif response['which'] == 'negative':
							# getall is selected then doit
							Dprint('getall')
							download = 1
						else:
							Dprint('cancel')
							download = 0
					#dummy = 0	
					Dprint('I have found %d Tracks.Download ?' % (n))
				else:
					Dprint('no Tracks for user xy')
					download = 0
			Dprint('download und xmlok: %d %d' % (download,xml_ok))		
			if download and xml_ok:
				n = len(mytracks)
				Dprint('DL_list count %d' % n)
				Dprint('jetzt dl')
				if ROA:
					# create progressbar for download
					droid.dialogCreateHorizontalProgress(
					'Download...',
					'receiving files',
					n)
					droid.dialogShow()
					Dprint('creating progressbar')
					
				p = totalkm = totaltps = totalhm = oks = failed = 0

				for mytrack in mytracks:
					# receiving file by file
					ok = 1
					try:
						#response = urllib.request.urlopen(mytracks[p][2])
						response = urlopen(mytracks[p][2])
					except:
						ok = 0
						failed += 1	
					
					if ok:
						# storing file
						Dprint('mytrack: %s' % (mytracks[p]))
						my_gpx_file = open(GPSIES_TRACKS_PATH+PS+mytracks[p][1],'wb')
						my_gpx_file.write(response.read())
						my_gpx_file.close()
						totalkm += mytracks[p][3]
						totaltps += mytracks[p][4]
						totalhm += mytracks[p][5]
						oks +=1
						if ROA:
							droid.dialogSetCurrentProgress(p+1)
					# wait 2 sec between DLs wanted by Klaus from GPSIES
					#	time.sleep(1)
					p += 1

				if ROA:
					droid.dialogDismiss()
					title='I have loaded %d File(s) with totaly %dkm and %dhm' % (oks,totalkm,totalhm)
					#droid.makeToast(title)
					#droid.ttsSpeak(title)
					summary = 'Filelocation: %s' % (PATH)
					droid.dialogCreateAlert(title, summary)
					droid.dialogSetPositiveButtonText('OK')
					droid.dialogShow()
					dummy = droid.dialogGetResponse().result

				if not ROA:
					print('Downloadet:%d\nFailed:%d' % (oks,failed))
					print('total km: %.1f' % (totalkm))
					print('total hm: %.1f' % (totalhm))
					print('total trackpoint %d' % (totaltps))
					print('downloadet to: %s' % (PATH))
				status_xml_ok = 1		
			else:
				print('Status: %s' % ('canceled'))
				status_xml_ok = 0
			status_got_XML = 1	
		else:
			print('Status: %s' % ('Failed'))
			status_got_XML = 0


	if status_user_cancel or not download:
		message = 'canceled by user or invalid Username'
	elif not status_got_XML:
		message = 'Network problem or invalid User?'
	else:
		message = 'job done'		

			
	if ROA:
		Dprint('result: %s' % (message))
		#cd = 2
		#droid.dialogCreateHorizontalProgress(message,'waiting to quit',cd)
		#droid.dialogShow()
		#for i in range(cd):
		#	Dprint('done in: %ds' % (i))
		#	droid.dialogSetCurrentProgress(i)
		#	time.sleep(1)
		# Tidy up and exit
		#droid.dialogDismiss()
	else:
		print('result: %s' % (message))

def Dprint(text2print):
	if DEBUG:
		print(text2print)

def getText(nodelist):
	rc = []
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
	return ''.join(rc)


if __name__=='__main__':
	main()


