import datetime
import logging
import os
import uuid
import base64

import requests
from bs4 import BeautifulSoup
from google.cloud import bigquery

from data_suppliers.otodom.otodom_po import Otodom
from data_suppliers.no.no_po import NieruchomosciOnline
from db.environment import Environment
from db.property import Advertiser, Flat, House, Lot, Property
from investments.data_suppliers.lanowe_zacisze_po import LanoweZacisze

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'propertymanager-385720-b6b166d89c3b.json'

# Stworzenie klienta BigQuery
client = bigquery.Client()

logger = logging.getLogger(__name__)
logging.basicConfig(filename='crawler.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    d1_keys.remove('description_history')
    d2_keys.remove('description_history')
    d1_keys.remove('price_history')
    d2_keys.remove('price_history')
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    same = set(o for o in shared_keys if d1[o] == d2[o])
    return added, removed, modified, same


def generate_advertiser_id(agent_name, company):
    author_id = base64.b64encode(agent_name.encode("utf-8"))[0:10].decode("utf-8") + base64.b64encode(
        company.encode("utf-8"))[0:10].decode("utf-8")
    return author_id


def update_price(env, announcement_id, new_price):
    # Update the price in properties_announcements
    update_query = f"""
    UPDATE `{env}.properties_announcements`
    SET price = {new_price}, updated_at = CURRENT_TIMESTAMP()
    WHERE announcement_id = '{announcement_id}'
    """
    client.query(update_query)
    return True


def log_price_change(env, announcement_id, old_value, new_value):
    query = f"""
    CALL `{env}.log_property_change`(
      '{announcement_id}',
      'price',
      '{old_value}',
      '{new_value}'
    )
    """
    logger.info('PRICE has changed')
    client.query(query)


def log_description_change(env, announcement_id, old_value, new_value):
    query = f"""
    CALL `{env}.log_property_change`(
      '{announcement_id}',
      'description',
      '{old_value}',
      '{new_value}'
    )
    """
    logger.info('DESCRIPTION has changed')
    client.query(query)


def update_description(env, announcement_id, new_description):
    # Update the price in properties_announcements
    update_query = f"""
    UPDATE `{env}.properties_announcements`
    SET description = {new_description}, updated_at = CURRENT_TIMESTAMP()
    WHERE announcement_id = '{announcement_id}'
    """
    client.query(update_query)
    return True


def update_last_seen(env, announcement_id):
    # Update the price in properties_announcements
    update_query = f"""
    UPDATE `{env}.properties_announcements`
    SET updated_at = CURRENT_TIMESTAMP()
    WHERE announcement_id = '{announcement_id}'
    """
    client.query(update_query)


def check_if_announcement_exists(project_dataset_table, url):
    """Sprawdza, czy rekord z podanym url istnieje w tabeli properties_announcements BigQuery.

    Args:
      project_id: ID projektu BigQuery.
      dataset_id: ID zbioru danych.
      table_id: ID tabeli.
      url: URL do sprawdzenia.

    Returns:
      True, jeśli rekord istnieje, False w przeciwnym wypadku.
    """

    query = f"""
    SELECT COUNT(*)
    FROM {project_dataset_table}
    WHERE url = '{url}'
    """

    results = client.query(query).result()

    for row in results:
        if row[0] > 0:
            return True
    return False


def check_if_advertiser_exists(project_dataset_table, value):
    """Sprawdza, czy rekord o podanym advertiser_id istnieje w tabeli BigQuery.

    Args:
      project_id: ID projektu BigQuery.
      dataset_id: ID zbioru danych.
      table_id: ID tabeli.
      advertiser_id: Wartość advertiser_id do sprawdzenia.

    Returns:
      True, jeśli rekord istnieje, False w przeciwnym wypadku.
    """

    query = f"""
  SELECT COUNT(*)
  FROM {project_dataset_table}
  WHERE advertiser_id = '{value}'
  """

    results = client.query(query).result()

    for row in results:
        if row[0] > 0:
            return True
    return False


def get_announcement_id_price_and_description_by_url(project_dataset_table, url):
    query = f"""
    SELECT announcement_id, price, description
    FROM {project_dataset_table}
    WHERE url = '{url}'
    """
    query_job = client.query(query)
    results = query_job.result()

    for row in results:
        return row.announcement_id, row.price, row.description

    return None, None, None


def add_next_js_announcement(data_supplier, data_type, announcement_type, url, ds, environment):
    if data_supplier == 'otodom.pl':
        announcement_id = str(uuid.uuid4())
        details_page = requests.get(url, headers=headers)
        details_page_soup = BeautifulSoup(details_page.content, 'html.parser')

        get_property_data_from_next_js_json_and_save(announcement_id, announcement_type, data_supplier, data_type,
                                                     details_page_soup, ds, environment, url)

        get_publisher_data_from_next_s_json_and_save(announcement_id, details_page_soup, ds, environment)

        if data_type == 'lots':
            get_lot_data_from_next_js_json_and_save(announcement_id, details_page_soup, ds, environment)
        elif data_type == 'flats':
            get_flat_data_from_next_js_json_and_save(announcement_id, details_page_soup, ds, environment)
        elif data_type == 'houses':
            get_house_data_from_next_js_json_and_save(announcement_id, details_page_soup, ds, environment)



def add_html_announcement(data_supplier, data_type, announcement_type, url, ds, environment):
    announcement_id = str(uuid.uuid4())
    details_page = requests.get(url, headers=headers)
    details_page_soup = BeautifulSoup(details_page.content, 'html.parser')
    get_property_data_from_html_and_save(announcement_id, announcement_type, data_supplier, data_type,
                                         details_page_soup, ds, environment, url)

    get_publisher_data_from_html_and_save(announcement_id, details_page_soup, ds, environment)


    if data_type == 'lots':
        get_lot_data_from_html_and_save(announcement_id, details_page_soup, ds, environment)
    elif data_type == 'flats':
        get_flat_data_from_html_and_save(announcement_id, details_page_soup, ds, environment)
    elif data_type == 'houses':
        get_house_data_from_html_and_save(announcement_id, details_page_soup, ds, environment)

def get_property_data_from_next_js_json_and_save(announcement_id, announcement_type, data_supplier, data_type,
                                                 details_page_soup,
                                                 ds, environment, url):
    price, district, commune, place, place_district, street, location_type, description, area, type_of_contract, source_created_at, source_updated_at, number_of_views, number_of_raises, images_urls = ds.get_property_data(
        details_page_soup)
    location = district + ", " + commune + ", " + place + ", " + place_district + ", " + street
    prop = Property(announcement_id, announcement_type, url, data_type, location)
    prop.price = price
    prop.source = data_supplier
    prop.district = district
    prop.commune = commune
    prop.place = place
    prop.place_district = place_district
    prop.street = street
    prop.location_type = location_type
    prop.description = description
    prop.area = area
    if prop.price == None or prop.area == None:
        prop.sq_met_price = None
    else:
        prop.sq_met_price = round(float(prop.price) / float(prop.area), 2)
    prop.created_at = datetime.datetime.now(tz=datetime.timezone.utc)
    prop.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)
    prop.type_of_contract = type_of_contract
    prop.source_created_at = source_created_at
    prop.source_updated_at = source_updated_at
    prop.number_of_views = number_of_views
    prop.number_of_raises = number_of_raises
    prop.images_urls = images_urls
    property_data = prop.to_dict()
    # Convert datetime fields to strings
    for key, value in property_data.items():
        if isinstance(value, datetime.datetime):
            property_data[key] = value.isoformat()  # Use ISO 8601 format for consistency
    property_data_str = str(property_data)
    print("Property data: " + property_data_str)
    # Wstawianie danych do tabeli properties_announcements
    errors = client.insert_rows_json(
        environment.get_project_and_dataset() + ".properties_announcements", [property_data])
    if errors == []:
        print("New property inserted successfully.")
        return
    else:
        print("Errors occurred while inserting property data." + errors)


