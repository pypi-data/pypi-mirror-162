#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def command_reset(address,channel):

    """
    ========== DESCRIPTION ==========

    This function can reset the parameters of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.reset()'

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 


#%%
def command_current_measure_autorange(address,channel,autorange):

    """
    ========== DESCRIPTION ==========

    This function can enable the autorange of the current measurement
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <autorange>
        -- string --
        The autorange status ('ON' or 'OFF')
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.measure.autorangei=smu'+channel+'.AUTORANGE_'+autorange

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_voltage_measure_autorange(address,channel,autorange):

    """
    ========== DESCRIPTION ==========

    This function can enable the autorange of the voltage measurement
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <autorange>
        -- string --
        The autorange status ('ON' or 'OFF')
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.measure.autorangev=smu'+channel+'.AUTORANGE_'+autorange

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_current_measure_range(address,channel,range_value):

    """
    ========== DESCRIPTION ==========

    This function can setup the range of the current measurement
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <range_value>
        -- int --
        The range value (0 = 100 nA,
                         1 = 1 uA,
                         2 = 10 uA,
                         3 = 100 uA,
                         4 = 1 mA,
                         5 = 10 mA,
                         6 = 100 mA,
                         7 = 1 A,
                         8 = 3 A)
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    intensity_range = ['100e-9','1e-6','10e-6','100e-6','1e-3','10e-3','100e-3','1','3']
    
    range_value = intensity_range[range_value]
    
    command = 'smu'+channel+'.measure.rangei='+range_value

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_voltage_measure_range(address,channel,range_value):

    """
    ========== DESCRIPTION ==========

    This function can setup the range of the voltage measurement
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <range_value>
        -- int --
        The range value (0 = 100 mV,
                         1 = 1 V,
                         2 = 6 V,
                         3 = 40 V)
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    intensity_range = ['100e-3','1','6','40']
    
    range_value = intensity_range[range_value]
    
    command = 'smu'+channel+'.measure.rangev='+range_value

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 


#%%
def query_current(address,channel):

    """
    ========== DESCRIPTION ==========

    This function can return the measured current of a given channel on 
    Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')
        
    ========== OUTPUT ==========

    <current>
        -- float --
        The measured current
        [A]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    command = 'print(smu'+channel+'.measure.i())'
    answer = instru.query(command)

    ################## FUNCTION ###############################################
    
    answer = float(answer)
    
    return answer

#%%
def query_voltage(address,channel):

    """
    ========== DESCRIPTION ==========

    This function can return the measured voltage of a given channel on 
    Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')
        
    ========== OUTPUT ==========

    <voltage>
        -- float --
        The measured voltage
        [V]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    command = 'print(smu'+channel+'.measure.v())'
    answer = instru.query(command)

    ################## FUNCTION ###############################################
    
    answer = float(answer)
    
    return answer

#%%
def query_resistance(address,channel):

    """
    ========== DESCRIPTION ==========

    This function can return the measured resistance of a given channel on 
    Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')
        
    ========== OUTPUT ==========

    <resistance>
        -- float --
        The measured resistance
        [Ohm]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    command = 'print(smu'+channel+'.measure.r())'
    answer = instru.query(command)

    ################## FUNCTION ###############################################
    
    answer = float(answer)
    
    return answer

