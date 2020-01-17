
import os, sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

from apiclient import discovery

import httplib2
from httplib2 import Http

class Sheet(object):
    """
    api to google sheet
    """
    
    DEFAULT_AUTH_FILE = "default_sheet_auth.json" 
    
    EVENT_ID_FIELD = 2
    TICKET_ID_FIELD = 6
    
    scope = None
    creds = None
    sheet = None
    
    # default_sheet_auth.json
    def __init__(self, auth_file_name = "", sheet_name = "stubhub_ticket_purchase_prices"):
        """
        init
        """
        
        try:
            if(auth_file_name == ""):
                self.auth_file_name = self.locate_auth_file_name()
            else:
                self.auth_file_name = auth_file_name
                
            logging.info("\nAuth file name: " + self.auth_file_name)
                
            self.sheet_name = sheet_name        
            logging.debug(self.auth_file_name)
            
            self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.resource_path(self.auth_file_name), self.scope)
            self.client = gspread.authorize(self.creds)

        except httplib2.ServerNotFoundError as e:
            raise Exception(" no internet connection ")
        
        except Exception as e:
            raise(" an unknown error had occured while connecting to google sheets ")
    
    
    def locate_auth_file_name(self):
        """
        default_sheet_auth.json
        """
        rtn = ""
        if(os.path.exists(self.resource_path(self.DEFAULT_AUTH_FILE))):
            rtn = self.DEFAULT_AUTH_FILE
            
        return rtn
        
        
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        
        return os.path.join(os.path.abspath("."), relative_path)
    
    
    def login(self):
        """
        refresh token
        """
        self.client.login()
        
        
    def open_sheet(self):
        """
        tries to open
        gets all records once
        """
        
        self.client.login()
        
        logging.debug(" opening sheet in sheet.open_sheet ")
        logging.debug(self.auth_file_name)
        self.sheet = self.client.open(self.sheet_name).sheet1
        self.all_sheet_records = self.sheet.get_all_records()
        self.event_ids = self.sheet.col_values(self.EVENT_ID_FIELD)
        self.ticket_ids = self.sheet.col_values(self.TICKET_ID_FIELD)
        
    
    def reload(self):
        """
        reload
        """
        logging.debug(" in sheet reload() ")
        self.sheet = self.client.open(self.sheet_name).sheet1
        self.all_sheet_records = self.sheet.get_all_records()
        
        
    
    def find_ticket_record(self, event_id, ticket_id):
        """
        takes ticket_id and returns sheet row or empty list
        """
        
        self.login()
        
        self.event_ids = self.sheet.col_values(self.EVENT_ID_FIELD)
        self.ticket_ids = self.sheet.col_values(self.TICKET_ID_FIELD)
        self.all_sheet_records = self.sheet.get_all_records()
        
        result = {}
        
        if event_id in self.event_ids and ticket_id in self.ticket_ids:
            
            try:
                event_index = self.event_ids.index(event_id)
                ticket_index = self.ticket_ids.index(ticket_id)
                    
                #if(event_index == ticket_index):
                result = self.all_sheet_records[ticket_index - 1]    
                        
            except Exception as e:
                
                logging.debug(e)
                logging.error("there was an issue fetching the record from sheet")
        
        return result
    
    
    def insert_ticket_record(self, record):
        """
        inserts record into sheet at the end
        """
        
        self.login()
        self.sheet.insert_row(record, len(self.all_sheet_records) + 2)
        self.all_sheet_records.append(record)
        
        
    def find(self, crit):
        """
        find
        """
        self.login()
        return self.sheet.find(crit)
    
    def get_cell_value(self, row, col):
        """
        get cell value
        """
        self.login()
        return self.sheet.cell(row, col).value
    
    
    def update_ticket(self, ticket_id, updates, fail_forward = False):
        """
        updates a record - param is a [coord:coord:value] - field, column index and value
        """
        
        try:
            self.login()
            self.all_sheet_records = self.sheet.get_all_records()
            
            row = 1
            for record in self.all_sheet_records:       
                if(str(ticket_id).strip() == str(record['ticket_id']).strip()):
                    
                    for col in updates:
                        value = updates[col]
                        logging.debug("updating sheet, setting sell price of ticket " + str(record['ticket_id']).strip() + " to " + str(value))
                        self.sheet.update_cell(row + 1, col, value)
                    
                row += 1
                
        except Exception as e:
            
            if(fail_forward == True):
                self.login()
                self.update_ticket(ticket_id, updates, False)
            else:
                raise e
            
            



if(__name__ == "__main__"):
    
    s = Sheet(sheet_name = "contacts")
    s.open_sheet()
    
    print(s.all_sheet_records)