def get_property_data_from_html_and_save(announcement_id, announcement_type, data_supplier, data_type,
                                         details_page_soup,
                                         ds, environment, url):
    price, district, commune, place, place_district, street, location_type, description, area, type_of_contract, source_created_at, source_updated_at, number_of_views, number_of_raises, images_urls = ds.get_property_data(
        details_page_soup)
    location = district + ", " + commune + ", " + place + ", " + place_district + ", " + street
    prop = Property(announcement_id, announcement_type, url, data_type, location)
    prop.price = price
    prop.source = data_supplier
    prop.district = district
    prop.commune = commune
    prop.place = place
    prop.place_district = place_district
    prop.street = street
    prop.location_type = location_type
    prop.description = description
#TODO    prop.publisher
    prop.area = area
    if prop.price == None or prop.area == None:
        prop.sq_met_price = None
    else:
        prop.sq_met_price = round(float(prop.price) / float(prop.area), 2)
    prop.created_at = datetime.datetime.now(tz=datetime.timezone.utc)
    prop.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)
    prop.type_of_contract = type_of_contract
    prop.source_created_at = source_created_at
    prop.source_updated_at = source_updated_at
    prop.number_of_views = number_of_views
    prop.number_of_raises = number_of_raises
    prop.images_urls = images_urls
    property_data = prop.to_dict()
    # Convert datetime fields to strings
    for key, value in property_data.items():
        if isinstance(value, datetime.datetime):
            property_data[key] = value.isoformat()  # Use ISO 8601 format for consistency
    property_data_str = str(property_data)
    print("Property data: " + property_data_str)
    # Wstawianie danych do tabeli properties_announcements

    errors = client.insert_rows_json(
        environment.get_project_and_dataset() + ".properties_announcements", [property_data])
    if errors == []:
        print("New property inserted successfully.")
        return
    else:
        print("Errors occurred while inserting property data." + errors)


