#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Ti90Al6V4 (TA6V)

    ========== VALIDITY ==========

    <temperature> : [20 -> 300]

    ========== FROM ==========

    E. D. Marquardt, J. P. Le, et R. Radebaugh, « Cryogenic Material
    Properties Database », p. 7, 2000.

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

    assert temperature <= 300 and temperature >= 20 ,'The function '\
        ' Ti90Al6V4.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## INITIALISATION #########################################

    coefficients = np.array([-5107.8774,19240.422,-30789.0064,27134.756,-14226.379,4438.2154,-763.07767,55.796592])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log10(temperature)**i

    return 10**result
    
    
#%%
def linear_thermal_expansion(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Ti90Al6V4 (TA6V)

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    E. D. Marquardt, J. P. Le, et R. Radebaugh, « Cryogenic Material
    Properties Database », p. 7, 2000.

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
        ' Ti90Al6V4.linear_thermal_expansion is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-1.711e2,-2.171e-1,4.841e-3,-7.202e-6,0])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*temperature**i

    return result*1e-5