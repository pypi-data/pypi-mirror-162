#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def thermal_expansion(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal expansion coefficient of HoY (Holmium-Yttrium)

    ========== VALIDITY ==========

    <temperature> : [4.2 -> 335]

    ========== FROM ==========

    Internal report - contact valentin.sauvage@outlook.com 

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <thermal_expansion>
        -- float --
        The thermal expansion coefficient of Holmium-Yttrium
        [Ø]

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 335 and temperature >= 4.2 ,'The function '\
        ' HoY.thermal_expansion is not defined for '\
            'T = '+str(temperature)+' K'

    ################## FUNCTION ###############################################

    expansion = 1.568530e-7*temperature**4 -1.595905e-4*temperature**3 + 6.090793e-2*temperature**2 -1.757427*temperature -1.859420e3
    
    return expansion*1e-6