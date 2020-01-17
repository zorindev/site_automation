from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineView


from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QTextEdit, QAction, QMenu, QLabel, QDialog, QInputDialog, QLineEdit, QFileDialog


from PyQt5 import QtCore, QtGui, QtWidgets

import logging
from logging.handlers import RotatingFileHandler

import sys, os


class CustomLineEdit(QtWidgets.QLineEdit):

    clicked = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()
        
        

class QTextEditLogger(logging.Handler):
    """
    text box that is also a logging handler
    """
    
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        

    def emit(self, record):
        
        self.widget.moveCursor(QTextCursor.End)
        
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        QApplication.processEvents()
        
        
class OptionsPopup(QDialog):
    """
    options dialog
    """
    
    auth_file = ""
    
    def __init__(self, name, parent_cntr, parent_app):
        """
        init
        """
        
        self.parent_cntr = parent_cntr
        self.parent_app = parent_app
        
        super().__init__(self.parent_cntr)
        self.setObjectName("Options")
        self.setWindowTitle("Options")
        
        
        auth_label = QtWidgets.QLabel(self)
        auth_label.setGeometry(QtCore.QRect(10, 20, 300, 20))
        auth_label.setObjectName("label")
        auth_label.setText("Specify Google Credentials JSON File")
        
        self.auth_file_name_field = QtWidgets.QLineEdit(self)
        #self.auth_file_name_field = CustomLineEdit(self)
        self.auth_file_name_field.setGeometry(QtCore.QRect(10, 50, 300, 22))
        self.auth_file_name_field.setObjectName("authfilename")
        
        self.google_auth_button_slct = QtWidgets.QPushButton(self)
        self.google_auth_button_slct.setGeometry(QtCore.QRect(320, 50, 71, 23))
        self.google_auth_button_slct.setObjectName("gglAutBtnSlct")
        self.google_auth_button_slct.setText("Select")
        self.google_auth_button_slct.clicked.connect(self.open_google_auth_file)
        
        self.google_auth_button_apply = QtWidgets.QPushButton(self)
        self.google_auth_button_apply.setGeometry(QtCore.QRect(410, 50, 71, 23))
        self.google_auth_button_apply.setObjectName("gglAutBtnApply")
        self.google_auth_button_apply.setText("Apply")
        self.google_auth_button_apply.setEnabled(False)
        self.google_auth_button_apply.clicked.connect(self.persist_google_auth_setting)
        
        
        log_label = QtWidgets.QLabel(self)
        log_label.setGeometry(QtCore.QRect(10, 100, 300, 20))
        log_label.setObjectName("label")
        log_label.setText("Specify log file destination and name")
        
        self.log_file_name_field = QtWidgets.QLineEdit(self)
        #self.log_file_name_field = CustomLineEdit(self)
        self.log_file_name_field.setGeometry(QtCore.QRect(10, 130, 300, 22))
        self.log_file_name_field.setObjectName("logfilename")
        
        self.log_button_slct = QtWidgets.QPushButton(self)
        self.log_button_slct.setGeometry(QtCore.QRect(320, 130, 71, 23))
        self.log_button_slct.setObjectName("LogBtnSlct")
        self.log_button_slct.setText("Select")
        self.log_button_slct.clicked.connect(self.select_log_destination)
        
        
        self.log_button_apply = QtWidgets.QPushButton(self)
        self.log_button_apply.setGeometry(QtCore.QRect(410, 130, 71, 23))
        self.log_button_apply.setObjectName("LogBtnApply")
        self.log_button_apply.setText("Apply")
        self.log_button_apply.setEnabled(False)
        self.log_button_apply.clicked.connect(self.save_log_destination_settings)
        
        
        self.quitButton = QtWidgets.QPushButton(self)
        self.quitButton.setGeometry(QtCore.QRect(570, 460, 71, 23))
        self.quitButton.setObjectName("quitButton")
        self.quitButton.setText("Close")
        self.quitButton.clicked.connect(self.close)
        
        
    def select_log_destination(self):
        """
        selects log destination
        """
        
        self.new_log_file = ""
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name = QFileDialog.getSaveFileName(self, "Specify log file name", "", "All (*.log)", options=options)
        
        if(len(file_name) > 0):
            self.new_log_file = file_name[0]
            self.log_file_name_field.setText(file_name[0])
            self.log_button_apply.setEnabled(True)
        
        
    def save_log_destination_settings(self):
        """
        saves log settings
        """
        
        if(self.new_log_file != ""):
            self.parent_app.add_file_logger(self.new_log_file)
            self.log_button_apply.setEnabled(False)
            logging.debug(" changing the log file ")
            
            
    def open_google_auth_file(self):
        """
        points to the abs location of the google auth file
        """
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Google Auth File", "", "JSON Files (*.json)", options=options)
        if file_name:
            self.auth_file = file_name
            self.google_auth_button_apply.setEnabled(True)
            self.auth_file_name_field.setText(self.auth_file)
        else:
            self.google_auth_button_apply.setEnabled(False)
        
            
            
    def persist_google_auth_setting(self):
        """
        persisting google auth settings
        """
        
        logging.info("\nSelected Google Auth file: " + str(self.auth_file))
        self.parent_app.persist_google_account(self.auth_file)
        self.google_auth_button_apply.setEnabled(False)


