#%%
def temperature(fraction_3he):

    """
    ========== DESCRIPTION ==========

    This function return the Fermi temperature of the same density
    quasi-particule of Helium 3

    ========== VALIDITY ==========

    <fraction_3he> : [0 -> 0.08]

    ========== FROM ==========

    Kuerten et al. - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (7)

    ========== INPUT ==========

    <fraction_3he>
        -- float --
        The fraction of Helium 3 on mixture
        []

    ========== OUTPUT ==========

    <temperature>
        -- float --
        The Fermi temperature 
        [J].[K]**(-1).[mol]**(-1)


    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    """        

    ################## MODULES ################################################
    
    from cryopy.Helium import Helium4
    from cryopy.Helium import Helium3
    from cryopy import Constant
    import numpy as np

    ################## FUNCTION ###############################################

    return Constant.reduced_planck()**2/(2*Helium3.effective_mass()*Constant.boltzmann())*(3*np.pi**2*Constant.avogadro()*fraction_3he/Helium7.molar_volume(fraction_3he))**(2/3)


#%% 
def molar_specific_heat(temperature,fraction_3he):

    """
    ========== DESCRIPTION ==========
    
    This function return the molar specific heat of an ideal Fermi gas with 
    the same density of quasiparticules as the mixture with the effective mass
    of Helium 3 
    
    ========== VALIDITY ==========
    
    <temperature> : [0 -> 0.250]
    <fraction_3he> : [0 -> 0.08]

    ========== SOURCE ==========
    
    Kuerten at al. - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (42)

    ========== ENTREE ==========
    
    <temperature>
        -- float --
        The temperature of the mixture
        [K]
        
    <fraction_3he>
        -- float --
        The fraction of Helium 3 on mixture
        []

    ========== SORTIE ==========
    
    <molar_specific_heat>
        -- float --
        The molar specific heat of the Fermi ideal gas
        [J].[K]**(-1).[mol]**(-1)
    
    ========== STATUS ==========     
    
    Status : Vérifiée

    """
    
    ################## MODULES ################################################
    
    from cryopy import Constant
    from cryopy.Helium import Fermi
    import numpy as np
    import pandas as pd

    ################## CONDITIONS #############################################

    assert fraction_3he <= 0.08 and fraction_3he >= 0 , 'The function '\
        ' Fermi.molar_specific_heat is not defined for '\
            'x = '+str(fraction_3he*100)+' %'

    assert tempertaure <= 0.250 and temperature >= 0 , 'The function '\
        ' Fermi.molar_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'
        
    ################## INITIALISATION #########################################
        
    result = 0
    t = temperature/Fermi.temperature(fraction_3he)
    coefficients = pd.DataFrame(np.array([[4.934802,-0.201414,1.5],
                                      [-14.400636,8.910152,-0.09973557],
                                      [-167.8453,-27.147564,0.00560236],
                                      [-4313.1735,56.254979,-0.00024872],
                                      [203138.64,-77.719456,np.nan],
                                      [np.nan,62.61363,np.nan],
                                      [np.nan,-21.64979,np.nan]]),
                                        columns = ['A_1','A_2','A_3'])
        
    ################## FUNCTION ###############################################
        
    if t<=0.15:
        for j in [0,1,2,3,4]:
            result = result + coefficients.A_1[j]*t**(2*j+1)
        return Constant.gas()*result
    if t<=0.7 and t>=0.15:
        for j in [0,1,2,3,4,5,6]:
            result = result + coefficients.A_2[j]*t**j
        return Constant.gas()*result	
    if t>=0.7:
        for j in [0,1,2,3]:
            result = result + coefficients.A_3[j]*t**(-3*j/2)
        return Constant.gas()*result


