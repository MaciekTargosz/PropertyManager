import datetime
import json
import requests
import logging
from bs4 import BeautifulSoup

from data_suppliers.otodom.otodom_constants import get_search_lots_url, get_search_flats_url, get_search_houses_url, get_landing_page_url
from data_suppliers.otodom.otodom_locators import get_results_records_css
from searchable import Searchable

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

logger = logging.getLogger(__name__)





class Otodom():
    p_iterator = 2

    __data_type = None
    __action = None
    __city = None
    __distance = None

    @staticmethod
    def __get_area(target):
        area = float(target.get('Area'))
        logger.info("AREA: " + str(area))
        return area

    @staticmethod
    def __get_description(ad):
        temp_description = ad.get('description')
        soup = BeautifulSoup(temp_description, 'html.parser')
        description = soup.getText()
        logger.info("DESCRIPTION: " + description)
        return description

    @staticmethod
    def __get_price(target):
        temp_price = target.get('Price')
        if temp_price is not None and temp_price != 'Zapytaj o cenę':
            price = float(temp_price)
        else:
            price = None
        logger.info("__PRICE: " + str(price))
        return price

    @staticmethod
    def __get_created_at(ad):
        return datetime.datetime.fromisoformat(ad.get('createdAt'))

    @staticmethod
    def __get_modified_at(ad):
        return datetime.datetime.fromisoformat(ad.get('modifiedAt'))

    def __init__(self, data_type, action, city, distance):
        self.__data_type = data_type
        self.__action = action
        self.__city = city
        self.__distance = distance

    def get_search_url(self, location):
        if self.__data_type == 'lots':
            return get_search_lots_url(location, self.__action)
        elif self.__data_type == 'houses':
            return get_search_houses_url(location, self.__action)
        elif self.__data_type == 'flats':
            return get_search_flats_url(location, self.__action)


    def get_results_records(self, soup, url):
        url_list = []
        json_txt = json.loads(soup.select('script#__NEXT_DATA__')[0].getText())
        total_items = json_txt.get('props').get('pageProps').get('tracking').get('listing').get('result_count')
        items_list = json_txt.get('props').get('pageProps').get('data').get('searchAds').get('items')
        for item in items_list:
            url_list.append(item.get('slug'))
        res_per_page = json_txt.get('props').get('pageProps').get('tracking').get('listing').get('results_per_page')
        page_count = json_txt.get('props').get('pageProps').get('tracking').get('listing').get('page_count')
        for i in range(2, page_count + 1):
            curr_url = url + '&page=' + str(i)
            page = requests.get(curr_url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            json_txt = json.loads(soup.select('script#__NEXT_DATA__')[0].getText())
            items_list = json_txt.get('props').get('pageProps').get('data').get('searchAds').get('items')
            for item in items_list:
                url_list.append(item.get('slug'))
        return url_list

    def build_offer_url(self, url):
        return get_landing_page_url() + '/pl/oferta/' + url

    def get_url(self, link):
        try:
            basic_url = link.select_one('a').get('href')
            if not basic_url.startswith(get_landing_page_url()):
                basic_url = get_landing_page_url() + basic_url
            logger.info("URL: " + basic_url)
            return basic_url
        except Exception:
            return None

    def get_data_for_update_check(self, detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        ad = json_txt.get('props').get('pageProps').get('ad')
        price = Otodom.__get_price(ad.get('target'))
        description = Otodom.__get_description(ad)
        return price, description

    def get_property_data(self, detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        district = None
        commune = ""
        place = ""
        place_district = ""
        street = ""
        description = ""
        area = None
        type_of_contract = ""
        source_created_at = None
        source_updated_at = None
        number_of_views = None
        number_of_raises = None
        images_urls = []
        ad = json_txt.get('props').get('pageProps').get('ad')
        target = ad.get('target')
        price = self.__get_price(target)
        district, commune, place, place_district, street = self.__get_detailed_locations(ad)
        location_type = self.__get_location_type(target)
        description = self.__get_description(ad)
        area = self.__get_area(target)
        source_created_at = self.__get_created_at(ad)
        source_updated_at = self.__get_modified_at(ad)
        images_urls = self.__get_images_urls(ad)
        return price, district, commune, place, place_district, street, location_type, description, area, type_of_contract, source_created_at, source_updated_at, number_of_views, number_of_raises, images_urls

    def get_house_details(self, detailed_page):
        house_type = None
        usable_area = None
        number_of_bedrooms = None
        type_of_kitchen = None
        number_of_bathrooms = None
        toilet_together_with_bathroom = None
        balcony = None
        terrace = None
        roof = None
        window_joinery = None
        lot_area = None
        market_type = None
        ownership_form = None
        condition_of_the_building = None
        building_material = None
        building_year = None
        heating = None
        garage = None

        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        details = json_txt.get('props').get('pageProps').get('ad')
        if details.get('market') is not None:
            if details.get('market') == 'SECONDARY':
                market_type = 'wtórny'
            elif details.get('market') == 'PRIMARY':
                market_type = 'pierwotny'
            else:
                market_type = ''

        if details.get('target') is not None and details.get('target').get('Construction_status') is not None:
            if details.get('target').get('Construction_status')[0] == 'ready_to_use':
                condition_of_the_building = 'do zamieszkania'
            elif details.get('target').get('Construction_status')[0] == 'to_completion':
                condition_of_the_building = 'do wykończenia'
            elif details.get('target').get('Construction_status')[0] == 'unfinished_open':
                condition_of_the_building = 'surowy otwarty'
            elif details.get('target').get('Construction_status')[0] == 'unfinished_close':
                condition_of_the_building = 'surowy zamknięty'
            elif details.get('target').get('Construction_status')[0] == 'to_renovation':
                condition_of_the_building = 'do remontu'
            else:
                condition_of_the_building = ''

        if details.get('target') is not None and details.get('target').get('Build_year') is not None:
            building_year = details.get('target').get('Build_year')
        else:
            building_year = ''

        if details.get('target') is not None and details.get('target').get('Building_material') is not None:
            material_temp = details.get('target').get('Building_material')[0]
            if material_temp == 'brick':
                building_material = 'cegła'
            elif material_temp == 'reinforced_concrete':
                building_material = 'żelbet'
            elif material_temp == 'concrete_plate':
                building_material = 'wielka płyta'
            elif material_temp == 'breezeblock':
                building_material = 'pustak'
            elif material_temp == 'other':
                building_material = 'inny'
            elif material_temp == 'cellular_concrete':
                building_material = 'beton komórkowy'
            elif material_temp == 'silikat':
                building_material = 'silikat'
            elif material_temp == 'wood':
                building_material = 'drewno'
            elif material_temp == 'hydroton':
                building_material = 'keramzyt'
            else:
                building_material = ''

        if details.get('target') is not None and details.get('target').get('Heating_types') is not None:
            heating_temp = details.get('target').get('Heating_types')[0]
            if heating_temp == 'urban':
                heating = 'miejskie'
            elif heating_temp == 'boiler_room':
                heating = 'kotłownia'
            elif heating_temp == 'electrical':
                heating = 'elektryczne'
            elif heating_temp == 'gas':
                heating = 'gazowe'
            elif heating_temp == 'heat_pump':
                heating = 'pompa ciepła'
            elif heating_temp == 'fireplace':
                heating = 'kominek'
            else:
                heating = ''

        if details.get('target') is not None and details.get('target').get('Building_type') is not None:
            house_type_temp = details.get('target').get('Building_type')[0]
            if house_type_temp == 'semi_detached':
                house_type = 'bliźniak'
            elif house_type_temp == 'detached':
                house_type = 'wolnostojący'
            elif house_type_temp == 'ribbon':
                house_type = 'szeregowiec'
            elif house_type_temp == 'residence':
                house_type = 'rezydencja'
            else:
                logger.warning("Undefined house type: " + house_type_temp)

        if details.get('target') is not None and details.get('target').get('Rooms_num')[0] is not None:
            temp_rooms = details.get('target').get('Rooms_num')[0]
            if temp_rooms != 'more':
                number_of_bedrooms = int(details.get('target').get('Rooms_num')[0]) - 1    # -1 because of living room

        if details.get('target') is not None and details.get('target').get('Terrain_area') is not None:
            lot_area = details.get('target').get('Terrain_area')

        if details.get('target') is not None and details.get('target').get('Roofing') is not None:
            roof_temp = details.get('target').get('Roofing')[0]
            if roof_temp == 'tile':
                roof = 'dachówka'
            elif roof_temp == 'metal':
                roof = 'blacha'
            elif roof_temp == 'sheet':
                roof = 'blacha'
            elif roof_temp == 'other':
                roof = 'inne'
            elif roof_temp == 'roofing_paper':
                roof = 'papa'
            else:
                roof = ''

        if details.get('target') is not None and details.get('target').get('Windows_type') is not None:
            window_joinery_temp = details.get('target').get('Windows_type')[0]
            if window_joinery_temp == 'plastic':
                window_joinery = 'plastikowe'
            elif window_joinery_temp == 'wooden':
                window_joinery = 'drewniane'
            elif window_joinery_temp == 'aluminium':
                window_joinery = 'aluminiowa'
            else:
                window_joinery = ''

        return market_type, condition_of_the_building, building_year, building_material, heating, house_type, usable_area, number_of_bedrooms, type_of_kitchen, number_of_bathrooms, toilet_together_with_bathroom, balcony, terrace, roof, window_joinery, lot_area, ownership_form, garage


    @staticmethod
    def __get_location_type(target):
        location_type = ""
        if target.get('Location') is not None:
            if target.get('Location') == 'city':
                location_type = 'miasto'
            elif target.get('Location') == 'country':
                location_type = 'wieś'
        logger.info("LOCATION TYPE: " + location_type)
        return location_type

    @staticmethod
    def __get_detailed_locations(ad):
        address = ad.get('location').get('address')
        if address.get('county') is not None:
            try:
                district = address.get('county').get('name')
            except Exception:
                logger.warning("Undefined district(powiat)")
        if address.get('municipality') is not None:
            commune = address.get('municipality').get('name')
        else:
            locations = ad.get('location').get('reverseGeocoding').get(
                'locations')
            for loc in locations:
                if loc.get('locationLevel') == 'commune':
                    commune = loc.get('name')
                    break
                else:
                    commune = ""
        if address.get('city') is not None:
            try:
                place = address.get('city').get('name')
            except Exception:
                logger.warning("Undefined place(miasto)")
        if address.get('district') is not None:
            place_district = address.get('district').get('name')
        else:
            locations = ad.get('location').get('reverseGeocoding').get(
                'locations')
            for loc in locations:
                if loc.get('locationLevel') == 'district':
                    place_district = loc.get('name')
                    break
                else:
                    place_district = ""
        if address.get('street') is not None:
            street = address.get('street').get('name').replace('ul.', '')
        else:
            street = ""
        logger.info("COMMUNE: " + commune)
        logger.info("DISTRICT: " + district)
        logger.info("PLACE: " + place)
        logger.info("PLACE_DIST: " + place_district)
        logger.info("STREET: " + street)
        return district, commune, place, place_district, street
    def get_detailed_locations(self, detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        address = json_txt.get('props').get('pageProps').get('ad').get('location').get('address')
        if address.get('county') is not None:
            try:
                district = address.get('county').get('name')
            except Exception:
                logger.warning("Undefined district(powiat)")
        if address.get('municipality') is not None:
            commune = address.get('municipality').get('name')
        else:
            locations = json_txt.get('props').get('pageProps').get('ad').get('location').get('reverseGeocoding').get(
                'locations')
            for loc in locations:
                if loc.get('locationLevel') == 'commune':
                    commune = loc.get('name')
                    break
                else:
                    commune = ""
        if address.get('city') is not None:
            try:
                place = address.get('city').get('name')
            except Exception:
                logger.warning("Undefined place(miasto)")
        if address.get('district') is not None:
            place_district = address.get('district').get('name')
        else:
            locations = json_txt.get('props').get('pageProps').get('ad').get('location').get('reverseGeocoding').get(
                'locations')
            for loc in locations:
                if loc.get('locationLevel') == 'district':
                    place_district = loc.get('name')
                    break
                else:
                    place_district = ""
        if address.get('street') is not None:
            street = address.get('street').get('name').replace('ul.', '')
        else:
            street = ""


        logger.info("COMMUNE: " + commune)
        logger.info("DISTRICT: " + district)
        logger.info("PLACE: " + place)
        logger.info("PLACE_DIST: " + place_district)
        logger.info("STREET: " + street)
        return district, commune, place, place_district, street

    def get_flat_details(self, detailed_page):
        number_of_rooms = None
        building_material = None
        building_year = None
        heating = None
        market_type = None
        condition_of_the_flat = None
        floor = None
        number_of_floors = None
        number_of_bedrooms = None
        number_of_bathrooms = None
        type_of_kitchen = None
        toilet_together_with_bathroom = None
        balcony = None
        basement = None
        window_joinery = None
        lift = None
        garage = None
        terrace = None
        parking = None
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        details = json_txt.get('props').get('pageProps').get('ad')
        if details.get('market') is not None:
            if details.get('market') == 'SECONDARY':
                market_type = 'wtórny'
            elif details.get('market') == 'PRIMARY':
                market_type = 'pierwotny'
            else:
                market_type = ''
        if details.get('target') is not None and details.get('target').get('Construction_status') is not None:
            if details.get('target').get('Construction_status')[0] == 'ready_to_use':
                condition_of_the_flat = 'do zamieszkania'
            elif details.get('target').get('Construction_status')[0] == 'to_completion':
                condition_of_the_flat = 'do wykończenia'
            else:
                condition_of_the_flat = 'do remontu'
        if details.get('target') is not None and details.get('target').get('Floor_no') is not None:
            floor_temp = details.get('target').get('Floor_no')[0]
            if floor_temp == 'ground_floor':
                floor = 0
            if floor_temp.startswith('floor_'):
                floor = floor_temp.replace('floor_', '')
            if floor_temp.startswith('higher_10'):
                floor = floor_temp.replace('higher_', '') #TODO opracować dl apieter powyzej 10. piętra
        else:
            floor = ''

        if details.get('target') is not None and details.get('target').get('Building_floors_num') is not None:
            number_of_floors = details.get('target').get('Building_floors_num')
        else:
            number_of_floors = ''

        if details.get('target') is not None and details.get('target').get('Rooms_num') is not None:
            number_of_rooms = details.get('target').get('Rooms_num')[0]

        if details.get('target') is not None and details.get('target').get('Build_year') is not None:
            building_year = details.get('target').get('Build_year')
        else:
            building_year = ''

        if details.get('target') is not None and details.get('target').get('Building_material') is not None:
            material_temp = details.get('target').get('Building_material')[0]
            if material_temp == 'brick':
                building_material = 'cegła'
            elif material_temp == 'reinforced_concrete':
                building_material = 'żelbet'
            elif material_temp == 'concrete_plate':
                building_material = 'wielka płyta'
            elif material_temp == 'breezeblock':
                building_material = 'pustak'
            else:
                building_material = ''

        if details.get('target') is not None and details.get('target').get('Extras_types') is not None:
            for extra in details.get('target').get('Extras_types'):
                if extra == 'balcony':
                    balcony = True
                if extra == 'basement':
                    basement = True
                if extra == 'toilet':
                    toilet_together_with_bathroom = 'tak'
                if extra == 'garage':
                    garage = True
                if extra == 'terrace':
                    terrace = True
                if extra == 'parking':
                    parking = True
                if extra == 'lift':
                    lift = True
                if extra == 'separate_kitchen':
                    type_of_kitchen = 'oddzielna'

        if details.get('target') is not None and details.get('target').get('Heating') is not None:
            heating_temp = details.get('target').get('Heating')[0]
            if heating_temp == 'urban':
                heating = 'miejskie'
            elif heating_temp == 'boiler_room':
                heating = 'kotłownia'
            elif heating_temp == 'electrical':
                heating = 'elektryczne'
            elif heating_temp == 'gas':
                heating = 'gazowe'
            else:
                heating = ''


        return market_type, condition_of_the_flat, floor, number_of_floors, number_of_rooms, number_of_bedrooms, number_of_bathrooms, type_of_kitchen, toilet_together_with_bathroom, balcony, window_joinery, building_year, building_material, heating, lift, garage, terrace, parking, basement

    def get_publisher_data(self, detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        publisher = json_txt.get('props').get('pageProps').get('ad').get('owner')

        publisher_type = ""

        if publisher.get('type') == 'agency':
            publisher_type = 'agencja'
        elif publisher.get('type') == 'private':
            publisher_type = 'osoba prywatna'
        if publisher.get('name') is not None:
            publisher_name = publisher.get('name')
        else:
            publisher_name = ""
        if publisher.get('phones') is not None and len(publisher.get('phones')) > 0:
            contact = publisher.get('phones')[0]
        else:
            contact = ""
        agency = json_txt.get('props').get('pageProps').get('ad').get('agency')
        if agency is not None:
            if agency.get('name') is not None:
                company = agency.get('name')
            else:
                company = ""
            if agency.get('address') is not None:
                address = agency.get('address')
            else:
                address = ""
        else:
            company = ""
            address = ""
        # tu jest też możliwość wyświetlenia wszystkich ofert danej agencji

        return publisher_type, publisher_name, contact, company, address

    @staticmethod
    def __get_publisher_data(detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        ad = json_txt.get('props').get('pageProps').get('ad')
        publisher = ad.get('owner')
        publisher_type = ""

        if publisher.get('type') == 'agency':
            publisher_type = 'agencja'
        elif publisher.get('type') == 'private':
            publisher_type = 'osoba prywatna'
        if publisher.get('name') is not None:
            publisher_name = publisher.get('name')
        else:
            publisher_name = ""
        if publisher.get('phones') is not None and len(publisher.get('phones')) > 0:
            contact = publisher.get('phones')[0]
        else:
            contact = ""
        agency = ad.get('agency')
        if agency is not None:
            if agency.get('name') is not None:
                company = publisher.get('name')
            else:
                company = ""
            if agency.get('address') is not None:
                address = agency.get('address')
            else:
                address = ""
        else:
            company = ""
            address = ""
        # tu jest też możliwość wyświetlenia wszystkich ofert danej agencji

        return publisher_type, publisher_name, contact, company, address

    @staticmethod
    def __get_utilities_data(detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        utilities = json_txt.get('props').get('pageProps').get('ad').get('features')
        gas = ""
        water = ""
        sewerage = ""
        electricity = ""
        telco = ""
        road_access = ""
        fence = ""
        if 'prąd' in utilities:
            electricity = 'tak'
        if 'woda' in utilities:
            water = 'tak'
        if 'kanalizacja' in utilities:
            sewerage = 'tak'
        if 'gaz' in utilities:
            gas = 'tak'
        if 'telefon' in utilities:
            telco = 'tak'
        additionalInfo = json_txt.get('props').get('pageProps').get('ad').get('additionalInformation')
        for info in additionalInfo:
            if info.get('label') == 'fence':
                if info.get('values')[0] != '::n':
                    fence = 'tak'
                else:
                    fence = 'b.d'
            if info.get('label') == 'access_types':
                if len(info.get('values')) == 0:
                    road_access = 'b.d.'
                elif info.get('values')[0] == 'access_types::asphalt':
                    road_access = 'tak, asfaltowy'
                else:
                    road_access = 'tak'
        return road_access, fence, electricity, water, gas, sewerage, telco

    def get_utilities_data(self, detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        utilities = json_txt.get('props').get('pageProps').get('ad').get('features')
        gas = ""
        water = ""
        sewerage = ""
        electricity = ""
        telco = ""
        road_access = ""
        fence = ""
        if 'prąd' in utilities:
            electricity = 'tak'
        if 'woda' in utilities:
            water = 'tak'
        if 'kanalizacja' in utilities:
            sewerage = 'tak'
        if 'gaz' in utilities:
            gas = 'tak'
        if 'telefon' in utilities:
            telco = 'tak'
        additionalInfo = json_txt.get('props').get('pageProps').get('ad').get('additionalInformation')
        for info in additionalInfo:
            if info.get('label') == 'fence':
                if info.get('values')[0] != '::n':
                    fence = 'tak'
                else:
                    fence = 'b.d'
            if info.get('label') == 'access_types':
                if len(info.get('values')) == 0:
                    road_access = 'b.d.'
                elif info.get('values')[0] == 'access_types::asphalt':
                    road_access = 'tak, asfaltowy'
                else:
                    road_access = 'tak'
        target = json_txt.get('props').get('pageProps').get('ad').get('target')

        if target.get('Fence_types') is not None and len(target.get('Fence_types')) > 0:
            fence = target.get('Fence_types')[0]

        return road_access, fence, electricity, water, gas, sewerage, telco

    def get_next_page_url(self, soup):
        next_page_btn = soup.findAll("li", {"aria-label": "Go to next Page"})
        if next_page_btn == []:
            return None
        else:
            if next_page_btn[0]['aria-disabled'] == 'false':
                npu = get_search_parcel_url() + '&page=' + str(self.p_iterator)
                self.p_iterator = self.p_iterator + 1
                return npu
            else:
                return None

    def get_location(self, link):
        try:
            location = link.select_one("div p.css-42r2ms").getText()
        except Exception:
            location = ""
        logger.info("LOCATION: " + location)
        return location

    def get_offer_creation_date(self, link):
        results = link.findAll("p", {"data-testid": "location-date"})
        for result in results:
            location_and_date = result.getText()
            date = location_and_date.split(' - ')[1]
            if 'Dzisiaj' in date:
                date = date.replace('Dzisiaj o', str(datetime.date.today()))
            if date.startswith('Odświeżono '):
                date = date.replace('Odświeżono ', '')
                update_type = 'refresh'
            else:
                update_type = 'add'
            date = date.replace('Odświeżono dnia ', '')
            offer_date = {
                'update_type': update_type,
                'date': date,
            }
            logger.info("OFFER CREATION: " + str(offer_date))
            return offer_date

    def get_area(self, detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        target = json_txt.get('props').get('pageProps').get('ad').get('target')
        return self.__get_area(target)

    def __convert_string_to_date(self, date_string):
        date_format = "%d.%m.%Y"
        return datetime.strptime(date_string, date_format).date()

    def get_announcement_meta_data(self, details_page_soup):
        json_txt = json.loads(details_page_soup.select('script#__NEXT_DATA__')[0].getText())
        metadata = json_txt.get('props').get('pageProps').get('ad')
        type_of_contract = ""
        source_created_at = datetime.datetime.fromisoformat(metadata.get('createdAt'))
        source_updated_at = datetime.datetime.fromisoformat(metadata.get('modifiedAt'))
        number_of_views = None
        number_of_raises = None
        if metadata.get('target').get('Type') is not None:
            if 'building' in metadata.get('target').get('Type'):
                property_type = 'budowlana'
            elif 'agricultural' in metadata.get('target').get('Type'):
                property_type = 'rolna'
            elif 'agricultural_building' in metadata.get('target').get('Type'):
                property_type = 'rolno-budowlana'
            elif 'commercial' in metadata.get('target').get('Type'):
                property_type = 'inwestycyjna'
            elif 'other' in metadata.get('target').get('Type'):
                property_type = 'inna'
            else:
                logger.warning("Undefined property type: " + metadata.get('target').get('Type')[0])
                property_type = 'sprawdź'
        else:
            property_type = ''
        return type_of_contract, source_created_at, source_updated_at, number_of_views, number_of_raises, property_type

    def get_parcel_type(self, details_page):
        results = details_page.select("div.css-t7cajz.etn78ea2")
        for result in results:
            params = result.getText()
            if params.startswith('Typ działki:'):
                parcel_type = params.split(":")[1].strip()
                logger.info("TYPE: " + parcel_type)
                return parcel_type

    def get_description(self, detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        ad = json_txt.get('props').get('pageProps').get('ad')
        return self.__get_description(ad)

    def get_price(self, link):
        price_temp = link.select_one("div span.css-2bt9f1").getText()
        if price_temp != 'Zapytaj o cenę':
            price = float(price_temp.replace('zł', '').replace(' ', '').replace(' ', '').strip())
        else:
            price = None
        logger.info("PRICE: " + str(price))
        return price

    def get_images_urls(self, page):
        temp_img_urls = []
        imgs = page.select('span.image-gallery-thumbnail-inner img')
        for img in imgs:
            img_url = img['src']
            temp_img_urls.append(img_url)
        return temp_img_urls

    def get_search_parcel_url(self):
        return get_search_parcel_url()

    @staticmethod
    def __get_lot_type(detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        target = json_txt.get('props').get('pageProps').get('ad').get('target')
        if target.get('Type') is not None:
            if 'building' in target.get('Type'):
                property_type = 'budowlana'
            elif 'agricultural' in target.get('Type'):
                property_type = 'rolna'
            elif 'agricultural_building' in target.get('Type'):
                property_type = 'rolno-budowlana'
            elif 'commercial' in target.get('Type'):
                property_type = 'inwestycyjna'
            elif 'other' in target.get('Type'):
                property_type = 'inna'
            else:
                logger.warning("Undefined property type: " + target.get('Type')[0])
                property_type = 'sprawdź'
        else:
            property_type = ''
        return property_type

    def get_lot_type(self, detailed_page):
        json_txt = json.loads(detailed_page.select('script#__NEXT_DATA__')[0].getText())
        target = json_txt.get('props').get('pageProps').get('ad').get('target')
        if target.get('Type') is not None:
            if 'building' in target.get('Type'):
                property_type = 'budowlana'
            elif 'agricultural' in target.get('Type'):
                property_type = 'rolna'
            elif 'agricultural_building' in target.get('Type'):
                property_type = 'rolno-budowlana'
            elif 'commercial' in target.get('Type'):
                property_type = 'inwestycyjna'
            elif 'other' in target.get('Type'):
                property_type = 'inna'
            else:
                logger.warning("Undefined property type: " + target.get('Type')[0])
                property_type = 'sprawdź'
        else:
            property_type = ''
        return property_type

    @staticmethod
    def __get_images_urls(ad):
        images = []
        for img in ad.get('images'):
            images.append(img.get('large'))
        return images
