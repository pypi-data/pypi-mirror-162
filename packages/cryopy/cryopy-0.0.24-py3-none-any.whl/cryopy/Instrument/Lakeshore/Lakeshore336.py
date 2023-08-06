# -*- coding: utf-8 -*-

#%%
def query_identification(address):

    """
    ========== DESCRIPTION ==========

    This function can return the identification of the LakeShore Model 336
    Cryogenic Temperature Controller

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')

    ========== OUTPUT ==========

    <manufacturer>
        -- string --
        Should be "LSCI"

    <model>
        -- string --
        Should be "MODEL336"

    <instrument_serial>
        -- string --
        Depend on your instrument

    <option_serial>
        -- string --
        Depend on your instrument

    <firmware_version>
        -- string --
        Depend on your instrument

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    from cryopy import cryopy.Instrument.Lakeshore.Lakeshore336
    manufacturer,model,instrument_serial,option_serial,firmware_version = Lakeshore336.query_identification('GPIB0::15::INSTR')

    """

    ################## MODULES ###############################################

    import pyvisa
 
    ################## INITIALISATION ########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    answer = instru.query('*IDN?')
    
    manufacturer = answer[0:4]
    model = answer[5:13]
    instrument_serial = answer[14:21]
    option_serial = answer[22:29]
    firmware_version = answer[30:33]

    return manufacturer,model,instrument_serial,option_serial,firmware_version


#%%
def query_temperature(address):

    """
    ========== DESCRIPTION ==========

    This function can return the measured temperatures of the four channels
    A, B, C and D of the LakeShore Model 336 Cryogenic Temperature Controller

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')

    ========== OUTPUT ==========

    <temperature_a>
        -- float --
        The measured temperature of the channel A
        [K]

    <temperature_b>
        -- float --
        The measured temperature of the channel B
        [K]

    <temperature_c>
        -- float --
        The measured temperature of the channel C
        [K]

    <temperature_d>
        -- float --
        The measured temperature of the channel D
        [K]

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    from cryopy import cryopy.Instrument.Lakeshore.Lakeshore336
    
    temperature_a,temperature_b,temperature_c,temperature_d = Lakeshore336.temperature_query('GPIB0::15::INSTR')


    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    answer = instru.query('KRDG? 0')
    
    temperature_a = float(answer[0:8])
    temperature_b = float(answer[9:17])
    temperature_c = float(answer[18:26])
    temperature_d = float(answer[27:35])

    return temperature_a,temperature_b,temperature_c,temperature_d

#%% 
def query_input_reading_status(address):
    """
    ========== DESCRIPTION ==========

    This function can return the input reading status

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')

    ========== OUTPUT ==========

    <status_indicator>
        -- string --
        The status of input reading
        []

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    from cryopy import cryopy.Instrument.Lakeshore.Lakeshore336
    
    input_reading_status = Lakeshore336.input_reading_status_query('GPIB0::15::INSTR')

    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    answer = instru.query('RDGST?')
    
    ################## FUNCTION ###############################################
    
    if int(answer[0:3])==0:
        return 'valid reading'
    
    if int(answer[0:3])==1:
        return 'invalid reading'
    
    if int(answer[0:3])==16:
        return 'temp underrange'
    
    if int(answer[0:3])==32:
        return 'temp overrange'
    
    if int(answer[0:3])==64:
        return 'sensor unit zero'
    
    if int(answer[0:3])==128:
        return 'sensor unit overrange'


#%%
def query_pid_parameters(address, output):
    """
    ========== DESCRIPTION ==========

    This function can return the PID parameters

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')

    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2)
        []

    ========== OUTPUT ==========

    <p>
        -- float --
        The P parameter
        []

    <i>
        -- float --
        The I parameter
        []
        
    <d>
        -- float --
        The D parameter
        []
        
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========

    from cryopy import cryopy.Instrument.Lakeshore.Lakeshore336
    
    p,i,d= Lakeshore336.pid_parameters_query('GPIB0::15::INSTR')

    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    output = str(output)
    answer = instru.query('PID? ' + output)
    
    ################## FUNCTION ###############################################
    
    p = int(answer[0:5])
    i = int(answer[8:13])
    d = int(answer[16:20])

    return p,i,d

#%%
def command_pid_parameters(address,p,i,d,output):
    """
    ========== DESCRIPTION ==========

    This function can setup the PID parameters on specific output

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <p>
        -- float --
        The P parameter
        []

    <i>
        -- float --
        The I parameter
        []
        
    <d>
        -- float --
        The D parameter
        []
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2)
        []

    ========== OUTPUT ==========
        
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    from cryopy import cryopy.Instrument.Lakeshore.Lakeshore336
    
    Lakeshore336.pid_parameters_command('GPIB0::15::INSTR',P,I,D)

    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    p = str(p)
    i = str(i)
    d = str(d)
    output = str(output)
    
    answer = 'PID '+output+','+p+','+i+','+d
    
    ################## FUNCTION ###############################################
    
    instru.write(answer)
    
    return 

