import datetime


class Property:
    def __init__(self, announcement_id, announcement_type, url, property_type, location):
        self.__announcement_id = announcement_id  # str(uuid.uuid4())
        self.__location = location
        self.__location_type = None
        self.__property_type = property_type
        self.__url = url
        self.__announcement_type = announcement_type
        self.__area = None
        self.__description = None
        self.__district = None
        self.__commune = None
        self.__place = None
        self.__place_district = None
        self.__publisher = None
        self.__images_urls = None
        self.__created_at = datetime.datetime.now()
        self.__updated_at = datetime.datetime.now()
        self.__source = None
        self.__source_created_at = None
        self.__source_updated_at = None
        self.__status = None
        self.__street = None
        self.__price = None
        self.__sq_met_price = None
        self.__type_of_contract = None
        self.__number_of_views = None
        self.__number_of_raises = None

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def area(self):
        return self.__area

    @area.setter
    def area(self, value):
        self.__area = float(value)

    @property
    def announcement_type(self):
        return self.__announcement_type

    @announcement_type.setter
    def announcement_type(self, value):
        self.__announcement_type = value

    @property
    def location_type(self):
        return self.__location_type

    @location_type.setter
    def location_type(self, value):
        self.__location_type = value

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def district(self):
        return self.__district

    @district.setter
    def district(self, value):
        self.__district = value

    @property
    def commune(self):
        return self.__commune

    @commune.setter
    def commune(self, value):
        self.__commune = value

    @property
    def place(self):
        return self.__place

    @place.setter
    def place(self, value):
        self.__place = value

    @property
    def place_district(self):
        return self.__place_district

    @place_district.setter
    def place_district(self, value):
        self.__place_district = value

    @property
    def street(self):
        return self.__street

    @street.setter
    def street(self, value):
        self.__street = value

    @property
    def images_urls(self):
        return self.__images_urls

    @images_urls.setter
    def images_urls(self, value):
        self.__images_urls = value

    @property
    def publisher(self):
        return self.__publisher

    @publisher.setter
    def publisher(self, value):
        self.__publisher = value

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        self.__price = value

    @property
    def sq_met_price(self):
        return self.__sq_met_price

    @sq_met_price.setter
    def sq_met_price(self, value):
        self.__sq_met_price = value

    @property
    def property_type(self):
        return self.__property_type

    @property_type.setter
    def property_type(self, value):
        self.__property_type = value

    @property
    def created_at(self):
        return self.__created_at

    @created_at.setter
    def created_at(self, value):
        self.__created_at = value

    @property
    def updated_at(self):
        return self.__updated_at

    @updated_at.setter
    def updated_at(self, value):
        self.__updated_at = value

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, value):
        self.__source = value

    @property
    def source_created_at(self):
        return self.__source_created_at

    @source_created_at.setter
    def source_created_at(self, value):
        self.__source_created_at = value

    @property
    def source_updated_at(self):
        return self.__source_updated_at

    @source_updated_at.setter
    def source_updated_at(self, value):
        self.__source_updated_at = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def type_of_contract(self):
        return self.__type_of_contract

    @type_of_contract.setter
    def type_of_contract(self, value):
        self.__type_of_contract = value

    @property
    def number_of_views(self):
        return self.__number_of_views

    @number_of_views.setter
    def number_of_views(self, value):
        self.__number_of_views = value

    @property
    def number_of_raises(self):
        return self.__number_of_raises

    @number_of_raises.setter
    def number_of_raises(self, value):
        self.__number_of_raises = value

    def to_dict(self):
        return {
            "announcement_id": self.__announcement_id,
            "announcement_type": self.__announcement_type,
            "url": self.__url,
            "location": self.__location,
            "location_type": self.__location_type,
            "district": self.__district,
            "commune": self.__commune,
            "place": self.__place,
            "place_district": self.__place_district,
            "street": self.__street,
            "property_type": self.__property_type,
            "area": self.__area,
            "price": self.__price,
            "description": self.__description,
            "images": self.__images_urls,
            "publisher": self.__publisher,
            "sq_met_price": self.__sq_met_price,
            "status": "active",
            "created_at": self.__created_at,
            "updated_at": self.__updated_at,
            "source": self.__source,
            "source_created_at": self.__source_created_at,
            "source_updated_at": self.__source_updated_at,
            "type_of_contract": self.__type_of_contract,
            "number_of_views": self.__number_of_views,
            "number_of_raises": self.__number_of_raises
        }


