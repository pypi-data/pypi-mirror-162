#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def thermal_conductivity(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Stainless Steel 304

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/304LStainless/304Stainless_rev.htm

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

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 4 ,'The function '\
        ' SS304.thermal_conductivity is not defined for '\
            'T = '+str(temperature)+' K'

    ################## INITIALISATION #########################################

    coefficients = np.array([-1.4087,1.3982,0.2543,-0.6260,0.2334,0.4256,-0.4658,0.1650,-0.0199])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log10(temperature)**i
    return 10**result


#%%
def mass_specific_heat(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Stainless Steel 304

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/304LStainless/304Stainless_rev.htm

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <mass_specific_heat>
        -- float --
        The specific heat
        [J].[Kg]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 300 and temperature >= 4 ,'The function '\
        ' SS304.mass_specific_heat is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([22.0061,-127.5528,303.6470,-381.0098,274.0328,-112.9212,24.7593,-2.239153,0])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(coefficients)):
        result = result + coefficients[i]*np.log10(temperature)**i

    return 10**result

#%%
def linear_thermal_expansion(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Stainless Steel 304

    ========== VALIDITY ==========

    <temperature> : [4 -> 300]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/304LStainless/304Stainless_rev.htm

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
        ' NbTi.linear_thermal_expansion is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients = np.array([-2.9554e2,-3.9811e-1,9.2683e-3,-2.026e-5,1.7127e-8])
    result = 0

    ################## FUNCTION ###############################################

    for i in range(len(coefficients)):
        result = result + coefficients[i]*temperature**i

    return result*1e-5


#%%
def young_modulus(temperature):

    """
    ========== DESCRIPTION ==========

    This function return the Young's modulus of Stainless Steel 304

    ========== VALIDITY ==========

    <temperature> : [5 -> 293]

    ========== FROM ==========

    https://trc.nist.gov/cryogenics/materials/304LStainless/304Stainless_rev.htm

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

    assert temperature <= 293 and temperature >= 5 ,'The function '\
        ' SS304.young_modulus is not defined for '\
            'T = '+str(temperature)+' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    coefficients1 = np.array([2.100593e2,1.534883e-1,-1.617390e-3,5.117060e-6,-6.154600e-9])
    coefficients2 = np.array([2.098145e2,1.217019e-1,-1.1469999e-2,3.605430e-4,-3.017900e-6])

    result = 0

    ################## FUNCTION ###############################################

    if temperature <= 293 and temperature >= 57:
      for i in range(len(coefficients1)):
          result = result + coefficients1[i]*temperature**i
    else:
      for i in range(len(coefficients2)):
          result = result + coefficients2[i]*temperature**i

    return result*10**9
