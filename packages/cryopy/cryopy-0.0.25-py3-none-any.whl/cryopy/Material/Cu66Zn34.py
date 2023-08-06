#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Cu66Zn34 (Brass)

    ========== VALIDITY ==========

    <temperature> : [5 -> 110]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/Brass/Brass_rev.htm

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

    assert temperature <= 110 and temperature >= 5 ,'The function '\
        ' Cu66Zn34.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    Coefficients = np.array([0.021035,-1.01835,4.54083,-5.03374,3.20536,-1.12933,0.174057,-0.0038151])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(Coefficients)):
        result = result + Coefficients[i]*np.log10(temperature)**i

    return 10**result
