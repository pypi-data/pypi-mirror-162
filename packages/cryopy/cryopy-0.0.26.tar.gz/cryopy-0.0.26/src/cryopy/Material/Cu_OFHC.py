#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Cu-OFHC

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

    <thermal_conductivity>
        -- float --
        The thermal conductivity
        [W].[m]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 400 and temperature >= 4 ,'The function '\
        ' Cu-OFHC.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## FUNCTION ###############################################

    result = (2.2154 - 0.88068*temperature**0.5 + 0.29505*temperature - 0.048310*temperature**1.5 + 0.003207*temperature**2)/(1 - 0.47461*temperature**0.5 + 0.13871*temperature - 0.020430*temperature**1.5 +  0.001281*temperature**2)

    return 10**result
    
#%%
def mass_specific_heat(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Cu-OFHC

    ========== VALIDITY ==========

    <temperature> : [3 -> 300]

    ========== FROM ==========

    E. D. Marquardt, J. P. Le, et R. Radebaugh, « Cryogenic Material
    Properties Database », p. 7, 2000.

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
        ' Cu-OFHC.mass_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-1.91844,-0.15973,8.61013,-18.99640,21.96610,-12.73280,3.54322,-0.37970,0])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log10(temperature)**i

    return 10**result