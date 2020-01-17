
import random
import logging
import datetime

class Util(object):
    """
    utils
    """
    
    def __init__(self):
        """
        """
        
        pass
    
    
    def get_current_date(self, format = "%Y-%m-%d %H:%M"):
        """
        returns current date
        """
        
        now = datetime.datetime.now()
        return now.strftime(format)
    
    def get_waiting_period(self, frq = 0, frq_type = ""):
        """
        gets random 0 - 9 times x
        """
        
        frq = int(frq)
        
        r = 0
        try:
            if(frq_type == "minute"):
                r = (random.randint(10, (60 / frq)))
                
            elif(frq_type == "hour"):
                r = (random.randint(300, (3600 / frq)))
                
            
            elif(frq_type == "day"):
                r = (random.randint(1800, (72000 / frq)))
            
            return r
        
        except Exception as e:
            
            return 0
        
        