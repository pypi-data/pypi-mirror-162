# -*- coding: utf-8 -*-
#%%
def molar_specific_heat(temperature,pressure,fraction_3he):

    """
    ========== DESCRIPTION ==========

    This function return the molar specific heat of a mixture of Helium 3 & 
    Helium 4 

    ========== FROM ==========

    Kuerten et al. - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (6)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    <fraction_3he>
        -- float --
        The fraction of Helium 3 on mixture
        []

    ========== OUTPUT ==========

    <molar_specific_heat>
        -- float --
        The molar specific heat of Helium 3/4 mixture
        [J].[K]**(-1).[mol]**(-1)


    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    """        

    ################## MODULES ################################################
    
    from cryopy.Helium import Helium4
    from cryopy.Helium import Fermi

    ################## FUNCTION ###############################################
    
    return fraction_3he*Fermi.molar_specific_heat(temperature,fraction_3he)+(1-fraction_3he)*Helium4.molar_specific_heat(temperature,pressure)


#%% 
def molar_volume(temperature,pressure,fraction_3he):

    """
    ========== DESCRIPTION ==========

    This function return the molar volume of a mixture of Helium 3 & 
    Helium 4 

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (43)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    <fraction_3he>
        -- float --
        The fraction of Helium 3 on mixture
        []

    ========== OUTPUT ==========

    <molar_volume>
        -- float --
        The molar volume of Helium 3/4 mixture
        [m]**(3).[mol]**(-1)

    ========== STATUS ==========

    Status : Checked
    
    ========== NOTES ==========

    Add pressure constraint 

    """

    ################## MODULES ################################################

    from cryopy import Helium4

    ################## FUNCTION ###############################################
        
    return Helium4.molar_volume(temperature,pressure)*(1+0.286*fraction_3he)


#%% 
def osmotic_pressure(temperature,pressure,fraction_3he):

    """
    ========== DESCRIPTION ==========

    This function return the osmotic pressure of a mixture of Helium 3 & 
    Helium 4 

    ========== FROM ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (24)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of Helium 4
        [K]

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    <fraction_3he>
        -- float --
        The fraction of Helium 3 on mixture
        []

    ========== OUTPUT ==========

    <osmotic_pressure>
        -- float --
        The osmotic pressure of Helium 3/4 mixture
        [Pa]

    ========== STATUS ==========

    Status : Checked

    2020-02-25:
        Modification des valeurs pour T=0 par un polynôme en utilisant les
        valeurs (Table 19) et non l'équation (45)

    ========== NOTES ==========

    Add constraint on pressure
    
    2020-02-25:
        Modification of value to T=0 by a polynôm using values from table (19)
        instead of equation (45)
    
    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy.Helium import Helium4
    from cryopy.Helium import Fermi
    from cryopy.Helium import Helium7
    from scipy.misc import derivative
    from scipy.integrate import quad
        
    ################## INITIALISATION #########################################

    coefficients = [ 7.71714007e+09, -2.28854069e+09,  2.80349751e+08, -2.01610697e+07, 7238437e+06,  3.68490992e+03, -4.60897007e-01]
    polynom = np.poly1d(coefficients)
    
    t = temperature/Fermi.temperature(fraction_3he)
    
    # Temporary function for derivation of Fermi temperature 
    def fun(fraction_3he):
        return Fermi.temperature(temperature,fraction_3he)
    
    ################## FUNCTION ###############################################
    
    if temperature == 0:
            return polynom(fraction_3he)
    else:
        return Helium7.osmotic_pressure(0,pressure,fraction_3he) + fraction_3he**2/Helium4.molar_volume(temperature,pressure)*derivative(fun,fraction_3he)*quad(Fermi.molar_specific_heat,0,t,fraction_3he)
    

#%% 
def molar_entropy(temperature,pressure,fraction_3he):

    """
    ========== DESCRIPTION ==========


    This function return the molar entropy of a mixture of Helium 3 & 
    Helium 4 

    ========== VALIDITE ==========

    0 <= Temperature <= 2 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 100 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (2)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [EntropieMolaire]
        L'entropie molaire du mélange 3He-4He en [J/K/mol]

    ========== STATUS ==========

    Status : Vérifiée

    ========== A FAIRE ==========

    Contrainte sur la pression à vérifier
    A verifier pour les prochaines valeurs de l'entropie 3He et 4He

    """

    ################## MODULES ###############################################

    import Helium4,Fermi,Helium3

    ################## CONDITION 1 ####################################
    # Helium 4 est superfluide, Helium 3 assimilable à un liquide de Fermi
    if Temperature < TemperatureTransition(Pression,Concentration3He) or Concentration3He < ConcentrationConcentre(Temperature,Pression):
        return Concentration3He*Fermi.EntropieMolaire(Temperature,Pression,Concentration3He)+(1-Concentration3He)*Helium4.EntropieMolaire(Temperature,Pression)
    
    else:
    # Helium 4 est normal, Helium 3 est normal
        return Concentration3He*Helium3.EntropieMolaire(Temperature,Pression,Concentration3He)+(1-Concentration3He)*Helium4.EntropieMolaire(Temperature,Pression)


#%% PotentielChimique4He - Vérifiée
def PotentielChimique4He(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer le potentiel chimique de l'Helium4 dans
    un mélange 3He-4He en fonction de la température, de la pression et 
    de la concentration en Helium3 dans le mélange.

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (19)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [PotentielChimique4He]
        le potentiel chimique de l'Helium4 pur en [J/mol]

    ========== STATUS ==========

    Status : Vérifiée

    """

    ################## MODULES ###############################################

    import numpy as np
    import Helium4

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################
        
    ################## FONCTION SI CONDITIONS REMPLIE #####################
    
                Helium4.PotentielChimique(Temperature,Pression)-Helium4.VolumeMolaire(Temperature,Pression)*PressionOsmotique(Temperature,Pression,Concentration3He)

    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.PotentielChimique4He est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.PotentielChimique4He est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.PotentielChimique4He est invalide pour cette valeur de température T = '+str(Temperature)+' %')
        return np.nan


