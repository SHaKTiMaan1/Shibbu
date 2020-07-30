## ==> GUI FILE
import pickle
from datetime import datetime
from inandout_track.FaceRecognition import *
from faceblinkdetection.FaceRecognition import *
from main import *

## ==> APP FUNCTIONS
from app_functions import *

## ==> GLOBALS
GLOBAL_STATE = 0
GLOBAL_TITLE_BAR = True

## ==> COUT INITIAL MENU
count = 1

class UIFunctions(MainWindow):

    ## ==> GLOBALS
    GLOBAL_STATE = 0
    GLOBAL_TITLE_BAR = True

    ########################################################################
    ## START - GUI FUNCTIONS
    ########################################################################

    ## ==> MAXIMIZE/RESTORE
    ########################################################################
    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE
        if status == 0:
            self.showMaximized()
            GLOBAL_STATE = 1
            self.ui.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.ui.btn_maximize_restore.setToolTip("Restore")
            self.ui.btn_maximize_restore.setIcon(QtGui.QIcon(u":/16x16/icons/16x16/cil-window-restore.png"))
            self.ui.frame_top_btns.setStyleSheet("background-color: rgb(27, 29, 35)")
            self.ui.frame_size_grip.hide()
        else:
            GLOBAL_STATE = 0
            self.showNormal()
            self.resize(self.width()+1, self.height()+1)
            self.ui.horizontalLayout.setContentsMargins(10, 10, 10, 10)
            self.ui.btn_maximize_restore.setToolTip("Maximize")
            self.ui.btn_maximize_restore.setIcon(QtGui.QIcon(u":/16x16/icons/16x16/cil-window-maximize.png"))
            self.ui.frame_top_btns.setStyleSheet("background-color: rgba(27, 29, 35, 200)")
            self.ui.frame_size_grip.show()

    ## ==> RETURN STATUS
    def returStatus():
        return GLOBAL_STATE

    ## ==> SET STATUS
    def setStatus(status):
        global GLOBAL_STATE
        GLOBAL_STATE = status

    ## ==> ENABLE MAXIMUM SIZE
    ########################################################################
    '''def enableMaximumSize(self, width, height):
        if width != '' and height != '':
            self.setMaximumSize(QSize(width, height))
            self.ui.frame_size_grip.hide()
            self.ui.btn_maximize_restore.hide()'''

    ## ==> SET TITLE BAR
    ########################################################################
    def removeTitleBar(status):
        global GLOBAL_TITLE_BAR
        GLOBAL_TITLE_BAR = status

    ## ==> HEADER TEXTS
    ########################################################################
    # LABEL TITLE
    def labelTitle(self, text):
        self.ui.label_title_bar_top.setText(text)

    # LABEL DESCRIPTION
    def labelDescription(self, text):
        self.ui.label_top_info_1.setText(text)

    ## ==> DYNAMIC MENUS
    ########################################################################
    def addNewMenu(self, name, objName, icon, isTopMenu):
        font = QFont()
        font.setFamily(u"Century Schoolbook")
        font.setPointSize(12)
        button = QPushButton(str(count),self)
        button.setObjectName(objName)
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy3)
        button.setMinimumSize(QSize(0, 70))
        button.setLayoutDirection(Qt.LeftToRight)
        button.setFont(font)
        button.setStyleSheet(Style.style_bt_standard.replace('ICON_REPLACE', icon))

        button.setText(name)
        button.setToolTip(name)
        button.clicked.connect(self.Button)
        
        self.ui.layout_menus.addWidget(button)

    ## ==> SELECT/DESELECT MENU
    ########################################################################
    ## ==> SELECT
    def selectMenu(getStyle):
        select = getStyle + ("QPushButton { border-right: 7px solid white }")
        return select

    ## ==> DESELECT
    def deselectMenu(getStyle):
        deselect = getStyle + ("QPushButton { border-right: 7px solid rgb(44, 49, 60); }")
        return deselect

    ## ==> START SELECTION
    def selectStandardMenu(self, widget):
        for w in self.ui.frame_menus.findChildren(QPushButton):
            if w.objectName() == widget:
                w.setStyleSheet(UIFunctions.selectMenu(w.styleSheet()))

    ## ==> RESET SELECTION
    def resetStyle(self, widget):
        for w in self.ui.frame_menus.findChildren(QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(UIFunctions.deselectMenu(w.styleSheet()))

    ## ==> CHANGE PAGE LABEL TEXT
    def labelPage(self, text):
        newText = '| ' + text.upper()
        self.ui.label_top_info_2.setText(newText)

    ########################################################################
    ## END - GUI FUNCTIONS
    ########################################################################
    ## START OF ADDING FUNCTION TO BUTTONS
    ########################################################################
    ''' To check in and out detail datewise'''
    def inandout(self):
        vr_date = self.ui.dateEdit_4.date()
        vr1_date = vr_date.toPyDate()
        picked_date = vr1_date.strftime('%d-%m-%Y')
        conn = sqlite3.connect('child.db')
        c = conn.cursor()
        query = '''SELECT C_Id, DATE_out, TIME_out, DATE_in, TIME_in  FROM in_and_out WHERE DATE_out =?'''
        result = c.execute(query, (picked_date, ))
        self.ui.tableWidget_4.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.ui.tableWidget_4.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.tableWidget_4.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

        conn.close()

    ''' To display the in and out detail of current day'''
    ###################################################################################################
    def inandouttoday(self):
        conn = sqlite3.connect('child.db')  # Replace it to child.db
        c = conn.cursor()
        now = datetime.now()
        today_date = now.strftime('%d-%m-%Y')
        global running
        running = True
        while running:
            # give the loop a stoppable condition
            (model, face_detector, open_eyes_detector, left_eye_detector, right_eye_detector, video_capture, images,
             source_resolution) = init()

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

            query = (
                '''SELECT C_Id, DATE_out, TIME_out, DATE_in, TIME_in  FROM in_and_out WHERE DATE_out =?''')
            result = c.execute(query, (today_date,))
            self.ui.tableWidget_3.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.ui.tableWidget_3.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.ui.tableWidget_3.setItem(row_number, column_number,
                                               QtWidgets.QTableWidgetItem(str(data)))

     ########################################################################################################################

    ''' Message box to save attendance and stopping the process of taking attendance'''

    def attendancestopped(self):
        mess = QtWidgets.QMessageBox()
        mess.setWindowTitle("Attendance Saved")
        mess.setText("Today Attendance is saved.")
        mess.setStandardButtons(QtWidgets.QMessageBox.Ok)
        mess.exec()

    ''' Message box to save in/out and stopping the process of taking in/out'''

    def inandoutstopped(self):
        mess = QtWidgets.QMessageBox()
        mess.setWindowTitle("IN/OUT Saved")
        mess.setText("Today IN/OUT is saved.")
        mess.setStandardButtons(QtWidgets.QMessageBox.Ok)
        mess.exec()

    ''' To display the attendance of picked date'''

    def showattendancedetail(self):
        vr_date = self.ui.dateEdit_5.date()
        vr1_date = vr_date.toPyDate()
        picked_date = vr1_date.strftime('%d-%m-%Y')
        conn = sqlite3.connect('child.db')
        c = conn.cursor()
        query = '''Select  C_ID, FNAME, LNAME, Attend, ROA FROM attendance NATURAL JOIN  details WHERE DATE =?'''
        result = c.execute(query, (picked_date,))
        self.ui.tableWidget_6.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.ui.tableWidget_6.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.tableWidget_6.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
        conn.close()

    #####################################################################################################
    def takeattendance(self):
        conn = sqlite3.connect('child.db')  # Replace it to child.db
        c = conn.cursor()
        now = datetime.now()
        today_date = now.strftime('%d-%m-%Y')
        global running
        running = True
        while running:
            (model, face_detector, open_eyes_detector, left_eye_detector, right_eye_detector, video_capture, images,
             source_resolution) = init()

            with open('dataset_faces.dat', 'rb') as f:
                known_encodings = pickle.load(f)
            with open('dataset_c_ids.dat', 'rb') as f:
                known_c_ids = pickle.load(f)
            data = {"encodings": known_encodings, "c_ids": known_c_ids}

            # f = open("faceblinkdetection/encoding.txt", "w+")
            # f.write(str(data["encodings"]))
            # f.close()

            # overlay image (eye clipart) width: 100, height: 40
            img_overlay = cv2.imread('faceblinkdetection/data/icon_eye_100x40.png')

            eyes_detected = defaultdict(str)
            imshow_label = "Face Liveness Detector - Blinking Eyes (q-quit, p-pause)"
            print("[LOG] Detecting & Showing Images...")

            while True:
                frame = detect_and_display(model, video_capture, face_detector, open_eyes_detector, left_eye_detector,
                                           right_eye_detector, data, eyes_detected, source_resolution)
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
        query = '''Select  C_ID, FNAME, LNAME, Attend, ROA FROM attendance NATURAL JOIN  details WHERE DATE =?'''
        result = c.execute(query, (today_date,))
        self.ui.tableWidget_6.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.ui.tableWidget_6.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.tableWidget_6.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
    ###################################################################################################################



    ## END OF ADDING FUNCTION TO BUTTONS
    ########################################################################
    ########################################################################
    ## START - GUI DEFINITIONS
    ########################################################################

    ## ==> UI DEFINITIONS
    ########################################################################
    def uiDefinitions(self):
        def dobleClickMaximizeRestore(event):
            # IF DOUBLE CLICK CHANGE STATUS
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                QtCore.QTimer.singleShot(250, lambda: UIFunctions.maximize_restore(self))

        ## REMOVE ==> STANDARD TITLE BAR
        if GLOBAL_TITLE_BAR:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.ui.frame_label_top_btns.mouseDoubleClickEvent = dobleClickMaximizeRestore
        else:
            self.ui.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.ui.frame_label_top_btns.setContentsMargins(8, 0, 0, 5)
            self.ui.frame_label_top_btns.setMinimumHeight(42)
            self.ui.frame_icon_top_bar.hide()
            self.ui.frame_btns_right.hide()
            self.ui.frame_size_grip.hide()


        ## SHOW ==> DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.ui.frame_main.setGraphicsEffect(self.shadow)

        ## ==> RESIZE WINDOW
        self.sizegrip = QSizeGrip(self.ui.frame_size_grip)
        self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")

        ### ==> MINIMIZE
        self.ui.btn_minimize.clicked.connect(lambda: self.showMinimized())

        ## ==> MAXIMIZE/RESTORE
        self.ui.btn_maximize_restore.clicked.connect(lambda: UIFunctions.maximize_restore(self))

        ## SHOW ==> CLOSE APPLICATION
        self.ui.btn_close.clicked.connect(lambda: self.close())


        self.ui.showinandout_2.clicked.connect(lambda: UIFunctions.showattendancedetail(self))
        self.ui.showinandout.clicked.connect(lambda: UIFunctions.inandout(self))
        self.ui.show_4.clicked.connect(lambda: UIFunctions.inandoutstopped(self))
        self.ui.show.clicked.connect(lambda: UIFunctions.inandouttoday(self))
        self.ui.show_3.clicked.connect(lambda: UIFunctions.attendancestopped(self))
        self.ui.show_2.clicked.connect(lambda: UIFunctions.takeattendance(self))
    ########################################################################
    ## END - GUI DEFINITIONS
    ########################################################################