#%%
def molar_entropy(temperature,fraction_3he):

    """
    ========== DESCRIPTION ==========
    
    This function return the molar entropy of an ideal Fermi gas with 
    the same density of quasiparticules as the mixture with the effective mass
    of Helium 3 

     ========== VALIDITY ==========
     
     <temperature> : [0 -> 0.250]
     <fraction_3he> : [0 -> 0.08]

     ========== SOURCE ==========
     
     Kuerten at al. - Thermodynamic properties of liquid 3He-4He mixtures
     at zero pressure for temperatures below 250 mK and 3He concentrations
     below 8% - Equation (8)

     ========== INPUT ==========
     
     <temperature>
         -- float --
         The temperature of the mixture
         [K]
         
     <fraction_3he>
         -- float --
         The fraction of Helium 3 on mixture
         []

     ========== OUTPUT ==========
     
     <molar_entropy>
         -- float --
         The molar entropy of the Fermi ideal gas
         [J].[K]**(-1).[mol]**(-1)
     
     ========== STATUS ==========     
     
     Status : checked

    """
    
    ################## MODULES ###############################################
    
    from cryopy import Constant
    from cryopy.Helium import Fermi
    import numpy as np
    import pandas as pd

    ################## CONDITIONS #############################################

    assert fraction_3he <= 0.08 and fraction_3he >= 0 , 'The function '\
        ' Fermi.molar_entropy is not defined for '\
            'x = '+str(fraction_3he*100)+' %'

    assert tempertaure <= 0.250 and temperature >= 0 , 'The function '\
        ' Fermi.molar_entropy is not defined for '\
            'T = '+str(temperature)+' K'
    
    ################## INITIALISATION #########################################
    
    result = 0
    t = temperature/Fermi.temperature(fraction_3he)
    coefficients = pd.DataFrame(np.array([[4.934802,-0.201414,1.5],
                                  [-14.400636,8.910152,-0.09973557],
                                  [-167.8453,-27.147564,0.00560236],
                                  [-4313.1735,56.254979,-0.00024872],
                                  [203138.64,-77.719456,np.nan],
                                  [np.nan,62.61363,np.nan],
                                  [np.nan,-21.64979,np.nan]]),
                                    columns = ['A_1','A_2','A_3'])
    
    ################## FUNCTION ###############################################
    
    if t<=0.15:
        for j in [0,1,2,3,4]:
            result = result + coefficients.A_1[j]*t**(2*j+1)/(2*j+1)
        return Constant.gas()*result
    
    if t<=0.7 and t>0.15:
        result = result+coefficients.A_2[0]*np.log(t)-0.7462941987437959
        for j in [1,2,3,4,5,6]:
            result = result + Coefficients.A_2[j]*(t**j)/j
        return Constant.gas()*result
    
    if t>0.7:
        result = result + coefficients.A_3[0]*np.log(t) +2.779744103011612 -2/3*Coefficients.A_3[1]*t**(-3/2)-1/3*Coefficients.A_3[2]*t**(-3)-9/2*Coefficients.A_3[3]*t**(-9/2)
        return Constant.gas()*result    
        

         
#%% 
def chemical_potential(temperature,fraction_3he):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the molar entropy of an ideal Fermi gas with 
    the same density of quasiparticules as the mixture with the effective mass
    of Helium 3 

     ========== VALIDITY ==========

     ========== FROM ==========
     
     Kuerten at al. - Thermodynamic properties of liquid 3He-4He mixtures
     at zero pressure for temperatures below 250 mK and 3He concentrations
     below 8% - Equation (15)

     ========== INPUT ==========
     
     <temperature>
         -- float --
         The temperature of the mixture
         [K]
         
     <fraction_3he>
         -- float --
         The fraction of Helium 3 on mixture
         []

     ========== OUTPUT ==========
     
     <chemical_potential>
         -- float --
         The chemical potential of a Fermi gas
         [J].[mol]**(-1)
         
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    ################## MODULES ################################################

    import numpy as np
    from cryopy import Constant
    from cryopy.Helium import Helium3
    from cryopy.Helium import Fermi
    from cryopy.Helium import Helium4
    from scipy import integrate
      
    
    ################## INITIALISATION #########################################
    
    t = temperature/Fermi.temperature(fraction_3he)
       
    ################## FUNCTION ###############################################
    
    return Constant.gas()*Fermi.temperature(fraction_3he)+5/3*Fermi.temperature(fraction_3he)*integrate.quad(Fermi.molar_specific_heat,0,t,fraction_3he) - temperature*molar_entropy(temperature,fraction_3he)
    

