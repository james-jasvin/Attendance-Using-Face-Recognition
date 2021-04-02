import os
import sys
import time
from distutils.sysconfig import get_python_lib
from PyQt5.QtCore import Qt, QAbstractTableModel, QSize, QCoreApplication, QTimer, QVariant
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QBrush, QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QMainWindow, QApplication, QLabel, QFileDialog, QVBoxLayout, \
	QTableWidget, QTableView, QComboBox, QDialog, QLineEdit, QMessageBox, QStyleFactory
import pandas as pd
from Data import *
from FaceRecognition import *
import datetime


# This upscales the resolution for High Dpi Monitors
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
	QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
	QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# Class required for the display table
class pandasModel(QAbstractTableModel):

	def __init__(self, data):

		QAbstractTableModel.__init__(self)
		self._data = data

	def rowCount(self, parent=None):
		return self._data.shape[0]

	def columnCount(self, parent=None):
		return self._data.shape[1]

	def data(self, index, role=Qt.DisplayRole):
		if index.isValid():
			if role == Qt.DisplayRole:
				return str(self._data.iloc[index.row(), index.column()])
		return None

	def headerData(self, col, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			print(self._data.columns[col])
			return self._data.columns[col]
		return None


# Attendance marking class. This class is the one for an unscheduled lecture
class UIWindow(QWidget):
	def __init__(self, parent=None):
		super(UIWindow, self).__init__(parent)
		self.setWindowIcon(QIcon('feather.png'))

		#This is the combobox stuff
		font = QFont("Times", 8, QFont.Bold)
		year = ['FE', 'SE', 'TE', 'BE']
		self.year = QLabel("YEAR:", self)
		self.year.setFont(font)
		self.year.move(20, 60)

		self.combo = QComboBox(self)
		self.combo.addItems(year)
		self.combo.resize(50, 30)
		self.combo.move(70, 50)
		self.combo.currentTextChanged.connect(self.selectedcombo)

		branch = ['CMPN', 'INFT', 'EXTC', 'ETRX', 'BIOM']
		self.branch = QLabel("BRANCH:", self)
		self.branch.setFont(font)
		self.branch.move(130, 60)
		self.comboBranch = QComboBox(self)
		self.comboBranch.addItems(branch)
		self.comboBranch.resize(100, 30)
		self.comboBranch.move(200, 50)
		self.comboBranch.currentTextChanged.connect(self.selectedcombo)

		div = ['A', 'B', 'C']
		self.div = QLabel('DIV:', self)
		self.div.setFont(font)
		self.div.move(320, 60)
		self.comboDiv = QComboBox(self)
		self.comboDiv.addItems(div)
		self.comboDiv.resize(50, 30)
		self.comboDiv.move(370, 50)
		self.comboDiv.currentTextChanged.connect(self.selectedcombo)

		lab_lect = ['Theory', 'LabB1', 'LabB2', 'LabB3']
		self.lab_lect = QLabel('Type :', self)
		self.lab_lect.setFont(font)
		self.lab_lect.move(600, 60)
		self.comboLect = QComboBox(self)
		self.comboLect.addItems(lab_lect)
		self.comboLect.resize(100, 30)
		self.comboLect.move(650, 50)
		self.comboLect.currentTextChanged.connect(self.selectedcombo)

		lect_subj = ['OST', 'AOA', 'COA', 'AMIV', 'CG', 'OS']
		self.lect_subj = QLabel('Subject :', self)
		self.lect_subj.setFont(font)
		self.lect_subj.move(430, 60)
		self.comboSubj = QComboBox(self)
		self.comboSubj.addItems(lect_subj)
		self.comboSubj.resize(100, 30)
		self.comboSubj.move(480, 50)
		self.comboSubj.currentTextChanged.connect(self.selectedcombo)

		self.selectedcombo()

		# Close Session Button
		self.ToolsBTN = QPushButton('Close Session', self)
		self.ToolsBTN.move(300, 400)
		self.ToolsBTN.resize(250,75)

		self.btn_for_unscheduled = QPushButton('Mark Attendance', self)
		self.btn_for_unscheduled.resize(250, 75)
		self.btn_for_unscheduled.move(300, 200)
		self.btn_for_unscheduled.clicked.connect(self.load_image_and_mark_attendance)

		self.show()

	# This gives you the sheet_name, the division and subject name
	def selectedcombo(self):
		self.year_text = self.combo.currentText()
		self.branch_text = self.comboBranch.currentText()
		self.div_text = self.comboDiv.currentText()
		self.lect_text = self.comboLect.currentText()
		self.lect_subj_text = self.comboSubj.currentText()

		# This takes the option selected in the combobox and stores it into these variables
		self.string_path = self.year_text + ' ' + self.branch_text + ' ' + self.div_text
		self.sheet_name = self.lect_text
		self.subj_name = self.lect_subj_text

		print(self.subj_name)
		print(self.string_path)
		print(self.sheet_name)

	# This function marks the attendance
	def load_image_and_mark_attendance(self):
		'''
			  rip faculty_login()
			  Never forget
		'''

		lect_details, valid = get_lecture_details(faculty_name)
		print(lect_details)

		# image_paths[0] contains image paths, image_paths[1] contains extensions
		# If user opens browse but doesnt select file, then we are checking for that here using len
		try:
			date = datetime.datetime.now().strftime("%d-%m-%y")

			lect_details = {'subject': self.lect_subj_text, 'type': self.lect_text, 'year_branch_div': self.string_path,
							'date': date}

			lect_details['subject'] = self.lect_subj_text
			lect_details['type'] = self.lect_text
			lect_details['year_branch_div'] = self.string_path

			print("Lect details done")
			image_paths = QFileDialog.getOpenFileNames(self, 'Open file', 'Image files', ".png *.jpg")
			if len(image_paths[0]) > 0:
				matched_roll_numbers = face_detect_and_recognize(image_paths[0], lect_details)
				print(matched_roll_numbers)

				# If no face was detected then to prevent crash use this if
				if len(matched_roll_numbers) > 0:
					# date = today's date
					mark_attendance(matched_ids=matched_roll_numbers, subject= self.lect_subj_text, division=self.string_path,
									lecture_type=self.sheet_name)

					# current_date = mark_attendance(matched_roll_numbers)
					# print(current_date)
					print("Marked Attendance")

					# This is where the PROBLEM LIES

					# self.display_current_table('2019-03-28')

					# PROBLEM LITERALLY ENDS IF YOU COMMENT IT

				else:
					choice = QMessageBox.question(self, 'Error!',
												  "No faces found in provided image, Upload another image",
												  QMessageBox.Ok)
					if choice == QMessageBox.Ok:
						pass

		except:
			choice = QMessageBox.question(self, 'Error!',
										  "No PATH exists for specified for combo boxes, please edit them",
										  QMessageBox.Ok)
			if choice == QMessageBox.Ok:
				pass


# Table Class. Same stuff but this only includes the spreadsheet feature
class UIWindow1(QWidget):
	def __init__(self, parent=None):
		super(UIWindow1, self).__init__(parent)
		self.setWindowIcon(QIcon('feather.png'))

		font = QFont("Times", 8, QFont.Bold)
		year = ['FE', 'SE', 'TE', 'BE']
		self.year = QLabel("YEAR:", self)
		self.year.setFont(font)
		self.year.move(20, 60)

		self.combo = QComboBox(self)
		self.combo.addItems(year)
		self.combo.resize(50, 30)
		self.combo.move(70, 50)
		self.combo.currentTextChanged.connect(self.selectedcombo)

		branch = ['CMPN', 'INFT', 'EXTC', 'ETRX', 'BIOM']
		self.branch = QLabel("BRANCH:", self)
		self.branch.setFont(font)
		self.branch.move(130, 60)
		self.comboBranch = QComboBox(self)
		self.comboBranch.addItems(branch)
		self.comboBranch.resize(100, 30)
		self.comboBranch.move(200, 50)
		self.comboBranch.currentTextChanged.connect(self.selectedcombo)

		div = ['A', 'B', 'C']
		self.div = QLabel('DIV:', self)
		self.div.setFont(font)
		self.div.move(320, 60)
		self.comboDiv = QComboBox(self)
		self.comboDiv.addItems(div)
		self.comboDiv.resize(50, 30)
		self.comboDiv.move(370, 50)
		self.comboDiv.currentTextChanged.connect(self.selectedcombo)

		lab_lect = ['Theory', 'LabB1', 'LabB2', 'LabB3']
		self.lab_lect = QLabel('Type :', self)
		self.lab_lect.setFont(font)
		self.lab_lect.move(600, 60)
		self.comboLect = QComboBox(self)
		self.comboLect.addItems(lab_lect)
		self.comboLect.resize(100, 30)
		self.comboLect.move(650, 50)
		self.comboLect.currentTextChanged.connect(self.selectedcombo)

		lect_subj = ['OST', 'AOA', 'COA', 'AMIV', 'CG', 'OS']
		self.lect_subj = QLabel('Subject :', self)
		self.lect_subj.setFont(font)
		self.lect_subj.move(430, 60)
		self.comboSubj = QComboBox(self)
		self.comboSubj.addItems(lect_subj)
		self.comboSubj.resize(100, 30)
		self.comboSubj.move(480, 50)
		self.comboSubj.currentTextChanged.connect(self.selectedcombo)

		self.selectedcombo()

		self.ToolsBTN1 = QPushButton('Close Session', self)
		self.ToolsBTN1.move(300, 400)
		self.ToolsBTN1.resize(250,75)

		self.disp_excel = QPushButton('Display SpreadSheet', self)
		self.disp_excel.move(300, 200)
		self.disp_excel.resize(250, 75)
		self.disp_excel.clicked.connect(self.table_disp)

		self.show()

	def selectedcombo(self):
		self.year_text = self.combo.currentText()
		self.branch_text = self.comboBranch.currentText()
		self.div_text = self.comboDiv.currentText()
		self.lect_text = self.comboLect.currentText()
		self.lect_subj_text = self.comboSubj.currentText()

		self.string_path = self.year_text + ' ' + self.branch_text + ' ' + self.div_text
		self.sheet_name = self.lect_text
		self.subj_name = self.lect_subj_text

		print(self.subj_name)
		print(self.string_path)
		print(self.sheet_name)

	def table_disp(self):
		try:
			path = compute_percentages(division=self.string_path, subject=self.subj_name, lecture_type=self.sheet_name)
			excel_to_display = pd.read_excel(path, header=None)
			excel_to_display = excel_to_display.fillna(' ')
			os.remove(path)
			print(excel_to_display)

			self.model = pandasModel(excel_to_display)

			self.view = QTableView()
			self.view.setWindowIcon(QIcon('feather.png'))  # The Feather is super important
			self.view.setWindowTitle('Excel Sheet in Table Form')

			self.view.setModel(self.model)
			self.view.resize(800, 600)
			self.view.show()
		except:
			choice = QMessageBox.question(self, 'Error!',
										  "Incorrect path provided",
										  QMessageBox.Ok)
			if choice == QMessageBox.Ok:
				pass


# Graph displaying class. Only contains the graph stuff
class UIWindow2(QWidget):
	def __init__(self, parent=None):
		super(UIWindow2, self).__init__(parent)
		self.setWindowIcon(QIcon('feather.png'))

		font = QFont("Times", 8, QFont.Bold)
		year = ['FE', 'SE', 'TE', 'BE']
		self.year = QLabel("YEAR:", self)
		self.year.setFont(font)
		self.year.move(20, 60)

		self.combo = QComboBox(self)
		self.combo.addItems(year)
		self.combo.resize(50, 30)
		self.combo.move(70, 50)
		self.combo.currentTextChanged.connect(self.selectedcombo)

		branch = ['CMPN', 'INFT', 'EXTC', 'ETRX', 'BIOM']
		self.branch = QLabel("BRANCH:", self)
		self.branch.setFont(font)
		self.branch.move(130, 60)
		self.comboBranch = QComboBox(self)
		self.comboBranch.addItems(branch)
		self.comboBranch.resize(100, 30)
		self.comboBranch.move(200, 50)
		self.comboBranch.currentTextChanged.connect(self.selectedcombo)

		div = ['A', 'B', 'C']
		self.div = QLabel('DIV:', self)
		self.div.setFont(font)
		self.div.move(320, 60)
		self.comboDiv = QComboBox(self)
		self.comboDiv.addItems(div)
		self.comboDiv.resize(50, 30)
		self.comboDiv.move(370, 50)
		self.comboDiv.currentTextChanged.connect(self.selectedcombo)

		lab_lect = ['Theory', 'LabB1', 'LabB2', 'LabB3']
		self.lab_lect = QLabel('Type :', self)
		self.lab_lect.setFont(font)
		self.lab_lect.move(600, 60)
		self.comboLect = QComboBox(self)
		self.comboLect.addItems(lab_lect)
		self.comboLect.resize(100, 30)
		self.comboLect.move(650, 50)
		self.comboLect.currentTextChanged.connect(self.selectedcombo)

		lect_subj = ['OST', 'AOA', 'COA', 'AMIV', 'CG', 'OS']
		self.lect_subj = QLabel('Subject :', self)
		self.lect_subj.setFont(font)
		self.lect_subj.move(430, 60)
		self.comboSubj = QComboBox(self)
		self.comboSubj.addItems(lect_subj)
		self.comboSubj.resize(100, 30)
		self.comboSubj.move(480, 50)
		self.comboSubj.currentTextChanged.connect(self.selectedcombo)

		self.selectedcombo()

		self.ToolsBTN2 = QPushButton('Close Session', self)
		self.ToolsBTN2.move(300, 400)
		self.ToolsBTN2.resize(250,75)

		self.graph_button = QPushButton("Display Graph", self)
		self.graph_button.resize(250, 75)
		self.graph_button.move(300, 200)
		self.graph_button.clicked.connect(self.display_graph)

		self.show()

	def selectedcombo(self):
		self.year_text = self.combo.currentText()
		self.branch_text = self.comboBranch.currentText()
		self.div_text = self.comboDiv.currentText()
		self.lect_text = self.comboLect.currentText()
		self.lect_subj_text = self.comboSubj.currentText()

		self.string_path = self.year_text + ' ' + self.branch_text + ' ' + self.div_text
		self.sheet_name = self.lect_text
		self.subj_name = self.lect_subj_text
		print(self.subj_name)

		print(self.string_path)
		print(self.sheet_name)

	def display_graph(self):
		try:
			plot_bargraph(division=self.string_path, lecture_type=self.sheet_name, subject=self.subj_name)
		except:
			choice = QMessageBox.question(self, 'Error!',
										  "Incorrect path provided",
										  QMessageBox.Ok)
			if choice == QMessageBox.Ok:
				pass


# The window that opens up after logging in
# This window remains intact if on clicking mark attendance, it was a scheduled lecture, else UIWindow is called
# This is the main window.
class UIToolTab(QWidget):
	def __init__(self, parent=None):
		super(UIToolTab, self).__init__(parent)

		self.setWindowIcon(QIcon('feather.png'))

		self.btn = QPushButton('Mark Attendance', self)
		self.btn.resize(250, 75)
		self.btn.move(50, 120)

		lect_details, valid = get_lecture_details(faculty_name)

		if valid is True:
			self.btn.clicked.connect(self.load_image_and_mark_attendance)


		self.disp_excel = QPushButton('Display SpreadSheet', self)
		self.disp_excel.move(500, 120)
		self.disp_excel.resize(250, 75)

		self.btn_quit1 = QPushButton("Quit", self)
		self.btn_quit1.clicked.connect(self.quitter)
		self.btn_quit1.resize(250, 75)
		self.btn_quit1.move(300, 400)

		self.graph_button = QPushButton("Display Graph", self)
		self.graph_button.resize(250, 75)
		self.graph_button.move(50, 230)

	def quitter(self):
		sys.exit()

	# Repeat of the mark attendance function
	def load_image_and_mark_attendance(self):
		lect_details, valid = get_lecture_details(faculty_name)
		print(lect_details)

		image_paths = QFileDialog.getOpenFileNames(self, 'Open file', 'Image files', ".png *.jpg")

		if len(image_paths[0]) > 0:
			matched_roll_numbers = face_detect_and_recognize(image_paths[0], lect_details)
			print(matched_roll_numbers)
			# If no face was detected then to prevent crash use this if
			if len(matched_roll_numbers) > 0:
				mark_attendance(matched_ids=matched_roll_numbers, division=lect_details['year_branch_div'],
								lecture_type=lect_details['type'], subject=lect_details['subject'], hour=lect_details['duration'])

				print("Marked Attendance")

			else:
				choice = QMessageBox.question(self, 'Error!',
											  "No faces found in provided image, Upload another image",
											  QMessageBox.Ok)
				if choice == QMessageBox.Ok:
					pass
				print("No faces found in provided image, Upload another image")  # This could be like a popup

	def display_current_table(self, current_date):
		# You get the name from faculty_login() which is called at the very bottom in __main__() function

		lecture_details, valid = get_lecture_details(Login.faculty_name)
		if valid:
			path = "Attendance Sheets/" + lecture_details['division'] + "/" + lecture_details['subject'] + "/" + \
				   lecture_details['subject'] + " Attendance.xlsx"
			excel_to_display = pd.read_excel(path, sheet_name=lecture_details['type'], index_col=0,
											 usecols=[current_date])
		else:
			print("No lecture scheduled, this shouldn't have happened, check what's going on")

		self.model = pandasModel(excel_to_display)

		self.view = QTableView()
		self.view.setWindowIcon(QIcon('feather.png'))  # The Feather is super important
		self.view.setWindowTitle('Excel Sheet in Table Form')

		self.view.setModel(self.model)
		self.view.resize(800, 600)
		self.view.show()


class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setGeometry(100, 100, 800, 500)
		self.setWindowTitle('V-Attendance')
		self.setWindowIcon(QIcon('feather.png'))

		self.setStyle(QStyleFactory.create('Fusion'))

		self.setStyleSheet("background-color: white;")
		self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
		print(faculty_name)
		lect_details, valid = get_lecture_details(faculty_name)

		self.startUIToolTab()

	def startUIToolTab(self):

		# Creates the start session and faculty button window
		self.ToolTab = UIToolTab(self)
		self.setCentralWidget(self.ToolTab)

		# If start session button clicked then create the window with open image and close session buttons
		lect_details, valid = get_lecture_details(faculty_name)

		if valid is False:
			# Mark attendance extra window
			self.ToolTab.btn.clicked.connect(self.startUIWindow)

		# Spreadsheet window
		self.ToolTab.disp_excel.clicked.connect(self.startUI1Window)

		# Graph window start. (I might have mixed up spreadsheet and graph)
		self.ToolTab.graph_button.clicked.connect(self.startUI2Window)

		self.show()

	# Window after clicking start session
	def startUIWindow(self):
		self.Window = UIWindow(self)
		self.setWindowTitle("Session Started")
		self.setCentralWidget(self.Window)

		# Main window
		self.Window.ToolsBTN.clicked.connect(self.startUIToolTab)

		self.show()

	# Main window again
	def startUI1Window(self):
		self.Window1 = UIWindow1(self)

		self.setWindowTitle("Faculty Menu")
		self.setCentralWidget(self.Window1)
		self.Window1.ToolsBTN1.clicked.connect(self.startUIToolTab)

		self.show()

	# Too many main windows
	def startUI2Window(self):
		self.Window2 = UIWindow2(self)

		self.setWindowTitle("Faculty Menu")
		self.setCentralWidget(self.Window2)
		self.Window2.ToolsBTN2.clicked.connect(self.startUIToolTab)

		self.show()


class Login(QDialog):
	def __init__(self, parent=None):
		super(Login, self).__init__(parent)

		self.setStyleSheet("background-color: white;")
		self.setStyle(QStyleFactory.create('Fusion'))
		self.setWindowIcon(QIcon('feather.png'))

		self.setGeometry(0, 0, 650, 409)
		self.labeluser = QLabel("USERNAME:", self)
		self.labeluser.move(250, 100)
		self.username = QLineEdit(self)
		self.username.move(250, 130)
		self.password = QLineEdit(self)
		self.labelpass = QLabel("PASSWORD", self)
		self.labelpass.move(250, 160)
		self.password.move(250, 180)
		self.password.setEchoMode(QLineEdit.Password)
		self.buttonLogin = QPushButton('Login', self)
		self.buttonLogin.move(250, 230)

		print(self.username.text())
		self.buttonLogin.clicked.connect(self.handleLogin)

	def handleLogin(self):

		valid, name_or_error = faculty_login(self.username.text(), self.password.text())
		print(valid, name_or_error)

		if valid is True:
			global faculty_name
			faculty_name = name_or_error
			choice = QMessageBox.question(self, 'Welcome',
										  "Welcome, Professor " + name_or_error,
										  QMessageBox.Ok)
			if choice == QMessageBox.Ok:
				self.accept()
		elif name_or_error is "Username not found":
			QMessageBox.warning(self, 'Error', name_or_error)
		else:
			QMessageBox.warning(self, 'Error', name_or_error)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	login = Login()
	login.setWindowTitle('Login')
	login.setGeometry(100, 100, 605, 409)

	if login.exec_() == QDialog.Accepted:
		w = MainWindow()

		sys.exit(app.exec_())