#%% Integrale Pression Osmotique - Vérifiée
def IntegralePressionOsmotique(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer l'intégraler de la pression osmotique du mélange 3He-4He
    par rapport à la Concentration d'Helium 3 divisée par x**2 en fonction de 
    la température, de la pression et de la concentration en Helium 3 dans le 
    mélange

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (24)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité


    ========== SORTIE ==========

    [IntegralePressionOsmotique]
        L'intégrale de la pression osmotique en [Pa]

    ========== STATUS ==========

    Status : Vérifiée
    
    ========== A FAIRE ==========

    Contrainte sur la pression à ajouter

    """

    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################


                Coefficients = [ 1.10244858e+09, -3.81423449e+08,  5.60699503e+07, -5.04026742e+06,
                3.57461458e+05,  1.84245496e+03, -4.60897007e-01,  0.00000000e+00]
                value = 0
                
    ################## FONCTION SI CONDITIONS REMPLIE #####################
    
                if Temperature == 0:
                    for i in range(len(Coefficients)):
                        value = value+Concentration3He**(i-2)*Coefficients[len(Coefficients)-i-1]
                    return value
                
    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de température T = '+str(Temperature)+' %')
        return np.nan

#%% 
def tricritical_temperature(pressure):

    """
    ========== DESCRIPTION ==========

    This function return the tempertature of helium 3 of the tri critical point
    at a given pressure

    ========== VALIDITE ==========

    <pressure> : [0->22e5]

    ========== FROM ==========

    CHAUDHRY (2012) - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (3.9)

    ========== INPUT ==========

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    ========== OUTPUT ==========

    <tricritical_temperature>
        -- float --
        The temperature of Helium 3 at the tricritical point
        []

    ========== STATUS ==========

    Status : Checked

    """
    ################## MODULES ################################################

    from cryopy.Helium import Helium7

    ################## CONDITION ##############################################
    
    assert pressure <= 22e5 and pressure >= 0 , 'The function '\
        ' Helium7.tricritical_temperature is not defined for '\
            'P = '+str(pressure)+' Pa'

    ################## INITIALISATION #########################################

    # Convert [Pa] to [Bar]
    pressure = pressure*1e-5
        
    ################## FUNCTION ###############################################
    
    if pressure == 0:
        return 0.867
    else :
        return Helium7.tricritical_temperature(0) - 0.12992576*pressure/(pressure + 2.5967345)-6.457263e-4*pressure


#%% 
def tricritical_fraction_3he(pressure):

    """
    ========== DESCRIPTION ==========

    This function return the fraction of helium 3 of the tri critical point
    at a given pressure

    ========== VALIDITE ==========

    <pressure> : [0->22e5]

    ========== FROM ==========

    CHAUDHRY (2012) - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A.5)

    ========== INPUT ==========

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]

    ========== OUTPUT ==========

    <tricritical_fraction_3he>
        -- float --
        The fraction of Helium 3 at the tricritical point
        []

    ========== STATUS ==========

    Status : Checked

    """
    ################## MODULES ###############################################

    from cryopy.Helium import Helium7

    ################## CONDITION ##############################################
    
    assert pressure <= 22e5 and pressure >= 0 , 'The function '\
        ' Helium7.tricritical_fraction_3he is not defined for '\
            'p = '+str(pressure)+' bar'
            
    ################## INITIALISATION #########################################

    # Convert from [Pa] to [Bar]
    pressure = pressure*1e-5
        
    ################## FUNCTION ###############################################
    
    if pressure == 0:
        return 0.674

    else:
        return Helium7.tricritical_fraction_3he(0) + 0.3037124*(Helium7.tricritical_temperature(0)-Helium7.tricritical_temperature(pressure))-4.41225e6*(Helium7.tricritical_temperature(0)-Helium7.tricritical_temperature(pressure))**9


#%% 
def transition_temperature(pressure,fraction_3he):

    """
    ========== DESCRIPTION ==========

    This function return the transition temperature called "lambda" 

    ========== VALIDITY ==========

    <pressure> : [0->15e5]
    <fraction_3he> : [0->Helium7.tricritical_fraction_3he(pressure)]
 
    ========== FRIL ==========

    CHAUDHRY - Thermoduynamic properties of liquid 3He-4He mixtures betxeen
    0.150mK and 1.8K - Equation (2.4)

    ========== ENTREE ==========

    <pressure>
        -- float --
        The pressure of Helium 4
        [Pa]
        
    <fraction_3he>
        -- float --
        The fraction of Helium 3 on mixture
        []
        
    ========== SORTIE ==========

    <transition_temperature>
        -- float --
        The transition temperature 
        [K]

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy.Helium import Helium7

    ################## CONDITIONS #############################################
    
    assert pressure <= 15e5 and pressure >= 0 , 'The function '\
        ' Helium7.transition_temperature is not defined for '\
            'P = '+str(pressure)+' Pa'

    assert fraction_3he <= Helium7.tricritical_fraction_3he(pressure) and fraction_3he >= 0 , 'The function Helium7.transition_temperature '\
            'is not defined for x = '+str(fraction_3He*100)+' %'
    
    ################## INITIALISATION #########################################

    # Convert from [Pa] to [Bar]
    pressure = pressure*1e-5
    
    coefficients = np.array([[-0.209148,-0.1269791,0.0102283],
                         [0.960222,-0.2165742,0.0169801],
                         [0.549920,-0.1198491,0.0092997],
                         [0.080280,0.02291499,-0.0020886],
                         [-0.746805,0.0173549,-0.0028598],
                         [-0.180743,0.1120251,-0.0152076],
                         [0.316170,0.1723264,-0.0201411],
                         [-2.620259,0.0024823,0.0009255],
                         [-1.023726,0.0013175,0.0009397]])
    
    ################## FUNCTION ###############################################

    K1 = coefficients[7][0]+coefficients[7][1]*pressure + coefficients[7][2]*pressure**2
    K2 = coefficients[8][0]+coefficients[8][1]*pressure + coefficients[8][2]*pressure**2
    
    return Helium7.tricritical_temperature(pressure)+K1*(fraction_3he-Helium7.tricritical_fraction_3he(pressure))+K2*(fraction_3he-Helium7.tricritical_fraction_3he(pressure))**2

