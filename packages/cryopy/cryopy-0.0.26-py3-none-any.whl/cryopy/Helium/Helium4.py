# -*- coding: utf-8 -*-
#%%
def molar_volume(temperature,pressure):
    
    """
    ========== DESCRIPTION ==========

    This function return the molar volume of a mole of Helium 3

    ========== VALIDITY ==========

    <temperature> : [0.05 -> 1.8]
    <pressure> : [0 -> 15.7e5]


    ========== FROM ==========

    TANAKA (2000) - Molar volume of pure liquide 4He : dependence on 
    temperature (50-1000mK) and pressure (0-1.57 MPa) - Equation (25)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 3
        [K]

    <pressure>
        -- float --
        The pressure of Helium 3
        [Pa]

    ========== OUTPUT ==========

    <molar_volume>
        -- float --
        The molar volume of Helium 4
        [m]**3.[mol]**(-1)

    ========== STATUS ==========

    Status : Checked
    
    ========== UPDATE ==========
    
    2021-05-07:
        On Chaudhry et al. (2012) - P59, we can continue up to 1.8K with
        an error of 0.1% 


    """

    ################## MODULES ################################################

    import numpy as np
    import pandas as pd
    from scipy.special import erfc

    ################## CONDITIONS #############################################

    assert pressure <= 15.7e5 and pressure >= 0 , 'The function '\
        ' Helium4.molar_volume is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 1.8 and temperature >= 0.05 ,'The function '\
        ' Helium4.molar_volume is not defined for '\
            'T = '+str(temperature)+' K'    

    ################## INITIALISATION #########################################
    
    coefficients = pd.DataFrame(np.array([[2.757930e-5,8.618,1.863e8,2.191],
                                          [-3.361585e-12,-7.487e-7,7.664e6,-1.702e-7],
                                          [1.602419e-18,5.308e-14,np.nan,np.nan],
                                          [-1.072604e-24,np.nan,np.nan,np.nan],
                                          [7.979064e-31,np.nan,np.nan,np.nan],
                                          [-5.356076e-37,np.nan,np.nan,np.nan],
                                          [2.703689e-43,np.nan,np.nan,np.nan],
                                          [-9.004790e-50,np.nan,np.nan,np.nan],
                                          [1.725962e-56,np.nan,np.nan,np.nan],
                                          [-1.429411e-63,np.nan,np.nan,np.nan]]),
                                        columns = ['V','Delta','A','B'])    
        
    pc = -1.00170e6
    
    ################## FUNCTION ###############################################
    
    sumV = 0
    for i in range(10):
        sumV = sumV+coefficients.V[i]*pressure**i
        
    sumA = (coefficients.A[0]/((pressure-pc)**2)+coefficients.A[1]/((pressure-pc)**(5/3)))*temperature**4/4
      
    sumB = coefficients.B[0]+coefficients.B[1]*pressure
    
    sumC = 0
    
    for i in range(3):
        sumC = sumC+coefficients.Delta[i]*pressure**i  
    
    return sumV*(1+sumA-sumB*erfc((sumC/temperature)**0.5))


#%% 
def molar_mass():

    """
    ========== DESCRIPTION ==========

    Return the constant molar mass of a single Helium 4 atom.

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    P. J. Mohr, B. N. Taylor, and D. B. Newell, Rev. Mod. Phys. 84, 1531 (2012).

    ========== OUTPUT ==========

    <molar_mass>
        -- float --
    	The molar mass of a single atom of Helium 3
        [g].[mol]**(-1)

    ========== STATUS ==========

    Status : Checked

    """
        
    ################## RETURN #################################################

    return 4.002602 


