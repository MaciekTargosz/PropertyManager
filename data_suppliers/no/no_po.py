import re
import logging
import requests

from data_suppliers.no.no_constants import get_search_lots_url, get_search_flats_url, get_search_houses_url
from data_suppliers.no.no_locators import get_results_records_css, get_pagination_next_page_btn
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}


def get_detailed_locations(detailed_page):
    address_element = detailed_page.select_one('ul#locationUl li.adress')

    if address_element is None:
        elements = detailed_page.select('ul#locationUl li')
        for element in elements:
            if element.getText().__contains__("Adres: "):
                address_element = element
                break
    temp_location = address_element.getText().replace("Adres: ", "").strip()
    logging.info("LOCATION: " + temp_location)
    location_array = temp_location.split(", ")
    array_len = len(location_array)
    if array_len == 5:
        district = location_array[3]
        commune = location_array[2]
        place = location_array[1]
        place_district = ''
        street = location_array[0]
        print("x5) Gmina: " + commune + ", miejscowość: " + place + ", ulica: " + street)
    elif array_len == 4:
        district = location_array[2]
        commune = location_array[1]
        if sprawdz_polozenie(location_array[0], location_array[1], location_array[2]) == "Miejscowość":
            place = location_array[0]
            place_district = ''
            street = ''
            print("4a) Gmina: " + commune + ", miejscowość: " + place)
        else:
            place = commune
            place_district = ''
            street = location_array[0]
            print("4b) Gmina: " + commune + ", miejscowość: " + place + ", ulica: " + street)
    elif array_len == 3:
        if location_array[2] == "małopolskie":
            district = ""
            commune = ""
            if location_array[1] == "krakowski":
                place = location_array[0]
                place_district = ''
                street = ''
            else:
                place = location_array[1]
                place_district = ''
                street = location_array[0]
            print("3) Gmina: " + commune + ", miejscowość: " + place)
        else:
            district = location_array[1]
            commune = location_array[0]
            place = location_array[0]
            place_district = ''
            street = ''
            print("3) Gmina: " + commune + ", miejscowość: " + place)
    elif array_len == 2:
        if location_array[1] == "małopolskie":
            district = ''
            commune = ''
            place = location_array[0]
            place_district = ''
            street = ''
    else:
        logging.error("LOCATION ARRAY LENGTH IS NOT 5 , LOCATION IS: ")
    return district, commune, place, place_district, street


# -*- coding: utf-8 -*-