#%%
def command_remote_interface_mode(address,mode):
    """
    ========== DESCRIPTION ==========

    This function can setup the remote interface mode command

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <mode>
        -- int --
        The mode of the interface command (0 = local, 
                                           1 = remote, 
                                           2 = remote with local lockout)
        []

    ========== OUTPUT ==========
        
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    "I want to setup the interface mode to remote"
    
    from cryopy import cryopy.Instrument.Lakeshore.Lakeshore336
    
    Lakeshore336.remote_interface_mode_command('GPIB0::15::INSTR',1)

    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    mode = str(mode)

    ################## FUNCTION ###############################################
    
    instru.write('MODE '+mode)
    
    return 

#%%
def command_autotune(address,output,mode):
    """
    ========== DESCRIPTION ==========

    This function can setup the autotune command on specific output

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2,
                            3 = output 3,
                            4 = output 4)
        []
        
    <mode>
        -- int --
        The mode of the interface command (0 = P only,
                                           1 = P and I, 
                                           2 = P, I and D)
        []
        
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    "I want to setup the autotune with P and I parameters on output 2"
    
    from cryopy import cryopy.Instrument.Lakeshore.Lakeshore336
    
    Lakeshore336.autotune_command('GPIB0::15::INSTR',2,1)

    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    output = str(output)
    mode = str(mode)
    
    request = 'ATUNE '+output+','+mode
    
    ################## FUNCTION ###############################################
    
    instru.write(request)
    
    return 