class Lot:

    def __init__(self, announcement_id):
        self.__announcement_id = announcement_id
        self.__lot_type = None
        self.__lot_shape = None
        self.__lot_number = None
        self.__fence = None
        self.__road_access = None
        self.__electricity = None
        self.__gas = None
        self.__water = None
        self.__sewerage = None
        self.__telco = None
        self.__dimensions = None

    @property
    def lot_type(self):
        return self.__lot_type

    @lot_type.setter
    def lot_type(self, value):
        self.__lot_type = value

    @property
    def lot_shape(self):
        return self.__lot_shape

    @lot_shape.setter
    def lot_shape(self, value):
        self.__lot_shape = value

    @property
    def lot_number(self):
        return self.__lot_number

    @lot_number.setter
    def lot_number(self, value):
        self.__lot_number = value

    @property
    def fence(self):
        return self.__fence

    @fence.setter
    def fence(self, value):
        self.__fence = value

    @property
    def road_access(self):
        return self.__road_access

    @road_access.setter
    def road_access(self, value):
        self.__road_access = value

    @property
    def electricity(self):
        return self.__electricity

    @electricity.setter
    def electricity(self, value):
        self.__electricity = value

    @property
    def gas(self):
        return self.__gas

    @gas.setter
    def gas(self, value):
        self.__gas = value

    @property
    def water(self):
        return self.__water

    @water.setter
    def water(self, value):
        self.__water = value

    @property
    def sewerage(self):
        return self.__sewerage

    @sewerage.setter
    def sewerage(self, value):
        self.__sewerage = value

    @property
    def telco(self):
        return self.__telco

    @telco.setter
    def telco(self, value):
        self.__telco = value

    @property
    def dimensions(self):
        return self.__dimensions

    @dimensions.setter
    def dimensions(self, value):
        self.__dimensions = value

    def to_dict(self):
        return {
            "announcement_id": self.__announcement_id,
            "lot_type": self.__lot_type,
            "lot_shape": self.__lot_shape,
            "lot_number": self.__lot_number,
            "fence": self.__fence,
            "road_access": self.__road_access,
            "electricity": self.__electricity,
            "gas": self.__gas,
            "water": self.__water,
            "sewerage": self.__sewerage,
            "telco": self.__telco,
            "dimensions": self.__dimensions
        }


