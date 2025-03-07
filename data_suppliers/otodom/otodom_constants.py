OTODOM_LANDING_PAGE_URL = 'https://www.otodom.pl'
OTODOM_SEARCH_PARCEL_URL = 'https://www.otodom.pl/pl/wyniki/sprzedaz/dzialka/malopolskie/krakowski/{location}/{location}?ownerTypeSingleSelect=ALL&distanceRadius=2&viewType=listing&limit=72'
OTODOM_SEARCH_RENT_PARCEL_URL = 'https://www.otodom.pl/pl/wyniki/wynajem/dzialka/malopolskie/krakowski/{location}/{location}?limit=72&by=DEFAULT&direction=DESC&viewType=listing'
OTODOM_SEARCH_FLAT_URL = 'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/malopolskie/krakowski/{location}/{location}?distanceRadius=2&viewType=listing&limit=72'
OTODOM_SEARCH_RENT_FLAT_URL = 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/malopolskie/krakowski/{location}/{location}?distanceRadius=2&limit=72&by=DEFAULT&direction=DESC&viewType=listing'
OTODOM_SEARCH_HOUSE_URL ='https://www.otodom.pl/pl/wyniki/sprzedaz/dom/malopolskie/krakowski/{location}/{location}?ownerTypeSingleSelect=ALL&distanceRadius=2&by=DEFAULT&direction=DESC&viewType=listing&limit=72'
OTODOM_SEARCH_RENT_HOUSE_URL = 'https://www.otodom.pl/pl/wyniki/wynajem/dom/malopolskie/krakowski/{location}/{location}?distanceRadius=2&by=DEFAULT&direction=DESC&viewType=listing'

#TODO
OTODOM_WAREHOUSE_URL = 'https://www.otodom.pl/pl/wyniki/sprzedaz/haleimagazyny/malopolskie/krakowski/{location}/{location}?ownerTypeSingleSelect=ALL&distanceRadius=2&by=DEFAULT&direction=DESC&viewType=listing'
OTODOM_WAREHOUSE_RENT_URL = 'https://www.otodom.pl/pl/wyniki/wynajem/haleimagazyny/malopolskie/krakowski/{location}/{location}a?distanceRadius=2&by=DEFAULT&direction=DESC&viewType=listing'

OTODOM_COMMERCIAL_PREMISES_URL = 'https://www.otodom.pl/pl/wyniki/sprzedaz/lokal/malopolskie/krakowski/{location}/{location}?ownerTypeSingleSelect=ALL&by=DEFAULT&direction=DESC&viewType=listing&limit=72'
OTODOM_COMMERCIAL_PREMISES_RENT_URL = 'https://www.otodom.pl/pl/wyniki/wynajem/lokal/malopolskie/krakowski/{location}/{location}?ownerTypeSingleSelect=ALL&by=DEFAULT&direction=DESC&viewType=listing&limit=72'

OTODOM_GARAGE_URL = 'https://www.otodom.pl/pl/wyniki/sprzedaz/garaz/malopolskie/krakowski/{location}/{location}?ownerTypeSingleSelect=ALL&by=DEFAULT&direction=DESC&viewType=listing'
OTODOM_GARAGE_RENT_URL = 'https://www.otodom.pl/pl/wyniki/wynajem/garaz/malopolskie/krakowski/{location}/{location}?by=DEFAULT&direction=DESC&viewType=listing'



def get_landing_page_url():
    return OTODOM_LANDING_PAGE_URL


def get_search_parcel_url():
    return OTODOM_SEARCH_PARCEL_URL

def get_search_lots_url(location, action):
    if action == 'sell':
        return OTODOM_SEARCH_PARCEL_URL.replace("{location}", location)
    elif action == 'rent':
        return OTODOM_SEARCH_RENT_PARCEL_URL.replace("{location}", location)

def get_search_flats_url(location, action):
    if action == 'sell':
        return OTODOM_SEARCH_FLAT_URL.replace("{location}", location)
    elif action == 'rent':
        return OTODOM_SEARCH_RENT_FLAT_URL.replace("{location}", location)

def get_search_houses_url(location, action):
    if action == 'sell':
        return OTODOM_SEARCH_HOUSE_URL.replace("{location}", location)
    elif action == 'rent':
        return OTODOM_SEARCH_RENT_HOUSE_URL.replace("{location}", location)