#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Al6063-T5

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/6063_T5%20Alulminum/6063-T5Aluminum_rev.htm

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
        ' Al6063_T5.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    Coefficients = np.array([22.401433,-141.13433,394.95461,-601.15377,547.83202,-305.99691,102.38656,-18.810237,1.4576882])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(Coefficients)):
        result = result + Coefficients[i]*np.log(temperature)**i

    return np.exp(result)
