#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def mass_specific_heat(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Apiezon N grease

    ========== VALIDITY ==========

    <temperature> : [3 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/Apiezon%20N/ApiezonN_rev.htm

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
        ' Apiezon_N.mass_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    Coefficients = np.array([-1.61975,3.10923,-0.712719,4.93675,-9.37993,7.58304,-3.11048,0.628309,-0.0482634])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(Coefficients)):
        result = result + Coefficients[i]*np.log(temperature)**i

    return np.exp(result)