#%%
def molar_specific_heat(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the molar specific heat of pure Helium 4

    ========== VALIDITY ==========

    <temperature> : [0 -> 1.8]
    <pressure> : [0]

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (46)
   
    CHAUDHRY - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A15)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    ========== OUTPUT ==========

    <molar_specific_heat>
        -- float --
        The molar specific heat of pure Helium 4
        [J].[K]**(-1).[mol]**(-1)


    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    This function requires the implementation of pressure changes


    """
    
    ################## CONDITIONS #############################################

    assert pressure <= 0 and pressure >= 0 , 'The function '\
        ' Helium4.molar_specific_heat is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 1.8 and temperature >= 0.000 ,'The function '\
        ' Helium4.molar_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################
    
    import numpy as np
    import pandas as pd
    
    ################## INITIALISATION #########################################
    
    result = 0
    coefficients = pd.DataFrame(np.array([[0.08137],
                                          [0],
                                          [-0.0528],
                                          [0.05089],
                                          [0.019]]),
                                columns = ['B'])

    ################## FUNCTION ###############################################
    
    
    if temperature <= 0.4 and temperature >= 0:
        for j in [0,1,2,3,4]:
            result = result + coefficients.B[j]*temperature**(j+3)
        return result 

    else:
        first = 82.180127 * temperature**3 - 87.45899 * temperature**5 + 129.12758 * temperature**6 - 6.6314726 * temperature**7
        second = 70198.836 * (8.8955141/temperature)**(3/2) * np.exp(-8.8955141/temperature) * (1 + (temperature/8.8955141) + 0.75*((temperature/8.8955141)**2))
        third = (10244.198/temperature) * (22.890183/temperature)**2 * np.exp(-22.890183/temperature) * (1 - 2*(temperature/22.890183))
        value = (first + second + third) * 1e-3
        
        return value


#%%
def molar_enthalpy(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function can return the molar enthalpy of Helium 4

    ========== VALIDITY ==========

    <temperature> : [0 -> 0.400]
    <pressure> : [0]

    ========== FROM ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Table (17)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    ========== OUTPUT ==========

    <molar_enthalpy>
        -- float --
        The molar enthalpy of pure Helium 4
        [J].[mol]**(-1)


    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    This function requires the implementation of pressure changes


    """
    
    ################## CONDITIONS #############################################

    assert pressure <= 0 and pressure >= 0 , 'The function '\
        ' Helium4.molar_enthalpy is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 0.400 and temperature >= 0.000 ,'The function '\
        ' Helium4.molar_enthalpy is not defined for '\
            'T = '+str(temperature)+' K'    
    
    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = [ 3.19794159e-03, -6.48309258e-03,  2.19933824e-02, -2.09571258e-04,
    1.23491357e-05, -2.67718222e-07,  1.07444578e-09]
    polynom = np.poly1d(coefficients)

    ################## FUNCTION ###############################################
    
    return polynom(temperature)


#%%
def molar_entropy(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function can return the molar entropy of Helium 4

    ========== VALIDITY ==========

    <temperature> : [0 -> 0.400]
    <pressure> : [0]

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Table (17)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    ========== OUTPUT ==========

    <molar_entropy>
        -- float --
        The molar entropy of pure Helium 4
        [J].[K]**(-1).[mol]**(-1)


    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    This function requires the implementation of pressure changes


    """

    ################## MODULES ################################################

    import numpy as np

    ################## CONDITIONS #############################################

    assert pressure <= 0 and pressure >= 0 , 'The function '\
        ' Helium3.molar_entropy is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 0.400 and temperature >= 0.000 ,'The function '\
        ' Helium3.molar_entropy is not defined for '\
            'T = '+str(temperature)+' K'    

    ################## INITIALISATION #########################################

    coefficients = [-2.08468571e-03,  2.73347674e-03,
                    -5.46990881e-03,  2.81129291e-02,
                    -7.81349812e-05,  2.17304932e-06,
                    -1.05591438e-08]
    polynom = np.poly1d(coefficients)

    ################## FUNCTION ###############################################

    return polynom(temperature)


#%%
def chemical_potential(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the chemical potential of Helium 4

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (38)
    
    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    ========== OUTPUT ==========

    <chemical_potential>
        -- float --
        The chemical potential of pure Helium 4
        [J].[mol]**(-1)

    ========== STATUS ==========

    Status : In progress (need to be verified with new values of pressure)

    """

    ################## MODULES ################################################

    from cryopy.Helium import Helium4

    ################## RETURN #################################################

    return Helium4.molar_enthalpy(temperature,pressure)-temperature*Helium4.molar_entropy(temperature,pressure)


#%% 
def dynamic_viscosity(temperature):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the dynamic viscosity of pure helium 4

    ========== VALIDITY ==========
    
    <temperature> : [273.15->1800]

    ========== FROM ==========
    
    KPetersen, H. (1970). The properties of helium: Density, specific heats, 
    viscosity, and thermal conductivity at pressures from 1 to 100 bar and 
    from room temperature to about 1800 K. Risø National Laboratory. Denmark. 
    Forskningscenter Risoe. Risoe-R No. 224

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]
        
    ========== OUTPUT ==========
    
    <dynamic_viscosity>
        -- float --
        The dynamic viscosity of Helium 4
        [Pa].[s]
    
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    
    ################## CONDITIONS #############################################
    
    assert temperature <= 1800 and temperature >= 273.15 ,'The function '\
        ' Helium4.dynamic_viscosity is not defined for '\
            'T = '+str(temperature)+' K'


    ################## FUNCTION ###############################################

    return 3.674e-7*temperature**0.7