class Flat:
    def __init__(self, announcement_id, market_type):
        self.__announcement_id = announcement_id
        self.__market_type = market_type
        self.__condition_of_the_flat = None
        self.__floor = None
        self.__number_of_floors = None
        self.__number_of_rooms = None
        self.__number_of_bedrooms = None
        self.__number_of_bathrooms = None
        self.__type_of_kitchen = None
        self.__toilet_together_with_bathroom = None
        self.__balcony = None
        self.__garden = None
        self.__window_joinery = None
        self.__building_year = None
        self.__building_material = None
        self.__heating = None
        self.__lift = None
        self.__garage = None
        self.__parking = None
        self.__terrace = None
        self.__basement = None
        self.__flat_number = None
        self.__investment_name = None
        self.__status = None

    @property
    def market_type(self):
        return self.__market_type

    @market_type.setter
    def market_type(self, value):
        self.__market_type = value

    @property
    def condition_of_the_flat(self):
        return self.__condition_of_the_flat

    @condition_of_the_flat.setter
    def condition_of_the_flat(self, value):
        self.__condition_of_the_flat = value

    @property
    def floor(self):
        return self.__floor

    @floor.setter
    def floor(self, value):
        self.__floor = value

    @property
    def number_of_floors(self):
        return self.__number_of_floors

    @number_of_floors.setter
    def number_of_floors(self, value):
        self.__number_of_floors = value

    @property
    def number_of_rooms(self):
        return self.__number_of_rooms

    @number_of_rooms.setter
    def number_of_rooms(self, value):
        self.__number_of_rooms = value

    @property
    def number_of_bedrooms(self):
        return self.__number_of_bedrooms

    @number_of_bedrooms.setter
    def number_of_bedrooms(self, value):
        self.__number_of_bedrooms = value

    @property
    def number_of_bathrooms(self):
        return self.__number_of_bathrooms

    @number_of_bathrooms.setter
    def number_of_bathrooms(self, value):
        self.__number_of_bathrooms = value

    @property
    def type_of_kitchen(self):
        return self.__type_of_kitchen

    @type_of_kitchen.setter
    def type_of_kitchen(self, value):
        self.__type_of_kitchen = value

    @property
    def toilet_together_with_bathroom(self):
        return self.__toilet_together_with_bathroom

    @toilet_together_with_bathroom.setter
    def toilet_together_with_bathroom(self, value):
        self.__toilet_together_with_bathroom = value

    @property
    def balcony(self):
        return self.__balcony

    @balcony.setter
    def balcony(self, value):
        self.__balcony = value

    @property
    def garden(self):
        return self.__garden

    @garden.setter
    def garden(self, value):
        self.__garden = value

    @property
    def window_joinery(self):
        return self.__window_joinery

    @window_joinery.setter
    def window_joinery(self, value):
        self.__window_joinery = value

    @property
    def building_year(self):
        return self.__building_year

    @building_year.setter
    def building_year(self, value):
        self.__building_year = value

    @property
    def building_material(self):
        return self.__building_material

    @building_material.setter
    def building_material(self, value):
        self.__building_material = value

    @property
    def heating(self):
        return self.__heating

    @heating.setter
    def heating(self, value):
        self.__heating = value

    @property
    def lift(self):
        return self.__lift

    @lift.setter
    def lift(self, value):
        self.__lift = value

    @property
    def garage(self):
        return self.__garage

    @garage.setter
    def garage(self, value):
        self.__garage = value

    @property
    def parking(self):
        return self.__parking

    @parking.setter
    def parking(self, value):
        self.__parking = value

    @property
    def terrace(self):
        return self.__terrace

    @terrace.setter
    def terrace(self, value):
        self.__terrace = value

    @property
    def basement(self):
        return self.__basement

    @basement.setter
    def basement(self, value):
        self.__basement = value

    @property
    def flat_number(self):
        return self.__flat_number

    @flat_number.setter
    def flat_number(self, value):
        self.__flat_number = value

    @property
    def investment_name(self):
        return self.__investment_name

    @investment_name.setter
    def investment_name(self, value):
        self.__investment_name = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value


    def to_dict(self):
        return {
            "announcement_id": self.__announcement_id,
            "market_type": self.__market_type,
            "condition_of_the_flat": self.__condition_of_the_flat,
            "floor": self.__floor,
            "number_of_floors": self.__number_of_floors,
            "number_of_rooms": self.__number_of_rooms,
            "number_of_bedrooms": self.__number_of_bedrooms,
            "number_of_bathrooms": self.__number_of_bathrooms,
            "type_of_kitchen": self.__type_of_kitchen,
            "toilet_together_with_bathroom": self.__toilet_together_with_bathroom,
            "balcony": self.__balcony,
            "garden": self.__garden,
            "window_joinery": self.__window_joinery,
            "building_year": self.__building_year,
            "building_material": self.__building_material,
            "heating": self.__heating,
            "lift": self.__lift,
            "garage": self.__garage,
            "parking": self.__parking,
            "terrace": self.__terrace,
            "basement": self.__basement,
            "flat_number": self.__flat_number,
            "investment_name": self.__investment_name,
            "status": self.__status
        }


