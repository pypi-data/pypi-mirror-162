#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Cu97Be3

    ========== VALIDITY ==========

    <temperature> : [4.4 -> 300]

    ========== FROM ==========

    Internal report - contact valentin.sauvage@outlook.com

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

    assert temperature <= 300 and temperature >= 4.4 ,'The function '\
        ' Cu97Be3.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## INITIALISATION #########################################

    coefficients = np.array([-0.8517934,2.22797618,-0.29595893,0.01743955])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log(temperature)**i

    return np.exp(result)