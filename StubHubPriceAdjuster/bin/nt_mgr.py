
import sys
import tempfile
import subprocess
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal

from notifier import *
from sheet import Sheet
import os
import logging 
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QObject

class NtMgr(QThread):
    
    """
    manages instantiation of google services
    
    bot constructor calls the thread start and waits for the signal
    
    once the signal is done bot constructor gets the inited sheet and notifier objects from NtMgr and enables controls
    
    """
    
    # the ui link
    ui = None
    
    # signal to exit thread
    nt_ready_signal = pyqtSignal()
    
    # notifier instance
    ntfr = None
    
    # sheet instance
    sheet = None
    
    
    def __init__(self, ui = None, signal_callback = None, auth_file = ""):
        """
        init
        """
        QThread.__init__(self)
        
        self.ui = ui
        self.nt_ready_signal.connect(signal_callback)
    
    
    def run(self):
        """
        initialize sheets and notifier
        """
        
        
                
        try:
            logging.info("\nOpening notification sheet ... ")
            self.ntfr = Notifier(auth_file = self.ui.get_google_auth_file_name())
        
            logging.info("\nOpening the tracking sheet ... ")        
            if(self.ui.get_google_auth_file_name() != ""):
                self.sheet = Sheet(auth_file_name = self.ui.get_google_auth_file_name())
            else:
                self.sheet = Sheet()
                
            
            self.sheet.open_sheet()
            
            
            # get back to caller from this thread
            self.nt_ready_signal.emit()
            
            #self.ui.activateButton.setEnabled(True)
            #self.ui.deactivateButton.setEnabled(False)
            
        except Exception as e:
            
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            
            logging.error(" An issue occurred while initializing network components ")
            logging.error(e)
            
            #self.ui.activateButton.setEnabled(False)
            #self.ui.refreshButton.setEnabled(True)
            
            self.nt_ready_signal.emit()
    
    
    def get_inited_objects(self):
        """
        get the objects
        """
        
        return self.ntfr, self.sheet
    
