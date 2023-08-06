#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def query_measurement(address):

    """
    ========== DESCRIPTION ==========

    This function can query the measurement value

    ========== FROM ==========

    Manual of Keithley 196

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
     
    ========== OUTPUT ==========
    
    <measurement>
        -- float --
        The measurement
        [depend]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    answer = instru.read()
    
    measurement = float(answer[4:16])
    
    ################## FUNCTION ###############################################
    
    return voltage


#%%
def command_function(address,function):

    """
    ========== DESCRIPTION ==========

    This function can command the function

    ========== FROM ==========

    Manual of Keithley 196

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <function>
        -- int --
        The function (0     =   DV Volts,
                      1     =   AC Volts,
                      2     =   Ohms,
                      3     =   DC current,
                      4     =   AC current,
                      5     =   ACV dB,
                      6     =   ACA dB,
                      7     =   Offset compensation Ohms)

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    function = str(function)
    
    instruction = 'F'+function+'X'

    instru.write(instruction)
    
    ################## FUNCTION ###############################################
    
    return 

#%%
def command_range(address,range_value):

    """
    ========== DESCRIPTION ==========

    This function can command the range_value

    ========== FROM ==========

    Manual of Keithley 196

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <range_value>
        -- int --
        The function (0     =   Autorange,
                      1     =   specific value,
                      2     =   specific value,
                      3     =   specific value,
                      4     =   specific value,
                      5     =   specific value,
                      6     =   specific value,
                      7     =   specific value)

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    range_value = str(range_value)
    
    instruction = 'F'+range_value+'X'

    instru.write(instruction)
    
    ################## FUNCTION ###############################################
    
    return 

