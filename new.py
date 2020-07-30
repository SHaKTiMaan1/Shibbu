
import pickle
from collections import defaultdict
from datetime import datetime, date

import cv2

from faceblinkdetection.FaceRecognition import *
from inandout_track.FaceRecognition import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QVBoxLayout
import sqlite3


class Worker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class

    ''' Connecting to the attendance taking process'''

    def attendance(self):
        d = date.today().strftime('%d-%m-%Y')

        print("[LOG] Initialization...")

        (model, face_detector, open_eyes_detector, left_eye_detector, right_eye_detector, video_capture, images,
         source_resolution) = init()

        with open('dataset_faces.dat', 'rb') as f:
            known_encodings = pickle.load(f)
        with open('dataset_c_ids.dat', 'rb') as f:
            known_c_ids = pickle.load(f)
        data = {"encodings": known_encodings, "c_ids": known_c_ids}

        img_overlay = cv2.imread('faceblinkdetection/data/icon_eye_100x40.png')

        eyes_detected = defaultdict(str)
        imshow_label = "Face Liveness Detector - Blinking Eyes (q-quit, p-pause)"
        print("[LOG] Detecting & Showing Images...")

        while True:
            frame = detect_and_display(model, video_capture, face_detector, open_eyes_detector,
                                       left_eye_detector, right_eye_detector, data, eyes_detected,
                                       source_resolution)
            if frame is None:
                break
            cv2.imshow(imshow_label, frame)

            # asama: modified to include p=pause
            key_pressed = cv2.waitKey(1)
            if key_pressed & 0xFF == ord('q'):
                break
            elif key_pressed & 0xFF == ord('p'):  # p=pause
                cv2.waitKey(-1)

            ls1 = []
            ls2 = []

        c.execute("SELECT C_ID FROM details")
        for x in c.fetchall():
            ls1.append(x[0])

        c.execute("SELECT C_ID FROM attendance")
        for y in c.fetchall():
            ls2.append(y[0])

        for x in ls1:
            if x not in ls2:
                c.execute("INSERT INTO attendance (DATE,C_ID,ATTEND) VALUES (?, ?, ?)", (d, x, "False"))
        conn.commit()
        video_capture.stop()
        cv2.destroyAllWindows()
        print("[LOG] All done.")
        conn.close()

    def do_work(self):

            conn = sqlite3.connect('child.db')
            c = conn.cursor()

            while self.continue_run:
                self.attendance()
                query = '''Select  C_ID, FNAME, LNAME, DATE, Attend, ROA FROM attendance NATURAL JOIN  details'''
                result = c.execute(query)
                self.tableWidget_4.setRowCount(0)
                for row_number, row_data in enumerate(result):
                    self.tableWidget_4.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.tableWidget_4.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
                self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
            self.continue_run = False

