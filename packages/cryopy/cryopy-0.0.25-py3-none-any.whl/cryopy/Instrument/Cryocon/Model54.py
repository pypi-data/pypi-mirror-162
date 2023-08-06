#!/usr/bin/env python3

#%%
def query_identification(address):

    """
    ========== DESCRIPTION ==========

    This function can return the identification of the Cryocon Model 54

    ========== FROM ==========

    Manual of Cryo-con Model 54

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')

    ========== OUTPUT ==========

    <manufacturer>
        -- string --
        Should be "Cryo-con"

    <model>
        -- string --
        Should be "Model 54"

    <serial>
        -- string --
        Depend on your instrument

    <firmware_version>
        -- string --
        Depend on your instrument

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    from cryopy import Instrument.Cryocon.Model54
    
    manufacturer,model,serial,firmware_version = Model54.query_identification('GPIB0::15::INSTR')

    """

    ################## MODULES ###############################################

    import pyvisa
 
    ################## INITIALISATION ########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    answer = instru.query('*IDN?')
    
    manufacturer = answer[0:8]
    model = answer[9:17]
    serial = answer[18:24]
    firmware_version = answer[25:30]

    return manufacturer,model,serial,firmware_version

#%%
def query_temperature(address,channel):

    """
    ========== DESCRIPTION ==========

    This function can return the temperature of a given channel of the Cryocon Model 54

    ========== FROM ==========

    Manual of Cryo-con Model 54

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <channel>
        -- string --
        The channel ('a','b','c' or 'd')

    ========== OUTPUT ==========

    <temperature>
        -- float --
        The temperature measured by the channel
        [K]
        
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    from cryopy import Instrument.Cryocon.Model54
    
    temperature= Model54.query_temperature('GPIB0::15::INSTR','a')

    """

    ################## MODULES ###############################################

    import pyvisa
 
    ################## INITIALISATION ########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    answer = instru.query('input? '+channel)
    
    temperature = float(answer)

    return temperature