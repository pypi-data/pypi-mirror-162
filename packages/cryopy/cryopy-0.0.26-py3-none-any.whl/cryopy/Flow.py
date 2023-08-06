#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def permeability(volumetric_flowrate,temperature,dynamic_viscosity,length,diameter,inlet_pressure,outlet_pressure):
    
    """
    ========== DESCRIPTION ==========

    This function return the permeability of a circular porous media.

    ========== VALIDITY ==========

    laminar flow -> reynolds_number < 2000 
    gas is compressible 
    
    ========== FROM ==========

    Whitaker, Stephen. « Flow in Porous Media I: A Theoretical Derivation of 
    Darcy’s Law ». Transport in Porous Media 1, nᵒ 1 (1986): 3‑25. 
    https://doi.org/10.1007/BF01036523 

    ========== INPUT ==========

    <volumetric_flowrate>
        -- float --
        The inlet flowrate of gas through the porous media
        [m]**3.[s]**(-1)

    <temperature>
        -- float --
        The temperature of the gas 
        [K]

    <dynamic_viscosity>
        -- float --
        The dynamic viscosity of the gas 
        [Pa].[s]
        
    <length>
        -- float --
        The length of the porous media
        [m]
        
    <diameter>
        -- float --
        The diameter of the porous media
        [m]
        
    <inlet_pressure>
        -- float --
        The upstream pressure of the gas 
        [Pa]
        
    <outlet_pressure>
        -- float --
        The downstream pressure of the gas
        [K]
        
    ========== OUTPUT ==========

    <permeability>
        -- float --
        The permeability of the porous media
        [m]**2

    ========== STATUS ==========

    Status : ... 

    ========== NOTES ===========

    """
    
    ################## CONDITIONS #############################################

    from cryopy import Flow
    from cryopy import Constant
    import numpy as np
    
    cross_section = np.pi*diameter**2/4
    
    flow_speed = molar_flow*Constant.GAS()*temperature/inlet_pressure/cross_section
    reynolds = Flow.reynolds_number(density,diameter,dynamic_viscosity,flow_speed)
    
    assert reynolds >= 2000 , 'The function '\
        ' Flow.permeability is not defined for '\
            'Re = '+str(reynolds)

    ################## FUNCTION ###############################################

    return -volumetric_flowrate*dynamic_viscosity*length/cross_section/(inlet_pressure-outlet_pressure)



#%%
def reynolds_number(density,characteristic_dimension,dynamic_viscosity,flow_speed):
    
    """
    ========== DESCRIPTION ==========

    This function return the Reynolds number of a flow

    ========== VALIDITY ==========

    <density> -> [all]
    <characteristic_dimension> -> [all]
    <dynamic_viscosity> -> [all]
    <flow_speed> -> [all]
    
    ========== FROM ==========

    Dude, trust me

    ========== INPUT ==========

    <density>
        -- float --
        The density of the flowing gas
        [kg].[m]**3

    <characteristic_dimension>
        -- float --
        The characteristic linear dimension of the flow 
        [m]

    <dynamic_viscosity>
        -- float --
        The dynamic viscosity of the gas 
        [Pa].[s]
        
    <flow_speed>
        -- float --
        The speed of the flow
        [m].[s]**(-1)
        
    ========== OUTPUT ==========

    <reynolds_number>
        -- float --
        The Reynolds number of the flow
        [Ø]

    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    """

    ################## FUNCTION ############################################### 
    
    return density*flow_speed*characteristic_dimension/dynamic_viscosity






