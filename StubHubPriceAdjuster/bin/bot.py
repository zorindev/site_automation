
import os
import sys
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PyQt5.QtCore import pyqtSignal, QObject
from listings_handler import ListingsHandler

import logging

from util import Util
import unicodedata
from bs4 import BeautifulSoup

import io

from notifier import *
from sheet import Sheet
from nt_mgr import *
import nt_mgr

global_counter = 0



class Bot(QObject):
    """
    BOT class. contains reference to UI and the main logic
    """

    #sheet = Sheet()
    
    ntfr = None
    
    process_listings_2_fail_counter = 0
    max_fails = 10
    
    min_update_by_currency = {
        "JPY": 1,
    }
    
    MIN_ADJUST = 0.01
    PRCT_THRESH = 20
    
    logged_in = 0

    # signals
    login_signal = pyqtSignal()
    next_event_signal = pyqtSignal()
    update_price_signal = pyqtSignal()
    
    # html string
    htmlstr = ""
    
    # active events list
    active_events_list = []
    
    # active sheet tickets 
    active_sheet_tickets = {}
    active_sheet_events = []
    
    # number of events
    event_count = 0
    event_click_index = -1
    
    # ticket list - expecting to populate this per event
    ticket_list = []
    ticket_category_list = []
    ticket_reference_list = []
    ticket_count_list = []
    
    ticket_index = -1
    ticket_price_list = {}
    competitor_price_list = {}
    competitor_price_list_counts = {}
    
    current_currency = ""
    
    # sensor to open and close event sections
    open_event_section = False
    
    site = ""
    username = ""
    password = ""
    mode = ""
    frequency = 0
    frequency_type = ""
    
    
    # wait for network termination flag
    network_services_have_been_enabled = False
    nt_mgr = None
    
    

    def __init__(self, params = None, manager = None):
        """
        init 
        """
    
        print(" WE ARE IN BOT CONSTRUCTOR ")
        if(params and manager):   
            QObject.__init__(self)
            
            self.util = Util()
            self.manager = manager
            
            self.ready_signal = self.manager.ready_signal
            self.ui = self.manager.ui
            self.update_params(params)
            
            # link the control for Test/Live
            
            if(params[5] == "Test"):
                self.exec_type = "paused"
            else:
                self.exec_type = "ok"
            
            
            self.nt_mgr = NtMgr(self.ui, self.connect_network_services_and_enable)
            self.nt_mgr.start()
            
            """
            logging.info(" opening the tracking sheet")
                    
            try:
                if(self.ui.get_google_auth_file_name() != ""):
                    self.sheet = Sheet(auth_file_name = self.ui.get_google_auth_file_name())
                else:
                    self.sheet = Sheet()
                    
                self.sheet.open_sheet()
                self.ntfr = Notifier()
                
                self.ui.activateButton.setEnabled(True)
                self.ui.deactivateButton.setEnabled(False)
                
            except Exception as e:
                
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.debug(exc_type, fname, exc_tb.tb_lineno)
                logging.debug(e)
                
                logging.error(" An issue occured while initializing bot ")
                logging.error(e)
                
                self.ui.activateButton.setEnabled(False)
                self.ui.refreshButton.setEnabled(True)
                
            """
        
    
    def terminate_attempt_to_connect_network_services(self):
        """
        timeout for nt_mgr connect
        """
    
        pass
    
    def connect_network_services_and_enable(self):
        """
        call back
        """
        
        self.ntfr, self.sheet = self.nt_mgr.get_inited_objects()
        
        if(self.ntfr != None and self.sheet != None):
            self.ui.activateButton.setEnabled(True)
            self.ui.refreshButton.setEnabled(True)
            self.ui.deactivateButton.setEnabled(False)
            
        else:
            self.ui.activateButton.setEnabled(False)
            self.ui.refreshButton.setEnabled(True)
            
            
            
    def update_params(self, params):
        """
        sets params
        """
        
        print(" IN BOT UPDATE_PARAMS ")
        
        self.site = params[2]
        if(".jp" in self.site or ".JP" in self.site):
            self.site = "jp"
        else:
            self.site = "com"
        
        self.username = params[0]
        self.password = params[1]
        self.mode = params[5]
        self.frequency = params[3]
        self.frequency_type = params[4]
        
        if(len(params) == 8):
            try:
                self.PRCT_THRESH = int(params[7])
            except:
                logging.error("\n\tUnable to use the threshold parameter. defaulting to 20% \n")
        
        
    def stop(self):
        """
        stops the exec
        """
        
        logging.info("\nStopping bot ... ")
        try:
            logging.debug("self.update_price_signal.disconnect(self.update_price1)")
            self.update_price_signal.disconnect(self.update_price1)
        except:
            pass
        
        try:
            logging.debug("self.ui.web_view.loadFinished.disconnect(self.login)")
            self.ui.web_view.loadFinished.disconnect(self.login)
        except:
            pass
        
        try:
            logging.debug("self.ui.web_view.loadFinished.disconnect(self.process_listings)")
            self.ui.web_view.loadFinished.disconnect(self.process_listings)
        except:
            pass
        
        try:
            logging.debug("self.next_event_signal.disconnect(self.process_listings3)")
            self.next_event_signal.disconnect(self.process_listings3)
        except:
            pass
            
        self.reset()
        
        #self.manager.state = 0
        #self.ready_signal.emit()
        
        
    def run(self):
        """
        bot runs
        """
        logging.info("\nBot is running ")    
        self.ui.web_view.loadFinished.connect(self.process_listings_0)
        self.url = "https://url." + self.site + "/path"
        logging.info("\nLoading URL: " + self.url)        
        self.ui.web_view.load(QUrl(self.url))
        
        
    def process_listings_0(self, event):
        """
        loads html of the first loaded page
        """
        self.ui.web_view.loadFinished.disconnect(self.process_listings_0)
        self.ui.web_view.page().runJavaScript("document.documentElement.outerHTML", self.process_listings_0_0)
        
        
    def process_listings_0_0(self, html):
        """
        access html of the initial page and evaluate whether it has a login forn
        if it does then go to login
        if it does not then go to processing
        """
        
        soup = BeautifulSoup(html, "html.parser")
        el = soup.select("form#formLogin")

        
        if(len(el) > 0):
            # we need to login
            self.login()
        else:
            self.delay(1000)
            self.process_listings(html)
        
        
    def login(self):
        """
        logs in 
        """
        
        try:
            #logging.debug("self.ui.web_view.loadFinished.disconnect(self.login)")
            #self.ui.web_view.loadFinished.disconnect(self.login)
            logging.debug("self.ui.web_view.loadFinished.connect(self.process_listings_login_verify)")
            self.ui.web_view.loadFinished.connect(self.process_listings_login_verify)
            
            self.ui.web_view.page().runJavaScript("try{document.getElementById(\"loginInput\").setAttribute(\"value\", \"" + self.username + "\");}catch{}")
            self.ui.web_view.page().runJavaScript("try{document.getElementById(\"passwordInput\").setAttribute(\"value\", \"" + self.password + "\");}catch{}")
            self.ui.web_view.page().runJavaScript("try{document.getElementsByClassName(\"button sendButton pull-right\")[0].click();}catch{}", self.set_logged_in)
                
                
        except Exception as e:
        
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            logging.error("\n\tAn issue occured while attemting to log in \n")
            
            #self.stop()
            self.manager.deactivate()
            
            #self.manager.deactivate()
            
            #logging.debug("self.ready_signal.emit()")
            #self.ready_signal.emit()
    
    
    def get_str_of_competitor_prices(self, ticket_id):
        """
        returns str of self competitor prices
        """
        rtn = ""
        
        comp_prices = self.competitor_price_list[ticket_id]
        comp_price_count = self.competitor_price_list_counts[ticket_id]
        
        i = 0
        for entr in comp_prices:
            rtn += str(comp_price_count[i]) + ": " + str(entr) + ", "
            i += 1
        
        return rtn
        
        
    def persist_new_ticket_record(self, ticket_id, fail_forward = False):
        """
        creates a new sheet entry
        """

        
        logging.info("\nRegistering new event: " + str(int(self.current_event_id.replace("'", "").strip())))
        
        try:
            self.login()
            
            new_record = [
                self.site,
                int(self.current_event_id.replace("'", "").strip()),
                "N",
                self.current_event_name,
                str(self.ticket_reference_list[self.ticket_index]),
                int(ticket_id.replace("'", "").strip()),
                str(self.ticket_category_list[self.ticket_index]),
                int(self.ticket_count_list[self.ticket_index]),
                str(self.current_currency),
                0.0,
                0.0,
                str(self.ticket_price_list[ticket_id]),
                'N', 
                'N',
                self.get_str_of_competitor_prices(ticket_id),
                self.util.get_current_date(),
                self.util.get_current_date()
            ]
            
            self.sheet.insert_ticket_record(new_record)
                
        except Exception as e:
            
            logging.debug(" as exception occured ")
            logging.debug(e)

            if(fail_forward == True):
                
                logging.debug(" in persist_new_ticket_record we are going to try to call this methoid again ")
                self.sheet.login()
                self.persist_new_ticket_record(ticket_id, False)
                
            else:
                
                logging.debug(" the method was called again and the exception occured so bot is re-raising the exception ")
                raise e
        
        
    def get_all_comp_price_per_event(self, event_id):
        """
        given the event id gets all competitor prices and ticket counts
        """    
        
        here
            
    def get_new_price2(
            self, 
            ticket_key, 
            purchase_price, 
            current_price, 
            event_id, 
            compare_to_any_group_size, 
            compare_to_all_categories
        ):
        """
        calculates the price value
        
        business logic
        """
        
        
        """
        
        first we need the flags in the sheet
        
        pass the event id to find all related tickets
        
        pass the flag that indicates whether we need to do this
        
        if we do, concat all competitor prices into comp_list_price and then get the comp price count
        
        """
        
        new_price = current_price
        comp_list_price = self.competitor_price_list[ticket_key]
        comp_list_price_count = self.competitor_price_list_counts[ticket_key]
        ticket_count = int(self.ticket_count_list[self.ticket_index])
        
        if(compare_to_all_categories == True):
            comp_list_price, comp_list_price_count = self.get_all_comp_price_per_event(event_id)
        
        if(len(comp_list_price) > 0):    
            discarded_comp_prices = []
            lower_comp_prices = []
            greater_comp_prices = [] 
            
            try:
                comp_list_price.sort()
                
                for i in range(0, len(comp_list_price)):
                
                    # if competitors price count is greater that this ticket count then we consider that competitor
                    if(int(comp_list_price_count[i]) >= int(ticket_count)):
                    
                        # this competitors price
                        fl_comp_price = float(comp_list_price[i])
                        
                        if(fl_comp_price > float(purchase_price)):
                        
                            # calculate less-by-percentage
                            ltprct = ((float(fl_comp_price) - float(current_price))/float(current_price) * 100)
                        
                            # this competitor is higher that current price
                            if(ltprct > 0):
                                ##print("price " + str(fl_comp_price) + " is greater than the current price of " + str(current_price) + " by " + str(round(ltprct, 2)) + "%")
                                greater_comp_prices.append(fl_comp_price)
                                
                            # this competitor is lower than current price
                            elif(ltprct < 0):
                                ##print("price " + str(fl_comp_price) + " is less than the current price of " + str(current_price) + " by " + str(round((ltprct * (-1)), 2)) + "%")
                            
                                if(abs(ltprct) <= self.PRCT_THRESH):
                                    ##print("retaining competitor price of " + str(fl_comp_price) + " for further processing ")
                                    lower_comp_prices.append(fl_comp_price)
                                
                                else:
                                    discarded_comp_prices.append(fl_comp_price)
                        
                
                min_adjust = self.MIN_ADJUST
                if(self.current_currency in self.min_update_by_currency):
                    min_adjust = self.min_update_by_currency[self.current_currency]
                    
                if(len(lower_comp_prices) > 0):    
                    # sort the prices
                    # select lowest proce applicable prices
                    # reduce it by min 
                    # assign
                    
                    lower_comp_prices.sort()
                    new_price = round((lower_comp_prices[0] - min_adjust), 2)
                    
                    
                elif(len(greater_comp_prices) > 0):
                    
                    # filtered prices 
                    
                    greater_comp_prices.sort()    
                    new_price = round((greater_comp_prices[0] - min_adjust), 2)
                    
                    
                # if there are filtered prices that are less than the new price then reduce the new price by 5%
                #if(len(discarded_comp_prices) > 0):
                #    """
                #    this means that we do have prices that are above the original purchase price and are less the the current price
                #    and they are less that the current price - 20%
                #    """
                # 
                #    pass#new_price *= ((100 - self.PRCT_THRESH)/100)
                #
                ##print("new price")
                ##print(new_price)
                
                
            except Exception as e:
                new_price = current_price    
        
        
        return new_price
        
            
    
    def get_new_price(self, ticket_key):
        """
        business logic - determines what to set the new price to
        
        sheet record:
            find the ticket in sheet based on the event and ticket ids
            if the given event/ticket do not exist then call a create_sheet_record and return current price
        
            if the record does exist, obtain the initial purchase price
        
        price update:
        
            sort competitors by price
            exclude competitors that are lower that the initial purchase price
            exclude competitors that are lower than 20% less of our current price
            
            if we are not the lowest price then
                select price of lowest competitor and reduce it by 1 cent
                
            else 
                increase the price to next competitor, reduced by 1 cent
            
        """
        
        logging.debug(" in get_new_price ")
        
        # init price
        new_price = self.ticket_price_list[self.ticket_list[self.ticket_index]]
        
        try:        
            ticket_record = self.sheet.find_ticket_record(self.current_event_id, ticket_key)
            
            print(" in get_new_price, ticket record ")
            print(ticket_record)
            
            price_history = ticket_record['price_history'] + ", " + self.ticket_price_list[ticket_key]
            
            if('event_id' in ticket_record and str(self.current_event_id) == str(ticket_record['event_id'])):
                
                if(str(ticket_record['event_status']).lower() == 'y'):
                
                    if('purchase_price' in ticket_record):
                        if(ticket_record['purchase_price'] > 0.0):
                            
                            # if record exists and purchase price has been set
                            # then price can be adjusted
                            
                            new_price = self.get_new_price2(
                                ticket_key,
                                ticket_record['purchase_price'], 
                                self.ticket_price_list[ticket_key],
                                self.current_event_id,
                                ticket_record['compare_to_any_group_size'],
                                ticket_record['compare_to_all_categories']
                            )
                                
                            if(str(new_price) != str(self.ticket_price_list[ticket_key])):
                                logging.info("\nNew price has been found: " + str(new_price)) 
                                
                                # set the new price on the page
                                self.update_new_price1(new_price)
                                
                                updates = {
                                    8: int(self.ticket_count_list[self.ticket_index]),
                                    11: new_price,
                                    12: price_history,
                                    15: self.get_str_of_competitor_prices(ticket_key),
                                    17: self.util.get_current_date()
                                }
                                
                                self.sheet.update_ticket(ticket_key, updates, True)
                                
                                try:
                                    self.ntfr.send(
                                        content = "Price change: event id = '" + str(self.current_event_id) + 
                                            "', ticket id = '" + str(ticket_key) + "', original price = '" + 
                                            str(self.ticket_price_list[ticket_key]) + "', new price = '" + 
                                            str(new_price) + "', initial purchase price = '" + 
                                            str(ticket_record['purchase_price']) + "' ",
                                        subject = "ticket price has been adjusted"              
                                    )
                                except Exception as e:
                                    logging.error("\n\tCould not send the notification \n")
                                    logging.error(e)
                            
                            else:
                                logging.info("\nExisting price and new price are the same")  
                                updates = {
                                    8: int(self.ticket_count_list[self.ticket_index]),
                                    11: new_price,
                                    12: price_history,
                                    15: self.get_str_of_competitor_prices(ticket_key),
                                    17: self.util.get_current_date()
                                }
                                self.sheet.update_ticket(ticket_key, updates, True)     
                            
                        else:
                            logging.info("\nOriginal purchase price was 0.0 ")
                            updates = {
                                8: int(self.ticket_count_list[self.ticket_index]),
                                12: price_history,
                                15: self.get_str_of_competitor_prices(ticket_key),
                                17: self.util.get_current_date()
                            }
                            self.sheet.update_ticket(ticket_key, updates, True)
                    
                    else:
                        logging.info("\nOriginal purchase price was not found in the sheet ")
                        updates = {
                            8: int(self.ticket_count_list[self.ticket_index]),
                            12: price_history,
                            15: self.get_str_of_competitor_prices(ticket_key),
                            17: self.util.get_current_date()
                        }
                        self.sheet.update_ticket(ticket_key, updates, True)
                        
                else:
                    logging.info("\nTicket " + str(ticket_key) + " is not active in the sheet and was skipped ")
                    
            else:
                logging.info("\nEvent id " + str(self.current_event_id) + " was NOT in the ticket_record ")
                logging.info("\nCreating a new ticket record in the sheet. Please update the purchase price of the ticket manually ")
                # create ticket record and skip this price update 
                self.persist_new_ticket_record(ticket_key)
                  
            return new_price
        
        except Exception as e:
            
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            
            logging.error("\n\tAn issue occured while adjusting the price of ticket " + str(ticket_key) + " \n")
            
            #self.stop()
            self.manager.deactivate()
            
            #logging.debug("self.ready_signal.emit()")
            #self.ready_signal.emit()
    
        return new_price
    
    
    def update_new_price3(self, html):
        """
        the price was updated and the ticket was clicked on
        """
        self.delay(1000)
        
    
    def update_new_price2(self, html):
        """
        delays price update
        """
        self.delay(4000)
    
    
    def update_new_price1(self, new_price):
        """
        updates the price - writes it in the box and clicks away on to the ticket div
        """
        
        try:
            ref = self.ticket_list[self.ticket_index]
            
            script = "document.getElementById('desiredPrice-" + ref + "').value = " + str(new_price) + "; "
            script += "document.getElementById('precioPublico-" + ref + "').value = " + str(new_price) + "; "
            script += "document.getElementById('desiredPrice').value=" + str(new_price) + "; "
            script += "document.getElementById('publicPrice').value=" + str(new_price) + "; "
            script += "document.getElementById('continuar').click(); "
            
            logging.info("Updating the price of " + str(ref) + " to " + str(new_price) + " from " + str(self.ticket_price_list[ref]) + " \n")
            logging.debug(script)
            self.ui.web_view.page().runJavaScript(script, self.update_new_price2)
            
            
        except Exception as e:
            
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            
            logging.error("\n\tAn issue occurred while updating the price of ticket: " + str(self.ticket_list[self.ticket_index]) + " \n")
            
            #self.stop()
            self.manager.deactivate()
            #self.ready_signal.emit()
        
        
    def update_new_price3_5(self, event):
        """
        scrolled
        """
        self.delay(0)
        
        
    def update_price3(self, html):
        """
        lets access the price box
        """
        
        logging.debug(" in update price 3")
        try:
            
            # price box popped up - scroll to the bottom
            #self.delay(1000)    
            #script = "window.scrollTo(0, (document.body.scrollHeight))"
            #self.ui.web_view.page().runJavaScript(script, self.update_new_price3_5)
            
            ticket_key = str(self.ticket_list[self.ticket_index]).replace("'", "").strip()
            
            print(" WORKING WITH ticket key of " + str(ticket_key))
            
            soup = BeautifulSoup(html, "html.parser")    
            #with open("html.html", "w", encoding='utf-8') as file:
            #    file.write(str(soup))
            
            logging.info("\nUpdating the price of ticket " + str(ticket_key) + " ... ")
                        
            currency_record = soup.select("div[tb-option-ticketid='" + ticket_key + "']")
            if(len(currency_record) > 0):
                self.current_currency = currency_record[0]['tb-currency-code']
            else:
                self.current_currency = ""
                
            # get competitor price list            
            competitor_list = []
            competitor_list_count = []
            lis = soup.select("div[tb-option-ticketid='" + ticket_key + "'] > form > section > article:nth-of-type(1) > div > ul > li")
            for li in lis:
                
                # get competitor ticket prices
                try:
                    competitor_list.append(float(li['data-price']))
                except:
                    competitor_list.append(0.0)
                    
                    
                # get competitor ticket counts
                try:
                    ticket_count_txt = li.select("span:nth-of-type(2)")
                    if(len(ticket_count_txt) > 0):
                        if(" " in ticket_count_txt[0].text):
                            count = int(ticket_count_txt[0].text.split(" ")[0])
                            competitor_list_count.append(count)
                        else:
                            competitor_list_count.append(1)
                
                except Exception as e:
                    competitor_list_count.append(0)
            
            self.competitor_price_list[ticket_key] = competitor_list
            self.competitor_price_list_counts[ticket_key] = competitor_list_count
            
            print(" competitor price count: ")
            print(self.competitor_price_list[ticket_key])
            
            try:
                log = ", ".self.competitor_price_list[ticket_key]
                logging.info("\nCompetitor price list for ticket " + ticket_key + ": [" + log +"]\n")
            except:
                pass
            
            # make event and ticket ids available in the price update function and get new price
            self.get_new_price(ticket_key)
                
            if(self.ticket_index < len(self.ticket_list) - 1):
                # go to update next ticket
                self.ticket_index += 1
                self.update_price_signal.emit()
                
            else:
                self.go_to_next_event()
                
        except Exception as e:
            
            logging.debug(" global exception occured in update_price3 ")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            
            self.manager.deactivate()
            
    
    def go_to_next_event(self):
        """
        tickets in this event are done being processed and control is going to next event
        """
        
        try:
            self.update_price_signal.disconnect(self.update_price1)
        except:
            pass
                
        # click on next event
        self.ticket_list = []
        
        self.ticket_category_list = []
        self.ticket_reference_list = []
        self.ticket_count_list = []
        
        self.ticket_index = -1
        self.ticket_price_list = {}
        self.competitor_price_list = {}
        self.competitor_price_list_counts = {}
        
        self.current_currency = ""
        
        self.next_event_signal.emit()
            
    
    def update_price2(self, event):
        """
        price was clicked on, we delay, and access html 
        """
        
        self.delay(2000)
        self.ui.web_view.page().runJavaScript("document.documentElement.outerHTML", self.update_price3)
        
        
    def update_price1_5(self, html):
        """
        writes the current ticket price into price array
        """
        
        self.delay(3000)
        try:
            value = html.replace(",", "")
            self.ticket_price_list[str(self.ticket_list[self.ticket_index])] = float(value)
            logging.info("\nSetting the existing price of ticket " + str(self.ticket_list[self.ticket_index]) + " to " + str(self.ticket_price_list[str(self.ticket_list[self.ticket_index])]))
            
        except Exception as e:
            
            try:
                logging.error("\n\tUnable to set the current ptice of ticket " + str(self.ticket_list[self.ticket_index]) + " \n")
                self.ticket_price_list[str(self.ticket_list[self.ticket_index])] = 0.0
                
            except IndexError as ie:
                
                """
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.debug(exc_type, fname, exc_tb.tb_lineno)
                logging.debug(ie)
                logging.error(" An error occurred while fetching prices. Terminating existing run and starting over.")
                
                self.stop()
                
                logging.debug("self.ready_signal.emit()")
                self.ready_signal.emit()
                """
                logging.error("\n\tUnable to get the price of the current ticket. moving to next tiket within this event \n")
                self.go_to_next_event()
                
    
    def update_price_2_trigger(self):
        """
        this call is reused in two paces so factored out
        """
        
        # attempts to get current price
        script = "document.getElementById('precioPublico-" + str(self.ticket_list[self.ticket_index]) + "').value"
        logging.debug(script)
        self.ui.web_view.page().runJavaScript(script, self.update_price1_5)

        # scroll to the bottom
        #self.delay(1000)    
        script = "window.scroll(0, document.getElementById('precioPublico-" + str(self.ticket_list[self.ticket_index]) + "').getBoundingClientRect()['y']);"
        self.ui.web_view.page().runJavaScript(script, self.redirect)
    
        # runs price update
        script = "document.getElementById('precioPublico-" + str(self.ticket_list[self.ticket_index]) + "').click()"
        logging.debug(script)
        self.ui.web_view.page().runJavaScript(script, self.update_price2)
        
        
    def update_price1(self):
        """
        starts the loop of ticket prices to click on
        """
        
        logging.debug("in update_price1")
        try:
            
            #raise Exception(" debug bot stop ")
        
            if(len(self.ticket_list) > 0):
                
                if(self.ticket_index < len(self.ticket_list) - 1):
                    
                    self.delay(1000)    
                    logging.info("\nProcessing ticket " + str(self.ticket_list[self.ticket_index]))
                    
                    print(" checking if " + str(self.ticket_list[self.ticket_index]) + " is int he active sheet list ")
                    
                    if(self.ticket_list[self.ticket_index] in self.active_sheet_tickets):
                        
                        print(" IT WAS  in it ")
                        if(self.active_sheet_tickets[self.ticket_list[self.ticket_index]]['event_status'] == "Y"):
                            print(" and self.active_sheet_tickets[self.ticket_list[self.ticket_index]]['event_status'] was " + str(self.active_sheet_tickets[self.ticket_list[self.ticket_index]]['event_status']))
                            self.update_price_2_trigger()
                            
                        else:
                            
                            print(" self.active_sheet_tickets[self.ticket_list[self.ticket_index]]['event_status'] was not Y so we are going to ")
                            logging.info("Ticket " + str(self.ticket_list[self.ticket_index]) + " is not active in the sheet ")
                            if(self.ticket_index < len(self.ticket_list) - 1):
                                
                                print(" next ticket")
                                self.ticket_index += 1
                                self.update_price_signal.emit()
                                
                            else:
                                
                                print(" next event ")
                                self.go_to_next_event()
                            
                    else:
                        
                        # if this ticket is not in the sheet AT ALL then call the trigger again
                        
                        ticket_id = self.find_in_sheet(
                            field_name = "ticket_id", 
                            criteria = self.ticket_list[self.ticket_index], 
                            return_field = "ticket_id"
                        )
                        if(ticket_id == ""):
                            self.update_price_2_trigger()
                            
                        else:
                            
                            logging.info("\nTicket " + str(ticket_id) + " is not active in the sheet and was skipped ")
                            if(self.ticket_index < len(self.ticket_list) - 1):
                                # go to update next ticket
                                self.ticket_index += 1
                                self.update_price_signal.emit()
                                
                            else:
                                self.go_to_next_event()
                    
                else:
                    
                    logging.info("Tickets for the given event are processed. going to next event \n")
                    self.go_to_next_event()
            
            else:
                
                logging.error("\n\tTicket list contained no entries. going to next event \n")
                
                """
                self.stop()
                logging.debug("self.ready_signal.emit()")
                self.ready_signal.emit()
                """
                
                self.go_to_next_event()
                
            
            
        except Exception as e:
        
            
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            
            #self.stop()
            self.manager.deactivate()
            #logging.debug("self.ready_signal.emit()")
            #self.ready_signal.emit()
            
        
        
    def process_listings5(self, html):
        """
        accesses prices of the event after clicking on it
        """
         
        try:
            self.htmlstr = html
            self.delay(1000)
            
            soup = BeautifulSoup(self.htmlstr, "html.parser")
            #with open("html_" + str(self.event_click_index) + "_" + str(global_counter) + ".html", "w", encoding='utf-8') as file:
            #    file.write(str(soup))
                                
            # TODO MODE
            if(self.exec_type == "paused"):
                self.ticket_type = " inactive"
            else:
                self.ticket_type = ""
            
            soup_str = "ul.list > li:nth-of-type(" + str(self.event_click_index + 1) + ") > div.silk-form > table.silk-table > tbody > tr[class='entrada" + self.ticket_type + "']"  
            ticket_list = soup.select(soup_str)
            
            print(" in process listings 5 the ticket list is ")
            print(ticket_list)
            
            if(len(ticket_list) > 0):
            
                for ee in ticket_list:
                    ticket_id = ee['id'].replace("form-", "")
                    self.ticket_list.append(ticket_id)
                    
                    self.ticket_category_list.append(ee.select("td:nth-of-type(2) > div > div > span > select > option[selected='selected']")[0].text)
                    self.ticket_reference_list.append(ee.select("td:nth-of-type(4)")[0].text)
                    self.ticket_count_list.append(ee.select("td:nth-of-type(5) > div[class='field-group'] > input")[0].get('value'))
                        
                log = ", ".join(self.ticket_list)
                logging.debug(" obtained ticket list: [" + log + "] ")
            
                logging.debug("self.update_price_signal.connect(self.update_price1)")    
                self.update_price_signal.connect(self.update_price1)
                
                logging.debug("self.update_price_signal.emit()")
                self.update_price_signal.emit()
                
            else:
                
                logging.error("\n\tExpected to be able to select tickets and found none for this event. going to next event \n")
                self.go_to_next_event()
            
            
            
        except Exception as e:
        
            logging.debug(" exception occured in process_listings5")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            
            #self.stop()
            self.manager.deactivate()
            #self.ready_signal.emit()
        
        
    def delay(self, frq):
        """
        sleep
        """
        
        loop = QEventLoop()
        QTimer.singleShot(frq, loop.quit)
        loop.exec_()
        
        
    def process_listings4(self, html):
        """
        saves updated html
        """
        
        try:
            self.delay(5000)
            self.ui.web_view.page().runJavaScript("document.documentElement.outerHTML", self.process_listings5)
            
        except Exception as e:
        
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            #self.stop()
            self.manager.deactivate()
            
            #logging.debug("self.ready_signal.emit()")
            #self.ready_signal.emit()
            
            
    def set_event_id(self):
        """
        attempts to obtain current event id
        """
        
        self.current_event_name = ""
        self.current_event_id = ""
        
        soup = BeautifulSoup(self.htmlstr, "html.parser")
        events = soup.select("ul.list > li:nth-of-type(" + str(self.event_click_index + 1) + ")")
        
        if(len(events) > 0):
            event = events[0]
            
            try:
                self.current_event_name = soup.select("ul.list > li:nth-of-type(" + str(self.event_click_index + 1) + ") > a.collapsible_header > div.listing > div.data > div.flex > h2.title ")[0].text
                #logging.info(" accessing event " + self.current_event_name)
                
            except:
                logging.error("\n\tUnable to set the event name for " + str(self.event_click_index + 1) + " \n")
                
            try:
                
                self.current_event_id = event['data-event-id']
                logging.info("(Event id = " + str(self.current_event_id) + ")")
                
            except:
                
                logging.error("\n\tUnable to obtain the event id. prices in this event cannot be adjusted. skipping event \n")
                #self.stop()
                self.manager.deactivate()
                
                
                #logging.debug(" self.ready_signal.emit()")
                #self.ready_signal.emit()
        
        
    def process_listings_3_5(self, event):
        """
        scroll to event
        """
        self.delay(1000)
        
        
    def process_listings3(self):
        """
        recursive calls to click in each event
        the first call starts in process_listings2
        """
        
        print(" now we are in process_listings3 ")
        
        # we exited the problematic loop and not can reset this counter 
        self.process_listings_2_fail_counter = 0
        
        print(" active event list ")
        print(self.active_events_list)
        
        try:
            log = ", ".join(self.ticket_list)
            logging.debug("ticket list " + log)
            
            print(" ticket list was " + str(log))
            print(" self.event_click_index is " + str(self.event_click_index))
            print(" event count is " + str(self.event_count))

            if(self.event_click_index < self.event_count - 1):
                
                self.event_click_index += 1
                
                if(self.active_events_list[self.event_click_index] != "0"):
                    
                    self.set_event_id()
                    
                    script = """window.scroll(0, 
                        document.getElementById("eventosDiv").
                        getElementsByClassName("container-account")[0].
                        getElementsByTagName("div")[0].
                        getElementsByTagName("ul")[0].
                        childNodes[{:d}].
                        getElementsByTagName("a")[0].getBoundingClientRect()['y']);
                    """
                    script = script.replace("\n", "")
                    script = script.replace(" ", "")
                    script = script.replace("\t", "")
                    script = script.replace("\r", "")
                    script = script.format(self.event_click_index)
                    #logging.debug(script)
                    #self.ui.web_view.page().runJavaScript(script, self.process_listings_3_5)
                    
                    
                    script = """
                        document.getElementById("eventosDiv").
                        getElementsByClassName("container-account")[0].
                        getElementsByTagName("div")[0].
                        getElementsByTagName("ul")[0].
                        childNodes[{:d}].
                        getElementsByTagName("a")[0].
                        click()
                    """    
                    script = script.replace("\n", "")
                    script = script.replace(" ", "")
                    script = script.replace("\t", "")
                    script = script.replace("\r", "")
                    script = script.format(self.event_click_index)
                    logging.debug(script)
                    self.ui.web_view.page().runJavaScript(script, self.process_listings4)
                    
                else:
                    
                    logging.debug(" event at click index " + str(self.event_click_index) + " was not active ")
                    logging.debug(" self.next_event_signal.emit() ")
                    self.next_event_signal.emit()
                
            else:
                
                # end of events processing
                logging.info("\n\tNo events were found. restarting cycle ")
                script = "window.scrollTo(0,  0);"
                logging.debug(script)
                self.ui.web_view.page().runJavaScript(script, self.redirect)
                logging.debug("self.next_event_signal.disconnect(self.process_listings3)")
                self.next_event_signal.disconnect(self.process_listings3)
                self.stop()
                self.ready_signal.emit()
                
        except Exception as e:
        
            try:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.debug(exc_type, fname, exc_tb.tb_lineno)
                logging.debug(e)
                logging.error("\n\tAn issue occurred while accessing tickets of event " + str(self.active_events_list[self.event_click_index]) + "\n")
                self.stop()
                
            except Exception as e2:
                
                logging.debug(e2)
                logging.error("\n\tCritical error. stopping bot \n")
                #self.stop()
                self.manager.deactivate()

            
            
    def reset(self):
        """
        reset
        """
        
        self.process_listings_2_fail_counter = 0
        self.htmlstr = ""
    
        self.logged_in = 0
        self.active_events_list = []
        self.event_count = 0
        self.event_click_index = -1
        self.ticket_list = []
        
        self.ticket_category_list = []
        self.ticket_reference_list = []
        self.ticket_count_list = []
        
        self.ticket_index = -1
        self.ticket_price_list = {}
        self.competitor_price_list = {}
        self.competitor_price_list_counts = {}
        
        self.active_sheet_tickets = {}
        self.active_sheet_events = []
        
        self.current_currency = "" 
        self.current_event_id = ""
        self.current_event_name = ""
        
        logging.debug(" reseting parameters ... ")    
        
           
            
    def redirect(self, event):
        """
        used to redirect javascript call
        """
        self.delay(1000)
            
            
    def build_active_sheet_tickets(self):
        """
        build active sheet tickets
        """
        
        logging.debug(" in build_active_sheet_tickets ")
        
        self.sheet.open_sheet()
        for record in self.sheet.all_sheet_records:
            if(record['event_status'] == "Y"):
                self.active_sheet_events.append(record['event_id'])
                self.active_sheet_tickets[str(record['ticket_id'])] = record
                
            
    def find_in_sheet(self, field_name = "", criteria = "", return_field = ""):
        """
        finds in self.sheet.all_sheet_records
        """                       
        
        logging.debug(" in find_in_sheet ")
        
        
        rtn = ""
        for record in self.sheet.all_sheet_records:
            if(field_name in record):
                if(str(record[field_name]) == str(criteria)):
                    rtn = record[return_field]
                    break
            
        return rtn
    
            
    def process_listings2(self, html):
        """
        callback for getting html
        obtains a list of active events
        """
        
        self.delay(1000)
        logging.debug(" IN PROCESS LISTING 2")
        logging.info(" loading events ... ")
        try:
            self.htmlstr = html
            soup = BeautifulSoup(self.htmlstr, "html.parser")
            #with open("html_" + str(global_counter) + ".html", "w", encoding='utf-8') as file:
            #    file.write(str(soup))
                
            events = soup.select("ul.list li")   
            print(" events found: " + str(len(events))) 
            
            event_ids = []
            if(len(events) > 0):
                event_ids = [event['data-event-id'] for event in events]
                
            print(" event ids are ")
            print(event_ids)
                
            soup_str = "ul.list li a.collapsible_header div.listing div.state-info span." + self.exec_type
            
            print(" active event list soup str is " + soup_str)
            
            active_events = soup.select(soup_str)
            self.active_events_list = [event.get_text() for event in active_events]
            
            print(" the active event list is ")
            print(self.active_events_list)
            
            # reduce active event list based on the sheet content
            self.build_active_sheet_tickets()
            
            print(" self.active_sheet_tickets: ")
            print(self.active_sheet_tickets)
            
            
            print(" activating events based on sheet ")
            corr_index = -1
            self.sheet.open_sheet()
            for event_id in event_ids:
                corr_index += 1
                
                print(" event id in loop is " + str(event_id))
                
                try:
                    #cell = self.sheet.find(event_id)
                    #active_sheet_flag = self.sheet.get_cell_value(cell.row, cell.col + 1)
                    
                    active_sheet_flag = self.find_in_sheet(
                        field_name = "event_id", 
                        criteria = event_id, 
                        return_field = "event_status"
                    )
                    
                    if(active_sheet_flag == "N"):
                        if(self.active_events_list[corr_index] != '0'):
                            if(int(event_id) not in self.active_sheet_events):
                                self.active_events_list[corr_index] = '0'
                        
                except Exception as e:
                    logging.debug(" an exception occured while searching the sheet in process_listings2")
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    logging.debug(exc_type, fname, exc_tb.tb_lineno)
                    logging.debug(e)
                    
                    if(self.process_listings_2_fail_counter < self.max_fails):
                        self.process_listings_2_fail_counter += 1
                        logging.info("\nThe bot is using too many Google Sheets connections and needs to pause ... ")
                        self.delay(15000)
                        self.process_listings(html)
                        
                    else:
                        
                        logging.error("\nGoogle Sheets API is not available and the bot is stopping. ")
                        self.manager.deactivate()
                    
                
            if(len(self.active_events_list) == 0):
                logging.error("\n\tActive event list could not be retrieved. stopping bot ")
                self.stop()
                
            else:
                self.open_event_section = True
                self.event_count = int(len(events))
                
                logging.debug("self.next_event_signal.connect(self.process_listings3)")
                logging.debug("self.next_event_signal.emit()")
                
                self.next_event_signal.connect(self.process_listings3)
                self.next_event_signal.emit()
            
            
        except Exception as e:
        
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            
            logging.debug(" this exception was caught in global handling of process_listings2 ")
            
            #self.stop()
            self.manager.deactivate()
            
            #logging.debug("self.ready_signal.emit()")
            #self.ready_signal.emit()
        
    
    def set_logged_in(self, event):
        """
        tracks if we are logged in
        """
        self.logged_in = 1
        
    
    def process_listings_login_verify(self, event):
        """
        gets html of the page to have the login verified
        """
        
        logging.debug("self.ui.web_view.loadFinished.disconnect(self.process_listings_login_verify)")
        self.ui.web_view.loadFinished.disconnect(self.process_listings_login_verify)
        self.delay(1000)
        self.ui.web_view.page().runJavaScript("document.documentElement.outerHTML", self.process_listings)
        
        
    def verify_login(self, html):
        """
        examines login html and returns status
        """
        
        logging.info(" verifying log in ")
        try:
            self.delay(1000)
            rtn = False
            soup = BeautifulSoup(html, "html.parser")    
            el = soup.select("div#errorServidor")
            
            if(len(el) == 0):
                rtn = True
                self.logged_in = 2
            else:
                self.logged_in = 0
                
        except TypeError:
            rtn = True
            self.logged_in = 2
        
        return rtn
        
    def process_listings(self, html):
        """
        process listings
        """
        
        try:
            global global_counter
            global_counter += 1
            logging.info(" performing run " + str(global_counter))
            
            if(self.verify_login(html)):
                self.ui.web_view.page().runJavaScript("document.documentElement.outerHTML", self.process_listings2)
                logging.info("\nLogin successful ")
                
            else:
                # stop the bot as the login was invalid
                logging.error("\n\tLogin error\n")
                raise Exception("invalid login")
                
            
        except Exception as e:
        
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.debug(exc_type, fname, exc_tb.tb_lineno)
            logging.debug(e)
            
            self.manager.deactivate()
        
        