#%% 
def fraction_3he_dilute(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the fraction of Helium 3 inside the dilute phase

    ========== VALIDITY ==========

    <temperature> : [0->Helium7.tricritical_temperature(pressure)]
    <pressure> : [0->15e5]

    ========== FROM ==========

    CHAUDHRY - Thermoduynamic properties of liquid 3He-4He mixtures betxeen
    0.150mK and 1.8K - Equation (2.4)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the dilute phase
        [Pa]

    <pressure>
        -- float --
        The pressure of the dilute phase
        [Pa]

    ========== OUTPUT ==========

    <fraction_3he_dilute>
        -- float --
        The fraction of Helium 3 inside the dilute phase
        []

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy.Helium import Helium7

    ################## CONDITIONS #############################################

    assert temperature <= Helium7.tricritical_temperature(pressure) and temperature >= 0 , 'The function Helium7.fraction_3he_dilute '\
            'is not defined for T = '+str(temperature)+' K'

    assert pressure <= 15e5 and pressure >= 0 , 'The function '\
        ' Helium7.fraction_3he_dilute is not defined for '\
            'P = '+str(pressure)+' Pa'
        
    ################## INITIALISATION #########################################
    
    # Convert from [Pa] to [Bar]
    pressure = pressure*1e-5

    coefficients = np.array([[-0.209148,-0.1269791,0.0102283],
                         [0.960222,-0.2165742,0.0169801],
                         [0.549920,-0.1198491,0.0092997],
                         [0.080280,0.02291499,-0.0020886]])
    

    ################## FUNCTION ###############################################

    K0 = coefficients[0][0]+coefficients[0][1]*pressure + coefficients[0][2]*pressure**2
    K1 = coefficients[1][0]+coefficients[1][1]*pressure + coefficients[1][2]*pressure**2
    K2 = coefficients[2][0]+coefficients[2][1]*pressure + coefficients[2][2]*pressure**2
    Ka = coefficients[3][0]+coefficients[3][1]*pressure + coefficients[3][2]*pressure**2
    
    return tricritical_fraction_3he(pressure) + K0*(temperature-tricritical_temperature(pressure))/((temperature-tricritical_temperature(pressure))-Ka) + K1*(temperature-tricritical_temperature(pressure))+K2*(temperature-tricritical_temperature(pressure))**2


#%% ConcentrationConcentre - 
def fraction_3he_concentrate(temperature,pressure):

    """
    ========== DESCRIPTION ==========

    This function return the fraction of Helium 3 inside the concentrate phase

    ========== VALIDITY ==========

    <pressure> : [0->15e5]
    <temperature> : []

    ========== FROM ==========

    CHAUDHRY - Thermoduynamic properties of liquid 3He-4He mixtures betxeen
    0.150mK and 1.8K - Equation (A.8)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the concentrate phase
        [Pa]

    <pressure>
        -- float --
        The pressure of the dilute concentrate
        [Pa]

    ========== OUTPUT ==========

    <fraction_3he_concentrate>
        -- float --
        The fraction of Helium 3 inside the concentrate phase
        []

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy.Helium import Helium7

    ################## CONDITIONS #############################################

    assert temperature <= Helium7.tricritical_temperature(pressure) and temperature >= 0 , 'The function Helium7.fraction_3he_concentrate '\
            'is not defined for T = '+str(temperature)+' K'
            
    assert pressure <= 15e5 and pressure >= 0 , 'The function '\
        ' Helium7.fraction_3he_concentrate is not defined for '\
            'P = '+str(pressure)+' Pa'

    ################## INITIALISATION #########################################
    
    # Convert [Pa] to [Bar]
    pressure = pressure*1e-5

    coefficients = np.array([[-0.746805,0.0173549,-0.0028598],
                         [-0.180743,0.1120251,-0.0152076],
                         [0.316170,0.1723264,-0.0201411]])
    
    ################## FUNCTION ###############################################

    K1 = coefficients[0][0]+coefficients[0][1]*pressure + coefficients[0][2]*pressure**2
    K2 = coefficients[1][0]+coefficients[1][1]*pressure + coefficients[1][2]*pressure**2
    K3 = coefficients[2][0]+coefficients[2][1]*pressure + coefficients[2][2]*pressure**2
    
    return Helium7.tricritical_fraction_3he(pressure) + K1*(temperature-Helium7.tricritical_temperature(pressure))+K2*(temperature-Helium7.tricritical_temperature(pressure))**2+K3*(temperature-Helium7.tricritical_temperature(pressure))**3
             