dane_adresowe = {
    "powiat_krakowski": {
        "gmina_skawina": {
            "Borek_Szlachecki": ["Szkolna", "Łanowa", "Leśna", "Szlachecka", "Długa", "Zakątek", "Topolowa", "Wesoła",
                                 "Wspólna", "Zawiła", "Nad Potokiem", "Dworska", "Cicha", "Szuwarowa", "Dworcowa",
                                 "Rekreacyjna", "Spacerowa", "Wernera", "Akacjowa", "Słoneczna"],
            "Facimiech": [],
            "Gołuchowice": [],
            "Grabie": [],
            "Jaśkowice": ["Różana", "Łąkowa", "Lipowa", "Brzozowa", "Spacerowa", "Lawendowa", "Słoneczna", "Cicha",
                          "Sosnowa", "Wiślana", "Mateczny", "Torowa", "Leśna", "Kościelna", "Ogrodowa", "Boczna",
                          "Graniczna", "Spokojna", "Krakowska", "Jagodowa", "Pod Górą", "Sportowa", "Źródlana"],
            "Jurczyce": ["prof. Marii Dzielskiej", "Lesisko", "Anny Haller", "Brzozowa", "Spacerowa", "Ogrodowa",
                         "Widokowa", "Spokojna", "Zacisze", "Dąbrowa", "gen. Józefa Hallera", "Dworska", "Kasztanowa"],
            "Kopanka": ["Za Kanałem", "rtm. Witolda Pileckiego", "Długa", "Skawińska", "Prosta", "Polna", "Podwale",
                        "Strażacka", "Spacerowa", "Słoneczna", "Skośna", "Sportowa", "Śliczna", "Kasztanowa", "Krótka",
                        "Wspólna", "Wiślna", "Wiklinowa", "Wesoła", "Topolowa", "Ofiar Katynia"],
            "Krzęcin": ["Za Browarem", "Wichrowe Wzgórze", "Ostra Góra", "Spokojna", "św. Floriana", "św. Mikołaja",
                        "św. Stanisława Biskupa", "Cicha", "Akacjowa", "Dębowa", "Brzozowa", "Brzegowa", "Krótka",
                        "Kalwaryjska", "Jodłowa", "Jesionowa", "Ogrodowa", "Lipowa", "Kwiatowa", "Sąsiedzka",
                        "Rokitowiec", "Prosta", "Podgórska", "Leśna", "Krakowska", "Dąbrówki", "Słoneczna",
                        "Ogrodnicza", "Szczęsna", "Spacerowa", "Sosnowicka", "Sosnowa", "Zgody", "Szkolna", "Zacisze",
                        "Wspólna", "Wodzieniec", "Wierzbowa", "Widokowa"],
            "Ochodza": ["Cicha", "Słoneczna", "Krótka", "Wspólna", "Brzozowa", "Fiołkowa", "Dworska", "Jaśminowa",
                        "Spacerowa", "Szlachetna", "Wiślana", "Starowiślna", "Kwiatowa", "Księżycowa"],
            "Polanka_Hallera": [],
            "Radziszów": ["Siedliska", "Zawodzie", "Wytrzyszczek", "Sądecka", "Sadowa", "Łąkowa", "Brzegi", "Kolejowa",
                          "Żwirowa", "Krótka", "Spokojna", "Wodna", "Widokowa", "Jarzębinowa", "Torowa",
                          "Zadworze Górne", "Nad Potokiem", "Leniecka", "Wąska", "Stawowa", "Przemysłowa",
                          "Modrzewiowa", "Zadworze", "Zacisze", "Drożdżownik", "Jaśminowa", "Zimnowiec", "Podwale",
                          "Różana", "Kolorowa", "Górki", "Leśna", "Wspólna", "Prosta", "Cicha", "Nad Pasieką",
                          "Podlesie", "Rynek", "Jagodowa", "Słoneczna", "Jagodowa Boczna", "Kamienna", "Kwiatowa",
                          "Polna", "Kęciki", "Wąwozowa", "Chorzyny", "Kościelna", "Skawińska", "Szkolna", "Pod Górą",
                          "Łanowa", "Jana Pawła II", "Lipowa", "Górna", "Spacerowa"],
            "Rzozów": [],
            "Skawina": ["Leśna", "Graniczna", "Stanisława Wyspiańskiego", "Pasternik", "płk. Andrzeja Hałacińskiego",
                        "Bolesława Jamroza", "gen. Emila Fieldorfa 'Nila'", "O. Adama F. Studzińskiego",
                        "ppor. Mieczysława Majdzika", "rtm. Witolda Pileckiego", "mjr Jana Żychonia",
                        "ks. Walentego Troski", "ks. Jerzego Popiełuszki", "Władysława Sikorskiego", "Biała Droga",
                        "Łanowa", "Łanowa", "Skawińska", "Konstytucji 3 Maja", "Adama Asnyka", "Torowa Boczna",
                        "Korabnicka Boczna", "Zacisze", "Jagielnia", "29 Listopada", "Mikołaja Kopernika",
                        "Józefa I. Kraszewskiego", "Krakowska", "Józefa Piłsudskiego", "Szkolna", "Spółdzielcza",
                        "Różana", "Podgórki", "Żwirki i Wigury", "Zielona", "Gościnna", "Przemysłowa", "Okrężna",
                        "Aleksandra Głowackiego", "Hallerów", "Wiklinowa", "Rzeczna", "Krzywa", "Kalinowa", "Jaśminowa",
                        "Tadeusza Kościuszki", "Pisary", "Spokojna", "Marka Kublińskiego", "Willowa", "Feliksa Pukły",
                        "Kwiatowa", "Nad Potokiem", "Hutników", "Ofiar Katynia", "Stefana Batorego",
                        "Stanisława Chmielka", "Obrońców Tobruku", "Szwedzka", "Jarosława Dąbrowskiego",
                        "Józefa Poniatowskiego", "Marii Skłodowskiej-Curie", "Na Stoku", "Za Górą", "Pokoju",
                        "Batalionów Chłopskich", "Torowa", "Jodłowa", "Jana Kilińskiego", "Spacerowa",
                        "Wojska Polskiego", "Niepodległości", "Kazimierza Wielkiego", "Brzozowa", "Bagienki", "Podwale",
                        "Jana Sobieskiego", "Żwirowa", "Kościelna", "Energetyków", "Monte Cassino", "Wincentego Witosa",
                        "Podbory", "Altanowa", "Kasztanowa", "Wyrwisko", "Konstantego Ildefonsa Gałczyńskiego",
                        "Marii Konopnickiej", "Estery", "Węgierska", "Kazimierza Pułaskiego", "Jana Pawła II",
                        "Zamkowa", "Browarna", "Babetty", "Tyniecka", "Lipowa", "Stefana Żeromskiego", "Kolejowa",
                        "Ignacego Daszyńskiego", "Groble", "Adama Mickiewicza", "Rynek", "Cicha", "Robotnicza",
                        "Korabnicka", "Dębca", "Wesoła", "Radziszowska", "Nad Wodą", "Piastowska", "Sadowa", "Falbówki",
                        "Sąsiedzka", "Armii Krajowej", "Juliusza Słowackiego", "Słoneczna", "Bukowska",
                        "Feliksa Pachla", "Działkowców", "Łąkowa", "Wspólna", "Ogrody", "Polna", "Żwirki Wigury"],
            "Wielkie_Drogi": ["Starowiejska", "Brzozowa", "Zachodnia", "Karoliny Olearskiej", "Krakowska",
                              "Jana Brandysa", "Kalwaryjska", "Radwanitów", "Rzemieślnicza", "Królewska", "Nowina",
                              "Torowa", "Zagrody", "Wierzbowa", "Wspólna", "Widokowa", "Spacerowa", "Szkolna",
                              "Parkowa", "Spokojna", "Kolejowa", "Łąkowa", "Wielicka", "Miodowa"],
            "Wola_Radziszowska": ["św. Jana Pawła II", "Skotnica", "Skawińska", "Ostra Góra", "Rokicie", "Podlipie",
                                  "Podskale", "Lipki", "Na Grani", "Spacerowa", "Spokojna", "Sosnowa", "Słoneczna",
                                  "Wesoła", "Stawiski", "Szkolna", "Łąkowa", "Wrzosowa", "Zacisze", "Brzozowa",
                                  "Widokowa", "Łęg", "Potokowa", "Rodzinna", "Krakowska", "Kolejowa", "Chorzyny",
                                  "Konwaliowa", "Kamieniec", "Kapelanka", "Krótka", "Miła", "Kościelna", "Królewska",
                                  "Na Wzgórzu", "Nad Torem", "Modrzewiowa", "Młyńska", "Różana", "Adama Mickiewicza",
                                  "Brzeg", "Jodłowa", "Kalwaryjska", "Garcowiec", "Górki"],
            "Zelczyna": ["Szkolna", "Wspólna", "Krakowska", "Dworska", "Lawendowa", "Leśna", "Kwiatowa", "Nowa",
                         "Nasza", "Podgórska", "Pasternik", "Spacerowa", "Solarna", "Widokowa", "Spokojna", "Krótka",
                         "Działowa"]
        },
        "gmina_liszki": {
            "Baczyn": [],
            "Budzyń": [],
            "Cholerzyn": [],
            "Chrosna": [],
            "Czułów": [],
            "Jeziorzany": [],
            "Kaszów": ["Zarzecze", "Pod Lasem", "Kasztanowa", "Krokusowa", "Słodka", "Akacjowa", "Nowa", "Św. Józefa",
                       "Bajeczna", "Na Gawinki", "Liliowa", "Wiśniowa", "Zielony Zakątek", "Willowa", "Rogatka",
                       "Potok", "Zakole", "Wiosenna", "Miodowa", "Fiołkowa", "Kręta", "Na Skarpie", "Kalinowa",
                       "Brzozowa", "Szmaragdowa", "Górka", "Aleja Kaszowska", "Babiorka", "Śląska", "Wadowicka",
                       "Malinowa"],
            "Kryspinów": ["Leśna", "Bielańska", "Kryspina Żeleńskiego", "Na Groblach", "Żabiniec", "Zaolsze", "Za Górą",
                          "Wspólna", "Wrzosowa", "Widokowa", "Wesoła", "Wenecka", "Wąska", "Urocza", "Św. Floriana",
                          "Sportowa", "Sosnowa", "Sojąka", "Różana", "rondo Jana Skirlińskiego", "Radosna",
                          "Przemysłowa", "Polnych Maków", "Pod Skałą", "Pod Borem", "Osiedlowa", "Ogrodowa",
                          "Nad Zalew", "Modrzewiowa", "Magnoliowa", "Łąkowa", "Lawendowa", "Krzywa", "Krótka",
                          "Krakowiaków", "Kąty", "Kamienna", "Jaśminowa", "Długa", "Dębowe Zacisze", "Cichy Kącik",
                          "Chabrowa", "Buki", "Boczna", "Błonia", "Balicka", "Prosta"],
            "Liszki": ["Św. Jana Pawła II", "Za Kościołem", "Polna", "Szkolna", "Rynek", "Maciejówka",
                       "Księdza Baścika", "Siostry Faustyny", "Ks. Jana Sali", "Garncarska", "Kaszowska", "Stroma",
                       "Krakowska", "Mały Rynek", "Spacerowa", "Św. Mikołaja", "Zielna", "Studzienki", "Słoneczna",
                       "Wołowska", "Na Borach", "Polnych Kwiatów", "Czernichowska", "Oświęcimska",
                       "Rondo Krzyża Świętego", "Św. Jana Kantego", "Kazimierza Wielkiego", "Spokojna", "Tyniecka",
                       "Dworska", "Zawiła", "Lisiecka", "Felicjanek", "Mazurowa", "Parkowa", "Poległych 1943 roku"],
            "Mników": [],
            "Morawica": [],
            "Piekary": [],
            "Rączna": [],
            "Ściejowice": []
        },
        "gmina_czernichów":{
            "Czernichów": [],
            "Czułówek": [],
            "Dąbrowa Szlachecka": [],
            "Kamień": [],
            "Kłokoczyn": [],
            "Nowa Wieś Szlachecka": [],
            "Przeginia Duchowna": [],
            "Przeginia Narodowa": [],
            "Rusocice": [],
            "Rybna": [],
            "Wołowice": [],
            "Zagacie": []
        },
        "gmina_mogilany": {
            "Brzyczyna": ["Widokowa", "Jana Pawła II", "Nad Rzepnikiem", "Nad Jarem", "Modrzewiowa", "Złota",
                          "Słoneczna", "Magnoliowa", "Dębowa", "Zacisze", "Spokojna", "Promienna", "Maleniec",
                          "Mirkówki", "Lipowa", "Polna", "Zielone Wzgórze", "Spacerowa"],
            "Buków": ["Gęsi Rynek", "Akacjowa", "Polna", "Zachodnia", "Pogodna", "Wodna", "Radziszowska", "Ludwiki",
                      "Krótka", "Górska", "Cedrowa", "Bajkowa", "Urocza", "Graniczna", "Orzechowa", "Jesionowa",
                      "Kamionna", "Zacisze", "Sarnia", "Zawiła", "Boczna", "Braterska", "Brzozowa", "Ogrodowa",
                      "Gościnna", "Lawendowa", "Szkolna", "Bukowska", "Babiogórska", "Jasna", "Długa"],
            "Chorowice": ["Widokowa", "Bukowska", "Łąkowa", "Zacisze", "Tarnowiec", "Spacerowa", "Sosnowa", "Sadowa",
                          "Podedworze", "Palmowa", "Lipowa", "Leśna", "Krajobrazowa", "Grądy", "Dębina", "Dąbrowy",
                          "Dworska", "Adama Doboszyńskiego", "Porzeczkowa"],
            "Gaj": ["Widokowa", "Słoneczna", "Spadzista", "Gilówka", "Wąska", "Brzezinka", "Lipowa", "Księżówka",
                    "Wzgórze", "Zgody", "Szkolna", "Kotarbówki", "Akacjowa", "Nowa", "Pod Górą", "Kwiatowa", "Sosnowa",
                    "Rudawa", "Wąwozowa", "Parkowa", "Klimkówka", "Polna", "Latochówki", "Zalesie",
                    "gen. Józefa Bema", "Maryjna", "Cicha", "Gaik", "Zadziele", "Myślenicka", "Grzmiąca", "Łąkowa",
                    "Wesoła", "Pogórze"],
            "Konary": ["Św. Floriana", "Bł. Anieli Salawy", "Sieprawska", "Świątnicka", "Zielona", "Wrzosowa",
                       "Willowa", "Wesoła", "Urocza", "Słoneczna", "Szkolna", "Stroma", "Sosnowa", "Nad Potokiem",
                       "Na Zieleńskie", "Na Skale", "Miodowa", "Malinowa", "Lipowa", "Leśna", "Kopań", "Konarska",
                       "Kamieniec", "Kalinowa", "Krakowska", "Królowej Polski", "Dworska", "Bonifraterska", "Kwiatowa",
                       "Górska", "Gubałówka", "Gołębia", "Gajowa"],
            "Kulerzów": ["Widokowa", "Św. Rozalii", "Dąbrowa", "Miodowa", "Rymarska", "Graniczna", "Źródlana",
                         "Kalinowa", "Na Wzgórzu", "Na Szlaku", "Św. Jana Pawła II"],
            "Libertów": ["Św. Brata Alberta", "Gajowa Łąka", "Szlachecka", "Widokowa", "Gwiezdna", "Południowa",
                         "Zagajnik", "Leśny Stok", "Spacerowiczów", "Sportowców", "Pogórze", "Magnoliowa", "Ligustrowa",
                         "Wesoła", "Przylesie", "Słoneczna", "Świetlista", "Korczynowa", "Rumiana", "Zgodna",
                         "Jabłoniowa", "Srebrna", "Borowa", "Przydworska", "Góra Libertowska", "Płomienna", "Bartnicka",
                         "Jana Pawła II", "Olszyńska", "Św. Floriana"],
            "Lusina": ["Źródlana", "Kościelna", "Stroma", "Wrzosowa", "Polna", "Górska", "Krótka", "Kwiatowa",
                       "Nad Wilgą", "Krakowska", "Spacerowa", "Przymiarki", "Zdrojowa", "Brzegi", "Świetlista",
                       "Św. Floriana", "Łąkowa", "Leśny Stok"],
            "Mogilany": ["Zakopiańska", "Krótka", "Skawińska", "Kwiatowa", "Podgórska", "Akacjowa", "Krakowska",
                         "Rzemieślnicza", "Oskara Kolberga", "Dębowa", "Sportowa", "Leszka Białego", "Jaśminowa",
                         "Wesoła", "Żary", "Wschodnia", "Podedworze", "Górska", "Cegielniana", "Parkowa",
                         "Ks. Józefa Mazurka", "Skrzyszów", "Lipowa", "Brzozowa", "Rzymska", "Leśna", "Leszczynowa",
                         "Kolorowa", "Nowa", "Grodzka", "Klonowa", "Osiedlowa", "Południowa", "Stroma", "Spokojna",
                         "Spacerowa", "Celiny", "Mogilańska", "Cicha", "Słowiańska", "Bukowa", "Ogrodowa", "Szkolna",
                         "Magnoliowa", "Zagórska", "Widokowa", "Słoneczna", "Markoszów", "Łobzowska", "Świątnicka",
                         "Myślenicka", "Jaworowa", "Św. Bartłomieja Apostoła", "Działy"],
            "Włosań": ["Św. Józefa", "Spacerowa", "Św. Rity", "Uzdrowiskowa", "Podlas", "Świątnicka", "Zamkowa",
                       "Wspólna", "Kamienna", "Leśna", "Sportowa", "Działkowa", "Brzozowa", "Kąty", "Spokojna",
                       "Bajeczna", "Królowej Polski", "Miodowa", "Słoneczna", "Krótka", "Łobzowska", "Kampinos",
                       "Leśników", "Rzeczna", "Św. Antoniego", "Widokowa", "Firmowa", "Zielony Stok", "Lipowa",
                       "Stolarska", "Chmielnik", "Stroma", "Gajowa", "Czarnoleska"]
        }
    },
    "powiat_myślenicki": {
        "gmina_myślenice": {
            "Głogoczów": []
        }
    }
}


