#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Cu60Ni40

    ========== VALIDITY ==========

    <temperature> : [4 -> 1000]

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

    ################## PACKAGES ###############################################

    import numpy as np
    from numpy.polynomial.chebyshev import chebval

    ################## CONDITIONS #############################################

    assert temperature <= 1000 and temperature >= 4 ,'The function '\
        ' Cu60Ni40.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## INITIALISATION #########################################

    coefficients = [-2.30898228e+00,  6.85983394e-01, -4.39606667e-03,
                    1.55003291e-05, -3.26232016e-08,  4.32251401e-11,
                    -3.68136398e-14,  2.00747488e-17, -6.76447346e-21,
                    1.28140575e-24, -1.04288668e-28]

    ################## FUNCTION ###############################################

    result = chebval(temperature,coefficients)

    return result