def get_publisher_data_from_next_s_json_and_save(announcement_id, details_page_soup, ds, environment):
    publisher_type, publisher_name, contact, company, address = ds.get_publisher_data(details_page_soup)
    advertiser_id = generate_advertiser_id(publisher_name, company)

    if not check_if_advertiser_exists(environment.get_project_and_dataset() + ".advertisers",
                                      advertiser_id):
        advertiser = Advertiser(advertiser_id, publisher_type, publisher_name, company)
        advertiser.address = address
        advertiser_data = advertiser.to_dict()

        print("Advertiser data: " + str(advertiser))
        errors = client.insert_rows_json(environment.get_project_and_dataset() + ".advertisers",
                                         [advertiser_data])
        if not errors:
            print("New advertiser inserted successfully.")
        else:
            print("Errors occurred while inserting advertiser data." + errors)
    else:
        print("Advertiser alerady existis in DB")

    announcements_advertisers_data = {
        "announcement_id": announcement_id,
        "advertiser_id": advertiser_id
    }

    errors = client.insert_rows_json(environment.get_project_and_dataset() + ".announcements_advertisers",
                                     [announcements_advertisers_data])
    if not errors:
        print("New announcement_advertiser entry inserted successfully.")
    else:
        print("Errors occurred while inserting announcement_advertiser data." + errors)

def get_publisher_data_from_html_and_save(announcement_id, details_page_soup, ds, environment):
    publisher_type, publisher_name, contact, company, address = ds.get_publisher_data(details_page_soup)
    advertiser_id = generate_advertiser_id(publisher_name, company)

    if not check_if_advertiser_exists(environment.get_project_and_dataset() + ".advertisers",
                                      advertiser_id):
        advertiser = Advertiser(advertiser_id, publisher_type, publisher_name, company)
        advertiser.address = address
        advertiser_data = advertiser.to_dict()

        print("Advertiser data: " + str(advertiser))
        errors = client.insert_rows_json(environment.get_project_and_dataset() + ".advertisers",
                                         [advertiser_data])
        if not errors:
            print("New advertiser inserted successfully.")
        else:
            print("Errors occurred while inserting advertiser data." + errors)
    else:
        print("Advertiser alerady existis in DB")

    announcements_advertisers_data = {
        "announcement_id": announcement_id,
        "advertiser_id": advertiser_id
    }

    errors = client.insert_rows_json(environment.get_project_and_dataset() + ".announcements_advertisers",
                                     [announcements_advertisers_data])
    if not errors:
        print("New announcement_advertiser entry inserted successfully.")
    else:
        print("Errors occurred while inserting announcement_advertiser data." + errors)