class Ui_MainWindow(object):
    finished = pyqtSignal()
    conn = sqlite3.connect('child.db')
    c = conn.cursor()

    ''' To display the in and out detail of searched date'''
    def inandout(self):
        vr_date = self.dateEdit_4.date()
        vr1_date = vr_date.toPyDate()
        picked_date = vr1_date.strftime('%d-%m-%Y')
        conn = sqlite3.connect('child.db')
        c = conn.cursor()
        query = '''SELECT C_Id, DATE_out, TIME_out, DATE_in, TIME_in  FROM in_and_out WHERE DATE_out =?'''
        result = c.execute(query, (picked_date, ))
        self.tableWidget_2.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget_2.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget_2.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

        conn.close()


    ''' To display the in and out detail of current day'''
    def inandouttoday(self):
        conn = sqlite3.connect('child.db')
        c = conn.cursor()
        now = datetime.now()
        today_date = now.strftime('%d-%m-%Y')
        query = '''SELECT C_Id, DATE_out, TIME_out, DATE_in, TIME_in  FROM in_and_out WHERE DATE_out =?'''
        result = c.execute(query, (today_date,))
        self.tableWidget_3.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget_3.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget_3.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))




    ''' Message box to save attendance and stopping the process of taking attendance'''
    def messagebox(self, title, message):
        mess = QtWidgets.QMessageBox()
        mess.setWindowTitle(title)
        mess.setText(message)
        mess.setStandardButtons(QtWidgets.QMessageBox.Ok)
        mess.exec()

    def attendancestopped(self):
        self.messagebox("Attendance Saved", "Today Attendance is saved.")

    ''' To display the attendance of picked date'''
    def showattendancedetail(self):
        vr_date = self.dateEdit.date()
        vr1_date = vr_date.toPyDate()
        picked_date = vr1_date.strftime('%d-%m-%Y')
        conn = sqlite3.connect('child.db')
        c = conn.cursor()
        query = '''Select  C_ID, FNAME, LNAME, Attend, ROA FROM attendance NATURAL JOIN  details WHERE DATE =?'''
        result = c.execute(query, (picked_date, ))
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

        conn.close()



    ''' To run in and out continue'''
    def runinandout(self):

         print("Initialization...")

         (model, face_detector, open_eyes_detector, left_eye_detector, right_eye_detector, video_capture, images,
                 source_resolution) = init()

         '''This is for when we do encoding do once in a project remove # and apply to line 308'''
         with open('dataset_faces.dat', 'rb') as f:
                known_encodings = pickle.load(f)
         with open('dataset_c_ids.dat', 'rb') as f:
                known_c_ids = pickle.load(f)
         data = {"encodings": known_encodings, "c_ids": known_c_ids}

         # data = process_and_encode(images)
         img_overlay = cv2.imread('data/icon_eye_100x40.png')
         eyes_detected = defaultdict(str)

         while True:
             frame = detect_and_display(model, face_detector, open_eyes_detector, left_eye_detector,
                                                   right_eye_detector,
                                                   video_capture, images, source_resolution)
             if frame is None:
                    break

             cv2.imshow("In And Out Tracking", frame)
             cv2.waitKey(1)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1331, 654)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_right = QtWidgets.QFrame(self.centralwidget)
        self.frame_right.setGeometry(QtCore.QRect(75, 55, 1261, 681))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_right.sizePolicy().hasHeightForWidth())
        self.frame_right.setSizePolicy(sizePolicy)
        self.frame_right.setStyleSheet("*{\n"
                                       "   background:white;\n"
                                       "}")
        self.frame_right.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_right.setObjectName("frame_right")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_right)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.stackedWidget = QtWidgets.QStackedWidget(self.frame_right)
        self.stackedWidget.setObjectName("stackedWidget")
        self.add_dataset = QtWidgets.QWidget()
        self.add_dataset.setObjectName("add_dataset")
        self.stackedWidget.addWidget(self.add_dataset)
        self.attendance = QtWidgets.QWidget()
        self.attendance.setObjectName("attendance")
        self.label = QtWidgets.QLabel(self.attendance)
        self.label.setGeometry(QtCore.QRect(-270, -10, 1701, 41))
        font = QtGui.QFont()
        font.setFamily("AcmeFont")
        font.setPointSize(22)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.tabWidget = QtWidgets.QTabWidget(self.attendance)
        self.tabWidget.setGeometry(QtCore.QRect(20, 60, 1201, 671))
        self.tabWidget.setMinimumSize(QtCore.QSize(1201, 0))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.tabWidget.setFont(font)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setIconSize(QtCore.QSize(16, 16))
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setObjectName("tabWidget")
        self.takeattendance = QtWidgets.QWidget()
        self.takeattendance.setObjectName("takeattendance")
        self.tableWidget_4 = QtWidgets.QTableWidget(self.takeattendance)
        self.tableWidget_4.setGeometry(QtCore.QRect(20, 60, 1161, 561))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tableWidget_4.setFont(font)
        self.tableWidget_4.setRowCount(20)
        self.tableWidget_4.setObjectName("tableWidget_4")
        self.tableWidget_4.setColumnCount(6)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(5, item)
        self.tableWidget_4.horizontalHeader().setDefaultSectionSize(192)
        self.takeattendancenow = QtWidgets.QPushButton(self.takeattendance)
        self.takeattendancenow.setGeometry(QtCore.QRect(20, 20, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.takeattendancenow.setFont(font)
        self.takeattendancenow.setObjectName("takeattendancenow")
        #self.takeattendancenow.clicked.connect(self.takeattendance_today)
        self.saveattendance = QtWidgets.QPushButton(self.takeattendance)
        self.saveattendance.setGeometry(QtCore.QRect(990, 20, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.saveattendance.setFont(font)
        self.saveattendance.setObjectName("saveattendance")
        ###############################################
        # Thread:
        self.thread = QThread()
        self.worker = Worker()
        self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.do_work)
        self.thread.finished.connect(self.worker.stop)

        # Start Button action:
        self.show.clicked.connect(self.thread.start)

        # Stop Button action:
        self.saveattendance.clicked.connect(self.stop_thread)

        self.saveattendance.clicked.connect(self.attendancestopped)

        self.tabWidget.addTab(self.takeattendance, "")
        self.showattendance = QtWidgets.QWidget()
        self.showattendance.setObjectName("showattendance")
        self.textBrowser = QtWidgets.QTextBrowser(self.showattendance)
        self.textBrowser.setGeometry(QtCore.QRect(10, 20, 121, 21))
        self.textBrowser.setObjectName("textBrowser")
        self.dateEdit = QtWidgets.QDateEdit(self.showattendance)
        self.dateEdit.setGeometry(QtCore.QRect(100, 20, 110, 21))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.dateEdit.setFont(font)
        self.dateEdit.setWrapping(False)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDate(QtCore.QDate(2020, 7, 27))
        self.dateEdit.setObjectName("dateEdit")
        vr_date = self.dateEdit.date()
        self.pushButton_2 = QtWidgets.QPushButton(self.showattendance)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 50, 201, 21))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")

        self.frame_2 = QtWidgets.QFrame(self.showattendance)
        self.frame_2.setGeometry(QtCore.QRect(10, 80, 1171, 481))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.tableWidget = QtWidgets.QTableWidget(self.frame_2)
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 1151, 491))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tableWidget.setFont(font)
        self.tableWidget.setRowCount(20)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(233)
        self.pushButton_2.clicked.connect(self.showattendancedetail)  ########
        self.tabWidget.addTab(self.showattendance, "")
        self.stackedWidget.addWidget(self.attendance)
        self.in_out = QtWidgets.QWidget()
        self.in_out.setObjectName("in_out")
        self.label_2 = QtWidgets.QLabel(self.in_out)
        self.label_2.setGeometry(QtCore.QRect(-4, -8, 1251, 41))
        font = QtGui.QFont()
        font.setFamily("AcmeFont")
        font.setPointSize(22)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.tabWidget_2 = QtWidgets.QTabWidget(self.in_out)
        self.tabWidget_2.setGeometry(QtCore.QRect(10, 50, 1211, 601))
        self.tabWidget_2.setMinimumSize(QtCore.QSize(1201, 0))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.tabWidget_2.setFont(font)
        self.tabWidget_2.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget_2.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget_2.setIconSize(QtCore.QSize(16, 16))
        self.tabWidget_2.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.takeattendance_2 = QtWidgets.QWidget()
        self.takeattendance_2.setObjectName("takeattendance_2")
        self.tableWidget_3 = QtWidgets.QTableWidget(self.takeattendance_2)
        self.tableWidget_3.setGeometry(QtCore.QRect(30, 50, 1151, 521))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget_3.sizePolicy().hasHeightForWidth())
        self.tableWidget_3.setSizePolicy(sizePolicy)
        self.tableWidget_3.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.tableWidget_3.setRowCount(20)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setColumnCount(5)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(8)
        item.setFont(font)
        self.tableWidget_3.setFont(font)
        self.tableWidget_3.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_3.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_3.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_3.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_3.setHorizontalHeaderItem(4, item)
        self.tableWidget_3.horizontalHeader().setDefaultSectionSize(233)
        self.tableWidget_3.horizontalHeader().setStretchLastSection(False)
        self.show = QtWidgets.QPushButton(self.takeattendance_2)
        self.show.setGeometry(QtCore.QRect(30, 10, 75, 23))
        self.show.setFont(font)
        self.show.setObjectName("show")
        self.show.clicked.connect(self.inandouttoday)  ##############
        self.tabWidget_2.addTab(self.takeattendance_2, "")
        self.showattendance_2 = QtWidgets.QWidget()
        self.showattendance_2.setObjectName("showattendance_2")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.showattendance_2)
        self.textBrowser_2.setGeometry(QtCore.QRect(10, 20, 121, 21))
        font = QtGui.QFont()
        font.setPointSize(6)
        self.textBrowser_2.setFont(font)
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.dateEdit_4 = QtWidgets.QDateEdit(self.showattendance_2)
        self.dateEdit_4.setGeometry(QtCore.QRect(100, 20, 121, 21))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.dateEdit_4.setFont(font)
        self.dateEdit_4.setCalendarPopup(True)
        self.dateEdit_4.setDate(QtCore.QDate(2020, 7, 27))
        self.dateEdit_4.setObjectName("dateEdit_4")
        self.showinandout = QtWidgets.QPushButton(self.showattendance_2)
        self.showinandout.setGeometry(QtCore.QRect(10, 50, 211, 21))
        self.showinandout.setFont(font)
        font = QtGui.QFont()
        font.setFamily("Leelawadee")
        font.setPointSize(7)
        self.showinandout.setFont(font)
        self.showinandout.setObjectName("showinandout")
        self.tableWidget_2 = QtWidgets.QTableWidget(self.showattendance_2)
        self.tableWidget_2.setGeometry(QtCore.QRect(20, 90, 1171, 481))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tableWidget_2.setFont(font)
        self.tableWidget_2.setRowCount(20)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(5)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(4, item)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(233)
        self.showinandout.clicked.connect(self.inandout)
        self.tabWidget_2.addTab(self.showattendance_2, "")
        self.stackedWidget.addWidget(self.in_out)
        self.detail = QtWidgets.QWidget()
        self.detail.setObjectName("detail")
        self.stackedWidget.addWidget(self.detail)
        self.verticalLayout_3.addWidget(self.stackedWidget)
        self.frame_top = QtWidgets.QFrame(self.centralwidget)
        self.frame_top.setGeometry(QtCore.QRect(-1, 0, 1331, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_top.sizePolicy().hasHeightForWidth())
        self.frame_top.setSizePolicy(sizePolicy)
        self.frame_top.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_top.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_top.setObjectName("frame_top")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_top)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(self.frame_top)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Bodoni MT")
        font.setPointSize(25)
        self.label_3.setFont(font)
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.frame_toggle = QtWidgets.QFrame(self.centralwidget)
        self.frame_toggle.setGeometry(QtCore.QRect(2, 52, 71, 55))
        self.frame_toggle.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_toggle.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_toggle.setObjectName("frame_toggle")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_toggle)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.toggle_button = QtWidgets.QPushButton(self.frame_toggle)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toggle_button.sizePolicy().hasHeightForWidth())
        self.toggle_button.setSizePolicy(sizePolicy)
        self.toggle_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/cil-menu.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toggle_button.setIcon(icon)
        self.toggle_button.setIconSize(QtCore.QSize(40, 40))
        self.toggle_button.setObjectName("toggle_button")
        self.verticalLayout_2.addWidget(self.toggle_button)
        self.frame_left = QtWidgets.QFrame(self.centralwidget)
        self.frame_left.setGeometry(QtCore.QRect(2, 108, 74, 635))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_left.sizePolicy().hasHeightForWidth())
        self.frame_left.setSizePolicy(sizePolicy)
        self.frame_left.setMinimumSize(QtCore.QSize(70, 0))
        self.frame_left.setStyleSheet("*{\n"
                                      "   background:grey;\n"
                                      "}")
        self.frame_left.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_left.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_left.setObjectName("frame_left")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_left)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_menu = QtWidgets.QFrame(self.frame_left)
        self.frame_menu.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(70)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_menu.sizePolicy().hasHeightForWidth())
        self.frame_menu.setSizePolicy(sizePolicy)
        self.frame_menu.setMinimumSize(QtCore.QSize(70, 0))
        self.frame_menu.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_menu.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_menu.setObjectName("frame_menu")
        self.layout_menus = QVBoxLayout(self.frame_menu)
        self.layout_menus.setSpacing(0)
        self.layout_menus.setObjectName(u"layout_menus")
        self.layout_menus.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addWidget(self.frame_menu, 0, QtCore.Qt.AlignTop)
        self.frame = QtWidgets.QFrame(self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(70, 85))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/cil-loop-circular.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon1)
        self.pushButton.setIconSize(QtCore.QSize(40, 40))
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_4.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.frame, 0, QtCore.Qt.AlignBottom)
        self.frame_top.raise_()
        self.frame_right.raise_()
        self.frame_toggle.raise_()
        self.frame_left.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1331, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(1)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow",
                                      "                                                                                                 ATTENDANCE"))
        item = self.tableWidget_4.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Child Id"))
        item = self.tableWidget_4.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "First Name"))
        item = self.tableWidget_4.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Last Name"))
        item = self.tableWidget_4.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Date"))
        item = self.tableWidget_4.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Attendance"))
        item = self.tableWidget_4.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Reason Of Absence"))
        self.takeattendancenow.setText(_translate("MainWindow", "TAKE ATTENDANCE"))
        self.saveattendance.setText(_translate("MainWindow", "SAVE"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.takeattendance), _translate("MainWindow",
                                                                                          "                            TAKE ATTENDANCE                            "))
        self.textBrowser.setHtml(_translate("MainWindow",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Select Date</span></p></body></html>"))
        self.pushButton_2.setText(_translate("MainWindow", "SHOW ATTENDANCE"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Child Id"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "First Name"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Last Name"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Attendance"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Reason Of Absence"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.showattendance), _translate("MainWindow",
                                                                                          "                           SHOW ATTENDANCE                           "))
        self.label_2.setText(
            _translate("MainWindow", "                                                          IN AND OUT MOVEMENT"))
        item = self.tableWidget_3.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Id "))
        item = self.tableWidget_3.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Date-Out"))
        item = self.tableWidget_3.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Time-Out"))
        item = self.tableWidget_3.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Date-In"))
        item = self.tableWidget_3.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Time-In"))
        self.show.setText(_translate("MainWindow", "SHOW"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.takeattendance_2), _translate("MainWindow",
                                                                                                "                        TODAYS IN AND OUT DETAIL                   "))
        self.textBrowser_2.setHtml(_translate("MainWindow",
                                              "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                              "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                              "p, li { white-space: pre-wrap; }\n"
                                              "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:6pt; font-weight:400; font-style:normal;\">\n"
                                              "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Select Date</span></p></body></html>"))
        self.showinandout.setText(_translate("MainWindow", "SHOW IN AND OUT"))
        item = self.tableWidget_2.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Id "))
        item = self.tableWidget_2.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Date-Out"))
        item = self.tableWidget_2.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Time-Out"))
        item = self.tableWidget_2.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Date-In"))
        item = self.tableWidget_2.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Time-In"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.showattendance_2), _translate("MainWindow",
                                                                                                "                     SHOW IN AND OUT DETAILS                       "))
        self.label_3.setText(_translate("MainWindow", "CARE"))