#%% 
def density(temperature,pressure):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the density of pure helium 4

    ========== VALIDITY ==========
    
    <temperature> : [273.15->1800]
    <pressure> : [0->100e5]

    ========== FROM ==========
    
    KPetersen, H. (1970). The properties of helium: Density, specific heats, 
    viscosity, and thermal conductivity at pressures from 1 to 100 bar and 
    from room temperature to about 1800 K. Risø National Laboratory. Denmark. 
    Forskningscenter Risoe. Risoe-R No. 224

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]
        
    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]
        
    ========== OUTPUT ==========
    
    <density>
        -- float --
        The density of Helium 4
        [kg].[m]**3
    
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    
    ################## CONDITIONS #############################################
    
    assert temperature <= 1800 and temperature >= 273.15 ,'The function '\
        ' Helium4.density is not defined for '\
            'T = '+str(temperature)+' K'
            
    assert pressure <= 100e5 and pressure >= 0 ,'The function '\
        ' Helium4.density is not defined for '\
            'P = '+str(temperature)+' Pa'

    ################## INITIALISATION #########################################
    
    # convert [Pa] to [Bar]
    pressure = pressure*1e-5

    ################## FUNCTION ###############################################

    return 48.18*pressure/temperature*(1+0.4446*pressure/(temperature**1.2))**(-1)


