from abc import abstractmethod

class Searchable():
    @abstractmethod
    def get_search_lots_url(self, location):
        pass

    @abstractmethod
    def get_search_houses_url(self, location):
        pass

    @abstractmethod
    def get_search_flats_url(self, location):
        pass

    @abstractmethod
    def get_landing_page_url(self):
        pass

    @abstractmethod
    def get_url(link):
        pass

    @abstractmethod
    def get_publisher_data(self, detailed_page):
        pass

    @abstractmethod
    def get_url(link):
        pass
    @abstractmethod
    def get_next_page_url(soup):
        pass

    @abstractmethod
    def get_location(link):
        pass

    @abstractmethod
    def get_area(details_page_soup):
        pass

    @abstractmethod
    def get_parcel_type(link):
        pass

    @abstractmethod
    def get_description(detailed_page):
        pass

    @abstractmethod
    def get_price(link):
        pass

    @abstractmethod
    def get_images_urls(page):
        pass