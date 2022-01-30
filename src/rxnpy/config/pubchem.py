
class ConfigPubChem:
    """

    Attributes
    ----------
    pubchem_identities:
    pubchem_properties:
    delete_text:

    """
    def __init__(self):
        self.pubchem_identities = [
            # [key on pubchem, key to be stored as]
            # "pubchem_cid" handled in class
            # "name" handled in class
            # "names" handled in class
            ["InChI", "inchi"],
            ["InChI Key", "inchi_key"],
            ["Canonical SMILES", "smiles"],
            ["Molecular Formula", "mol_form"],
            ["CAS", "cas"]
        ]

        self.pubchem_properties = [
            # [key on pubchem, key to be stored as, has units, default units (None skips)]
            # molar_mass calculated from molecular_formula
            ["Color/Form", "color", False, None],
            ["Taste", "taste", False, None],
            ['Polymerization', 'polymerization', False, None],
            ['Physical Description', 'physical_description', False, None],
            ["Odor", "odor", False, None],
            ['Solubility', "solubility", False, None],
            ["Stability/Shelf Life", "stability", False, None],
            ["Decomposition", "decomposition", False, None],
            ["Kovats Retention Index", "kovats_index", True, None],
            ["Odor Threshold", "oder_threshold", True, "part_per_million"],
            ["Density", "density", True, "kilogram / meter ** 3"],
            ["Boiling Point", "temp_boil", True, "kelvin"],
            ["Melting Point", "temp_melt", True, "kelvin"],
            ["Viscosity", "viscosity", True, None],
            ["Vapor Pressure", "vapor_pres", True, "kilogram / meter / second ** 2"],
            ["Vapor Density", "vapor_density", True, ""],  # (Relative to Air)
            ["Flash Point", "temp_flash", True, "kelvin"],
            ["Autoignition Temperature", "temp_autoignition", True, "kelvin"],
            ["Heat of Combustion", "heat_combustion", True, None],
            ["Heat of Vaporization", "heat_vaporization", True, None],
            ["Surface Tension", "surface_tension", True, "kilogram / second ** 2"],
            ["Refractive Index", "refract_index", True, ""],
            ["LogP", "log_p", True, ""],
            ["pKa", "pka", True, None],
            ["LogS", "log_s", True, None],
            ["LogKoa", "log_koa", True, None],
            ["pH", 'ph', True, None],
            ["Henrys Law Constant", "henry_constant", True, 'kilogram * meter ** 2 / mole / second ** 2'],
            ["Optical Rotation", "optical_rot", True, "deg"],
            ['Ionization Potential', 'ionization_potential', True, None],
            ['Dissociation Constants', "dissociation_constants", None, None],
            ['Corrosivity', "corrosivity", None, None],
            ["Atmospheric OH Rate Constant", "atm_oh_rate_constant", None, None]
        ]

        self.delete_text = [
            "approx.",
            "approximate",
            "approx",
            "closed cup",
            "(Closed cup)",
            "(closed cup)",
            "Closed cup",
            "- closed cup",
            "(NTP, 1992)",
            "NTP, 1992",
            "USCG, 1999",
            "Open cup",
            "open cup",
            "(open cup)",
            "(Open cup)",
            'EPA, 1998',
            '(EPA, 1998)',
            'NIOSH, 2016',
            '(NIOSH, 2016)',
            "c.c.",
            "/Estimated/",
            "/extrapolated/",
            "LogP",
            "HSDB"
            ]

        self.replace_text = [
            ["dec C", "degC"],
            ['°C/D', 'degC'],
            ["/4 °C", ""],
            ["MM HG", "mmHg"],
            ["MG", "mg"],
            ["Â°", "degC"],
            ["ºC", "degC"],
            ["[0-9]{1,5} ?%", ""]
        ]


config_PubChem = ConfigPubChem()
