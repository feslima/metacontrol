# ----------------------------- INPUT SECTION -----------------------------
BLOCKS_INPUT_CATALOGUE = {
    'Compr':
        [
            {'Name': 'PRES', 'Description': 'Discharge Pressure'},
            {'Name': 'DELP', 'Description': 'Pressure Change'},
            {'Name': 'PRATIO', 'Description': 'Pressure Ratio (outlet pressure/inlet pressure)'},
            {'Name': 'POWER', 'Description': 'Brake Horsepower Input'}
        ],
    'MCompr':
        [
            {'Name': 'PRES', 'Description': 'Outlet pressure of compressor.'},
            {'Name': 'CL_TEMP', 'Description': 'Outlet temperature of the cooler.'}
        ],
    'FSplit':
        [
            {'Name': 'FRAC', 'Description': 'Fraction of inlet stream going to this outlet stream'},
            {'Name': 'BASIS_FLOW', 'Description': 'Flow Rate'},
            {'Name': 'VOL_FLOW', 'Description': 'Volumetric Flow Rate'},
            {'Name': 'BASIS_LIMIT', 'Description': 'Limit Flow Rate'},
            {'Name': 'VOL_LIMIT', 'Description': 'Volumetric Limit Flow Rate'},
            {'Name': 'BASIS_C_LIM', 'Description': 'Cumulative Limit Flow Rate'},
            {'Name': 'VOL_C_LIM', 'Description': 'Volumetric Cumulative Limit Flow Rate'},
            {'Name': 'R_FRAC', 'Description': 'Fraction of residue going to this outlet stream'}
        ],
    'Flash2':
        [
            {'Name': 'TEMP', 'Description': 'Temperature'},
            {'Name': 'PRES', 'Description': 'Pressure'},
            {'Name': 'DUTY', 'Description': 'Heat duty'},
            {'Name': 'VFRAC', 'Description': 'Molar vapor fraction'}
        ],
    'Flash3':
        [
            {'Name': 'TEMP', 'Description': 'Flash Temperature'},
            {'Name': 'PRES', 'Description': 'Flash Pressure'},
            {'Name': 'VFRAC', 'Description': 'Vapor Fraction'},
            {'Name': 'DUTY', 'Description': 'Heat Duty'}
        ],
    'HeatX':
        [
            {'Name': 'SPEC', 'Description': 'Exchanger Specification'},
            {'Name': 'VALUE', 'Description': 'Value of the Exchanger Specification'}
        ],
    'Heater':
        [
            {'Name': 'TEMP', 'Description': 'Heater Temperature'},
            {'Name': 'PRES', 'Description': 'Heater Pressure'},
            {'Name': 'DUTY', 'Description': 'Heater Duty'},
            {'Name': 'VFRAC', 'Description': 'Heater Vapor Fraction'},
            {'Name': 'DPPARM', 'Description': 'Pressure Drop Correlation Parameter'},
            {'Name': 'DELT', 'Description': 'Heater Temperature Change'},
            {'Name': 'DEGSUP', 'Description': 'Degrees of Superheating'},
            {'Name': 'DEGSUB', 'Description': 'Degrees of Subcooling'}
        ],
    'MHeatX':
        [
            {'Name': 'VALUE', 'Description': 'Desired value fot the specification'}
        ],
    'Mixer':
        [
            {'Name': 'PRES', 'Description': 'Pressure'},
            {'Name': 'T_EST', 'Description': 'Temperature Estimate'}
        ],
    'Pump':
        [
            {'Name': 'PRES', 'Description': 'Pump Discharge Pressure'},
            {'Name': 'DELP', 'Description': 'Pressure Increase'},
            {'Name': 'PRATIO', 'Description': 'Pressure Ratio'},
            {'Name': 'POWER', 'Description': 'Power Required'},
            {'Name': 'EFF', 'Description': 'Pump Efficiency'},
            {'Name': 'DEFF', 'Description': 'Pump Driver Efficiency'}
        ],
    'RadFrac':
        [
            {'Name': "BASIS_D", 'Description': 'Total Distillate Flow Rate'},
            {'Name': "BASIS_B", 'Description': 'Liquid Bottoms Flow Rate'},
            {'Name': "BASIS_L1", 'Description': 'Reflux Flow Rate'},
            {'Name': "BASIS_VN", 'Description': 'Boilup Flow Rate'},
            {'Name': "BASIS_BR", 'Description': 'Boilup Ratio (Boilup Rate/Bottoms Rate)'},
            {'Name': "BASIS_RR", 'Description': 'Reflux Ratio (Reflux Rate/Distillate Rate)'},
            {'Name': "D:F", 'Description': 'Ratio of Distillate to Feed Flow Rate'},
            {'Name': "B:F", 'Description': 'Ratio of Bottoms to Feed Flow Rate'},
            {'Name': "Q1", 'Description': 'Condenser Duty'},
            {'Name': "QN", 'Description': 'Reboiler Duty'}
        ],
    'RPlug':
        [
            {'Name': 'CTEMP', 'Description': 'Constant thermal fluid temperature'},
            {'Name': 'PRES', 'Description': 'Absolute units: Process stream pressure at reactor inlet if value > 0; Pressure drop at inlet if value <= 0. Gauge units: Pressure at inlet for all values.'}
        ],
    'Valve':
        [
            {'Name': 'P_OUT', 'Description': 'Outlet Pressure'},
            {'Name': 'P_DROP', 'Description': 'Pressure Drop'}
        ],
}