def get_flat_data_from_next_js_json_and_save(announcement_id, details_page_soup, ds, environment):
    market_type, condition_of_the_flat, floor, number_of_floors, number_of_rooms, number_of_bedrooms, number_of_bathrooms, type_of_kitchen, toilet_together_with_bathroom, balcony, window_joinery, building_year, building_material, heating, lift, garage, terrace, parking, basement = ds.get_flat_details(
        details_page_soup)
    flat = Flat(announcement_id, market_type)
    flat.condition_of_the_flat = condition_of_the_flat
    flat.floor = floor
    flat.number_of_floors = number_of_floors
    flat.number_of_rooms = number_of_rooms
    flat.number_of_bedrooms = number_of_bedrooms
    flat.number_of_bathrooms = number_of_bathrooms
    flat.type_of_kitchen = type_of_kitchen
    flat.toilet_together_with_bathroom = toilet_together_with_bathroom
    flat.balcony = balcony
    flat.window_joinery = window_joinery
    flat.building_year = building_year
    flat.building_material = building_material
    flat.heating = heating
    flat.lift = lift
    flat.garage = garage
    flat.parking = parking
    flat.terrace = terrace
    flat.basement = basement
    flat_data = flat.to_dict()
    print("Flat data: " + str(flat_data))
    errors = client.insert_rows_json(environment.get_project_and_dataset() + ".flats_announcements",
                                     [flat_data])
    if errors == []:
        print("New flat inserted successfully.")
    else:
        print("Errors occurred while inserting flat data." + str(errors))
        # if not (data_supplier == 'olx.pl' and 'otodom' in url):

def get_flat_data_from_html_and_save(announcement_id, details_page_soup, ds, environment):
    market_type, condition_of_the_flat, floor, number_of_floors, number_of_rooms, number_of_bedrooms, number_of_bathrooms, type_of_kitchen, toilet_together_with_bathroom, balcony, window_joinery, building_year, building_material, heating, lift, garage, terrace, parking, basement, garden = ds.get_flat_details(
        details_page_soup)
    flat = Flat(announcement_id, market_type)
    flat.condition_of_the_flat = condition_of_the_flat
    flat.floor = floor
    flat.number_of_floors = number_of_floors
    flat.number_of_rooms = number_of_rooms
    flat.number_of_bedrooms = number_of_bedrooms
    flat.number_of_bathrooms = number_of_bathrooms
    flat.type_of_kitchen = type_of_kitchen
    flat.toilet_together_with_bathroom = toilet_together_with_bathroom
    flat.balcony = balcony
    flat.window_joinery = window_joinery
    flat.building_year = building_year
    flat.building_material = building_material
    flat.heating = heating
    flat.lift = lift
    flat.garage = garage
    flat.parking = parking
    flat.terrace = terrace
    flat.basement = basement
    flat.garden = garden
    flat_data = flat.to_dict()
    print("Flat data: " + str(flat_data))
    errors = client.insert_rows_json(environment.get_project_and_dataset() + ".flats_announcements",
                                     [flat_data])
    if errors == []:
        print("New flat inserted successfully.")
    else:
        print("Errors occurred while inserting flat data." + str(errors))
        # if not (data_supplier == 'olx.pl' and 'otodom' in url):

