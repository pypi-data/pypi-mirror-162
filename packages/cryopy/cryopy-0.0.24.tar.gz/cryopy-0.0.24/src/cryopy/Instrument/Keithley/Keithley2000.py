#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def query_voltage(address):
    
    """
    ========== DESCRIPTION ==========

    This function get the value of the voltage from Keithley 2000

    ========== FROM ==========

    Manual of Keithley 2000

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')

    ========== OUTPUT ==========

    <voltage> 
        -- float --
        The measured voltage
        [V]

    ========== STATUS ==========

    Status : Checked


    """

    ################## MODULES ################################################

    import pyvisa
    import numpy as np

    ################## INITIALISATION #########################################

    rm = pyvisa.ResourceManager()
    instru = rm.open_resource(address)
    instru.write("*rst; status:preset; *cls")
    interval_in_ms = 50
    number_of_readings = 5

    ################## FUNCTION ###############################################

    instru.write("status:measurement:enable 512; *sre 1")
    instru.write("sample:count %d" % number_of_readings) 
    instru.write("trigger:source bus")
    instru.write("trigger:delay %f" % (interval_in_ms / 1000.0))
    instru.write("trace:points %d" % number_of_readings)
    instru.write("trace:feed sense1; feed:control next")
    
    instru.write("initiate")
    instru.assert_trigger()
    instru.wait_for_srq()
    
    voltage = instru.query_ascii_values("trace:data?")
    
    instru.query("status:measurement?")
    instru.write("trace:clear; feed:control next")
    
    return np.mean(voltage)

#%%
def query_identification(address):
    
    """
    ========== DESCRIPTION ==========

    This function get the identification of Keithley 2000

    ========== FROM ==========

    Manual of Keithley 2000

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')

    ========== OUTPUT ==========

    <string>
        -- float --
        The measured voltage
        [V]

    ========== STATUS ==========

    Status : Checked


    """

    ################## MODULES ################################################

    import pyvisa
    import numpy as np

    ################## INITIALISATION #########################################

    rm = pyvisa.ResourceManager()
    instru = rm.open_resource(address)
    instru.write("*rst; status:preset; *cls")
    interval_in_ms = 50
    number_of_readings = 5

    ################## FUNCTION ###############################################

    instru.write("status:measurement:enable 512; *sre 1")
    instru.write("sample:count %d" % number_of_readings) 
    instru.write("trigger:source bus")
    instru.write("trigger:delay %f" % (interval_in_ms / 1000.0))
    instru.write("trace:points %d" % number_of_readings)
    instru.write("trace:feed sense1; feed:control next")
    
    instru.write("initiate")
    instru.assert_trigger()
    instru.wait_for_srq()
    
    voltage = instru.query_ascii_values("trace:data?")
    
    instru.query("status:measurement?")
    instru.write("trace:clear; feed:control next")
    
    return np.mean(voltage)
