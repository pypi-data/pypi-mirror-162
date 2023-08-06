#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Stainless Steel 304-L

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm

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

    ################## PACKAGES ###############################################

    import numpy as np

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 4 ,'The function '\
        ' SS304L.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## INITIALISATION #########################################

    coefficients = np.array([-1.4087,1.3982,0.2543,-0.6260,0.2334,0.4256,-0.4658,0.1650,-0.0199])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log10(temperature)**i
    return 10**result


#%%
def mass_specific_heat(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the mass specific heat of Stainless Steel 304-L

    ========== VALIDITY ==========

    <temperature> : [4 -> 20]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <mass_specific_heat>
        -- float --
        The specific heat
        [J].[Kg]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 20 and temperature >= 4 ,'The function '\
        ' SS304L.mass_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-351.51,3123.695,-12017.28,26143.99,-35176.33,29981.75,-15812.78,4719.64,-610.515])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log10(temperature)**i

    return 10**result
    
#%%
def linear_thermal_expansion(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Stainless Steel 304-L

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm

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
        ' SS304-L.linear_thermal_expansion is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-2.9546e2,-4.0518e-1,9.4014e-3,-2.1098e-5,1.8780e-8])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*temperature**i

    return result*1e-5