def sprawdz_polozenie(nazwa, gmina, powiat):
    """
    Sprawdza, czy podana nazwa jest nazwą miejscowości w danej gminie, czy ulicą w mieście-siedzibie gminy.
    Akceptuje nazwy w ich naturalnej formie (np. "Wielkie Drogi").

    Args:
        nazwa: Nazwa do sprawdzenia (ulica lub miejscowość).
        gmina: Nazwa gminy.
        powiat: Nazwa powiatu.

    Returns:
        "Miejscowość" jeśli nazwa jest miejscowością w danej gminie.
        "Ulica" jeśli nazwa jest ulicą w mieście-siedzibie gminy.
        None w przeciwnym przypadku.
    """
    try:
        powiat_str = "powiat_" + powiat.lower()
        gmina_str = "gmina_" + gmina.lower()
        gmina_data = dane_adresowe[powiat_str][gmina_str]

        # Sprawdzenie, czy nazwa (po przekształceniu na małe litery i usunięciu spacji) jest kluczem (miejscowością) w słowniku gminy
        nazwa_przetworzona = nazwa.replace(" ", "_")  # Przetwarzanie nazwy do porównania z kluczami
        if nazwa_przetworzona in gmina_data:
            return "Miejscowość"
        else:
            # miasto_siedziba = list(gmina_data.keys())[0]
            for ulica in gmina_data[gmina]:  # Iterujemy po ulicach w miescie siedzibie
                if nazwa.lower() == ulica.lower():  # Porównujemy nazwy ulic bez względu na wielkość liter
                    return "Ulica"
            return None  # Ani miejscowość, ani ulica

    except KeyError:
        return None


