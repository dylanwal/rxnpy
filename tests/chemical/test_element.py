

from rxnpy.chemical import Element

hydrogen = {
        "name": "Hydrogen",
        "appearance": "colorless",
        "atomic_mass": 1.008,
        "bp": 20.271,
        "category": "diatomic nonmetal",
        "color": "colorless",
        "density": 0.08988,
        "mp": 13.99,
        "molar_heat": 28.836,
        "atomic_number": 1,
        "period": 1,
        "phase": "gas",
        "symbol": "H",
        "shells": [
            1
        ],
        "electron_configuration": "1s1",
        "electron_configuration_semantic": "1s1",
        "electron_affinity": 72.769,
        "electronegativity_pauling": 2.2,
        "ionization_energies": [
            1312
        ],
        "cpk-hex": "ffffff",
        "group": 1
    }


def test_creation():
    e = Element(**hydrogen)
    assert e.name == "Hydrogen"
