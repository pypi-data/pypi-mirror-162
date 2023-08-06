#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Aluminium 6061-T6

    ========== VALIDITY ==========

    <temperature> : [0.095 -> 70]

    ========== FROM ==========

    Barucci et al. , "Aluminium alloys for space applications: low temperature
    thermal conductivity of A6061-T6 and A1050"

    Sauvage et al. , "A new thermo-mechanical structure design for space
    qualified close-cycle dilution refrigerator"

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <thermal_conductivity>
        -- float --
        The thermal conductivity of the material
        [W].[m]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========


    """
    ################## CONDITIONS #############################################

    assert temperature <= 70 and temperature >= 0.095 ,'The function '\
        ' Al6061_T6.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'


    ################## PACKAGES ###############################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = [ 2.39703410e-01,  1.88576787e+00, -4.39839595e-01,  9.53687043e-02,
            2.05443158e-03, -2.89908152e-03, -1.33420775e-04,  1.14453429e-04,
           -8.72830666e-06]

    ################## FUNCTION ###############################################

    if temperature <= 4.2 :
        result = np.exp(np.polynomial.chebyshev.chebval(np.log(temperature),coefficients))
    else:
        result = temperature / (0.445 + 4.9e-7*temperature**3)

    return result


#%%
def mass_specific_heat(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the mass specific heat of Aluminium 6061-T6

    ========== VALIDITY ==========

    <temperature> : [3 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/6061%20Aluminum/6061_T6Aluminum_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <mass_specific_heat>
        -- float --
        The specific heat
        [J].[kg]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 3 ,'The function '\
        ' AL6061_T6.mass_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([46.6467,-314.292,866.662,-1298.3,1162.27,-637.795,210.351,-38.3094,2.96344])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log10(temperature)**i

    return 10**result


#%%
def linear_thermal_expansion(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Aluminium 6061-T6

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <linear_thermal_expansion>
        -- float --
        The linear thermal expansion
        []

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 4 ,'The function '\
        ' Al6061_T6.linear_thermal_expansion is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-4.1277e2,-3.0389e-1,8.7696e-3,-9.9821e-6,0])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*temperature**i

    return result*1e-5

#%%
def young_modulus(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the Young's modulus of Aluminium 6061-T6

    ========== VALIDITY ==========

    <temperature> : [0 -> 295]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <young_modulus>
        -- float --
        The Young's modulus
        [Pa]

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 295 and temperature >= 0 ,'The function '\
      ' Al6061_T6.young_modulus is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([7.771221e1,1.030646e-2,-2.924100e-4,8.993600e-7,-1.070900e-9])

    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients1)):
      result = result + coefficients[i]*temperature**i

    return result*10**9
