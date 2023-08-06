# -*- coding: utf-8 -*-
#%%
def molar_mass():

    """
    ========== DESCRIPTION ==========

    Return the constant molar mass of a single Helium 3 atom.

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

    return  3.0160293191

#%%
def mass():

    """
    ========== DESCRIPTION ==========

    Return the constant mass of a single Helium 3 atom.

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    P. J. Mohr, B. N. Taylor, and D. B. Newell, Rev. Mod. Phys. 84, 1531 (2012).

    ========== OUTPUT ==========

    <mass>
        -- float --
    	The mass of a single atom of Helium 3
        [kg]

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ################################################
    
    from cryopy import Constant
    from cryopy.Helium import Helium3

    ################## RETURN #################################################

    return  Helium3.molar_mass()/Constant.avogadro()


#%%
def effective_mass():

    """
    ========== DESCRIPTION ==========

    Return the effective mass of a single atom of Helium 3.
    This function does not require parameter since this is a constant

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (44)

    POBELL - Matter and methods at low temperature - Second edition -  P.125

    ========== OUTPUT ==========

    <effective_mass>
        -- float --
    	The effective mass of a single atom of Helium 3
        [kg]

    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    A potential improvement can be done since the effective mass of Helium 3
    can change if Helium 3 is in a Helium 3 /Helium 4 mixture

    """

    ################## MODULES ################################################

    from cryopy.Helium import Helium3

    ################## RETURN ###############################################

    return  2.46*Helium3.mass()


#%%
def molar_specific_heat(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the molar specific heat of pure Helium 3

    ========== VALIDITY ==========

    <temperature> : [0 -> 1.8]
    <pressure> : [0]

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (48)

    CHAUDHRY - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A14)

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

    <molar_specific_heat>
        -- float --
        The molar specific heat of pure Helium 3
        [J].[K]**(-1).[mol]**(-1)


    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    This function requires the implementation of pressure changes


    """
    
    ################## CONDITIONS #############################################

    assert pressure <= 0 and pressure >= 0 , 'The function '\
        ' Helium3.molar_specific_heat is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 1.8 and temperature >= 0.000 ,'The function '\
        ' Helium3.molar_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    from cryopy import Constant
    import pandas as pd
    import numpy as np

    ################## INITIALISATION #########################################

    result = 0
    Coefficients = pd.DataFrame(np.array([[np.nan,0.0245435],
                                          [2.7415,1.85688],
                                          [0,9.39988],
                                          [-61.78929,-117.910],
                                          [-177.8937,440.368],
                                          [2890.0675,-735.836],
                                          [0,468.741]]),
                                columns = ['C_1','C_2'])

    ################## FUNCTION ###############################################

    if temperature<=0.1:
        for j in [1,2,3,4,5]:
            result = result + Coefficients.C_1[j]*temperature**j
        return Constant.gas()*result

    if temperature<=0.45 and temperature>0.1:
        for j in [0,1,2,3,4,5,6]:
            result = result + Coefficients.C_2[j]*temperature**j
        return Constant.gas()*result
    
    else:
        return 3.6851551 - 1.9650072*temperature + 3.3601049*temperature**2 - 0.8351251*temperature**3 - (0.0444842/(temperature**2))*np.exp(-0.0977175/temperature)


#%%
def molar_enthalpy(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function can return the molar enthalpy of Helium 3

    ========== VALIDITY ==========

    <temperature> : [0 -> 0.450]
    <pressure> : [0]

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (37)

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

    <molar_enthalpy>
        -- float --
        The molar enthalpy of pure Helium 3
        [J].[mol]**(-1)


    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    This function requires the implementation of pressure changes

    """
    
    ################## CONDITIONS #############################################

    assert pressure <= 0 and pressure >= 0 , 'The function '\
        ' Helium3.molar_enthalpy is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 0.450 and temperature >= 0.000 ,'The function '\
        ' Helium3.molar_enthalpy is not defined for '\
            'T = '+str(temperature)+' K'    
    
    ################## MODULES ################################################

    from cryopy import Constant
    import pandas as pd
    import numpy as np

    ################## INITIALISATION #########################################

    result = 0
    Coefficients = pd.DataFrame(np.array([[np.nan,0.0245435],
                                          [2.7415,1.85688],
                                          [0,9.39988],
                                          [-61.78929,-117.910],
                                          [-177.8937,440.368],
                                          [2890.0675,-735.836],
                                          [0,468.741]]),
                                columns = ['C_1','C_2'])

    ################## FUNCTION ###############################################
    
    if temperature<=0.1:
        for j in [1,2,3,4,5]:
            result = result + Coefficients.C_1[j]*temperature**(j+1)/(j+1)
        return Constant.gas()*result

    if temperature<=0.45 and temperature>0.1:
        result = result -0.0004006515045376974
        for j in [0,1,2,3,4,5,6]:
            result = result + Coefficients.C_2[j]*temperature**(j+1)/(j+1)
        return Constant.gas()*result


