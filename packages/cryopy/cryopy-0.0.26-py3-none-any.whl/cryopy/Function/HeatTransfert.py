# -*- coding: utf-8 -*- 
def PhononThermalConductivity(Temperature,Parameter):

    """
    ========== DESCRIPTION ==========
    
    This function can return the thermal conductivity of a material by phonons

    ========== VALIDITY ==========
    
    Temperature < DebyeTemperature/10

    ========== FROM ==========
    
    POBELL (1995) - Matter and Methods at Low Temperatures - P. 62
    

    ========== INPUT ==========
    
    [Temperature]
        The temperature of the material in [K]
        
    [Parameter]
        A coefficient in [W].[m]**(-1).[K]**(-1)
 
    ========== OUTPUT ==========
    
    [PhononThermalConductivity]
        The thermal conductivity (phonon contribution) in [W].[m]**(-1).[K]**(-1)
        
    ========== STATUS ==========     
    
    Status : TBC
    
    ========= IMPROVEMENT ========== 
    

    """
    
    ################## INITIALISATION ####################################
    
    return Parameter*Temperature**3


#%% 
def ElectronSuperconductorThermalConductivity(Temperature,CriticalTemperature,Parameter):

    """
    ========== DESCRIPTION ==========
    
    This function can return the thermal conductivity of a material by electrons in superconducting state

    ========== VALIDITY ==========
    
    Temperature < CriticalTemperature

    ========== FROM ==========
    
    POBELL (1995) - Matter and Methods at Low Temperatures - P. 63
    

    ========== INPUT ==========
    
    [Temperature]
        The temperature of the material in [K]
        
    [CriticalTemperature]
        The critical temperature of the material in [K]
        
    [Parameter]
        A coefficient in [W].[m]**(-1).[K]**(-1)
 
    ========== OUTPUT ==========
    
    [ElectronSuperconductorThermalConductivity]
        The thermal conductivity (electron contribution - superconducting state) in [W].[m]**(-1).[K]**(-1)
        
    ========== STATUS ==========     
    
    Status : TBC
    
    ========= IMPROVEMENT ========== 
    

    """
    
    ################## MODULES ###############################################
    
    import numpy as np
    
    ################## INITIALISATION ####################################
    
    return Parameter*Temperature*np.exp(-1.76*CriticalTemperature/Temperature)


#%% 
def ElectronNormalThermalConductivity(Temperature,Parameter):

    """
    ========== DESCRIPTION ==========
    
    This function can return the thermal conductivity of a material by electrons in normal state

    ========== VALIDITY ==========
    
    Temperature > CriticalTemperature
    Temperature < 10 K

    ========== FROM ==========
    
    POBELL (1995) - Matter and Methods at Low Temperatures - P. 62
    

    ========== INPUT ==========
    
    [Temperature]
        The temperature of the material in [K]
        
    [Parameter]
        A coefficient in [W].[m]**(-1).[K]**(-1)
 
    ========== OUTPUT ==========
    
    [ElectronNormalThermalConductivity]
        The thermal conductivity (electron contribution - normal state) in [W].[m]**(-1).[K]**(-1)
        
    ========== STATUS ==========     
    
    Status : TBC
    
    ========= IMPROVEMENT ========== 
    

    """
    
    ################## MODULES ###############################################
    
    ################## INITIALISATION ####################################
    
    return Parameter*Temperature

#%% 
def ElectronThermalConductivity(Temperature,CriticalTemperature,Parameter):

    """
    ========== DESCRIPTION ==========
    
    This function can return the thermal conductivity of a material by electrons

    ========== VALIDITY ==========
    
    Temperature < 10 K

    ========== FROM ==========
    
    POBELL (1995) - Matter and Methods at Low Temperatures - P. 62
    

    ========== INPUT ==========
    
    [Temperature]
        The temperature of the material in [K]
        
    [Parameter]
        A coefficient in [W].[m]**(-1).[K]**(-1)
        
    [CriticalTemperature]
        The critical temperature of the material in [K]
        
    ========== OUTPUT ==========
    
    [ElectronThermalConductivity]
        The thermal conductivity (electron contribution) in [W].[m]**(-1).[K]**(-1)
        
    ========== STATUS ==========     
    
    Status : TBC
    
    ========= IMPROVEMENT ========== 
    

    """
    
    ################## MODULES ###############################################
    
    from cryopy.Function import HeatTransfert
    import numpy as np

    ################## INITIALISATION ####################################
    
    ParameterSuperconductor = Parameter
    ParameterNormal = Parameter*np.exp(-1.76)

    
    if Temperature <= CriticalTemperature:
        return HeatTransfert.ElectronSuperconductorThermalConductivity(Temperature,CriticalTemperature,ParameterSuperconductor)
    else:
        return HeatTransfert.ElectronNormalThermalConductivity(Temperature,ParameterNormal)

#%% 
def ThermalConductivity(Temperature,CriticalTemperature,ParameterElectron,ParameterPhonon):

    """
    ========== DESCRIPTION ==========
    
    This function can return the thermal conductivity of a material

    ========== VALIDITY ==========
    
    Temperature < 10 K

    ========== FROM ==========
    
    POBELL (1995) - Matter and Methods at Low Temperatures - P. 62
    

    ========== INPUT ==========
    
    [Temperature]
        The temperature of the material in [K]
        
    [CriticalTemperature]
        The critical temperature of the material in [K]
        
    [ParameterElectron]
        A coefficient in [W].[m]**(-1).[K]**(-1)

    [ParameterPhonon]
        A coefficient in [W].[m]**(-1).[K]**(-1)
        
    ========== OUTPUT ==========
    
    [ThermalConductivity]
        The thermal conductivity in [W].[m]**(-1).[K]**(-1)
        
    ========== STATUS ==========     
    
    Status : TBC
    
    ========= IMPROVEMENT ========== 
    

    """
    
    ################## MODULES ###############################################
    
    from cryopy.Function import HeatTransfert
    import numpy as np

    ################## INITIALISATION ####################################
    
    return HeatTransfert.ElectronThermalConductivity(Temperature,CriticalTemperature,ParameterElectron)+HeatTransfert.PhononThermalConductivity(Temperature,ParameterPhonon)


                                                                                                                                                
                                                                                                                                                
                                                                                                                                                
                                                                                                                                                
                                                                                                                                                
                                                                                                                                                