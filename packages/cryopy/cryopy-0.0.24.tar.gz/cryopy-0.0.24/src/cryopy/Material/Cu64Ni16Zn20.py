#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of pure Cu64Ni16Zn20

    ========== VALIDITY ==========

    <temperature> : [2 -> 20]

    ========== FROM ==========


    J. K. Hulm, « The Thermal Conductivity of a Copper-Nickel Alloy at Low
    Temperatures », Proc. Phys. Soc. B, vol. 64, no 3, p. 207‑211, mars 1951,
    doi: 10.1088/0370-1301/64/3/304.


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

    assert temperature <= 20 and temperature >= 2 ,'The function '\
        ' Cu64Ni16Zn20.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## FUNCTION ###############################################

    result = 3.8*1e-2*temperature**2

    return result