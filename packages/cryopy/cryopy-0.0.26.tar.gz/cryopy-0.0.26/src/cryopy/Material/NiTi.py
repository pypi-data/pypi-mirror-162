#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of NbTi

    ========== VALIDITY ==========

    <temperature> : [0.1 -> 1; 4-> 9]

    ========== FROM ==========

    F. Pobell, Matter and methods at low temperatures, 3rd, rev.expanded ed
    éd. Berlin ; New York: Springer, 2007.

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

    assert temperature <= 9 and temperature >= 0.1 ,'The function '\
        ' Ti90Al6V4.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'
            
    ################## FUNCTION ###############################################

    if temperature <= 9 and temperature >= 4:
        return 0.0075*temperature**1.85

    if temperature <= 1 and temperature >= 0.1:
        return 0.015*temperature**2

#%%
def linear_thermal_expansion(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of NbTi

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
        ' NbTi.linear_thermal_expansion is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-1.862e2,-2.568e-1,8.334e-3,-2.951e-5,3.908e-8])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*temperature**i

    return result*1e-5
