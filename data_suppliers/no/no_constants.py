NO_LANDING_PAGE_URL = 'https://www.nieruchomosci-online.pl/'
NO_SEARCH_PARCEL_URL = 'https://{location}.nieruchomosci-online.pl/szukaj.html?3,dzialka,sprzedaz,,{location},,,{distance}'
NO_SEARCH_RENT_PARCEL_URL = 'https://{location}.nieruchomosci-online.pl/szukaj.html?3,dzialka,wynajem,,{location},,,{distance}'

NO_SEARCH_FLAT_URL = 'https://{location}.nieruchomosci-online.pl/szukaj.html?3,mieszkanie,sprzedaz,,{location},,,{distance}'
NO_SEARCH_RENT_FLAT_URL = 'https://{location}.nieruchomosci-online.pl/szukaj.html?3,mieszkanie,wynajem,,{location},,,{distance}'

NO_SEARCH_HOUSE_URL = 'https://{location}.nieruchomosci-online.pl/szukaj.html?3,dom,sprzedaz,,{location},,,{distance}'
NO_SEARCH_RENT_HOUSE_URL = 'https://{location}.nieruchomosci-online.pl/szukaj.html?3,dom,wynajem,,{location},,,{distance}'


def get_landing_page_url():
    return NO_LANDING_PAGE_URL


def get_search_lots_url(location, action, distance):
    if action == 'sell':
        temp_url = NO_SEARCH_PARCEL_URL.replace("{location}", location)
        temp_url = temp_url.replace("{distance}", distance)
        return temp_url
    elif action == 'rent':
        temp_url = NO_SEARCH_RENT_PARCEL_URL.replace("{location}", location)
        temp_url = temp_url.replace("{distance}", distance)
        return temp_url


def get_search_flats_url(location, action, distance):
    if action == 'sell':
        return NO_SEARCH_FLAT_URL.replace("{location}", location)
    elif action == 'rent':
        return NO_SEARCH_RENT_FLAT_URL.replace("{location}", location)


def get_search_houses_url(location, action, distance):
    if action == 'sell':
        return NO_SEARCH_HOUSE_URL.replace("{location}", location)
    elif action == 'rent':
        return NO_SEARCH_RENT_HOUSE_URL.replace("{location}", location)
