#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def planck():

    """
    ========== DESCRIPTION ==========

    This function return the Planck constant

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    Wikipedia : https://en.wikipedia.org/wiki/Planck_constant

    ========== INPUT ==========

    ========== OUTPUT ==========

    <planck>
        -- float --
    	The Planck constant
        [kg].[m]**(2).[s]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## RETURN #################################################

    return  6.626070040e-34

#%%
def reduced_planck():

    """
    ========== DESCRIPTION ==========

    This function return the reduced Planc constant

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    Wikipedia : https://en.wikipedia.org/wiki/Planck_constant

    ========== INPUT ==========

    ========== OUTPUT ==========

    <reduced_planck>
        -- float --
    	The reduced Planck constant
        [kg].[m]**(2).[s]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy import Constant

    ################## RETURN #################################################

    return  Constant.planck()/2/np.pi

#%%
def gas():

    """
    ========== DESCRIPTION ==========

    This function return the molar gas constant

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    Wikipedia : https://en.wikipedia.org/wiki/Gas_constant

    ========== INPUT ==========

    ========== OUTPUT ==========

    <gas>
        -- float --
        [J].[K]**(-1).[mol]**(-1)
    	The molar gas constant

    ========== STATUS ==========

    Status : Checked

    """

    ################## RETURN #################################################

    return  8.31446261815324

#%%
def boltzmann():

    """
    ========== DESCRIPTION ==========

    This function return the Boltzmann constant

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    Wikipedia : https://en.wikipedia.org/wiki/Boltzmann_constant

    ========== INPUT ==========

    ========== OUTPUT ==========

    <boltzmann>
        -- float --
    	The Boltzmann constant
        [J].[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## RETURN #################################################

    return  1.38064852e-23

#%%
def avogadro():

    """
    ========== DESCRIPTION ==========

    This function return the Avogadro constant

    ========== VALIDITY ==========

    Always

    ========== SOURCE ==========

    Wikipedia : https://en.wikipedia.org/wiki/Avogadro_constant

    ========== INPUT ==========

    ========== OUTPUT ==========

    <avogadro>
        -- float --
    	The Avogadro constant
        [mol]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## RETURN #################################################

    return  6.0221367e23

#%%
def speed_of_light():

    """
    ========== DESCRIPTION ==========

    This function return the speed of light in vacuum

    ========== VALIDITY ==========

    Only in Vacuum

    ========== FROM ==========

    Wikipedia : https://en.wikipedia.org/wiki/Speed_of_light

    ========== INPUT ==========

    ========== OUTPUT ==========

    <speed_of_light>
        -- int --
    	The speed of light
        [m].[s]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## RETURN #################################################

    return  299792458


#%%
def stefan_boltzmann():

    """
    ========== DESCRIPTION ==========

    This function return the Stefan-Boltzmann constant

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    Wikipedia : https://en.wikipedia.org/wiki/Stefan–Boltzmann_law

    ========== INPUT ==========

    ========== OUTPUT ==========

    <stefan_boltzmann>
        -- float --
    	The Stefan-Boltzmann constant
        [W].[m]**(-2).[K]**(-4)

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy import Constant

    ################## RETURN #################################################

    return 2*np.pi**5*Constant.boltzmann()**4/(15*Constant.speed_of_light()**2*Constant.planck()**3)