def get_lot_data_from_next_js_json_and_save(announcement_id, details_page_soup, ds, environment):
    lot = Lot(announcement_id)
    lot_type = ds.get_lot_type(details_page_soup)
    road_access, fence, electricity, water, gas, sewerage, telco = ds.get_utilities_data(
        details_page_soup)
    lot.fence = fence
    lot.road_access = road_access
    lot.electricity = electricity
    lot.gas = gas
    lot.water = water
    lot.sewerage = sewerage
    lot.telco = telco
    lot.lot_type = lot_type
    # lot.dimensions = znajdz_wymiary_dzialki(prop.description)
    lot_data = lot.to_dict()
    print("Lot data: " + str(lot_data))
    errors = client.insert_rows_json(environment.get_project_and_dataset() + ".lots_announcements",
                                     [lot_data])
    if errors == []:
        print("New lot inserted successfully.")
    else:
        print("Errors occurred while inserting lots data." + errors)


def get_lot_data_from_html_and_save(announcement_id, details_page_soup, ds, environment):
    lot = Lot(announcement_id)
    lot_type = ds.get_lot_type(details_page_soup)
    road_access, fence, electricity, water, gas, sewerage, telco, shape, dimensions = ds.get_utilities_data(
        details_page_soup)
    lot.fence = fence
    lot.road_access = road_access
    lot.electricity = electricity
    lot.gas = gas
    lot.water = water
    lot.sewerage = sewerage
    lot.telco = telco
    lot.lot_type = lot_type
    lot.lot_shape = shape
    lot.dimensions = dimensions
    lot_data = lot.to_dict()
    print("Lot data: " + str(lot_data))
    errors = client.insert_rows_json(environment.get_project_and_dataset() + ".lots_announcements",
                                     [lot_data])
    if errors == []:
        print("New lot inserted successfully.")
    else:
        print("Errors occurred while inserting lots data." + errors)

def get_house_data_from_next_js_json_and_save(announcement_id, details_page_soup, ds, environment):
    market_type, condition_of_the_building, building_year, building_material, heating, house_type, usable_area, number_of_bedrooms, type_of_kitchen, number_of_bathrooms, toilet_together_with_bathroom, balcony, terrace, roof, window_joinery, lot_area, ownership_form, garage = ds.get_house_details(
        details_page_soup)
    road_access, fence, electricity, water, gas, sewerage, telco = ds.get_utilities_data(details_page_soup)
    house = House(announcement_id, market_type)
    house.house_type = house_type
    house.condition_of_the_building = condition_of_the_building
    house.number_of_bedrooms = number_of_bedrooms
    house.number_of_bathrooms = number_of_bathrooms
    house.type_of_kitchen = type_of_kitchen
    house.toilet_together_with_bathroom = toilet_together_with_bathroom
    house.balcony = balcony
    house.window_joinery = window_joinery
    house.building_year = building_year
    house.building_material = building_material
    house.heating = heating
    house.usable_area = usable_area
    house.terrace = terrace
    house.roof = roof
    house.lot_area = lot_area
    house.ownership_form = ownership_form
    house.road_access = road_access
    house.fence = fence
    house.gas = gas
    house.electricity = electricity
    house.sewerage = sewerage
    house.water = water
    house.telco = telco
    house.market_type = market_type
    house.garage = garage

    house_data = house.to_dict()

    print("House data: " + str(house_data))
    errors = client.insert_rows_json(environment.get_project_and_dataset() + ".houses_announcements",
                                     [house_data])
    if errors == []:
        print("New house inserted successfully.")
    else:
        print("Errors occurred while inserting house data." + str(errors))