STREAMS_INPUT_CATALOGUE = {'HEAT':
    [
        {'Name': 'DUTY', 'Description': 'Stream duty'},
        {'Name': 'TEMP', 'Description': 'Starting temperature'},
        {'Name': 'TEND', 'Description': 'End temperature'}
    ],
    'WORK':
        [
            {'Name': 'SPEED', 'Description': 'Stream speed'},
            {'Name': 'POWER', 'Description': 'Stream power'},
        ],
    'MATERIAL':
        [
            {'Name': 'FLOW', 'Description': 'Component Flow, Fraction or Concentration of the Components'},
            {'Name': 'TOTFLOW', 'Description': 'Total Flow rate of the stream'},
            {'Name': 'PRES', 'Description': 'Stream Pressure'},
            {'Name': 'TEMP', 'Description': 'Stream Temperature'},
            {'Name': 'VFRAC', 'Description': 'Stream Vapor Fraction'}
        ]
}

# ----------------------------- OUTPUT SECTION -----------------------------

# RadFrac block profile vars that need to be inserted on tree construction
RADFRAC_PROFILE_VARS = ['B_PRES', 'B_TEMP', 'X', 'Y']

BLOCKS_OUTPUT_CATALOGUE = {
    'Compr':
        [
            {'Name': 'IND_POWER', 'Description': 'Indicated horsepower'},
            {'Name': 'BRAKE_POWER', 'Description': 'Brake horsepower'},
            {'Name': 'WNET', 'Description': 'Net work required'},
            {'Name': 'POWER_LOSS', 'Description': 'Power loss'},
            {'Name': 'EPC', 'Description': 'Efficiency'},
            {'Name': 'EFF_MECH', 'Description': 'Mechanical efficiency'},
            {'Name': 'POC', 'Description': 'Outlet pressure'},
            {'Name': 'TOC', 'Description': 'Outlet temperature'},
            {'Name': 'TOS', 'Description': 'Isentropic outlet temperature'},
            {'Name': 'B_VFRAC', 'Description': 'Vapor fraction'},
            {'Name': 'DIS', 'Description': 'Displacement'},
            {'Name': 'EV', 'Description': 'Volumetric efficiency'}
        ],
    'MCompr':
        [
            {'Name': 'B_PRES2', 'Description': 'Outlet pressure (last stage)'},
            {'Name': 'QCALC2', 'Description': 'Total Work'},
            {'Name': 'DUTY_OUT', 'Description': 'Total Cooling Duty'},
            {'Name': 'WNET', 'Description': 'Net work required'},
            {'Name': 'QNET', 'Description': 'Net cooling duty'}
        ],
    'FSplit':
        [
            {'Name': 'STREAMFRAC', 'Description': 'Split fraction'},
            {'Name': 'STREAM_ORDER', 'Description': 'Stream Order'}
        ],
    'Flash2':
        [
            {'Name': 'B_TEMP', 'Description': 'Outlet temperature'},
            {'Name': 'B_PRES', 'Description': 'Outlet pressure'},
            {'Name': 'B_VFRAC', 'Description': 'Vapor fraction(mole)'},
            {'Name': 'MVFRAC', 'Description': 'Vapor fraction(mass)'},
            {'Name': 'QCALC', 'Description': 'Heat duty'},
            {'Name': 'QNET', 'Description': 'Net Duty'},
            {'Name': 'LIQ_RATIO', 'Description': '1st liquid/total liquid'},
            {'Name': 'PDROP', 'Description': 'Pressure drop'}
        ],
    'Flash3':
        [
            {'Name': 'B_TEMP', 'Description': 'Outlet temperature'},
            {'Name': 'B_PRES', 'Description': 'Outlet pressure'},
            {'Name': 'B_VFRAC', 'Description': 'Vapor fraction(mole)'},
            {'Name': 'MVFRAC', 'Description': 'Vapor fraction(mass)'},
            {'Name': 'QCALC', 'Description': 'Heat duty'},
            {'Name': 'QNET', 'Description': 'Net Duty'},
            {'Name': 'LIQ_RATIO', 'Description': '1st liquid/total liquid'},
            {'Name': 'PDROP', 'Description': 'Pressure drop'}
        ],
    'HeatX':
        [
            {'Name': 'HOTINT', 'Description': 'Temperature of the inlet hot stream'},
            {'Name': 'HOTINP', 'Description': 'Pressure of the inlet hot stream'},
            {'Name': 'HOTINVF', 'Description': 'Vapor fraction of the inlet hot stream'},
            {'Name': 'HIN_L1FRAC', 'Description': '1st liquid/total liquid of the inlet hot stream'},
            {'Name': 'COLDINT', 'Description': 'Temperature of the inlet cold stream'},
            {'Name': 'COLDINP', 'Description': 'Pressure of the inlet cold stream'},
            {'Name': 'COLDINVF', 'Description': 'Vapor fraction of the inlet cold stream'},
            {'Name': 'CIN_L1FRAC', 'Description': '1st liquid/total liquid of the inlet cold stream'},
            {'Name': 'HOT_TEMP', 'Description': 'Temperature of the outlet hot stream'},
            {'Name': 'HOT_PRES', 'Description': 'Pressure of the outlet hot stream'},
            {'Name': 'HOT_VFRAC', 'Description': 'Vapor fraction of the outlet hot stream'},
            {'Name': 'HOUT_L1FRAC', 'Description': '1st liquid/total liquid of the outlet hot stream'},
            {'Name': 'COLD_TEMP', 'Description': 'Temperature of the outlet cold stream'},
            {'Name': 'COLD_PRES', 'Description': 'Pressure of the outlet cold stream'},
            {'Name': 'COLD_FRAC', 'Description': 'Vapor fraction of the outlet cold stream'},
            {'Name': 'COUT_L1FRAC', 'Description': '1st liquid/total liquid of the outlet cold stream'}
        ],
    'Heater':
        [
            {'Name': 'B_TEMP', 'Description': 'Outlet temperature'},
            {'Name': 'B_PRES', 'Description': 'Outlet pressure'},
            {'Name': 'B_VFRAC', 'Description': 'Vapor fraction'},
            {'Name': 'QCALC', 'Description': 'Heat duty'},
            {'Name': 'QNET', 'Description': 'Net Duty'},
            {'Name': 'LIQ_RATIO', 'Description': '1st liquid/total liquid'},
            {'Name': 'PDROP', 'Description': 'Pressure drop'}
        ],
    'MHeatX':
        [
            {'Name': 'IN_TEMP', 'Description': 'Inlet temperatures'},
            {'Name': 'IN_PRES', 'Description': 'Inlet pressure'},
            {'Name': 'IN_VF', 'Description': 'Inlet vapour fraction'},
            {'Name': 'B_TEMP', 'Description': 'Outlet temperature'},
            {'Name': 'B_PRES', 'Description': 'Outlet pressure'},
            {'Name': 'B_VFRAC', 'Description': 'Outlet vapour fraction'},
            {'Name': 'QCALC', 'Description': 'Duty'},
            {'Name': 'QCALC2', 'Description': 'Overall duty'}
        ],
    'Mixer':
        [
            {'Name': 'B_TEMP', 'Description': 'Outlet temperature'},
            {'Name': 'B_PRES', 'Description': 'Outlet pressure'},
            {'Name': 'B_VFRAC', 'Description': 'Vapor fraction'},
            {'Name': 'LIQ_RATIO', 'Description': '1st liquid/total liquid'},
            {'Name': 'PDROP', 'Description': 'Pressure drop'}
        ],
    'Pump':
        [
            {'Name': 'FLUID_POWER', 'Description': 'Fluid Power'},
            {'Name': 'BRAKE_POWER', 'Description': 'Brake Power'},
            {'Name': 'ELEC_POWER', 'Description': 'Electricity'},
            {'Name': 'VFLOW', 'Description': 'Volumetric Flow Rate'},
            {'Name': 'PDRP', 'Description': 'Pressure Change'},
            {'Name': 'NPSH-AVAIL', 'Description': 'NPSH Available'},
            {'Name': 'HEAD_CAL', 'Description': 'Head Developed'},
            {'Name': 'CEFF', 'Description': 'Pump Efficiency used'},
            {'Name': 'WNET', 'Description': 'Net Work Required'},
            {'Name': 'POC', 'Description': 'Outlet Pressure'},
            {'Name': 'TOC', 'Description': 'Outlet Temperature'}
        ],
    'RadFrac':
        [
            {'Name': 'TOP_TEMP', 'Description': 'Temperature of Condenser/Top Stage'},
            {'Name': 'SCTEMP', 'Description': 'Subcooled temperature of Condenser/Top Stage'},
            {'Name': 'COND_DUTY', 'Description': 'Heat duty of Condenser/Top Stage'},
            {'Name': 'SCDUTY', 'Description': 'Subcooled duty of Condenser/Top Stage'},
            {'Name': 'MOLE_D', 'Description': 'Distillate rate'},
            {'Name': 'MOLE_L1', 'Description': 'Reflux rate'},
            {'Name': 'MOLE_RR', 'Description': 'Reflux ratio'},
            {'Name': 'MOLE_DW', 'Description': 'Free water distillate rate'},
            {'Name': 'RW', 'Description': 'Free water reflux ratio'},
            {'Name': 'MOLE_DFR', 'Description': 'Distillate to feed ratio'},
            {'Name': 'BOTTOM_TEMP', 'Description': 'Temperature of Reboiler Bottom Stage'},
            {'Name': 'REB_DUTY', 'Description': 'Heat duty of Reboiler Bottom Stage'},
            {'Name': 'MOLE_B', 'Description': 'Bottoms rate'},
            {'Name': 'MOLE_VN', 'Description': 'Boilup rate'},
            {'Name': 'MOLE_BR', 'Description': 'Boilup ratio'},
            {'Name': 'MOLE_BFR', 'Description': 'Bottoms to feed ratio'},
            {'Name': 'B_PRES', 'Description': 'Pressure profile'},
            {'Name': 'B_TEMP', 'Description': 'Temperature profile'},
			{'Name': 'X', 'Description': 'Liquid phase molar composition profile'},
			{'Name': 'Y', 'Description': 'Vapour phase molar composition profile'}
        ],
    'RPlug':
        [
            {'Name': 'QCALC', 'Description': 'Heat duty'},
            {'Name': 'TMIN', 'Description': 'Minimum temperature'},
            {'Name': 'TMAX', 'Description': 'Maximum temperature'},
            {'Name': 'RES_TIME', 'Description': 'Residence time'}
        ],
    'Valve':
        [
            {'Name': 'P_OUT_OUT', 'Description': 'Outlet Pressure'},
            {'Name': 'VALVE_DP', 'Description': 'Pressure Drop'},
            {'Name': 'TCALC', 'Description': 'Outlet Temperature'},
            {'Name': 'VCALC', 'Description': 'Outlet Vapor Fraction'},
            {'Name': 'PIPE_FIT_FAC2', 'Description': 'Piping Geometry Factor'}
        ]
}

