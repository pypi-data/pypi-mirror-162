#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Al1100

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/1100%20Aluminum/1100%20Aluminum_rev.htm

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
        ' Al1100.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([23.39172,-148.5733,422.1917,-653.6664,607.0402,-346.152,118.4276,-22.2781,1.770187])

    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log(temperature)**i

    return np.exp(result)