#%%
def command_heater_setup(address,output,heater_resistance,max_current,max_user_current,current_or_power):
    """
    ========== DESCRIPTION ==========

    This function can setup the heater parameters

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2)
        []
        
    <heater_resistance>
        -- int --
        The heater resistance (1 = 25 Ohms,
                               2 = 50 Ohms)
        []

    <max_current>
        -- int --
        The maximum current (0 = user specified
                             1 = 0.707 A,
                             2 = 1 A,
                             3 = 1.141 A,
                             4 = 2 A)
        []        

    <max_user_current>
        -- int --
        The maxumum current setup by user
        [A]        
        
    <current_or_power>
        -- int --
        Is output displayed as current or power(1 = current,
                                                2 = power)
        []        
          
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========


    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)
    
    output = str(output)
    heater_resistance = str(heater_resistance)
    max_current = str(max_current)
    max_user_current = str(max_user_current)
    current_or_power = str(current_or_power)
    
    request = 'HTRSET '+output+','+heater_resistance+','+max_current+','+max_user_current+','+current_or_power
    
    ################## FUNCTION ###############################################
    
    instru.write(request)
    
    return 

#%%
def query_heater_setup(address,output):
    """
    ========== DESCRIPTION ==========

    This function can ask the heater parameters

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2)
        []
        
    ========== OUTPUT ==========
    
    <heater_resistance>
        -- int --
        The heater resistance (1 = 25 Ohms,
                               2 = 50 Ohms)
        []

    <max_current>
        -- int --
        The maximum current (0 = user specified
                             1 = 0.707 A,
                             2 = 1 A,
                             3 = 1.141 A,
                             4 = 2 A)
        []        

    <max_user_current>
        -- float --
        The maxumum current setup by user
        [A]        
        
    <current_or_power>
        -- int --
        Is output displayed as current or power(1 = current,
                                                2 = power)
        []        
          
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========


    """

    ################## MODULES ################################################

    import pyvisa

    instru = pyvisa.ResourceManager().open_resource(address)

    output = str(output)
    answer = instru.query('HTRSET? ' + output)
    
    ################## FUNCTION ###############################################
    
    heater_resistance = int(answer[0:1])
    max_current = int(answer[2:3])
    max_user_current = float(answer[5:10])
    current_or_power = int(answer[11:12])
    
    return heater_resistance,max_current,max_user_current,current_or_power


#%%
def command_setpoint(address,output,value):
    """
    ========== DESCRIPTION ==========

    This function can setup the setpoint of a specific output

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2)
        []
        
    <value>
        -- float --
        The setpoint temperature 
        [K]
        
          
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========


    """

    ################## MODULES ################################################

    import pyvisa

    instru = pyvisa.ResourceManager().open_resource(address)

    output = str(output)
    value = str(value)
    
    ################## FUNCTION ###############################################

    instru.write('SETP ' + output+','+value)
    
    return 

#%%
def query_setpoint(address,output):
    """
    ========== DESCRIPTION ==========

    This function can ask the setpoint of a specific output

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2)
        []
          
    ========== OUTPUT ==========
    
    <setpoint>
        -- float --
        The setpoint temperature 
        [K]
    
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========


    """

    ################## MODULES ################################################

    import pyvisa

    instru = pyvisa.ResourceManager().open_resource(address)

    output = str(output)
    answer = instru.query('SETP? ' + output)
    
    ################## FUNCTION ###############################################

    setpoint = float(answer)
    
    return setpoint 

#%%
def command_heater_range(address,output,value):
    """
    ========== DESCRIPTION ==========

    This function can setup the range of a specific heater

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2)
        []
        
    <value>
        -- int --
        The wanted range (0 = Off,
                          1 = Low,
                          2 = Medium,
                          3 = High)
        []
        
          
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========


    """

    ################## MODULES ################################################

    import pyvisa

    instru = pyvisa.ResourceManager().open_resource(address)

    output = str(output)
    value = str(value)
    
    ################## FUNCTION ###############################################

    instru.write('RANGE ' + output+','+value)
    
    return 

#%%
def query_heater_range(address,output):
    """
    ========== DESCRIPTION ==========

    This function can ask the heater range

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2)
        []
          
    ========== OUTPUT ==========
    
    <value>
        -- int --
        The wanted range (0 = Off,
                          1 = Low,
                          2 = Medium,
                          3 = High)
        []
        
    
    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========


    """

    ################## MODULES ################################################

    import pyvisa

    instru = pyvisa.ResourceManager().open_resource(address)

    output = str(output)
    answer = instru.query('RANGE? ' + output)
    
    ################## FUNCTION ###############################################

    value = int(answer)
    
    return value

#%%
def command_outmode(address,output,mode,channel,powerup):
    """
    ========== DESCRIPTION ==========

    This function can setup the output mode

    ========== FROM ==========

    Manual of Lakeshore 336 on https://www.lakeshore.com/

    ========== INPUT ==========

    <address>
        -- string --
        The address of the instrument (e.g. 'GPIB0::15::INSTR')
        
    <output>
        -- int --
        The channel output (1 = output 1,
                            2 = output 2,
                            3 = output 3,
                            4 = output 4)
        []   
    
    <mode>
        -- int --
        The output mode (0 = Off,
                         1 = Closed-loop,
                         2 = Zone,
                         3 = Open loop,
                         4 = Monitor out,
                         5 = Warmup summply)
        []
    
    <channel>
        -- int --
        The channel (0 = None,
                     1 = Channel A,
                     2 = Channel B,
                     3 = Channel C,
                     4 = Channel D)
        []        
    
    <powerup>
        -- int --
        The powerup status (0 = Powerup enable off,
                            1 = Powerup enable on)
        []        

    ========== STATUS ==========

    Status : Checked

    ========= EXAMPLE ==========
    
    import cryopy
    cryopy.Instrument.Lakeshore336.command_outmode('GPIB0::15::INSTR',1,1,1,0)

    """

    ################## MODULES ################################################

    import pyvisa

    ################## INITIALISATION #########################################

    instru = pyvisa.ResourceManager().open_resource(address)

    output = str(output)
    mode = str(mode)
    channel = str(channel)
    powerup = str(powerup)
    
    answer = 'OUTMODE '+output+','+mode+','+channel+','+powerup
    
    ################## FUNCTION ###############################################
    
    instru.write(answer)
    
    return 