class House:
    def __init__(self, announcement_id, market_type):
        self.__announcement_id = announcement_id
        self.__market_type = market_type
        self.__usable_area = None
        self.__number_of_bedrooms = None
        self.__type_of_kitchen = None
        self.__number_of_bathrooms = None
        self.__toilet_together_with_bathroom = None
        self.__balcony = None
        self.__terrace = None
        self.__roof = None
        self.__window_joinery = None
        self.__lot_area = None
        self.__market_type = None
        self.__ownership_form = None
        self.__condition_of_the_building = None
        self.__building_material = None
        self.__building_year = None
        self.__heating = None
        self.__road_access = None
        self.__sewerage = None
        self.__gas = None
        self.__water = None
        self.__electricity = None
        self.__telco = None
        self.__fence = None
        self.__garage = None

    @property
    def market_type(self):
        return self.__market_type

    @market_type.setter
    def market_type(self, value):
        self.__market_type = value

    @property
    def house_type(self):
        return self.__house_type

    @house_type.setter
    def house_type(self, value):
        self.__house_type = value

    @property
    def usable_area(self):
        return self.__usable_area

    @usable_area.setter
    def usable_area(self, value):
        self.__usable_area = value

    @property
    def condition_of_the_building(self):
        return self.__condition_of_the_building

    @condition_of_the_building.setter
    def condition_of_the_building(self, value):
        self.__condition_of_the_building = value

    @property
    def number_of_bedrooms(self):
        return self.__number_of_bedrooms

    @number_of_bedrooms.setter
    def number_of_bedrooms(self, value):
        self.__number_of_bedrooms = value

    @property
    def number_of_bathrooms(self):
        return self.__number_of_bathrooms

    @number_of_bathrooms.setter
    def number_of_bathrooms(self, value):
        self.__number_of_bathrooms = value

    @property
    def toilet_together_with_bathroom(self):
        return self.__toilet_together_with_bathroom

    @toilet_together_with_bathroom.setter
    def toilet_together_with_bathroom(self, value):
        self.__toilet_together_with_bathroom = value

    @property
    def type_of_kitchen(self):
        return self.__type_of_kitchen

    @type_of_kitchen.setter
    def type_of_kitchen(self, value):
        self.__type_of_kitchen = value

    @property
    def toilet_together_with_bathroom(self):
        return self.__toilet_together_with_bathroom

    @toilet_together_with_bathroom.setter
    def toilet_together_with_bathroom(self, value):
        self.__toilet_together_with_bathroom = value

    @property
    def balcony(self):
        return self.__balcony

    @balcony.setter
    def balcony(self, value):
        self.__balcony = value

    @property
    def terrace(self):
        return self.__terrace

    @terrace.setter
    def terrace(self, value):
        self.__terrace = value

    @property
    def roof(self):
        return self.__roof

    @roof.setter
    def roof(self, value):
        self.__roof = value

    @property
    def window_joinery(self):
        return self.__window_joinery

    @window_joinery.setter
    def window_joinery(self, value):
        self.__window_joinery = value


    @property
    def lot_area(self):
        return self.__lot_area

    @lot_area.setter
    def lot_area(self, value):
        self.__lot_area = value

    @property
    def building_year(self):
        return self.__building_year

    @building_year.setter
    def building_year(self, value):
        self.__building_year = value

    @property
    def building_material(self):
        return self.__building_material

    @building_material.setter
    def building_material(self, value):
        self.__building_material = value

    @property
    def heating(self):
        return self.__heating

    @heating.setter
    def heating(self, value):
        self.__heating = value

    @property
    def road_access(self):
        return self.__road_access

    @road_access.setter
    def road_access(self, value):
        self.__road_access = value

    @property
    def sewerage(self):
        return self.__sewerage

    @sewerage.setter
    def sewerage(self, value):
        self.__sewerage = value

    @property
    def gas(self):
        return self.__gas

    @gas.setter
    def gas(self, value):
        self.__gas = value

    @property
    def water(self):
        return self.__water

    @water.setter
    def water(self, value):
        self.__water = value

    @property
    def electricity(self):
        return self.__electricity

    @electricity.setter
    def electricity(self, value):
        self.__electricity = value

    @property
    def telco(self):
        return self.__telco

    @telco.setter
    def telco(self, value):
        self.__telco = value

    @property
    def fence(self):
        return self.__fence

    @fence.setter
    def fence(self, value):
        self.__fence = value

    @property
    def garage(self):
        return self.__garage

    @garage.setter
    def garage(self, value):
        self.__garage  = value

    def to_dict(self):
        return {
            "announcement_id": self.__announcement_id,
            "market_type": self.__market_type,
            "house_type": self.__house_type,
            "usable_area": self.__usable_area,
            "condition_of_the_building": self.__condition_of_the_building,
            "number_of_bedrooms": self.__number_of_bedrooms,
            "number_of_bathrooms": self.__number_of_bathrooms,
            "type_of_kitchen": self.__type_of_kitchen,
            "toilet_together_with_bathroom": self.__toilet_together_with_bathroom,
            "balcony": self.__balcony,
            "terrace": self.__terrace,
            "roof": self.__roof,
            "window_joinery": self.__window_joinery,
            "lot_area": self.__lot_area,
            "ownership_form": self.__ownership_form,
            "building_year": self.__building_year,
            "building_material": self.__building_material,
            "heating": self.__heating,
            "road_access": self.__road_access,
            "sewerage": self.__sewerage,
            "gas": self.__gas,
            "water": self.__water,
            "electricity": self.__electricity,
            "telco": self.__telco,
            "fence": self.__fence,
            "garage": self.__garage
        }


class Advertiser:
    def __init__(self, advertiser_id, type, name, company):
        self.__advertiser_id = advertiser_id
        self.__type = type
        self.__name = name
        self.__company = company
        self.__email = None
        self.__phone = None
        self.__address = None

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = value

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        self.__phone = value

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, value):
        self.__address = value

    def to_dict(self):
        return {
            "advertiser_id": self.__advertiser_id,
            "type": self.__type,
            "name": self.__name,
            "company": self.__company,
            "email": self.__email,
            "phone": self.__phone,
            "address": self.__address
        }
