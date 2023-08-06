# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 19:33:02 2022

@author: Utilisateur
"""


import pyvisa
import pandas as pd
from datetime import datetime
import time



Fuite = pd.DataFrame({'datetime':[] ,'leak_rate':[],'pressure':[]})

rm = pyvisa.ResourceManager()
rm.list_resources()
asm142 = rm.open_resource('COM8')

asm142.timeout = 5000
asm142.write('!VE')

test = asm142.read()
# leak_rate = float(test[21:29])
# pressure = float(test[32:40])
# timedate = datetime.now()
# data = {'datetime':timedate ,'leak_rate':leak_rate,'pressure':pressure}
# Fuite = Fuite.append(pd.DataFrame(data))






    