def get_description(detailed_page):
    desc = detailed_page.select_one('div.estate-desc-more')
    if desc is not None:
        description = desc.getText().strip()
    else:
        description = detailed_page.select_one('div.box-offer-custom-desc').getText().strip()
    # print("DESCRIPTION: " + description)
    return description


def get_price(detailed_page):
    price_temp = detailed_page.select_one('p.info-primary-price')
    if price_temp is not None:
        price = price_temp.getText().replace("zł", "").replace(" ", "").replace(" ","").strip()
        # print("PRICE: " + price)
        return float(price)
    else:
        return None



#TODO getting all images
def get_images_urls(detailed_page):
    temp_img_urls = []
    imgs = detailed_page.select('ul.box-gallery li img')
    for img in imgs:
        img_url = img['src']
        temp_img_urls.append(img_url)
    return temp_img_urls


def get_parcel_type(detailed_page):
    all_attributes = detailed_page.select("div.box__attributes--content")
    for attribute in all_attributes:
        if attribute.getText().__contains__("Rodzaj działki:"):
            parcel_type = attribute.getText().replace("Rodzaj działki:", "").replace(" ", "").strip()
            #        print("TYPE: " + parcel_type)
            return parcel_type


def get_area(detailed_page):
    area = detailed_page.select_one('li.info-area').getText().replace("m²", "").replace(" ", "").replace(",",
                                                                                                         ".").replace(
        " ", "").strip()
    #print("AREA: " + area)
    return area


