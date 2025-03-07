from time import sleep

from kw.control_digit_counter import count_control_digit
from datetime import datetime
from utils import get_index_from_kw_code
import db
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

opt = webdriver.FirefoxOptions()
opt.add_argument('-headless')
driver = webdriver.Firefox(options=opt)

start_value = get_index_from_kw_code(db.get_last_record_value("KR1K")) + 1


i = start_value
driver = webdriver.Firefox()
while i < start_value + 50 and start_value < 45000:
    if i % 6 == 0:
        if driver is not None:
            driver.close()
        print("SLEEPING")
        #sleep(180)
        driver = webdriver.Firefox()
    data = {}
    hipoteka = {}
    roszczenia = {}
    prop_id = "{:08d}".format(i)
    prop_district_code = "KR1K"
    control_number = count_control_digit(prop_district_code, prop_id)
    driver.get(r"https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "kodWydzialuInput"))).click()
    driver.find_element(By.ID, "kodWydzialuInput").send_keys(prop_district_code)
    driver.find_element(By.ID, "kodWydzialuInput").send_keys(Keys.ENTER)
    driver.find_element(By.ID, "numerKsiegiWieczystej").click()
    driver.find_element(By.ID, "numerKsiegiWieczystej").send_keys(prop_id)
    driver.find_element(By.ID, "cyfraKontrolna").click()
    driver.find_element(By.ID, "cyfraKontrolna").send_keys(control_number)
    data['kw_district_code'] = prop_district_code
    data['kw_id'] = prop_district_code + "/" + prop_id + "/" + str(control_number)
    try:
        driver.find_element(By.ID, "wyszukaj").click()
        location = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, '//div[./label[contains(text(),"Położenie")]]/following-sibling::div'))).text
        owner = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,
                                                                               '//div[./label[contains(text()," Właściciel / użytkownik wieczysty / uprawniony ")]]/following-sibling::div'))).text
        kw_type_text = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, '//div[./label[contains(text()," Typ księgi wieczystej ")]]/following-sibling::div'))).text

        data['kw_type'] = kw_type_text
        data['locality'] = location.split(',')[-1].strip()
        data['full_locality'] = location
        data['owners'] = owner.split('\n')
        data['creation_date'] = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,
                                                                                               '//div[./label[contains(text(),"Data zapisania księgi wieczystej")]]/following-sibling::div'))).text
        data_zamknięcia = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,
                                                                                               '//div[./label[contains(text(),"Data zamknięcia księgi wieczystej")]]/following-sibling::div'))).text
        if data_zamknięcia != '---':
            data['closing_date'] = data_zamknięcia
            data['status'] = 'CLOSED'

        if kw_type_text.strip() == 'NIERUCHOMOŚĆ GRUNTOWA':
            data['kw_type'] = 'NIERUCHOMOŚĆ GRUNTOWA'
            try:
                wydrukZupelnyBtn = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "przyciskWydrukZupelny")))
                driver.execute_script("arguments[0].scrollIntoView();", wydrukZupelnyBtn)
                wydrukZupelnyBtn.click()

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@value,'Dział I-O')]"))).click()

                # odpisWzmiankiTbl = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//table[contains(@class,'tbOdpis') and ./tbody/tr/td[contains(text(),'Wzmianki w dziale I-O')]]")))
                # data["oznaczenie_wzmianki"] = odpisWzmiankiTbl.find_element(By.CLASS_NAME, "csCDane").text

                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH,
                                                                               '//td[contains(text(),"Numer działki")]/following-sibling::td[contains(@class,"csDane")]')))
                elements = driver.find_elements(By.XPATH,
                                                '//td[contains(text(),"Numer działki")]/following-sibling::td[contains(@class,"csDane")][3]')
                plot_id_list = []
                for element in elements:
                    if element.text != '---':
                        plot_id_list.append(element.text)
                plot_ids = ", ".join(plot_id_list)
                data['plots'] = plot_id_list

                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//tr[./td[contains(text(),'Identyfikator działki')]]/td[contains(@colspan,'35') and contains(@class,'csDane')]")))
                plot_full_id_elements = driver.find_elements(By.XPATH, "//tr[./td[contains(text(),'Identyfikator działki')]]/td[contains(@colspan,'35') and contains(@class,'csDane')]")

                plot_full_id_list = []
                for full_id_element in plot_full_id_elements:
                    if full_id_element.text != '---':
                        plot_full_id_list.append(full_id_element.text)
                plot_full_ids = ", ".join(plot_full_id_list)
                data['plot_full_ids'] = plot_full_id_list

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@value,'Dział III')]"))).click()

                try:
                    roszczenia_text = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//table[./tbody/tr/td[contains(text(),'DZIAŁ III - PRAWA, ROSZCZENIA I OGRANICZENIA')]]/tbody/tr/td[contains(@class,'csBCDane')]"))).text

                    # if roszczenia_text != 'BRAK WPISÓW':
                    #     data['roszczenia'] = 'SPRAWDŹ'
                except TimeoutException as ex:
                    data['roszczenia'] = 'SPRAWDŹ'
                    print(prop_district_code + "/" + str(prop_id) + "/" + str(control_number) + ";" + location + "; ROSZCZENIA do sprawdzenia")

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@value,'Dział IV')]"))).click()

                try:
                    hipoteka_text = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//table[./tbody/tr/td[contains(text(),'DZIAŁ IV - HIPOTEKA')]]/tbody/tr/td[contains(@class,'csBCDane')]"))).text

                    #if hipoteka_text != 'BRAK WPISÓW':

                except TimeoutException as ex:
                    rodzaj_hipoteki_text = WebDriverWait(driver, 5).until(
                        "//table[contains(@class,'tbOdpis')]//tr[./td[contains(text(),'Rodzaj hipoteki')]]/td[contains(@class,'csDane')][3]").text
                    suma_hipoteki_text = WebDriverWait(driver, 5).until(
                        "//table[contains(@class,'tbOdpis')]//tr[./td[contains(text(),'Suma')]]/td[contains(@class,'csDane')][3]").text
                    wierzytelnosc_text = WebDriverWait(driver, 5).until(
                        "//table[contains(@class,'tbOdpis')]//tr[./td[contains(text(),'Oznaczenie wierzytelności i stosunku prawnego')]]/following-sibling::tr[1]/td[5]").text
                    stosunek_prawny_text = WebDriverWait(driver, 5).until(
                        "//table[contains(@class,'tbOdpis')]//tr[./td[contains(text(),'Oznaczenie wierzytelności i stosunku prawnego')]]/following-sibling::tr[2]/td[5]").text
                    hipoteka['rodzaj_hipoteki'] = rodzaj_hipoteki_text
                    hipoteka['suma'] = suma_hipoteki_text
                    hipoteka['wierzytelnosc'] = wierzytelnosc_text
                    hipoteka['stosunek_prawny'] = stosunek_prawny_text
                    data['hipoteka'] = hipoteka

                    print(prop_district_code + "/" + str(prop_id) + "/" + str(
                        control_number) + ";" + location + "; ERROR - HIPOTEKA")

                data['status'] = 'ACTIVE'

                print(prop_district_code + "/" + str(prop_id) + "/" + str(
                    control_number) + ";" + location + ";" + plot_ids + ";" + " OWN: " + owner.replace('\n', ",") + " ROSZCZENIA: " + roszczenia_text + " \nHIPOTEKA: " + hipoteka_text)
            except TimeoutException as ex:
                print(prop_district_code + "/" + str(prop_id) + "/" + str(
                    control_number) + ";" + location + "; ERROR")
        else:
            data['kw_type'] = kw_type_text
            data['status'] = 'ACTIVE'
            #print(prop_district_code + "/" + str(prop_id) + "/" + str(control_number) + " KW TYPE: " + kw_type_text + ";" + " OWN: " + owner.replace('\n', ","))
        # print(prop_district_code+ "/" + str(prop_id) + "/" + str(control_number) + " LOC: " + location + " OWN: " + owner.replace('\n', ","))
    except TimeoutException as ex:
        print(prop_district_code + "/" + str(prop_id) + "/" + str(control_number) + "; NOT_FOUND")
        data['status'] = 'NOT_FOUND'
    data['timestamp'] = datetime.now()
    db.add(data)
    i += 1
driver.close()
