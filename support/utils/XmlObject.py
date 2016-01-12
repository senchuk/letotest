import xml.etree.ElementTree as ET

__author__ = 'EIvonin'


class XmlObject:
    """
    Object for working with xml
    """
    def __init__(self, file_url):
        self.file_url = file_url
        self.xml_date = ''
        self.offers = []
        self.categories = []
        self.process_xml()

    def process_xml(self):
        tree = ET.parse(self.file_url)
        root = tree.getroot()

        self.xml_date = self.__get_date_from_xml(root)
        self.offers = self.__get_offers_list_from_xml(root)
        self.categories = self.__get_categories_list_from_xml(root)

    def __get_date_from_xml(self, root):
        return root.attrib['date']

    def __get_offers_list_from_xml(self, root):
        offers = []
        for offer in root.iter('offer'):
            offer_tmp = dict()
            offer_tmp['own_id'] = str(offer.attrib['id'])
            offer_tmp['available'] = offer.attrib['available']

            if offer.find('url') is not None:
                offer_tmp['url'] = offer.find('url').text

            if offer.find('delivery') is not None:
                offer_tmp['delivery'] = offer.find('delivery').text

            if offer.find('local_delivery_cost') is not None:
                offer_tmp['local_delivery_cost'] = offer.find('local_delivery_cost').text

            offer_tmp['price'] = offer.find('price').text
            offer_tmp['category_id'] = offer.find('categoryId').text

            if offer.find('pickup') is not None:
                offer_tmp['pickup'] = offer.find('pickup').text

            if offer.find('typePrefix') is not None:
                #TODO - Do it for many pictures in offer
                offer_tmp['picture'] = offer.find('picture').text

            if offer.find('typePrefix') is not None:
                offer_tmp['typePrefix'] = offer.find('typePrefix').text

            if offer.find('vendor') is not None:
                offer_tmp['vendor'] = offer.find('vendor').text

            if offer.find('model') is not None:
                offer_tmp['model'] = offer.find('model').text

            if offer.find('manufacturer_warranty') is not None:
                offer_tmp['manufacturer_warranty'] = offer.find('manufacturer_warranty').text

            if offer.find('currencyId') is not None:
                offer_tmp['currencyId'] = offer.find('currencyId').text

            if offer.find('description') is not None:
                offer_tmp['description'] = offer.find('description').text

            offers.append(offer_tmp)

        return offers

    def get_offers_list_by_own_id(self, own_id):
        result = []
        for offer in self.offers:
            if offer['own_id'] == own_id:
                result.append(offer)

        return result

    def get_offers_list_by_category_id(self, category_id):
        result = []
        for offer in self.offers:
            if offer['category_id'] == category_id:
                result.append(offer)

        return result

    def __get_categories_list_from_xml(self, root):
        categories = []
        for category in root.iter('category'):
            category_tmp = dict()
            category_tmp['id'] = category.attrib['id']

            if category.get('parentId') is not None:
                category_tmp['parent_id'] = category.attrib['parentId']

            category_tmp['category_name'] = category.text

            categories.append(category_tmp)

        return categories
