from unittest import TestCase

from data_suppliers.no.no_po import sprawdz_polozenie


class Test(TestCase):
    def test_sprawdz_polozenie(self):
        assert sprawdz_polozenie("Wielkie Drogi", "Skawina", "krakowski") == "Miejscowość"
        assert sprawdz_polozenie("Altanowa", "Skawina", "krakowski") == "Ulica"
        assert sprawdz_polozenie("Podbory", "Skawina", "krakowski") == "Ulica"
        assert sprawdz_polozenie("Skawińska", "Skawina", "krakowski") == "Ulica"
        assert sprawdz_polozenie("Rzozów", "Skawina", "krakowski") == "Miejscowość"
        assert sprawdz_polozenie("Ochodza", "Skawina", "krakowski") == "Miejscowość"