def get_house_data_from_html_and_save(announcement_id, details_page_soup, ds, environment):
    market_type, condition_of_the_building, building_year, building_material, heating, house_type, usable_area, number_of_bedrooms, type_of_kitchen, number_of_bathrooms, toilet_together_with_bathroom, balcony, terrace, roof, window_joinery, lot_area, ownership_form, garage = ds.get_house_details(
        details_page_soup)
    road_access, fence, electricity, water, gas, sewerage, telco, shape, dimensions = ds.get_utilities_data(details_page_soup)
    house = House(announcement_id, market_type)
    house.house_type = house_type
    house.condition_of_the_building = condition_of_the_building
    house.number_of_bedrooms = number_of_bedrooms
    house.number_of_bathrooms = number_of_bathrooms
    house.type_of_kitchen = type_of_kitchen
    house.toilet_together_with_bathroom = toilet_together_with_bathroom
    house.balcony = balcony
    house.window_joinery = window_joinery
    house.building_year = building_year
    house.building_material = building_material
    house.heating = heating
    house.usable_area = usable_area
    house.terrace = terrace
    house.roof = roof
    house.lot_area = lot_area
    house.ownership_form = ownership_form
    house.road_access = road_access
    house.fence = fence
    house.gas = gas
    house.electricity = electricity
    house.sewerage = sewerage
    house.water = water
    house.telco = telco
    house.market_type = market_type
    house.garage = garage

    house_data = house.to_dict()

    print("House data: " + str(house_data))
    errors = client.insert_rows_json(environment.get_project_and_dataset() + ".houses_announcements",
                                     [house_data])
    if errors == []:
        print("New house inserted successfully.")
    else:
        print("Errors occurred while inserting house data." + str(errors))

def run(event, context):
    global ds
    data_supplier = event['attributes'].get('data_supplier')
    data_type = event['attributes'].get('data_type')
    action = event['attributes'].get('action')
    city = event['attributes'].get('city')
    distance = event['attributes'].get('distance')
    env = event['attributes'].get('env')

    logger.info(
        f'Start Scraping {data_supplier} for {data_type} for {action} in City:{city}, Distance: {distance}, Environment: {env}')

    environment = Environment(env)

    if data_supplier == 'otodom.pl':
        ds = Otodom(data_type, action, city, distance)
    elif data_supplier == 'nieruchomosci-online.pl':
        ds = NieruchomosciOnline(data_type, action, city, distance)

    basic_url = ds.get_search_url(city)
    page = requests.get(basic_url, headers=headers)
    g = 1
    soup = BeautifulSoup(page.content, 'html.parser')
    if data_supplier == 'otodom.pl':
        res = ds.get_results_records(soup, basic_url)
        logger.info(f'Found {len(res)} records')
        for link in res:
            url = ds.build_offer_url(link)
            print(str(g) + ")" + url)
            saved_announcement_id, saved_price, saved_description = get_announcement_id_price_and_description_by_url(
                environment.get_project_and_dataset() + ".properties_announcements", url)
            # todo source_created source_updated sprawdzać za każdym razem?
            # todo sq_met_price - update?
            # todo number_of_views - może się przydać regularne updatowanie żeby szacować poziom zaintersowania ofertami
            if saved_announcement_id is None:  # means that announcement is not in the db
                add_announcement(data_supplier, data_type, action, url, ds, environment)
            else:
                update_announcement(ds, environment, saved_announcement_id, saved_description, saved_price, url)
            g = g + 1
    elif data_supplier == 'nieruchomosci-online.pl':
        res = ds.get_results_records(soup)
        logger.info(f'Found {len(res)} records')
        for url in res:
            print(str(g) + ")" + url)
            saved_announcement_id, saved_price, saved_description = get_announcement_id_price_and_description_by_url(
                environment.get_project_and_dataset() + ".properties_announcements", url)
            if saved_announcement_id is None:
                add_announcement(data_supplier, data_type, action, url, ds, environment)
            else:
                update_announcement(ds, environment, saved_announcement_id, saved_description, saved_price, url)
            g = g + 1
    logger.info(f'Succesfully completed scraping of {g} records')


def add_announcement(data_supplier, data_type, announcement_type, url, ds, environment):
    if data_supplier == 'otodom.pl':
        add_next_js_announcement(data_supplier, data_type, announcement_type, url, ds, environment)
    elif data_supplier == 'nieruchomosci-online.pl':
        add_html_announcement(data_supplier, data_type, announcement_type, url, ds, environment)


