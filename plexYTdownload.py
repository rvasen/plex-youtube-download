import sqlite3
import sys
import getpass
import platform
import os
import pafy
from PySide.QtCore import *
from PySide.QtGui import *

class MainPage(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		temp = QWidget()

		mainLayout = QVBoxLayout()
		temp.setLayout(mainLayout)
		self.setGeometry(1,1,0,0)

		self.landingPage()

	def landingPage(self):
		self.window = QWidget()
		self.window.setWindowTitle("Download YT Videos to Plex Library")
		self.window.setFixedWidth(450)
		self.window.setFixedHeight(370)
		self.window.show()

		#Create and populate dropdown menu for selecting library to have video downloaded into
		self.selectLibraryDropdown = QComboBox()
		self.selectLibraryDropdown.addItems(self.findLibraries(True))

		#Default list of URLs to empty array
		try:
			self.URLtitleArray
		except AttributeError:
			self.URLtitleArray = []
			self.URLarray = []

		#List box to display List of URLs
		urlListBox = QListWidget()
		urlListBox.addItems(self.URLtitleArray)

		#Line edit and label for inputting 
		urlLineLabel = QLabel("Specify URL or 11 Character Video ID for YouTube Video")
		self.urlLineEdit = QLineEdit(self)

		#Button to add QLineEdit space for entering another YouTube URL
		addURLbutton = QPushButton("Add URL to List to Download")
		addURLbutton.clicked.connect(self.addLineForURL)

		#Button to download YouTube videos in selected library
		submitButton = QPushButton("Download video(s)")
		submitButton.clicked.connect(self.downloadVideos)
		submitButton.setFixedWidth(150)

		libraryGroup = QGroupBox("Select Library for Downloading Video(s) into:")
		urlGroup = QGroupBox("Choose URL(s) to Download Video(s) from:")
		submitGroup = QGroupBox("")

		submitGroup.setFixedHeight(50)

		libraryGroupLayout = QVBoxLayout()
		urlGroupLayout = QVBoxLayout()
		submitGroupLayout = QHBoxLayout()

		libraryGroupLayout.addWidget(self.selectLibraryDropdown)
		urlGroupLayout.addWidget(urlListBox)
		urlGroupLayout.addWidget(urlLineLabel)
		urlGroupLayout.addWidget(self.urlLineEdit)
		urlGroupLayout.addWidget(addURLbutton)
		submitGroupLayout.addWidget(submitButton)

		libraryGroup.setLayout(libraryGroupLayout)
		urlGroup.setLayout(urlGroupLayout)
		submitGroup.setLayout(submitGroupLayout)

		mainLayout = QVBoxLayout(self)
		mainLayout.addWidget(libraryGroup)
		mainLayout.addWidget(urlGroup)
		mainLayout.addWidget(submitGroup)

		self.window.setLayout(mainLayout)


	def downloadVideos(self):
		db = sqlite3.connect(self.dbFile)
		cursor = db.cursor()
		cursor.execute("SELECT id FROM library_sections WHERE name = '%s'" % self.selectLibraryDropdown.currentText())
		sectionID = cursor.fetchone()
		cursor.execute('''SELECT root_path FROM section_locations WHERE library_section_id = %s''' % sectionID)
		downloadDir = cursor.fetchone()[0]
		cursor.close()
		db.close()
		for url in self.URLarray:
			video = pafy.new(url)
			best = video.getbest(preftype="mp4")
			myFilePath = downloadDir + best.title + "." + best.extension
			pd = QProgressDialog("Downloading Video(s)", "Cancel", 0, 100)
			best.download(filepath=myFilePath, quiet=True)

	def addLineForURL(self):
		url = self.urlLineEdit.text()
		try:
			video = pafy.new(url)
			self.URLtitleArray.append(video.title)
			self.URLarray.append(url)
			self.landingPage()
		except IOError:
			self.alertPopUp("YouTube says this video does not exist.")
		except ValueError:
			self.alertPopUp("Need 11 character video ID or the URL of the video.")
		except:
			self.alertPopUp("Something went wrong with validating your URL. Make sure your internet connection is working.")

	def alertPopUp(self, message):
		msgBox = QMessageBox()
		msgBox.setText(message)
		msgBox.setWindowTitle("Download YT Videos to Plex Library")
		msgBox.exec_()

	def findLibraries(self, firstTry):
		try:
			#firstTry is a parameter used to determine whether this function is being called from landingPage() or from selectDBFile (used when database is not found in default location)
			if(firstTry):
				#Determines OS to determine which default location to look in; only supports Windows as of now
				user = getpass.getuser()
				if(platform.system() == "Windows"):
					if(platform.release() == ("XP" or "Server 2003" or "Home Server")):
						self.dbFile = "C:\\Documents and Settings\\%s\\Local Settings\\Application Data\\Plex Media Server\\Plug-In Support\\Databases\\com.plexapp.plugins.library.db" % user
					elif(platform.release() == "7"):
						localAppData = os.environ['LOCALAPPDATA']
						self.dbFile = "%s\\Plex Media Server\\Plug-In Support\\Databases\\com.plexapp.plugins.library.db" % localAppData
			#This variable is used later by createBackup and retrieveBackup
			self.dbDir = self.dbFile.replace("\\com.plexapp.plugins.library.db", "")
			#Connects to database, looks in the table that holds information about the library sections, and returns an array of the names of the library sections
			db = sqlite3.connect(self.dbFile)
			cursor = db.cursor()
			cursor.execute('''SELECT name FROM library_sections''')
			rows = cursor.fetchall()
			sections = []
			for row in rows:
				sections.append(row[0])
			cursor.close()
			db.close()
			return sections
		#Exception for when no database is found
		except sqlite3.OperationalError:
			#This will ultimately return an array of the names of the library sections from the database the user defines; see lines 144-145
			return self.noDatabaseAlert()

	def noDatabaseAlert(self):
		msgBox = QMessageBox()
		msgBox.setText("The SQLite database necessary to find your Plex libraries could not be found. Either you do not have an installation of the Plex Media Server or it is located elsewhere.")
		msgBox.setInformativeText("For help locating the database file, click Help. To download a copy of Plex Media Server, click Download. To locate the database file, click Locate.")
		msgBox.setWindowTitle("Change Icons for Plex")
		closeButton = msgBox.addButton("Close", QMessageBox.AcceptRole)
		helpButton = msgBox.addButton("Help", QMessageBox.HelpRole)
		downloadButton = msgBox.addButton("Download", QMessageBox.HelpRole)
		locateButton = msgBox.addButton("Locate", QMessageBox.YesRole)
		msgBox.exec_()
		if(msgBox.clickedButton() == closeButton):
			#I'm not sure why but the red x in the corner is greyed out; this should suffice 
			sys.exit()
		elif(msgBox.clickedButton() == helpButton):
			QDesktopServices.openUrl(QUrl("http://raspberrypihtpc.wordpress.com/how-to/how-to-plex-media-server-change-the-section-icons/"))
			self.noDatabaseAlert()
		elif(msgBox.clickedButton() == downloadButton):
			QDesktopServices.openUrl(QUrl("https://plex.tv/downloads/1/archive"))
			self.noDatabaseAlert()
		elif(msgBox.clickedButton() == locateButton):
			#Passes the returned value from selectDBFile to the findLibraries sqlite3.OperationError exception and onto self.selectLibraryDropdown.addItems() in the MainPage.__init__ function
			return self.selectDBFile()

	def selectDBFile(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.AnyFile)
		dialog.setNameFilter("Databases (*.db)")
		dialog.setViewMode(QFileDialog.Detail)
		if dialog.exec_():
			self.dbFile = dialog.selectedFiles()[0]
			#Finally the list of library names
			return self.findLibraries(False)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainPage()
	window.show()
	sys.exit(app.exec_())