#%%
def query_power(address,channel):

    """
    ========== DESCRIPTION ==========

    This function can return the measured power of a given channel on 
    Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')
        
    ========== OUTPUT ==========

    <voltage>
        -- float --
        The measured voltage
        [V]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    command = 'print(smu'+channel+'.measure.p())'
    answer = instru.query(command)

    ################## FUNCTION ###############################################
    
    answer = float(answer)
    
    return answer

#%%
def command_current_source_autorange(address,channel,autorange):

    """
    ========== DESCRIPTION ==========

    This function can enable the autorange of the current source
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <autorange>
        -- string --
        The autorange status ('ON' or 'OFF')
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.autorangei=smu'+channel+'.AUTORANGE_'+autorange

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_voltage_source_autorange(address,channel,autorange):

    """
    ========== DESCRIPTION ==========

    This function can enable the autorange of the voltage source
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <autorange>
        -- string --
        The autorange status ('ON' or 'OFF')
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.autorangev=smu'+channel+'.AUTORANGE_'+autorange

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_source(address,channel,source):

    """
    ========== DESCRIPTION ==========

    This function can define the source type of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <source>
        -- string --
        The source type ('VOLTS' or 'AMPS')
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.func=smu'+channel+'.OUTPUT_'+source

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_source_current_value(address,channel,value):

    """
    ========== DESCRIPTION ==========

    This function can define the source current value of a given channel 
    on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <value>
        -- float --
        The current value
        [A]
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.leveli='+str(value)

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_source_voltage_value(address,channel,value):

    """
    ========== DESCRIPTION ==========

    This function can define the source voltage value of a given channel 
    on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <value>
        -- float --
        The voltage value
        [V]
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.levelv='+str(value)

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_source_current_limit(address,channel,limit):

    """
    ========== DESCRIPTION ==========

    This function can define the source current value limit of a given channel 
    on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <limit>
        -- float --
        The current limit value
        [A]
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.limiti='+str(value)

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_source_voltage_limit(address,channel,limit):

    """
    ========== DESCRIPTION ==========

    This function can define the source voltage limit value of a given channel 
    on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <limit>
        -- float --
        The voltage limit value
        [V]
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.limitv='+str(value)

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_source_power_limit(address,channel,limit):

    """
    ========== DESCRIPTION ==========

    This function can define the source power limit value of a given channel 
    on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <limit>
        -- float --
        The power limit value
        [W]
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.limitp='+str(value)

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_source_status(address,channel,status):

    """
    ========== DESCRIPTION ==========

    This function can define the source power limit value of a given channel 
    on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <status>
        -- string --
        The status of the output source ('ON' or 'OFF')
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    command = 'smu'+channel+'.source.output=smu'+channel+'.OUTPUT_'+status

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return

#%%
def command_current_source_range(address,channel,range_value):

    """
    ========== DESCRIPTION ==========

    This function can setup the range of the current source
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <range_value>
        -- int --
        The range value (0 = 100 nA,
                         1 = 1 uA,
                         2 = 10 uA,
                         3 = 100 uA,
                         4 = 1 mA,
                         5 = 10 mA,
                         6 = 100 mA,
                         7 = 1 A,
                         8 = 3 A)
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    intensity_range = ['100e-9','1e-6','10e-6','100e-6','1e-3','10e-3','100e-3','1','3']
    
    range_value = intensity_range[range_value]
    
    command = 'smu'+channel+'.source.rangei='+range_value

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 

#%%
def command_voltage_source_range(address,channel,range_value):

    """
    ========== DESCRIPTION ==========

    This function can setup the range of the voltage source
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <range_value>
        -- int --
        The range value (0 = 100 mV,
                         1 = 1 V,
                         2 = 6 V,
                         3 = 40 V)
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    intensity_range = ['100e-3','1','6','40']
    
    range_value = intensity_range[range_value]
    
    command = 'smu'+channel+'.source.rangev='+range_value

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return 


#%%
def command_sense_type(address,channel,sense_type):

    """
    ========== DESCRIPTION ==========

    This function can setup the sense type
    of a given channel on Keithley 2602

    ========== FROM ==========

    Manual of Keithley 2602

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument 
        
    <channel>
        -- string --
        The channel of the instrument ('a' or 'b')

    <sense_type>
        -- string --
        The sense type ('LOCAL' or 'REMOTE')
     
    ========== OUTPUT ==========

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    
    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    command = 'smu'+channel+'.sense=smu'+channel+'.SENSE_'+sense_type

    ################## FUNCTION ###############################################
    
    instru.write(command)
    
    return
