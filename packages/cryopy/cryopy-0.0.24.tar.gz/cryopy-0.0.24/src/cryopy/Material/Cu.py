#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def molar_specific_heat(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of pure copper

    ========== VALIDITY ==========

    <temperature> : [0.3 -> 25]

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
        [J].[mol]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 25 and temperature >= 0.3 ,'The function '\
        ' Cu.molar_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np
    import pandas as pd

    ################## INITIALISATION #########################################

    coefficients = pd.DataFrame(np.array([[6.9434e-1],
                                          [4.7548e-2],
                                          [1.6314e-6],
                                          [9.4786e-8],
                                          [-1.3639e-10],
                                          [5.3898e-14]]),
                                columns = ['A'])

    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients.A[i]*temperature**(2*i-1)

    return result*1e-3