#%%
def molar_entropy(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function can return the molar entropy of Helium 3

    ========== VALIDITY ==========

    <temperature> : [0 -> 0.450]
    <pressure> : [0]

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (37)

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

    <molar_entropy>
        -- float --
        The molar entropy of pure Helium 3
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

    assert temperature <= 0.450 and temperature >= 0.000 ,'The function '\
        ' Helium3.molar_entropy is not defined for '\
            'T = '+str(temperature)+' K'    

    ################## INITIALISATION #########################################

    Coefficients = [ 5.64822229e+02, -8.94486733e+02,  5.54757487e+02,
                    -1.45763639e+02, -9.26752184e+00,  2.31209308e+01,
                    -1.62015854e-03]
    Polynome = np.poly1d(Coefficients)

    ################## FUNCTION ###############################################

    return Polynome(temperature)


#%%
def chemical_potential(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the chemical potential of Helium 3

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (38)

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

    <chemical_potential>
        -- float --
        The chemical potential of pure Helium 3
        [J].[mol]**(-1)

    ========== STATUS ==========

    Status : In progress (need to be verified with new values of pressure)

    """

    ################## MODULES ################################################

    from cryopy.Helium import Helium3

    ################## RETURN #################################################

    return Helium3.molar_enthalpy(temperature,pressure)-temperature*Helium3.molar_entropy(temperature,pressure)


#%%
def internal_energy(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the internal energy of Helium 3

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (37)

    ========== INPUT ==========

    <temperature>
        The temperature of Helium 3
        [K]

    <pressure>
        The pressure of Helium 3
        [Pa]

    ========== OUTPUT ==========

    <internal_energy>
        The internal energy of pure Helium 3
        [J].[mol]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : In progress (need to be verified with new values of pressure)

    """

    ################## MODULES ################################################

    from cryopy.Helium import Helium3

    ################## FUNCTION ###############################################

    return Helium3.molar_enthalpy(temperature,pressure)


#%%
def molar_volume(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the molar volume of a mole of Helium 3

    ========== VALIDITY ==========

    <temperature> : [0 -> 1]
    <pressure> : [0 -> 15.7e5]


    ========== FROM ==========

    CHAUDHRY - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A.22)

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
        The molar volume of Helium 3
        [m]**3.[mol]**(-1)

    ========== STATUS ==========

    Status : Checked


    """

    ################## MODULES ################################################

    import numpy as np

    ################## CONDITIONS #############################################

    assert pressure <= 15.7e5 and pressure >= 0 , 'The function '\
        ' Helium3.molar_volume is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 1 and temperature >= 0.000 ,'The function '\
        ' Helium3.molar_volume is not defined for '\
            'T = '+str(temperature)+' K'    

    ################## INITIALISATION #########################################

    Coefficients = np.array([[40.723012,-1.3151948,0.0409498],
                             [-0.6614794,0.1275125,-0.0091931],
                             [0.5542147,-0.1527959,0.0113764],
                             [0.1430724,-0.0034712,-0.0008515],
                             [-0.2603492,np.nan,-0.0051946]])

    pressure = pressure*1e-5 # From [Pa] to [Bar]

    result = 0

    ################## FUNCTION ###############################################
    
    for i in range(3):
        for j in range(2):
            result = result + Coefficients[i][j]*temperature**i*pressure**j

    return (result + 1/(Coefficients[4][2]*pressure**2+Coefficients[4][0]))*1e-6 # 1e-6 to SI


#%%
def solid_liquid_transition(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the pressure of the Solid/Liquid transition of Helium 3 at a given temperature

    ========== VALIDITY ==========

    <temperature> : [1 -> 3.15]

    ========== FROM ==========

    SHERMAN - pressure-Volume-temperature Relations of Liquid He3 from 1K
    to 3.3K - Equation (1)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 3
        [K]

    ========== OUTPUT ==========

    <solid_liquid_transition>
        -- float --
        The pressure of solid/liquid helium 3 transition
        [Pa]

    ========== STATUS ==========

    Status : Checked


    """
    ################## CONDITIONS #############################################

    assert temperature <= 3.15 and temperature >= 1 ,'The function '\
        ' Helium3.molar_volume is not defined for '\
            'T = '+str(temperature)+' K'    

    ################## FUNCTION ###############################################
    
    return (24.599 + 16.639*temperature**2 - 2.0659*temperature**3 + 0.11212*temperature**4)*1e5


#%%
def liquid_thermal_conductivity(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Helium 3

    ========== VALIDITY ==========

    <temperature> : [0.003 -> 300]
    <pressure> : [0 -> 20e6]

    ========== FROM ==========

    HUANG - Thermal conductivity of helium-3 between 3 mK and 300 K

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

    <liquid_thermal_conductivity>
        -- float --
        The thermal conductivity of liquid Helium 3
        [W].[m]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked


    """

    ################## MODULES ################################################

    import numpy as np

    ################## CONDITIONS #############################################

    assert pressure <= 20e6 and pressure >= 0 , 'The function '\
        ' Helium3.liquid_thermal_conductivity is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 300 and temperature >= 0.003 ,'The function '\
        ' Helium3.liquid_thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'    

    ################## INITIALISATION #########################################

    Coefficients = np.array([[-4.96046174,-0.65469605,0.22709943,-0.048878330,-0.014822690,-0.0065179072],
                             [0.73147012,1.1285816,-0.35962597,0.068654087,0.016518400,np.nan],
                             [0.89421626,-0.079608445,0.018861074,0.029884542,np.nan,np.nan],
                             [-0.0084984819,-0.054117908,0.016515130,np.nan,np.nan,np.nan],
                             [-0.10296191,-0.022615875,np.nan,np.nan,np.nan,np.nan],
                             [-0.015211058,np.nan,np.nan,np.nan,np.nan,np.nan]])

    x = np.log(temperature) # Log scale of the temperature
    y = pressure/101325 # From [Pa] to [Bar]

    x = x*2/np.log(300/0.003)-np.log(0.003)*2/np.log(300/0.003)-1  # Normalize between -1 and 1
    y = y*0.010132500000000001-1 # Normalize between -1 and 1

    ################## FUNCTION ###############################################
    
    result = 0

    for j in np.arange(1,6):
        for i in np.arange(1,6-j):
            result = result + Coefficients[i][j]*np.cos(i*np.arccos(x))*np.cos(j*np.arccos(y))

    for i in np.arange(1,6):
        result = result + Coefficients[i][0]*np.cos(i*np.arccos(x))

    for j in np.arange(1,6):
        result = result + Coefficients[0][j]*np.cos(j*np.arccos(y))

    result = result + Coefficients[0][0]

    return np.exp(result)

#%%
def gas_thermal_conductivity(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of gaseous Helium 3

    ========== VALIDITY ==========

    <temperature> : [0.003 -> 300]
    <pressure> : [0 -> 20e6]

    ========== FROM ==========

    HUANG - Thermal conductivity of helium-3 between 3 mK and 300 K

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

    <thermal_conductivity_gas>
        -- float --
        The thermal conductivity of gaseous Helium 3
        [W].[m]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : To be checked

    """

    ################## CONDITIONS #############################################

    assert pressure <= 20e6 and pressure >= 0 , 'The function '\
        ' Helium3.gas_thermal_conductivity is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert temperature <= 300 and temperature >= 0.003 ,'The function '\
        ' Helium3.gas_thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    Coefficients = np.array([[85.487315,5.495659,3.089753,1.276371,0.577591],
                             [98.529019,-4.351606,-2.525931,-0.430895,np.nan],
                             [38.396887,-1.862116,-0.798918,np.nan,np.nan],
                             [12.020784,2.80104,np.nan,np.nan,np.nan],
                             [2.159515,np.nan,np.nan,np.nan,np.nan]])

    # Log scale of the temperature
    x = np.log(temperature)

    # From [Pa] to [Bar]
    y = pressure/101325

    # Normalize between -1 and 1
    x = x*2/np.log(300/0.003)-np.log(0.003)*2/np.log(300/0.003)-1

    # Normalize between -1 and 1
    y = y*0.010132500000000001-1

    ################## FUNCTION ###############################################

    result = 0

    for j in np.arange(1,5):
        for i in np.arange(1,5-j):
            result = result + Coefficients[i][j]*np.cos(i*np.arccos(x))*np.cos(j*np.arccos(y))

    for i in np.arange(1,5):
        result = result + Coefficients[i][0]*np.cos(i*np.arccos(x))

    for j in np.arange(1,5):
        result = result + Coefficients[0][j]*np.cos(j*np.arccos(y))

    result = result + Coefficients[0][0]

    return np.exp(result)

#%%
def is_liquid(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function determine if the current Helium 3 is liquid or not

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
     
     <is_liquid>
         -- boolean --
         Helium 3 is liquid or not
         []
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## FUNCTION ##############################################
     
     
#%%
def is_solid(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function determine if the current Helium 3 is solid or not

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
     
     <is_solid>
         -- boolean --
         Helium 3 is solid or not
         []
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## FUNCTION ##############################################
     

#%%
def is_gaseous(temperature,pressure):
     
     """
     ========== DESCRIPTION ==========
     
     This function determine if the current Helium 3 is gaseous or not

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
     
     <is_gaseous>
         -- boolean --
         Helium 3 is gaseous or not
         []
     
     ========== STATUS ==========     
     
     Status : Checked

     """
     
     ################## FUNCTION ##############################################