def update_announcement(ds, environment, saved_announcement_id, saved_description, saved_price, url):
    details_page = requests.get(url, headers=headers)
    details_page_soup = BeautifulSoup(details_page.content, 'html.parser')
    current_price, current_description = ds.get_data_for_update_check(details_page_soup)
    is_price_updated = False
    is_description_updated = False
    if current_price is not None and saved_price is not None and current_price != saved_price:
        log_price_change(environment.get_project_and_dataset(), saved_announcement_id, saved_price,
                         current_price)
        is_price_updated = update_price(environment.get_project_and_dataset(), saved_announcement_id,
                                        current_price)
        logger.info(f'Price has changed for {saved_announcement_id} from {saved_price} to {current_price}')
    if current_description != saved_description:
        log_description_change(environment.get_project_and_dataset(), saved_announcement_id,
                               saved_description, current_description)
        is_description_updated = update_description(environment.get_project_and_dataset(),
                                                    saved_announcement_id,
                                                    current_description)
        logger.info(f'Description has changed for {saved_announcement_id}')
    if not is_price_updated and not is_description_updated:
        update_last_seen(environment.get_project_and_dataset(), saved_announcement_id)


def inv_update_price(env, announcement_id, new_price):
    # Update the price in properties_announcements
    update_query = f"""
    UPDATE `{env}.properties_announcements`
    SET price = {new_price}, updated_at = CURRENT_TIMESTAMP()
    WHERE announcement_id = '{announcement_id}'
    """
    client.query(update_query)
    return True


def inv_log_price_change(env, announcement_id, old_value, new_value):
    query = f"""
    CALL `{env}.log_property_change`(
      '{announcement_id}',
      'price',
      '{old_value}',
      '{new_value}'
    )
    """
    logger.info('PRICE has changed')
    client.query(query)


def inv_update_status(env, announcement_id, flat_or_house, new_status):
    # Update the status in flats_announcements
    update_query = f"""
    UPDATE `{env}.{flat_or_house}_announcements`
    SET status = '{new_status}'
    WHERE announcement_id = '{announcement_id}'
    """
    client.query(update_query)

    update_date_query = f"""
    UPDATE `{env}.properties_announcements`
    SET updated_at = CURRENT_TIMESTAMP()
    WHERE announcement_id = '{announcement_id}'
    """
    client.query(update_date_query)
    return True


def inv_log_status_change(env, announcement_id, old_value, new_value):
    query = f"""
    CALL `{env}.log_property_change`(
      '{announcement_id}',
      'status',
      '{old_value}',
      '{new_value}'
    )
    """
    logger.info('STATUS has changed')
    client.query(query)


def inv_update_last_seen(env, announcement_id):
    # Update the price in properties_announcements
    update_query = f"""
    UPDATE `{env}.properties_announcements`
    SET updated_at = CURRENT_TIMESTAMP()
    WHERE announcement_id = '{announcement_id}'
    """
    client.query(update_query)


def inv_get_price_by_announcement_id(project_dataset_table, announcement_id):
    query = f"""
    SELECT price
    FROM {project_dataset_table}
    WHERE announcement_id = '{announcement_id}'
    """
    query_job = client.query(query)
    results = query_job.result()

    for row in results:
        return row.price

    return None


def inv_get_announcement_id_price_and_status_by_url_and_flat_num(project_dataset_table, investment_name, flat_number):
    query = f"""
    SELECT announcement_id, status
    FROM {project_dataset_table}.flats_announcements
    WHERE investment_name = '{investment_name}' AND flat_number = '{flat_number}'
    """
    query_job = client.query(query)
    results = query_job.result()

    for row in results:
        return row.announcement_id, inv_get_price_by_announcement_id(
            project_dataset_table + ".properties_announcements",
            row.announcement_id), row.status

    return None, None, None


