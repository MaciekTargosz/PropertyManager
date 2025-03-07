import datetime
import logging
import os

import requests
from bs4 import BeautifulSoup
from google.cloud import bigquery

from investments.data_suppliers.lanowe_zacisze_po import LanoweZacisze
from db.environment import Environment

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

# Stworzenie klienta BigQuery
client = bigquery.Client()

logger = logging.getLogger(__name__)
logging.basicConfig(filename='crawler.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


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
        return row.announcement_id, inv_get_price_by_announcement_id(project_dataset_table + ".properties_announcements",
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
                inv_update_announcement(saved_announcement_id, saved_price, saved_status, prop, flat, environment, "flats")

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
        print("Errors occurred while inserting flat data." + str(errors))
        # if not (data_supplier == 'olx.pl' and 'otodom' in url):


def inv_update_announcement(saved_announcement_id, saved_price, saved_status, property, flat, environment, flat_or_house):
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
             'attributes': dict(data_type='flats', data_supplier='lanowezacisze.pl', env='test'),
             'data': 'G3JhdGth'}
    context = {'name': 'projects/propertymanager-385720/topics/gratka', 'service': 'pubsub.googleapis.com',
               'type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage'}
    run(event, context)
