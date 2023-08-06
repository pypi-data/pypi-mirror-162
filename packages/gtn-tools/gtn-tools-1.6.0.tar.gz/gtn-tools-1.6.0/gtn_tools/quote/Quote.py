"""Quote class for automated quotes."""
import re
from typing import Any, Dict, List, Union
import json
import shopify
from gtn_tools.exceptions import QuoteException


class QuoteClass:
    """
    Class for automated quotes.

    Attributes:
    ----------
    price
    vat
    duration
    shopify_shop_url
    shopify_api_version
    shopify_password
    shopify_invoice_url
    shopify_draft_order_id
    shopify_customer_id
    shopify_line_item_id

    Methods:
    -------
    calculate_price: Calculate the price of an preprocessed document.
    create_draft_order: Create a new shopify draft order.
    init_quote: Initialize the Quote by running calculate_price and
    create_draft_order
    add_document: Add a new document as new line item.
    get_invoice_url: Returns the invoice url under which the order can be paid.
    add_certification: Add line item named 'Beglaubigung' to an existing order.
    load_shopify_order: Loads an existing shopify draft-order for editing.
    """
    def __init__(
        self,
        order_id: int,
        shop_url: str,
        api_version: str,
        password: str,
        vat_rate: float,
        porto: float,
        cert_net_amount: float,
        shopify_draft_order_id: str = None
    ) -> None:
        self.order_id = order_id
        self.vat_rate: float = vat_rate
        self.porto: float = porto
        self.cert_net_amount: float = cert_net_amount
        self.shopify_shop_url: str = shop_url
        self.shopify_api_version: str = api_version
        self.shopify_password: str = password
        self.net_amount: float = 0.0
        self.vat: float = 0.0
        self.duration: int = 0
        self.initialized: bool = False
        self.shopify_invoice_url: str = None
        self.shopify_draft_order_id: str = None
        self.shopify_customer_id: str = None
        self.shopify_line_item_id: str = None
        if shopify_draft_order_id:
            self.shopify_draft_order_id = shopify_draft_order_id
            self.initialized = True

    def __rep__(self):
        if self.price is not None:
            str(self.price)
        else:
            'price not yet calculated'

    def calculate_price(
        self,
        num_words: int,
        source_lang: str,
        target_langs: List[str],
        pricebook: str
    ) -> float:
        """
        Calculate the price of the document.

        Arguments:
        ---------
        num_words: The number of words to be translated
        source_lang: ISO 639-1 code of source language
        target_langs: A list of ISO 639-1 codes of target languages
        pricebook: The path to the json pricebook
        vat_rate: The current vat rate
        """
        for target_lang in target_langs:
            if source_lang == target_lang:
                raise QuoteException('Source language equals target language.')
            # skip if already read
            if not isinstance(pricebook, dict):
                with open(pricebook) as f:
                    prices = json.load(f)
                    pricebook = prices[str(source_lang)]
            threshold = pricebook[str(target_lang)]['threshold']
            word_price = pricebook[str(target_lang)]['price']
            duration = pricebook[str(target_lang)]['duration']
            price = (num_words * word_price
                     if num_words * word_price >= threshold
                     else threshold)

            # declare variables for entire quote
            self.net_amount += price
            self.vat = self.vat_rate*self.net_amount
            self.duration = (duration if duration > self.duration
                             else self.duration)

        return self.net_amount

    def create_draft_order(
        self,
        id: int,
        email: str,
        source_lang: str,
        target_langs: List[str],
        total_pages: int,
        postal: bool,
        certs: int = None
    ) -> None:
        """
        Create a shopify Draft Order.

        Arguments:
        ---------
        id: The order id
        email: The customer's email
        source_lang: ISO 639-1 code of source language
        target_langs: A list of ISO 639-1 codes of target languages
        filename: The name of the file or document that is added to the draft
        order.
        """
        gross_amount = self.net_amount + self.vat
        target_langs = ", ".join(target_langs)
        if self.initialized:
            raise QuoteException("Draft Order is already initialized")

        with shopify.Session.temp(self.shopify_shop_url,
                                  self.shopify_api_version,
                                  self.shopify_password):
            # create draft order
            do = shopify.DraftOrder()
            do.name = (f"AN-{id}: Übersetzung von {total_pages} Seite(n) "
                       f"{source_lang.upper()} - {target_langs.upper()}")
            # assign shopify_customer
            if len(shopify.Customer.find(email=email)) == 1:
                # if shopify_customer with this email address already
                # exists get him by id
                shopify_customer = shopify.Customer.find(email=email)[0]
            else:
                # create new shopify_customer
                shopify_customer = shopify.Customer()
                shopify_customer.email = email
                shopify_customer.save()
            do.customer = {"id": shopify_customer.id}
            do.email = str(email)
            # assign line items to the draft order
            do.line_items = [
                {
                    "title": str(do.name),
                    "price": float(gross_amount),
                    "taxable": True,
                    "quantity": 1,
                    "requires_shipping": postal
                }
            ]
            # add shipping to the shopify order
            if postal:
                do.shipping_line = {
                    "title": "Postversand",
                    "price": self.porto
                }
            if certs:
                do.line_items.append({
                    "title": ('Offizielle Beglaubigung'),
                    "price": (1 + self.vat_rate) * self.cert_net_amount,
                    "taxable": True,
                    "quantity": certs
                })
            # save draft order
            created = do.save()
            if created and shopify.DraftOrder().exists(do.id):
                do = shopify.DraftOrder().find(do.id)
                # save relevant info
                self.shopify_invoice_url = do.invoice_url
                self.shopify_draft_order_id = str(do.id)
                self.shopify_customer_id = str(shopify_customer.id)
                self.shopify_line_item_id = str(do.line_items[0].id)
                self.initialized = True
        return None

    def init_quote(
        self,
        num_words: int,
        source_lang: str,
        target_langs: List[str],
        email: str,
        pricebook: str,
        total_pages: int,
        postal: bool,
        certs: int = None
    ) -> None:
        """
        Pipeline for quote creation on shopify. Runs the `calculate_price`
        and `create_draft_order` methods.

        Arguments:
        ---------
        email: The customer's email
        filename: The name of the file or document that is added to the draft
        order.
        """
        price = self.calculate_price(num_words, source_lang, target_langs,
                                     pricebook)
        self.create_draft_order(self.order_id, email, source_lang,
                                target_langs, total_pages, postal, certs)
        return price

    def get_invoice_url(self) -> str:
        """
        Returns the invoice url under which the order can be paid
        """
        if self.shopify_invoice_url is None:
            raise QuoteException('Quote not initialized.'
                                 ' No Draft Order available')
        else:
            return self.shopify_invoice_url

    def add_certification(
        self,
        number: int
    ) -> None:
        """
        !! Deprecated - you may want to use update_draft_order instead
        Add line item named 'Beglaubigung' to an existing order.

        Arguments:
        ---------
        number: how many certifications should be added
        """
        line_items = [{
            "title": ('Offizielle Beglaubigung'),
            "price": (1 + self.vat_rate) * self.cert_net_amount,
            "taxable": True,
            "quantity": number
            }]
        with shopify.Session.temp(self.shopify_shop_url,
                                  self.shopify_api_version,
                                  self.shopify_password):
            if shopify.DraftOrder().exists(self.shopify_draft_order_id):
                do = shopify.DraftOrder().find(self.shopify_draft_order_id)
                do.line_items.extend(line_items)
                do.save()
        return None

    def get_draft_order(
        self,
        shopify_draft_order_id: str = None
    ) -> Dict[str, Union[str, float]]:
        """
        Return the existing draft order as dictionary.
        """
        if shopify_draft_order_id is not None:
            if self.shopify_draft_order_id is None:
                self.shopify_draft_order_id = shopify_draft_order_id
                self.initialized = True
            else:
                print(("WARNING: Order is already initialized, skipping "
                       "input draft_order_id."))

        with shopify.Session.temp(self.shopify_shop_url,
                                  self.shopify_api_version,
                                  self.shopify_password):
            if shopify.DraftOrder().exists(self.shopify_draft_order_id):
                do = shopify.DraftOrder().find(self.shopify_draft_order_id)
                shipping = do.shipping_line
                for line_item in do.line_items:
                    if "Übersetzung" in line_item.title:
                        translation_item = line_item
                    elif "Beglaubigung" in line_item.title:
                        certification_item = line_item

                result = {
                    "translation": None,
                    "certification": None,
                    "shipping": None
                }

                if shipping:
                    result['shipping'] = {
                        'title': shipping.title,
                        'price': float(shipping.price)
                    }
                try:
                    result['translation'] = {
                        "title": translation_item.title,
                        "price": float(translation_item.price),
                        "quantity": translation_item.quantity
                    }
                except UnboundLocalError:
                    # no translations
                    pass
                try:
                    result['certification'] = {
                        "title": certification_item.title,
                        "price": float(certification_item.price),
                        "quantity": certification_item.quantity
                    }
                except UnboundLocalError:
                    # no certifications
                    pass

                return result

            else:
                raise QuoteException("Draft order does not exist.")

    def set_draft_order(
        self,
        do_dict: dict
    ) -> bool:
        with shopify.Session.temp(self.shopify_shop_url,
                                  self.shopify_api_version,
                                  self.shopify_password):
            if shopify.DraftOrder().exists(self.shopify_draft_order_id):
                do = shopify.DraftOrder().find(self.shopify_draft_order_id)
                for i in range(len(do.line_items)):
                    if "Übersetzung" in do.line_items[i].title:
                        translation_index = i
                    elif "Beglaubigung" in do.line_items[i].title:
                        certification_index = i

                # set shipping line
                try:
                    do.shipping_line = do_dict['shipping']
                except KeyError:
                    do.shipping_line = None

                # set translation line item
                do.line_items[translation_index].title = \
                    do_dict['translation']['title']
                do.line_items[translation_index].quantity = \
                    do_dict['translation']['quantity']
                do.line_items[translation_index].price = \
                    do_dict['translation']['price']

                # set certification
                if do_dict['certification'] is not None:
                    try:
                        do.line_items[certification_index].title = \
                            do_dict['certification']['title']
                        do.line_items[certification_index].quantity = \
                            do_dict['certification']['quantity']
                        do.line_items[certification_index].price = \
                            do_dict['certification']['price']
                    except NameError:
                        # certification does not yet exist
                        do.line_items.append(do_dict['certification'])
                else:
                    # certification does exist and should be removed
                    try:
                        do.line_items[certification_index] = None
                    except NameError:
                        # certification does not exist and nothing should
                        # be changed
                        pass

                # save draft order
                created = do.save()
                if created and shopify.DraftOrder().exists(do.id):
                    do = shopify.DraftOrder().find(do.id)
                    # save relevant info
                    self.shopify_invoice_url = do.invoice_url
                    self.shopify_draft_order_id = str(do.id)
                    self.shopify_line_item_id = str(do.line_items[0].id)

                return created
            else:
                raise QuoteException("Draft order does not exist.")

    def update_draft_order(
        self,
        shipping: bool = None,
        net_amount: float = None,
        total_pages: int = None,
        languages: List[str] = None,
        certifications: int = None,
    ) -> Dict[str, Union[str, float]]:
        """
        Update an existing draft order.

        Arguments:
        ---------
        """

        with shopify.Session.temp(self.shopify_shop_url,
                                  self.shopify_api_version,
                                  self.shopify_password):
            if (not shopify.DraftOrder().exists(self.shopify_draft_order_id)
                    or self.shopify_draft_order_id is None):
                raise QuoteException("Draft order does not exist.")

            do_dict = self.get_draft_order()

            # update shipping
            if shipping is not None:
                do_dict = self.__update_shipping(shipping, do_dict)

            # update translation price
            if net_amount:
                do_dict = self.__update_price(net_amount, do_dict)

            # update translation title
            if total_pages:
                do_dict = self.__update_total_pages(total_pages, do_dict)
            if languages:
                do_dict = self.__update_languages(languages, do_dict)

            # update number of certifications
            if certifications is not None:
                do_dict = self.__update_certifications(certifications, do_dict)

            if self.set_draft_order(do_dict):
                return self.get_draft_order()
            else:
                raise QuoteException("Cloud not update draft order")

    def get_order(
        self,
        shopify_order_id: str
    ) -> shopify.Order:
        with shopify.Session.temp(self.shopify_shop_url,
                                  self.shopify_api_version,
                                  self.shopify_password):
            if shopify.Order().exists(shopify_order_id):
                return shopify.Order().find(shopify_order_id)

    def fulfill_order(
        self,
        shopify_order_id: str,
        notify_customer: bool = True,
    ) -> bool:
        """Fulfill order and mark it as payed.

        Args:
            shopify_order_id (str): id of the order to fulfill
            notify_customer (bool, optional): should shopify send an email to
            the customer. Defaults to True.

        Raises:
            QuoteException: Order already fulfilled.
            QuoteException: Order cannot be fulfilled.
            QuoteException: Draft order does not exist.

        Returns:
            bool: fulfillment successful
        """

        with shopify.Session.temp(self.shopify_shop_url,
                                  self.shopify_api_version,
                                  self.shopify_password):
            if shopify.Order().exists(shopify_order_id):
                fulfillment_order = shopify.FulfillmentOrders().find(
                    order_id=shopify_order_id)[0]
                actions = fulfillment_order.supported_actions
                if 'closed' in actions:
                    raise QuoteException('Order already fulfilled.')
                elif 'create_fulfillment' not in actions:
                    raise QuoteException('Order cannot be fulfilled.')
                else:
                    fulfillment = shopify.Fulfillment(attributes={
                        "order_id": fulfillment_order.order_id,
                        "notify_customer": notify_customer,
                        "location_id": shopify.Location().find()[0].id,
                        "line_items_by_fulfillment_order": [{
                            "fulfillment_order_id": fulfillment_order.id,
                            "fulfillment_order_line_items":
                                [{'id': item.id, 'quantity': item.quantity}
                                 for item in fulfillment_order.line_items]
                        }]
                    })
                    fulfillment_status = fulfillment.save()
                return fulfillment_status
            else:
                raise QuoteException("Draft order does not exist.")

    def __create_address(self, address: Dict[str, Any]) -> shopify.Address:
        a = shopify.Address()
        a.first_name = address['first_name']
        a.last_name = address['last_name']
        a.address1 = address['street1']
        if address.get('street2'):
            a.address2 = address['street2']
        a.country_code = address['country']
        a.zip = address['zip_code']
        a.city = address['city']

        return a

    def mark_as_payed(
        self,
        payment_amount: float,
        shipping_address: Dict[str, str],
        shopify_draft_order_id: str = None,
        billing_address: Dict[str, str] = None,
    ) -> bool:
        if shopify_draft_order_id is not None:
            if self.shopify_draft_order_id is None:
                self.shopify_draft_order_id = shopify_draft_order_id
                self.initialized = True
            else:
                print(("WARNING: Order is already initialized, skipping "
                       "input draft_order_id."))
        with shopify.Session.temp(self.shopify_shop_url,
                                  self.shopify_api_version,
                                  self.shopify_password):
            if shopify.DraftOrder().exists(self.shopify_draft_order_id):
                do = shopify.DraftOrder().find(self.shopify_draft_order_id)

                sa = self.__create_address(shipping_address)
                do.shipping_address = do.billing_address = sa
                if billing_address:
                    ba = self.__create_address(billing_address)
                    do.billing_address = ba

                do.save()

                line_items_gross = sum([float(li.price)
                                        for li in do.line_items])
                shipping_gross = 0
                if do.shipping_line:
                    shipping_gross = float(do.shipping_line.price)
                total = line_items_gross + shipping_gross

                if total - payment_amount < 0.01:
                    do.complete()
                else:
                    raise QuoteException(("Incorrect amount: expected about "
                                          f"{round(total, 2)} EUR"))

        return True

    def __update_shipping(
        self,
        shipping: bool,
        do_dict: dict
    ) -> dict:
        if shipping:
            do_dict['shipping'] = {'title': 'Postversand', 'price': self.porto}
        else:
            do_dict.pop('shipping')
        return do_dict

    def __update_price(
        self,
        net_amount: float,
        do_dict: dict
    ) -> dict:
        self.net_amount, self.vat = net_amount, self.vat_rate * net_amount
        gross_amount = self.net_amount + self.vat
        do_dict['translation']['price'] = gross_amount
        return do_dict

    def __update_total_pages(
        self,
        total_pages: int,
        do_dict: dict
    ) -> dict:
        title = do_dict['translation']['title']
        new_title = re.sub('(?<=von )(.*)(?= Seite)', str(total_pages), title)
        do_dict['translation']['title'] = new_title
        return do_dict

    def __update_languages(
        self,
        languages: List[str],
        do_dict: dict
    ) -> dict:
        title = do_dict['translation']['title']
        language_string = f"{languages[0].upper()} - {languages[1].upper()}"
        old_languages = re.findall(r'[A-Z]{2}\s-\s.*', title)
        if len(old_languages) == 1:
            title = title.replace(old_languages[0], language_string)
        else:
            raise QuoteException(("Could not update number of docs: title "
                                  "format invalid"))
        do_dict['translation']['title'] = title
        return do_dict

    def __update_certifications(
        self,
        certifications: int,
        do_dict: dict
    ) -> dict:
        if certifications == 0:
            do_dict['certification'] = None
        else:
            do_dict['certification'] = {
                'title': 'Offizielle Beglaubigung',
                'price': (1 + self.vat_rate) * self.cert_net_amount,
                'quantity': certifications
            }

        return do_dict
