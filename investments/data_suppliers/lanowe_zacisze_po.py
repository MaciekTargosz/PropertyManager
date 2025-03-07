import logging
import datetime
import uuid


from db.property import Flat, Property

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
}
logger = logging.getLogger(__name__)

class LanoweZacisze():
    __investment_name = "Łanowe Zacisze"
    __URL = "https://lanowezacisze.pl/#mieszkania"

    def get_search_url(self):
        return self.__URL

    def get_flats_rows(self, soup):
        return soup.select("table.wpDataTable tbody tr")

    def get_flat_data(self, flat_row):
        rows = flat_row.select("td")
        flat_id = rows[0].text
        level_temp = rows[1].text
        if level_temp == "parter":
            level = 0
        else:
            level = 1
        area = float(rows[2].text)
        #parking_place = rows[3].text
        garden = rows[4].text
        balcony = rows[5].text
        #price_per_m2_temp = rows[6].text
        #price_per_m2 = float(price_per_m2_temp.replace(" zł", "").replace(",", "").replace(" ", ""))
        price_temp = rows[7].text
        price = float(price_temp.replace(" zł", "").replace(",", "").replace(" ", ""))
        status_temp = rows[8].text
        if status_temp == "Dostępne":
            status = "available"
        else:
            status = "??"
            logger.warning("Nieznany status mieszkania: " + status_temp)

        announcement_id = str(uuid.uuid4())

        prop = Property(announcement_id, "sell", self.__URL, "flats", "Skawina, Korabniki, Łanowa")
        prop.price = price
        prop.source = self.__investment_name
        prop.district = 'krakowski'
        prop.commune = 'Skawina'
        prop.place = 'Skawina'
        prop.place_district = "Korabniki"
        prop.street = "Łanowa"
        prop.location_type = "miasto"
        prop.description = ""
        prop.area = area
        prop.images_urls = []
        if prop.price == None or prop.area == None:
            prop.sq_met_price = None
        else:
            prop.sq_met_price = round(float(prop.price) / float(prop.area), 2)
        prop.created_at = datetime.datetime.now(tz=datetime.timezone.utc)
        prop.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)

        flat = Flat(announcement_id, 'pierwotny')
        flat.condition_of_the_flat = 'do wykończenia'
        flat.floor = level
        flat.number_of_floors = 2
        flat.number_of_rooms = 4
        flat.number_of_bedrooms = 3
        if level == 1:
            flat.number_of_bathrooms = 2
        else:
            flat.number_of_bathrooms = 1
        flat.type_of_kitchen = 'aneks'
        flat.toilet_together_with_bathroom = True
        if balcony is not None and balcony != "":
            flat.balcony = True
        else:
            flat.balcony = False
        if garden is not None and garden != "":
            flat.garden = True
        else:
            flat.garden = False
        flat.window_joinery = 'plastikowe'
        flat.building_year = '2026'
        flat.building_material = 'żelbet i pustak'
        flat.heating = 'gazowe'
        flat.lift = False
        flat.garage = False
        flat.parking = True
        flat.terrace = False
        flat.basement = False
        flat.flat_number = flat_id
        flat.investment_name = self.__investment_name
        flat.status = status
        return prop, flat
