#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def mass_specific_heat(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Beryllium

    ========== VALIDITY ==========

    <temperature> : [14 -> 284]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/Beryllium/Beryllium_rev.htm

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
        ' Be.mass_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    Coefficients = np.array([-526.84477,2755.4105,-6209.8985,7859.2257,-6106.2095,2982.9958,-894.99967,150.85256,-10.943615])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(Coefficients)):
        result = result + Coefficients[i]*np.log10(temperature)**i

    return 10**result
