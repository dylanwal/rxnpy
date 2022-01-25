
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
            ["Molecular Formula", "chem_formula"],
            ["CAS", "cas"]
        ]

        self.pubchem_properties = [
            # [key on pubchem, key to be stored as, has units, default units (None skips)]
            ["Color/Form", "color", False],
            ["Taste", "taste", False],
            ['Polymerization', 'polymerization', False],
            ['Physical Description', 'physical_description', False],
            ["Odor", "odor", False],
            ['Solubility', "solubility", False],
            ["Stability/Shelf Life", "stability", False],
            ["Decomposition", "decomposition", False],
            ["Kovats Retention Index", "kovats_index", True, None],
            ["Odor Threshold", "oder_threshold", True, None],
            ["Density", "density", True, "kilogram / meter ** 3"],
            ["Boiling Point", "temp_boil", True, "kelvin"],
            ["Melting Point", "temp_melt", True, "kelvin"],
            ["Viscosity", "viscosity", True, None],
            ["Vapor Pressure", "vapor_pres", True, "kilogram / meter / second ** 2"],
            ["Vapor Density", "vapor_density", True, "kilogram / meter ** 3"],  # (Relative to Air)
            ["Flash Point", "temp_flash", True, "kelvin"],
            ["Autoignition Temperature", "temp_autoignition", True, "kelvin"],
            ["Heat of Combustion", "heat_combustion", True, None],
            ["Heat of Vaporization", "heat_vaporization", True, None],
            ["Surface Tension", "surface_tension", True, "kilogram / second ** 2"],
            ["Refractive Index", "refract_index", True, None],
            ["LogP", "log_p", True, None],
            ["pKa", "pka", True, None],
            ["LogS", "log_s", True, None],
            ["LogKoa", "log_koa", True, None],
            ["pH", 'ph', True, None],
            ["Henrys Law Constant", "henry_constant", True, None],
            ["Optical Rotation", "optical_rot", True, None],
            ['Ionization Potential', 'ionization_potential', True, None],
            ['Dissociation Constants', "dissociation_constants", None],
            ['Corrosivity', "corrosivity", None],
            ["Atmospheric OH Rate Constant", "atm_oh_rate_constant", None]
        ]

        self.delete_text = [
            "approx.",
            "approximate",
            "approx",
            "closed cup",
            "(Closed cup)"
            "(closed cup)"
            "Closed cup"
            "(NTP, 1992)",
            "USCG, 1999",
            "Open cup",
            "open cup",
            "(open cup)",
            "(Open cup)"
            'EPA, 1998',
            'NIOSH, 2016',
            "c.c."
            ]


config_PubChem = ConfigPubChem()
