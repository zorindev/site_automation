
from PyQt5 import QtTest
from bot import *
from util import *

import logging

import datetime


from PyQt5.QtCore import pyqtSignal, QObject

import time

class Manager(QObject):
    """
    Manager class. Responsible for trigerring Bot.run continuously.
    """
    
    ready_signal = pyqtSignal()
    
    state = 0
    
    number_of_runs = 0
    last_run_timestamp = None
    
    selected_frequency_type = None
    frequency = 0
    
    bot = None
    
    
    def __init__(self, ui):
        """
        inits 
        """
        
        QObject.__init__(self)
        
        self.ui = ui
        self.util = Util()
        
        
    def init_bot(self, params):
        """
        init bot
        """
        
        print(" GOT TOT INIT BOT ")
        logging.debug(" init bot ")
        self.params = params
        
        self.bot = Bot(params, self)
        
        #if(self.bot == None):
        #    self.bot = Bot(params, self)
        #else:
        #    self.bot.update_params(params)
        
        
    def delay(self, frq):
        """
        sleep
        """
        
        loop = QEventLoop()
        QTimer.singleShot(frq, loop.quit)
        loop.exec_()
        
        
    def activate(self):
        """
        sets the state to 1 - active
        """
        
        self.state = 1
        self.bot.update_params(self.params)
        self.ui.activateButton.setEnabled(False)
        self.ui.refreshButton.setEnabled(False)
        self.ui.deactivateButton.setEnabled(True)
        
        # deactivate the input form
        self.ui.fileMenu.setEnabled(False)
        self.ui.cmbbox_site.setEnabled(False)
        self.ui.username_field.setEnabled(False)
        self.ui.password_field.setEnabled(False)
        self.ui.reduct_field.setEnabled(False)
        self.ui.freq_value_box.setEnabled(False)
        self.ui.cmbbox_freq.setEnabled(False)
        self.ui.exec_type_box.setEnabled(False)
        
        
        logging.debug(" in manager.activate connecting self.ready_signal.connect(self.ready)")
        self.ready_signal.connect(self.ready)
        
        self.last_run_timestamp = int(time.time())
        self.bot.run()
            
     
    
    def run_again(self):
        """
        run again
        """
        
        try:
            self.ui.web_view.loadFinished.disconnect(self.run_again)
            logging.debug(" in manager.run_again disconnecting self.ui.web_view.loadFinished.disconnect(self.run_again) ")
        except Exception as e:
            logging.debug(" in manager.run_again disconnecting self.ui.web_view.loadFinished.disconnect(self.run_again) ")
        
        wait_period = self.util.get_waiting_period(frq = self.params[4], frq_type = self.params[3])
        
        next_start_time = datetime.datetime.now()
        next_start_time = next_start_time + datetime.timedelta(0, wait_period)
        next_start_time = next_start_time.strftime('%Y-%m-%d %H:%M:%S')
        logging.info("\n next run will start in " + str(wait_period) + " seconds ... ( at " + str(next_start_time) + ")")
        self.delay(wait_period * 1000)
        
        if(self.state == 1):          
            self.bot.run()
        
        
        
    def ready(self):
        """
        ready to run again
        """
        
        # events are done processing in process_listsings3 and control returns here
        try:
            logging.debug(" in ready disconnecting self.ui.web_view.loadFinished.disconnect(self.bot.process_listings) ")
            self.ui.web_view.loadFinished.disconnect(self.bot.process_listings)
        except:
            pass
        
        # events are done processing in process_listsings3 and control returns here
        try:
            logging.debug(" in ready disconnecting self.ui.web_view.loadFinished.disconnect(self.bot.process_listings_0) ")
            self.ui.web_view.loadFinished.disconnect(self.bot.process_listings_0)
        except:
            pass
        
        # events are done processing in process_listsings3 and control returns here
        try:
            logging.debug(" in ready disconnecting self.ui.web_view.loadFinished.disconnect(self.bot.process_listings_0_0) ")
            self.ui.web_view.loadFinished.disconnect(self.bot.process_listings_0_0)
        except:
            pass
        
        if(self.state == 1):
            self.ui.web_view.loadFinished.connect(self.run_again)
            self.ui.web_view.load(QUrl("about:blank"))
            
        else:
            logging.debug("deactivated becasue state was not 1")
            self.deactivate()
            
        
    def deactivated(self):
        """
        park
        """
        
        logging.info("\nThe bot has been deactivated.\n")
        self.ui.web_view.loadFinished.disconnect(self.deactivated)
        self.ui.deactivateButton.setEnabled(False)
        self.ui.refreshButton.setEnabled(True)
        
    
    
    def deactivate(self):
        """
        deactivates the bot - 0
        """    
        logging.info("\nDeactivating bot ... \n")
        
        try:
            self.ui.web_view.loadFinished.disconnect(self.run_again)
        except:
            logging.debug(" in manager.deactivate disconnecting self.ui.web_view.loadFinished.disconnect(self.run_again) ")
        
        try:
            self.ready_signal.disconnect(self.ready)
        except Exception as e:
            logging.debug(" in manager.deactivate disconnecting self.ready_signal.disconnect(self.ready) ")
            
        try:
            self.ui.web_view.loadFinished.disconnect(self.bot.process_listings)
        except Exception as e:
            logging.debug(" in manager.deactivate disconnecting self.ui.web_view.loadFinished.disconnect(self.bot.process_listings) ")
            
        self.ui.activateButton.setEnabled(True)
        self.state = 0
        
        try:
            self.bot.stop()
        except:
            logging.debug(" bot was not initialized and a stop call was made ")
        
        self.ui.web_view.loadFinished.connect(self.deactivated)
        self.ui.web_view.load(QUrl("about:blank"))
        
        self.ui.fileMenu.setEnabled(True)
        self.ui.cmbbox_site.setEnabled(True)
        self.ui.username_field.setEnabled(True)
        self.ui.password_field.setEnabled(True)
        self.ui.reduct_field.setEnabled(True)
        self.ui.freq_value_box.setEnabled(True)
        self.ui.cmbbox_freq.setEnabled(True)
        self.ui.exec_type_box.setEnabled(True)