#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def query_input(address):

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