def get_location(detailed_page):
    location = detailed_page.select_one('p.province span.margin-right4').getText().strip()
    # print("LOCATION: " + location)
    return location


def get_type_of_contract(detailed_page):
    contractType_temp = detailed_page.select_one('div.box-offer-prov-excl p.excl')
    if contractType_temp is not None:
        return "na wyłączność"
    else:
        return "zwykła"


def get_modified_at(detailed_page):
    all_attributes = detailed_page.select("ul.list-h li")
    for attribute in all_attributes:
        if attribute.getText().__contains__("Źródło:"):
            last_modified_temp = attribute.select_one('li span').getText().split(',')[1].replace("zaktualizowane:",
                                                                                                 "").strip()
            return datetime.strptime(last_modified_temp, "%d.%m.%Y").timestamp()


def get_next_page_url(soup):
    try:
        return soup.select_one(get_pagination_next_page_btn()).get('href')
    except Exception:
        return None


class NieruchomosciOnline:

    def __init__(self, data_type, action, city, distance):
        self.__data_type = data_type
        self.__action = action
        self.__city = city
        self.__distance = distance

    def get_search_url(self, location):
        if self.__data_type == 'lots':
            return get_search_lots_url(location, self.__action, self.__distance)
        elif self.__data_type == 'houses':
            return get_search_houses_url(location, self.__action, self.__distance)
        elif self.__data_type == 'flats':
            return get_search_flats_url(location, self.__action, self.__distance)

    def get_results_records(self, soup):
        links = []

        while True:
            for link in soup.select(get_results_records_css()):
                url = self.get_url(link)
                links.append(url)

            npu = get_next_page_url(soup)
            if npu:
                page = requests.get(npu, headers=headers)
                soup = BeautifulSoup(page.content, 'html.parser')
                print("Next Page Url requested: " + npu)
            else:
                break
        return links

    def get_data_for_update_check(self, detailed_page):
        price = get_price(detailed_page)
        description = get_description(detailed_page)
        return price, description

    @staticmethod
    def get_url(link):
        basic_url = link.select_one('a').get('href')
        print("URL: " + basic_url)
        return basic_url

    def get_property_data(self, detailed_page):
        district = None
        commune = ""
        place = ""
        place_district = ""
        street = ""
        description = ""
        area = None
        type_of_contract = get_type_of_contract(detailed_page)
        source_created_at = None
        source_updated_at = None
        number_of_views = None
        number_of_raises = None
        images_urls = get_images_urls(detailed_page)
        price = get_price(detailed_page)
        district, commune, place, place_district, street = get_detailed_locations(detailed_page)
        location_type = ''
        description = get_description(detailed_page)
        area = get_area(detailed_page)
        source_created_at = None
        source_updated_at = get_modified_at(detailed_page)
        return price, district, commune, place, place_district, street, location_type, description, area, type_of_contract, source_created_at, source_updated_at, number_of_views, number_of_raises, images_urls

    def get_publisher_data(self, details_page):
        publisher_type = ''
        company = ''
        all_attributes = details_page.select("ul.list-h li")
        for attribute in all_attributes:
            if attribute.getText().__contains__("Źródło:"):
                if attribute.getText().__contains__("biuro"):
                    publisher_type = "agencja"
                    company = attribute.getText().split(':')[2].split(',')[0].strip()
                else:
                    publisher_type = "osoba prywatna"
                    company = ''
        publisher_name = details_page.select_one('p.name').getText()
        # print("PUBLISHER_NAME: " + publisher)
        phone = details_page.select_one('div.phone-wrapper.full p.phone.first').getText()
        # print("PHONE_NUM: " + phone)
        address = None
        return publisher_type, publisher_name, phone, company, address

    def get_lot_type(self, details_page):
        all_attributes = details_page.select("div.box__attributes--content")
        for attribute in all_attributes:
            if attribute.getText().__contains__("Rodzaj działki:"):
                parcel_type = attribute.getText().replace("Rodzaj działki:", "").replace(" ", "").strip()
                print("TYPE: " + parcel_type)
                return parcel_type

    def get_utilities_data(self, details_page):
        gas = ""
        water = ""
        sewerage = ""
        electricity = ""
        telco = ""
        road_access = ""
        fence = ""
        shape = ""
        dimensions = ""

        all_attributes = details_page.select("div.box-offer-inside ul li")
        for attribute in all_attributes:
            if attribute.getText().__contains__("Dojazd:"):
                road_access = attribute.getText().replace("Dojazd:", "").strip()
                print("Droga: " + road_access)

            if attribute.getText().__contains__("Media:"):
                media_list = attribute.getText()
                if media_list.__contains__("gaz"):
                    gas = "tak"
                if media_list.__contains__("prąd"):
                    electricity = "tak"
                if media_list.__contains__("woda"):
                    water = "tak"
                if media_list.__contains__("kanalizacja") or media_list.__contains__("odprowadzanie ścieków"):
                    sewerage = "tak"

        all_attributes = details_page.select("ul.list-h li")
        for attribute in all_attributes:
            if attribute.getText().__contains__("ogrodzenie częściowe"):
                fence = "częściowo"
            if attribute.getText().__contains__("działka ogrodzona") or attribute.getText().__contains__("ogrodzenie całkowite"):
                fence = "tak"
            if attribute.getText().__contains__("działka nieogrodzona"):
                fence = "nie"
            if attribute.getText().__contains__("kształt:"):
                tekst = attribute.getText()
                match_shape = re.search(r"kształt:\s*(\w+)", tekst)
                if match_shape:
                    shape = match_shape.group(1)
            if attribute.getText().__contains__("Internet"):
                telco = "tak"
            if attribute.getText().__contains__("długość:"):
                tekst = attribute.getText()
                dlugosc = ""
                szerokosc = ""
                match_dlugosc = re.search(r"długość:\s*(\d+)m", tekst)
                if match_dlugosc:
                    dlugosc = match_dlugosc.group(1)

                # Wyszukiwanie szerokości
                match_szerokosc = re.search(r"szerokość:\s*(\d+)m", tekst)
                if match_szerokosc:
                    szerokosc = match_szerokosc.group(1)

                dimensions = dlugosc + "x" + szerokosc
        return road_access, fence, electricity, water, gas, sewerage, telco, shape, dimensions


    def get_flat_details(self, detailed_page):
        number_of_rooms = ""
        building_material = ""
        building_year = ""
        heating = ""
        market_type = ""
        condition_of_the_flat = ""
        floor = ""
        number_of_floors = ""
        number_of_bedrooms = ""
        number_of_bathrooms = None
        type_of_kitchen = ""
        toilet_together_with_bathroom = None
        balcony = None
        basement = None
        window_joinery = ""
        lift = None
        garage = None
        terrace = None
        parking = None
        garden = None

        all_attributes = detailed_page.select("div.box__attributes--content")
        for attibute in all_attributes:
            if attibute.getText().__contains__("Termin realizacji:"):
                building_year = attibute.getText().replace("Termin realizacji:", "").strip()

            if attibute.getText().__contains__("Liczba pokoi:"):
                number_of_rooms = attibute.getText().replace("Liczba pokoi:", "").strip()
                number_of_bedrooms = int(number_of_rooms) -1

            if attibute.getText().__contains__("Piętro:"):
                floor_temp = attibute.getText().replace("Piętro:", "").strip()
                floor_t = floor_temp.split('/')[0]
                if  floor_t.__contains__("parter"):
                    floor = 0
                else:
                    try:
                        floor = int(floor_t)
                    except ValueError:
                        floor = None
                try:
                    number_of_floors = floor_temp.split('/')[1]
                except IndexError:
                    number_of_floors = None

            if attibute.getText().__contains__("Stan mieszkania:"):
                condition_of_the_flat = attibute.getText().replace("Stan mieszkania:", "").strip()

        all_details = detailed_page.select("div.box-offer-inside ul li")
        for detail in all_details:
            if detail.getText().__contains__("Rynek:"):
                market_type = detail.getText().replace("Rynek:", "").strip()

            if detail.getText().__contains__("Charakterystyka mieszkania:"):
                building_characteristic_temp = detail.getText().replace("Charakterystyka mieszkania:", "").strip()
                building_characteristic = building_characteristic_temp.split(',')
                for tekst in building_characteristic:
                    match_bathrooom_count = re.search(r", \s*(\d+) łazien", tekst)
                    if match_bathrooom_count:
                        number_of_bathrooms = int(match_bathrooom_count.group(1))

            if detail.getText().__contains__("Kuchnia:"):
                type_of_kitchen = detail.getText().replace("Kuchnia:", "").strip()

            if detail.getText().__contains__("Powierzchnia dodatkowa:"):
                additional_area_temp = detail.getText().replace("Powierzchnia dodatkowa:", "").strip()
                if additional_area_temp.__contains__("balkon"):
                    balcony = True
                if additional_area_temp.__contains__("ogródek"):
                    garden = True
                if additional_area_temp.__contains__("taras"):
                    terrace = True
                if additional_area_temp.__contains__("piwnica"):
                    basement = True

            if detail.getText().__contains__("Miejsce/a postojowe"):
                parking_temp = detail.getText().replace("Miejsce/a postojowe", "").strip()
                if parking_temp.__contains__("naziemne"):
                    parking = True


        return market_type, condition_of_the_flat, floor, number_of_floors, number_of_rooms, number_of_bedrooms, number_of_bathrooms, type_of_kitchen, toilet_together_with_bathroom, balcony, window_joinery, building_year, building_material, heating, lift, garage, terrace, parking, basement, garden

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


        all_attributes = detailed_page.select("div.box__attributes--content")
        for attibute in all_attributes:
            if attibute.getText().__contains__("Rodzaj domu:"):
                house_type = attibute.getText().replace("Rodzaj domu:", "").strip()

            if attibute.getText().__contains__("Liczba pokoi:"):
                number_of_rooms = attibute.getText().replace("Liczba pokoi:", "").strip()
                number_of_bedrooms = int(number_of_rooms) -1

            if attibute.getText().__contains__("Powierzchnia działki:"):
                lot_area_temp = attibute.getText().replace("Powierzchnia działki:", "").replace(" m²", "").replace(" ", "").strip()
                if lot_area_temp != '-' and lot_area_temp is not None:
                    lot_area = float(lot_area_temp)

            if attibute.getText().__contains__("Miejsce postojowe"):
                parking_temp = attibute.getText().replace("Miejsce postojowe:", "").strip()
                if parking_temp.__contains__("naziemne") or parking_temp.__contains__("tak"):
                    parking = True
                if parking_temp.__contains__("garaż"):
                    garage = True

            if attibute.getText().__contains__("Rok budowy:"):
                building_year = attibute.getText().replace("Rok budowy:", "").strip()

        all_details = detailed_page.select("div.box-offer-inside ul li")
        for detail in all_details:
            if detail.getText().__contains__("Rynek:"):
                market_type = detail.getText().replace("Rynek:", "").strip()

            if detail.getText().__contains__("Forma własności:"):
                ownership_form = detail.getText().replace("Forma własności:", "").strip()

            if detail.getText().__contains__("Charakterystyka domu"):
                building_characteristic_temp = detail.getText().replace("Charakterystyka domu", "").strip()
                building_characteristic = building_characteristic_temp.split(',')
                for tekst in building_characteristic:
                    match_bathrooom_count = re.search(r", \s*(\d+) łazien", tekst)
                    if match_bathrooom_count:
                        number_of_bathrooms = int(match_bathrooom_count.group(1))

                    match_usable_area = re.search(r", \s*(\d+) m² powierzchni użytkowej", tekst)
                    if match_usable_area:
                        usable_area = float(match_usable_area.group(1))
                    else:
                        match_usable_area_2 = re.search(r", \s*(\d+) m²", tekst)
                        if match_usable_area_2:
                            usable_area = float(match_usable_area_2.group(1))

            detail_text = detail.getText()
            match_roof = re.search(r"pokrycie dachu:(.*)", detail_text)
            if match_roof:
                roof = match_roof.group(1)

            match_window_joinery = re.search(r"okna:(.*)", detail_text)
            if match_window_joinery:
                window_joinery = match_window_joinery.group(1)

            match_building_material = re.search(r"materiał budowy:(.*)", detail_text)
            if match_building_material:
                building_material = match_building_material.group(1)

            if detail.getText().__contains__("Kuchnia:"):
                type_of_kitchen = detail.getText().replace("Kuchnia:", "").strip()

            if detail.getText().__contains__("Powierzchnia dodatkowa:"):
                additional_area_temp = detail.getText().replace("Powierzchnia dodatkowa:", "").strip()
                if additional_area_temp.__contains__("balkon"):
                    balcony = True
                if additional_area_temp.__contains__("ogródek"):
                    garden = True
                if additional_area_temp.__contains__("taras"):
                    terrace = True
                if additional_area_temp.__contains__("piwnica"):
                    basement = True


        return market_type, condition_of_the_building, building_year, building_material, heating, house_type, usable_area, number_of_bedrooms, type_of_kitchen, number_of_bathrooms, toilet_together_with_bathroom, balcony, terrace, roof, window_joinery, lot_area, ownership_form, garage