STREAMS_OUTPUT_CATALOGUE = {
    'MATERIAL':
        [
            {'Name': 'TEMP_OUT', 'Description': 'Temperature'},
            {'Name': 'PRES_OUT', 'Description': 'Pressure'},
            {'Name': 'VFRAC_OUT', 'Description': 'Molar Vapor Fraction'},
            {'Name': 'LFRAC', 'Description': 'Molar Liquid Fraction'},
            {'Name': 'SFRAC', 'Description': 'Molar Solid Fraction'},
            {'Name': 'MASSVFRA', 'Description': 'Mass Vapor Fraction'},
            {'Name': 'MASSSFRA', 'Description': 'Mass Solid Fraction'},
            {'Name': 'HMX', 'Description': 'Molar Enthalpy'},
            {'Name': 'HMX_MASS', 'Description': 'Mass Enthalpy'},
            {'Name': 'SMX', 'Description': 'Molar Entropy'},
            {'Name': 'SMX_MASS', 'Description': 'Mass Entropy'},
            {'Name': 'RHOMX', 'Description': 'Molar Density'},
            {'Name': 'RHOMX_MASS', 'Description': 'Mass Density'},
            {'Name': 'HMX_FLOW', 'Description': 'Enthalpy Flow'},
            {'Name': 'MWMX', 'Description': 'Average Molecular Weight'},
            {'Name': 'MOLEFLMX', 'Description': 'Total Mole Flow'},
            {'Name': 'MOLEFLOW', 'Description': 'Mole Flow of Component'},
            {'Name': 'MOLEFRAC', 'Description': 'Mole Fraction of Component'},
            {'Name': 'MASSFLMX', 'Description': 'Total Mass Flow'},
            {'Name': 'MASSFLOW', 'Description': 'Mass Flow of Component'},
            {'Name': 'MASSFRAC', 'Description': 'Mass Fraction of Component'},
            {'Name': 'VOLFLMX', 'Description': 'Total Volume Flow'}
		]
}

# ----------------------------- MERGE SECTION -----------------------------
BLOCKS_CATALOGUE = {'Input': BLOCKS_INPUT_CATALOGUE,
                    'Output': BLOCKS_OUTPUT_CATALOGUE}

STREAMS_CATALOGUE = {'Input': STREAMS_INPUT_CATALOGUE,
                     'Output': STREAMS_OUTPUT_CATALOGUE}