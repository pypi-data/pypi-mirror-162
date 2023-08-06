#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 14:05:48 2021

@author: valentinsauvage
"""



def All():
    
    """
    ========== DESCRIPTION ==========

    This function plot the thermal conductivity of cryopy referenced materials 

    ========== STATUS ==========

    Status : Checked

    """
    
    import matplotlib.pyplot as plt
    #from cryopy.material import *
    import numpy as np
    
    
    plt.figure()
    
    
    Temperature = np.arange(3,300,0.1)
    ThermalConductivity = [Teflon.ThermalConductivity(T) for T in Temperature]
    
    plt.loglog(Temperature,ThermalConductivity)
    
    plt.xlabel('Temperature [K]')
    plt.ylabel(r'Thermal Conductivity $[W.m^{-1}.K^{-1}]$')
    plt.grid()
    plt.title(r'Thermal Conductivity of some materials in \textit{cryopy}')