class Ui_MainWindow(object):
    
    google_auth_file_name = ""
    
    log_file_dir = "c:\\temp\\"
    log_file_name = "priceupdater.log"
    
    size_ranges_h = {
        900: 832,
        1152: 1075,
    }
    
    size_ranges_w = {
        1600: 1593,
        2048: 1900
    }
    
    
    def determin_window_size(self):
        """
        """
        x = 832
        y = 1593
        
        try:
            size = QtWidgets.QDesktopWidget().screenGeometry(-1)
            height_idx = int(size.height())
            width_idx = int(size.width())
            if(height_idx in self.size_ranges_h and width_idx in self.size_ranges_w):
                x = int(self.size_ranges_h[height_idx])
                y = int(self.size_ranges_w[width_idx])
            else:
                logging.error(" unable to select window size . defaulting to " + str(x) + " by " + str(y))
                
        except Exception as e:
            logging.error(" unable to select window size . defaulting to " + str(x) + " by " + str(y))
            logging.debug(e)
            
        return x, y
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("StubHub Price Bot")
        
        wx, wy = self.determin_window_size()
        #MainWindow.resize(1593, 832)
        MainWindow.resize(wy, wx)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.activateButton = QtWidgets.QPushButton(self.centralwidget)
        self.activateButton.setGeometry(QtCore.QRect(10, 770, 61, 23))
        self.activateButton.setObjectName("activateButton")
        
        self.deactivateButton = QtWidgets.QPushButton(self.centralwidget)
        self.deactivateButton.setGeometry(QtCore.QRect(80, 770, 61, 23))
        self.deactivateButton.setObjectName("deactivateButton")
        
        
        self.refreshButton = QtWidgets.QPushButton(self.centralwidget)
        self.refreshButton.setGeometry(QtCore.QRect(150, 770, 71, 23))
        self.refreshButton.setObjectName("refreshButton")
        
        
        self.quitButton = QtWidgets.QPushButton(self.centralwidget)
        self.quitButton.setGeometry(QtCore.QRect(230, 770, 71, 23))
        self.quitButton.setObjectName("quitButton")
        
        self.cmbbox_site = QtWidgets.QComboBox(self.centralwidget)
        self.cmbbox_site.setGeometry(QtCore.QRect(70, 20, 151, 22))
        self.cmbbox_site.setObjectName("cmbboxSite")
        self.cmbbox_site.addItem("")
        self.cmbbox_site.addItem("https://stubhub.jp/")
        self.cmbbox_site.addItem("https://intl.stubhub.com")
        
        #self.username_field = QtWidgets.QLineEdit(self.centralwidget)
        self.username_field = CustomLineEdit(self.centralwidget)
        self.username_field.setGeometry(QtCore.QRect(70, 60, 151, 20))
        self.username_field.setObjectName("usernameField")
        
        
        #self.password_field = QtWidgets.QLineEdit(self.centralwidget)
        self.password_field = CustomLineEdit(self.centralwidget)
        self.password_field.setGeometry(QtCore.QRect(70, 90, 151, 21))
        self.password_field.setObjectName("passwordField")
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 51, 16))
        self.label.setObjectName("label")
        
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 47, 13))
        self.label_2.setObjectName("label_2")
        
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 90, 47, 13))
        self.label_3.setObjectName("label_3")
        
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10, 165, 51, 16))
        self.label_4.setObjectName("label_4")
        
        self.price_reduction_lbl = QtWidgets.QLabel(self.centralwidget)
        self.price_reduction_lbl.setGeometry(QtCore.QRect(10, 125, 120, 16))
        self.price_reduction_lbl.setObjectName("price_reduction_lbl")
        
        #self.reduct_field = QtWidgets.QLineEdit(self.centralwidget)
        self.reduct_field = CustomLineEdit(self.centralwidget)
        self.reduct_field.setGeometry(QtCore.QRect(180, 125, 40, 20))
        self.reduct_field.setObjectName("usernameField")
        self.reduct_field.setText("20")
        
            
        feedback_box = QTextEditLogger(self.centralwidget)
        feedback_box.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(feedback_box)
        
        feedback_box.widget.setGeometry(QtCore.QRect(10, 310, 440, 440))
        feedback_box.widget.setObjectName("feedbackBox")
        feedback_box.widget.setReadOnly(True)
        feedback_box.widget.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        feedback_box.widget.moveCursor(QTextCursor.End)
        
        feedback_box.widget.setStyleSheet(
            """
            QPlainTextEdit {background-color: #333345;
                           color: #AAFFDD;
                           font-family: Courier;
                           white-space: nowrap;
                           }
            """
        )
        
        feedback_box.setLevel(logging.INFO)
        self.add_file_logger()

        
        logging.getLogger().setLevel(logging.DEBUG)
        
        logging.info("Welcome\n")
        
        #self.freq_value_box = QtWidgets.QLineEdit(self.centralwidget)
        self.freq_value_box = CustomLineEdit(self.centralwidget)
        self.freq_value_box.setGeometry(QtCore.QRect(70, 165, 41, 20))
        self.freq_value_box.setObjectName("freqValueBox")
        
        self.cmbbox_freq = QtWidgets.QComboBox(self.centralwidget)
        self.cmbbox_freq.setGeometry(QtCore.QRect(140, 165, 81, 22))
        self.cmbbox_freq.setObjectName("cmbbox_freq")
        self.cmbbox_freq.addItem("")
        self.cmbbox_freq.addItem("minute")
        self.cmbbox_freq.addItem("hour")
        self.cmbbox_freq.addItem("day")
        
        self.exec_type_box = QtWidgets.QComboBox(self.centralwidget)
        self.exec_type_box.setGeometry(QtCore.QRect(70, 210, 151, 22))
        self.exec_type_box.setObjectName("execTypeBox")
        self.exec_type_box.addItem("")
        self.exec_type_box.addItem("Test")
        self.exec_type_box.addItem("Live")
        
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(10, 210, 51, 16))
        self.label_5.setObjectName("label_5")
        
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(10, 280, 51, 16))
        self.label_6.setObjectName("label_6")
        
        
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 872, 18))
        self.menubar.setObjectName("menubar")
        
        self.fileMenu = self.menubar.addMenu('File')
        self.optionAction = QAction('Options')
        self.exitAction = QAction('Exit')
        
        
        self.fileMenu.addAction(self.optionAction)
        self.fileMenu.addAction(self.exitAction)
        
        self.exitAction.triggered.connect(sys.exit)
        self.optionAction.triggered.connect(self.show_options)
        
        
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        
        # get screen resolution
        self.web_view = QWebEngineView(self.centralwidget)
        #self.web_view = QWebEngineView()
        profile = QWebEngineProfile(self.web_view)
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36")
        webpage = QWebEnginePage(profile, self.web_view)
        self.web_view.setPage(webpage)
        
        self.web_view.setGeometry(QtCore.QRect(470, 20, 1100, 800))
        self.web_view.setObjectName("webContainer")
        self.web_view.setUrl(QtCore.QUrl("about:blank"))
        self.web_view.show()
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        
        return os.path.join(os.path.abspath("."), relative_path)
    
    def add_file_logger(self, file_name = "./priceupdater.log"):
        """
        add file logger
        """
        
        
        # drop file loggers
        logging.getLogger().handlers = [h for h in logging.getLogger().handlers if not isinstance(h, RotatingFileHandler)]
        
        # create file logger based on name
        file_handler = RotatingFileHandler(self.resource_path(file_name), maxBytes=(1024*1000), backupCount=5)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        file_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(file_handler)
    
        
        
    def show_options(self, event):
        """
        pop up options
        """
        
        options_dialog = OptionsPopup("Options", self.centralwidget, self)
        options_dialog.setGeometry(175, 200, 700, 500)
        options_dialog.setFixedSize(options_dialog.size())
        options_dialog.show()
        
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("StubHub Price Bot", "StubHub Price Bot"))
        self.activateButton.setText(_translate("StubHub Price Bot", "Activate"))
        self.deactivateButton.setText(_translate("StubHub Price Bot", "Deactivate"))
        self.quitButton.setText(_translate("StubHub Price Bot", "Quit"))
        self.refreshButton.setText("Refresh")
        self.refreshButton.setEnabled(False)
        
        self.label.setText(_translate("StubHub Price Bot", "Select Site"))
        self.label_2.setText(_translate("StubHub Price Bot", "Username"))
        self.label_3.setText(_translate("StubHub Price Bot", "Password"))
        self.label_4.setText(_translate("StubHub Price Bot", "Frequency"))
        
        self.label_5.setText(_translate("StubHub Price Bot", "Exec type"))
        self.label_6.setText(_translate("StubHub Price Bot", "Output"))
        
        self.price_reduction_lbl.setText(_translate("StubHub Price Bot", "Price Threshhold %"))
        
        
    def persist_google_account(self, file_name):
        """
        sets google auth file name in parent
        """
        self.google_auth_file_name = file_name
        
        
    def get_google_auth_file_name(self):
        """
        returns it
        """
        return self.google_auth_file_name
    