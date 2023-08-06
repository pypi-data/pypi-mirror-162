#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def command_local(address):

    """
    ========== DESCRIPTION ==========

    This function can define the "local" mode of the instrument

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    instruction = "LOCAL"
    
    ################## FUNCTION ###############################################
    
    instru.write(instruction)
    return 




#%%
def command_voltage(address,channel,voltage):

    """
    ========== DESCRIPTION ==========

    This function can define a voltage output on a specific channel

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2

    <voltage>
        -- float --
        The voltage output
        [V]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    voltage = str(voltage)
    channel = str(channel)
    
    instruction = 'V'+channel+' '+voltage
    
    ################## FUNCTION ###############################################
    
    instru.write(instruction)
    command_local(address)
    
    return 

#%%
def command_voltage_with_checking(address,channel,voltage):

    """
    ========== DESCRIPTION ==========

    This function can define a voltage output on a specific channel with a 
    checking of the voltage output

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2

    <voltage>
        -- float --
        The voltage output
        [V]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    voltage = str(voltage)
    channel = str(channel)
    
    instruction = 'V'+channel+'V '+voltage
    
    ################## FUNCTION ###############################################
    
    instru.write(instruction)
    command_local(address)
    
    return 

#%%
def command_ovp(address,channel,voltage):

    """
    ========== DESCRIPTION ==========

    This function can define the over voltage power on a specific channel

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2

    <voltage>
        -- float --
        The voltage output
        [V]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    voltage = str(voltage)
    channel = str(channel)
    
    instruction = 'OVP'+channel+' '+voltage
    
    ################## FUNCTION ###############################################
    
    instru.write(instruction)
    command_local(address)
    
    return 

#%%
def command_current(address,channel,current):

    """
    ========== DESCRIPTION ==========

    This function can define the limit current on a specific channel

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2
        
    <current>
        -- float --
        The limit current output
        [A]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    current = str(current)
    channel = str(channel)
    
    instruction = 'I'+channel+' '+current
    
    ################## FUNCTION ###############################################
    
    instru.write(instruction)
    command_local(address)
    
    return 

#%%
def command_ocp(address,channel,current):

    """
    ========== DESCRIPTION ==========

    This function can define the over current power on a specific channel

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2

    <current>
        -- float --
        The current output
        [A]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    current = str(current)
    channel = str(channel)
    
    instruction = 'OCP'+channel+' '+current
    
    ################## FUNCTION ###############################################
    
    instru.write(instruction)
    command_local(address)
    
    return 


#%%
def query_voltage(address,channel):

    """
    ========== DESCRIPTION ==========

    This function can query a voltage output of a specific channel

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2
     
    ========== OUTPUT ==========
    
    <voltage>
        -- float --
        The voltage output
        [V]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    channel = str(channel)
    
    instruction = 'V'+channel+'?'
    answer = instru.query('instruction')
    
    voltage = float(answer[3:8])
    
    command_local(address)
    
    ################## FUNCTION ###############################################
    
    return voltage

#%%
def query_current(address,channel):

    """
    ========== DESCRIPTION ==========

    This function can query a current output of a specific channel

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2
     
    ========== OUTPUT ==========
    
    <current>
        -- float --
        The current output
        [A]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    channel = str(channel)
    
    instruction = 'I'+channel+'?'
    answer = instru.query('instruction')
    
    current = float(answer[3:9])
    
    command_local(address)
    
    ################## FUNCTION ###############################################
    
    return current



#%%
def command_range(address,channel,range_value):

    """
    ========== DESCRIPTION ==========

    This function can define the range of a specific output

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2
        
    <range_value>
        -- int --
        The range value (0  =   15 V (5 A)
                         1  =   35 V (3 A)
                         2  =   35 V (500 mA))

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    range_value = str(range_value)
    channel = str(channel)
    
    instruction = 'RANGE'+channel+' '+range_value
    
    ################## FUNCTION ###############################################
    
    instru.write(instruction)
    command_local(address)
    
    return 


#%%
def command_status(address,channel,status):

    """
    ========== DESCRIPTION ==========

    This function can define the status of a specific channel

    ========== FROM ==========

    Manual of QL355TP

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- int --
        The channel of the instrument from 1 to 2
        
    <status>
        -- int --
        The status (0   =   OFF
                    1   =   ON)

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    status = str(status)
    channel = str(channel)
    
    instruction = 'OP'+channel+' '+status
    
    ################## FUNCTION ###############################################
    
    instru.write(instruction)
    command_local(address)
    
    return 