def run_investments(event, context):
    global investment
    data_supplier = event['attributes'].get('data_supplier')
    data_type = event['attributes'].get('data_type')
    env = event['attributes'].get('env')

    logger.info(
        f'Start Scraping {data_supplier} for {data_type} , Environment: {env}')

    environment = Environment(env)

    if data_supplier == 'lanowezacisze.pl':
        investment = LanoweZacisze()

    basic_url = investment.get_search_url()
    page = requests.get(basic_url, headers=headers)
    g = 1
    soup = BeautifulSoup(page.content, 'html.parser')
    if data_supplier == 'lanowezacisze.pl':
        flats = investment.get_flats_rows(soup)
        logger.info(f'Found {len(flats)} records')
        for flat_row in flats:
            prop, flat = investment.get_flat_data(flat_row)
            print(flat.investment_name + " " + flat.flat_number + " " + flat.status)
            saved_announcement_id, saved_price, saved_status = inv_get_announcement_id_price_and_status_by_url_and_flat_num(
                environment.get_project_and_dataset(), flat.investment_name, flat.flat_number)
            if saved_announcement_id is None:  # means that announcement is not in the db
                inv_add_announcement(prop, flat, environment)
            else:
                inv_update_announcement(saved_announcement_id, saved_price, saved_status, prop, flat, environment,
                                        "flats")

            g = g + 1
    logger.info(f'Succesfully completed scraping of {g} records')


def inv_add_announcement(prop, flat, environment):
    property_data = prop.to_dict()
    # Convert datetime fields to strings
    for key, value in property_data.items():
        if isinstance(value, datetime.datetime):
            property_data[key] = value.isoformat()  # Use ISO 8601 format for consistency
    property_data_str = str(property_data)
    print("Property data: " + property_data_str)
    # Wstawianie danych do tabeli properties_announcements
    errors = client.insert_rows_json(
        environment.get_project_and_dataset() + ".properties_announcements", [property_data])
    if errors == []:
        print("New property inserted successfully.")
    else:
        print("Errors occurred while inserting property data." + errors)

    flat_data = flat.to_dict()
    print("Flat data: " + str(flat_data))
    flat_errors = client.insert_rows_json(environment.get_project_and_dataset() + ".flats_announcements",
                                          [flat_data])
    if flat_errors == []:
        print("New flat inserted successfully.")
    else:
        print("Errors occurred while inserting flat data (INV)." + str(errors))
        # if not (data_supplier == 'olx.pl' and 'otodom' in url):


def inv_update_announcement(saved_announcement_id, saved_price, saved_status, property, flat, environment,
                            flat_or_house):
    current_price = property.price
    current_status = flat.status
    is_price_updated = False
    if current_price is not None and saved_price is not None and current_price != saved_price:
        inv_log_price_change(environment.get_project_and_dataset(), saved_announcement_id, saved_price,
                             current_price)
        is_price_updated = inv_update_price(environment.get_project_and_dataset(), saved_announcement_id,
                                            current_price)
        logger.info(f'Price has changed for {saved_announcement_id} from {saved_price} to {current_price}')

    is_status_updated = False
    if current_status is not None and saved_status is not None and current_status != saved_status:
        inv_log_status_change(environment.get_project_and_dataset(), saved_announcement_id, saved_status,
                              current_status)
        is_status_updated = inv_update_status(environment.get_project_and_dataset(), saved_announcement_id,
                                              flat_or_house, current_status)
        logger.info(f'Status has changed for {saved_announcement_id} from {saved_status} to {current_status}')
    if not is_price_updated and not is_status_updated:
        inv_update_last_seen(environment.get_project_and_dataset(), saved_announcement_id)


if __name__ == "__main__":
    event = {'@type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage',
             'attributes': dict(data_type='flats', action='sell', data_supplier='nieruchomosci-online.pl',
                                city='skawina',
                                distance='2',
                                env='test'),
             'data': 'G3JhdGth'}
    context = {'service': 'pubsub.googleapis.com',
               'type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage'}
    run(event, context)

# if __name__ == "__main__":
#     event = {'@type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage',
#              'attributes': dict(data_type='flats', data_supplier='lanowezacisze.pl', env='test'),
#              'data': 'G3JhdGth'}
#     context = {'name': 'projects/propertymanager-385720/topics/gratka', 'service': 'pubsub.googleapis.com',
#                'type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage'}
#     run_investments(event, context)
