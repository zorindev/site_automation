

from PyQt5.QtCore import pyqtSignal, QObject

from PyQt5 import QtWidgets
from ui import Ui_MainWindow

import sys
import os

from manager import *
import logging

import threading


# global app instance
container = None

class App(QtWidgets.QMainWindow):
    """
    main app window
    """
    
    #logger = Logger("c:\\temp\\price_bot.log").get_logger()
    
    # params to init bot with
    params = []
    
    username = ""
    password = ""
    
    selected_site = ""
    selected_exec_type = ""
    selected_frequency = ""
    
    thresh = ""
    
    bot_state = "off"
    
    
    def __init__(self):
        """
        constructor
        """
        
        
        logging.debug(" init apps ")
        
        # ui init
        super(App, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.mgr = Manager(self.ui)
        
        self.selected_google_auth_file = self.ui.get_google_auth_file_name()
        
        # init starting events
        self.ui.activateButton.setEnabled(False)
        self.ui.deactivateButton.setEnabled(False)
        self.ui.refreshButton.setEnabled(False)
        self.ui.activateButton.clicked.connect(self.mgr.activate)
        self.ui.deactivateButton.clicked.connect(self.mgr.deactivate)
        self.ui.quitButton.clicked.connect(self.quit)
        
        self.ui.refreshButton.clicked.connect(self.refresh)
        
        # init and make selections
        self.ui.cmbbox_site.activated[str].connect(self.on_site_select)
        self.ui.exec_type_box.activated[str].connect(self.on_exec_type_select)
        self.ui.cmbbox_freq.activated[str].connect(self.on_frequency_select)
        
        
    def capture_thresh(self):
        """
        capture threshold
        """
        
        print(" *** IN CAPTURE REFRESH ")
        thresh_val = self.ui.reduct_field.text()
        
        if(isinstance(thresh_val, str)):
            if(thresh_val.isdigit()):
                if(isinstance(int(thresh_val), int)):
                    
                    if(int(thresh_val) >= 0 and int(thresh_val) <= 100):
                        self.thresh = thresh_val
                    else:
                        logging.error("frequency must be greater than zero")
                        self.reset_form()
                else:
                    logging.error("frequency is not numeric")
                    self.reset_form()
            else:
                logging.error("frequency is not numeric")
                self.reset_form()
        else:
            logging.error("frequency is not numeric")
            self.reset_form()
        
        
        
    def refresh(self):
        """
        tries to re-init the bot
        """
        
        print(" *** IN REFRESH ")
        self.ui.activateButton.setEnabled(False)
        self.params = []
        self.capture_thresh()
        self.enable_buttons()
        
        
    def on_site_select(self, site):
        """
        selecting site
        """
        self.selected_site = site
        if(self.bot_state == "off"):
            self.capture_thresh()
            self.enable_buttons()
        else:
            self.ui.refreshButton.setEnabled(True)
            self.ui.activateButton.setEnabled(False)
            self.bot_state = "off"
        
        
    def on_exec_type_select(self, exec_type):
        """
        exec type select
        """
        self.selected_exec_type = exec_type
        if(self.bot_state == "off"):
            self.capture_thresh()
            self.enable_buttons()
        else:
            self.ui.refreshButton.setEnabled(True)
            self.ui.activateButton.setEnabled(False)
            self.bot_state = "off"
        
        
    def on_frequency_select(self, freq):
        """
        frequency select
        """
        
        self.selected_frequency_type = freq
        if(self.bot_state == "off"):
            self.frequency = str(self.ui.freq_value_box.text())
            
            if(isinstance(self.frequency, str)):
                if(self.frequency.isdigit()):
                    if(isinstance(int(self.frequency), int)):
                        
                        if(int(self.frequency) > 0):
                                
                            self.capture_thresh()
                            self.enable_buttons()
                        else:
                            logging.error("frequency must be greater than zero")
                            self.ui.reduct_field.setText("")
                    else:
                        logging.error("frequency is not numeric")
                        self.ui.reduct_field.setText("")
                else:
                    logging.error("frequency is not numeric")
                    self.ui.reduct_field.setText("")
            else:
                logging.error("frequency is not numeric")
                self.ui.reduct_field.setText("")
        else:
            self.ui.refreshButton.setEnabled(True)
            self.ui.activateButton.setEnabled(False)
            self.bot_state = "off"
        
                
    def reset_form(self):
        """
        reset freq 
        """
        
        #self.capture_thresh()
        self.ui.freq_value_box.setText("")
        self.ui.cmbbox_freq.setCurrentIndex(0)
        
        
        
    def enable_buttons(self):
        """
        enable buttons
        """
        
        try:
            print(" *** ENABLING BUTTONS ")
            if(self.selected_exec_type != "" and self.selected_frequency_type != "" and self.selected_site != ""):
                
                self.username = self.ui.username_field.text()
                self.password = self.ui.password_field.text()   
                self.frequency = self.ui.freq_value_box.text()
                
                self.params.append(self.username)
                self.params.append(self.password)
                self.params.append(self.selected_site)
                self.params.append(self.selected_frequency_type)
                self.params.append(self.frequency)
                self.params.append(self.selected_exec_type)
                self.params.append(self.selected_google_auth_file)
                self.params.append(self.thresh)
                
                #self.ui.refreshButton.setEnabled(False)
                
                print(self.params)
                
                self.mgr.init_bot(self.params)
                self.bot_state = "on"
                
            else:
                
                print(" CANNOT ENABLE ")
                
                
        except Exception as e:
                
            print(" *** EXCEPTION WHEN ENABLING ")
            print(e)
            
            self.ui.refreshButton.setEnabled(True)
            self.ui.activateButton.setEnabled(False)
            logging.debug(e)
            
        
            
    
    def quit(self):
        
        self.mgr.deactivate()
        sys.exit()
        
    
    
    
if __name__ == "__main__":
    """
    instantiates app
    """
    
    container = QtWidgets.QApplication([])
    app = App()
    app.show()
    
    sys.exit(container.exec())

