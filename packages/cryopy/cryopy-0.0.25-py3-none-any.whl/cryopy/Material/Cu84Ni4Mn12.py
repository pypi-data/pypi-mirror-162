#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Cu84Ni4Mn12 (Manganin)

    ========== VALIDITY ==========

    <temperature> : [0.1 -> 4]

    ========== FROM ==========

    I. Peroni, E. Gottardi, A. Peruzzi, G. Ponti, et G. Ventura,
    « Thermal conductivity of manganin below 1 K », Nuclear Physics B -
    Proceedings Supplements, vol. 78, no 1‑3, p. 573‑575, août 1999,
    doi: 10.1016/S0920-5632(99)00606-4.

    D.T. Corzett, A.M.Miller and P.Seligmann, Cryogenics 16,505 (1976)

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

    assert temperature <= 4 and temperature >= 0.1 ,'The function '\
        ' Cu84Ni4Mn12.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## FUNCTION ###############################################

    result = 0.095*temperature**1.19

    return result
