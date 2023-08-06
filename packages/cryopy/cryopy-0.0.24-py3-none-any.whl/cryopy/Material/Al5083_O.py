#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Al5083-O

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <thermal_conductivity>
        -- float --
        The thermal conductivity
        [W].[m]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 4 ,'The function '\
        ' Al5083_O.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-0.90933,5.751,-11.112,13.612,-9.3977,3.6873,-0.77295,0.067336])

    result = 0

    ################## FUNCTION ###############################################


    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log(temperature)**i

    return np.exp(result)

#%%
def mass_specific_heat(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Al5083-O

    ========== VALIDITY ==========

    <temperature> : [3 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <specific_heat>
        -- float --
        The specific heat
        [J].[Kg]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 3 ,'The function '\
        ' Al5083_O.mass_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([46.6467,-314.292,866.662,-1298.3,1162.27,-637.795,210.351,-38.3094,2.96344])

    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log(temperature)**i

    return np.exp(result)

#%%
def linear_thermal_expansion(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Al5083-O

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <linear_thermal_expansion>
        -- float --
        The linear thermal expansion
        []

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 4 ,'The function '\
        ' Al5083_O.linear_thermal_expansion is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-4.1277e2,-3.0389e-1,8.7696e-3,-9.9821e-6,0])

    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*temperature**i

    return result*1e-5

#%%
def young_modulus(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the Young's modulus of Al5083-O

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <young_modulus>
        -- float --
        The Young's modulus
        [Pa]

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 4 ,'The function '\
        ' Al5083_O.young_modulus is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([8.083212e1,1.061708e-2,-3.016100e-4,7.561340e-7,-6.99487e-10])

    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*temperature**i

    return result*10**9