#%% 
def compressibility_factor(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function return the compressibility factor of pure helium 4

     ========== VALIDITY ==========
     
     <temperature> : [273.15->1800]
     <pressure> : [0->100e5]

     ========== FROM ==========
     
     KPetersen, H. (1970). The properties of helium: Density, specific heats, 
     viscosity, and thermal conductivity at pressures from 1 to 100 bar and 
     from room temperature to about 1800 K. Risø National Laboratory. Denmark. 
     Forskningscenter Risoe. Risoe-R No. 224

     ========== INPUT ==========

     <temperature>
         -- float --
         The temperature of Helium 4
         [K]
         
     <pressure>
         -- float --
         The pressure of Helium 4
         [Pa]
         
     ========== OUTPUT ==========
     
     <compressibility_factor>
         -- float --
         The compressibility factor of Helium 4
         [Ø]
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## CONDITIONS #############################################
     
     assert temperature <= 1800 and temperature >= 273.15 ,'The function '\
         ' Helium4.compressibility_factor is not defined for '\
             'T = '+str(temperature)+' K'
             
     assert pressure <= 100e5 and pressure >= 0 ,'The function '\
         ' Helium4.compressibility_factor is not defined for '\
             'P = '+str(temperature)+' Pa'

     ################## MODULES ################################################
     
     #from cryopy import Helium4

     ################## INITIALISATION #########################################
     
     # convert [Pa] to [Bar]
     pressure = pressure*1e-5

     ################## FUNCTION ###############################################

     return 1 + 0.4446*pressure/(temperature**1.2)
 
    
#%% 
def thermal_conductivity(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function return the compressibility factor of pure helium 4

     ========== VALIDITY ==========
     
     <temperature> : [273.15->1800]
     <pressure> : [0->100e5]

     ========== FROM ==========
     
     KPetersen, H. (1970). The properties of helium: Density, specific heats, 
     viscosity, and thermal conductivity at pressures from 1 to 100 bar and 
     from room temperature to about 1800 K. Risø National Laboratory. Denmark. 
     Forskningscenter Risoe. Risoe-R No. 224

     ========== INPUT ==========

     <temperature>
         -- float --
         The temperature of Helium 4
         [K]
         
     <pressure>
         -- float --
         The pressure of Helium 4
         [Pa]
         
     ========== OUTPUT ==========
     
     <thermal_conductivity>
         -- float --
         The thermal conductivity of Helium 4
         [W].[m]**(-1).[K]**(-1)
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## CONDITIONS #############################################
     
     assert temperature <= 1800 and temperature >= 273.15 ,'The function '\
         ' Helium4.thermal_conductivity is not defined for '\
             'T = '+str(temperature)+' K'
             
     assert pressure <= 100e5 and pressure >= 0 ,'The function '\
         ' Helium4.thermal_conductivity is not defined for '\
             'P = '+str(temperature)+' Pa'

     ################## INITIALISATION #########################################
     
     # convert [Pa] to [Bar]
     pressure = pressure*1e-5

     ################## FUNCTION ###############################################

     return 2.682e-3*(1+1.123e-3*pressure)*temperature**(0.71*(1-2e-4*pressure))
 
#%% 
def prandtl_number(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function return the Prandtl number of pure Helium 4

     ========== VALIDITY ==========
     
     <temperature> : [273.15->1800]
     <pressure> : [0->100e5]

     ========== FROM ==========
     
     KPetersen, H. (1970). The properties of helium: Density, specific heats, 
     viscosity, and thermal conductivity at pressures from 1 to 100 bar and 
     from room temperature to about 1800 K. Risø National Laboratory. Denmark. 
     Forskningscenter Risoe. Risoe-R No. 224

     ========== INPUT ==========

     <temperature>
         -- float --
         The temperature of Helium 4
         [K]
         
     <pressure>
         -- float --
         The pressure of Helium 4
         [Pa]
         
     ========== OUTPUT ==========
     
     <prandtl_number>
         -- float --
         The Prandtl number of pure Helium 4
         [Ø]
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## CONDITIONS ############################################
     
     assert temperature <= 1800 and temperature >= 273.15 ,'The function '\
         ' Helium4.prandtl_number is not defined for '\
             'T = '+str(temperature)+' K'
             
     assert pressure <= 100e5 and pressure >= 0 ,'The function '\
         ' Helium4.prandtl_number is not defined for '\
             'P = '+str(temperature)+' Pa'

     ################## INITIALISATION ########################################
     
     # convert [Pa] to [Bar]
     pressure = pressure*1e-5

     ################## FUNCTION ##############################################

     return 0.7117/(1+1.123e-3*pressure)*temperature**(-0.01*1.42e-4*pressure)
                
#%%
def is_liquid(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function determine if the current Helium 4 is liquid or not

     ========== INPUT ==========

     <temperature>
         -- float --
         The temperature of Helium 4
         [K]
         
     <pressure>
         -- float --
         The pressure of Helium 4
         [Pa]
         
     ========== OUTPUT ==========
     
     <is_liquid>
         -- boolean --
         Helium 4 is liquid or not
         []
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## FUNCTION ##############################################
     
     
#%%
def is_solid(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function determine if the current Helium 4 is solid or not

     ========== INPUT ==========

     <temperature>
         -- float --
         The temperature of Helium 4
         [K]
         
     <pressure>
         -- float --
         The pressure of Helium 4
         [Pa]
         
     ========== OUTPUT ==========
     
     <is_solid>
         -- boolean --
         Helium 4 is solid or not
         []
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## FUNCTION ##############################################
     

#%%
def is_gaseous(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function determine if the current Helium 4 is gaseous or not

     ========== INPUT ==========

     <temperature>
         -- float --
         The temperature of Helium 4
         [K]
         
     <pressure>
         -- float --
         The pressure of Helium 4
         [Pa]
         
     ========== OUTPUT ==========
     
     <is_gaseous>
         -- boolean --
         Helium 4 is gaseous or not
         []
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## FUNCTION ##############################################
     
     
#%% 
def is_superfluid(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function determine if the current Helium 4 is superfluid or not

     ========== INPUT ==========

     <temperature>
         -- float --
         The temperature of Helium 4
         [K]
         
     <pressure>
         -- float --
         The pressure of Helium 4
         [Pa]
         
     ========== OUTPUT ==========
     
     <is_superfluid>
         -- boolean --
         Helium 4 is superfluid or not
         []
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
#%% 
def superfluid_ratio(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function determine the current proportion of superfluid Helium 4

     ========== INPUT ==========

     <temperature>
         -- float --
         The temperature of Helium 4
         [K]
         
     <pressure>
         -- float --
         The pressure of Helium 4
         [Pa]
         
     ========== OUTPUT ==========
     
     <superfluid_ratio>
         -- float --
         Proportion of superfluid Helium 4
         []
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     

     
     