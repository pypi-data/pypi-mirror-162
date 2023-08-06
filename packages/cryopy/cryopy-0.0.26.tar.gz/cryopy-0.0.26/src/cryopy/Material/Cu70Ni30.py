#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Cu70Ni30

    ========== VALIDITY ==========

    <temperature> : [0.05 -> 4]

    ========== FROM ==========


    C. Y. Ho, M. W. Ackerman, K. Y. Wu, S. G. Oh, et T. N. Havill,
    « Thermal conductivity of ten selected binary alloy systems »,
    Journal of Physical and Chemical Reference Data, vol. 7, no 3,
    p. 959‑1178, juill. 1978, doi: 10.1063/1.555583.

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

    assert temperature <= 4 and temperature >= 0.05 ,'The function '\
        ' Cu70Ni30.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## FUNCTION ###############################################

    if temperature >= 0.3:
      result = 0.093*temperature**1.23
    else:
      0.064*temperature
      
    return result
