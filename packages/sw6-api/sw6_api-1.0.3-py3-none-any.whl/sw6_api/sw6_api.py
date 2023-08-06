from typing import Tuple, Union, Any

import requests
import json
import os
import time
import math
import yaml

from rich.prompt import Prompt
from rich import print
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from rich.progress import (
    TextColumn,
    Progress,
    MofNCompleteColumn,
    SpinnerColumn,
    TimeElapsedColumn,
)

from hashlib import md5


class SW6Shop:

    def __init__(self, target, username=None, password=None, upload_product_images: bool = True):
        os.makedirs('.data/', exist_ok=True)
        self.upload_product_images = upload_product_images
        self.username = username
        self.password = password
        self.target = target
        # looking for config
        if not os.path.exists(f'.data/{target}_shop_config.yaml'):

            print('[yellow][-] No shop config file found. Collecting base data from target shop and creating config...')
            if self.username is None:
                self.username = Prompt.ask('[cyan2] > USERNAME:')
            if self.password is None:
                self.password = Prompt.ask('[cyan2] > PASSWORD:')
            sales_channel_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'name',
                            'value': 'Storefront'
                        },
                    ],
                'associations':
                    {
                        'salesChannels':
                            {
                                'limit': 50,
                            }
                    }
            }
            tax_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'taxRate',
                            'value': 19.0
                        },
                    ],
            }
            currency_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'isoCode',
                            'value': 'EUR'
                        },
                    ],
            }
            cms_page_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'name',
                            'value': 'Standard Produktseite-Layout'
                        },
                    ],
            }
            delivery_time_payload = {
                'filter':
                    [
                        {
                            'type': 'equals',
                            'field': 'name',
                            'value': '1-3 Tage'
                        },
                    ],
            }
            media_folder_payload = {}
            with Progress() as progress:
                progress_task1 = progress.add_task("[magenta bold]Reading shop data...", total=8)
                self.data = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/sales-channel-type', payload=sales_channel_payload).json()['included']
                progress.update(progress_task1, advance=1)
                self.tax_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/tax', payload=tax_payload).json()['data'][0]['id']
                progress.update(progress_task1, advance=1)
                self.currency_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/currency', payload=currency_payload).json()['data'][0]['id']
                progress.update(progress_task1, advance=1)
                self.product_cms_page_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/cms-page', payload=cms_page_payload).json()['data'][0]['id']
                progress.update(progress_task1, advance=1)
                self.delivery_time_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/delivery-time', payload=delivery_time_payload).json()['data'][0]['id']
                progress.update(progress_task1, advance=1)
                self.media_folder_configuration_id = self.generate_admin_request(
                    'POST', f'https://{self.target}/api/search/media-folder-configuration', payload=media_folder_payload).json()['data'][0]
                progress.update(progress_task1, advance=1)

                [self.data.pop(i) for i, val in enumerate(self.data) if val['type'] != 'sales_channel']
                self.data = self.data[0]
                self.sales_channel_id = self.data['id']
                self.attributes = self.data['attributes']
                self.currency_id = self.data['attributes']['currencyId']
                progress.update(progress_task1, advance=1)
                self.config = {
                    self.target: dict(
                        username=self.username,
                        password=self.password,
                        tax_id=self.tax_id,
                        currency_id=self.currency_id,
                        product_cms_page_id=self.product_cms_page_id,
                        delivery_time_id=self.delivery_time_id,
                        media_folder_configuration_id=self.media_folder_configuration_id,
                        sales_channel_id=self.sales_channel_id,
                    )
                }
                progress.update(progress_task1, advance=1)
            with open(f'.data/{target}_shop_config.yaml', 'w') as configfile:
                yaml.safe_dump(self.config, configfile)
                progress.update(progress_task1, advance=1)
        else:
            self.config = yaml.safe_load(open(f'.data/{target}_shop_config.yaml'))
            self.username = self.config[self.target]['username']
            self.password = self.config[self.target]['password']
            self.tax_id = self.config[self.target]['tax_id']
            self.currency_id = self.config[self.target]['currency_id']
            self.product_cms_page_id = self.config[self.target]['product_cms_page_id']
            self.delivery_time_id = self.config[self.target]['delivery_time_id']
            self.media_folder_configuration_id = self.config[self.target]['media_folder_configuration_id']
            self.sales_channel_id = self.config[self.target]['sales_channel_id']

    def obtain_access_token(self) -> str:
        if os.path.exists('.data/access_token.txt'):
            try:
                data = json.loads(open('.data/access_token.txt', 'r').read())
                access_token = data['access_token']
                timestamp = data['valid_until']
            except json.decoder.JSONDecodeError:
                timestamp = 0

            expired = True if time.time() > timestamp else False
            if not expired:
                return access_token

        else:
            expired = True

        if expired:
            payload = {
                'client_id': 'administration',
                'grant_type': 'password',
                'scopes': 'write',
                'username': self.username,
                'password': self.password
            }

            url = f'https://{self.target}/api/oauth/token'
            response = requests.request('POST', url, json=payload).json()
            token_data = dict(
                access_token=response['access_token'],
                valid_until=time.time() + 590,
            )

        with open('.data/access_token.txt', 'w') as tokenfile:
            tokenfile.write(json.dumps(token_data))

        return token_data['access_token']

    def generate_admin_request(self, method, url, payload=None) -> requests.Response:
        if payload is None:
            payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.obtain_access_token()}',
        }

        response = requests.request(method, url, json=payload, headers=headers)

        return response

    def get_all_products(self) -> list:
        if os.path.exists(f'{self.target} - all products.json'):
            print('[green][+] Reading products from file')
            all_products = json.loads(open(f'{self.target} - all products.json', 'r').read())

        else:

            all_products = []
            i = 100
            payload = {
                'total-count-mode': 1,
                'page': 1,
                'limit': i,
            }

            print(f'[+] getting existing products from {self.target}')
            response = self.generate_admin_request('POST', f'https://{self.target}/api/search/product', payload)
            data = response.json()
            total = data['meta']['total']
            print(f'[+] {total} products found in {self.target}')

            products = data['data']
            all_products.extend(products)
            payload['total-count-mode'] = 0
            pages = math.ceil(total / payload['limit'])

            with Progress(
                    MofNCompleteColumn(),
                    SpinnerColumn(),
                    *Progress.get_default_columns(),
                    TimeElapsedColumn(),
            ) as progress:
                progress_task = progress.add_task("[green bold]Reading products...", total=(pages - 1) * i)
                for page in range(2, pages + 1):
                    payload['page'] = page
                    response = self.generate_admin_request('POST', f'https://{self.target}/api/search/product', payload)
                    data = response.json()
                    products = data['data']
                    all_products.extend(products)
                    progress.update(progress_task, advance=i)

            with open(f'{self.target} - all products.json', 'w') as product_file:
                product_file.write(json.dumps(all_products))

        return all_products

    def get_all_product_ids(self) -> list:
        if os.path.exists(f'{self.target} - all product ids.json'):
            all_products = json.loads(open(f'{self.target} - all product ids.json', 'r').read())

        else:

            all_products = []
            i = 100
            payload = {
                'total-count-mode': 1,
                'page': 1,
                'limit': i,
                "includes": {
                    "product": ["id"]
                }
            }

            print(f'[+] getting existing products from {self.target}')
            response = self.generate_admin_request('POST', f'https://{self.target}/api/search/product', payload)
            data = response.json()
            total = data['meta']['total']
            print(f'[+] {total} products found in {self.target}')

            products = data['data']
            all_products.extend(products)
            payload['total-count-mode'] = 0
            pages = math.ceil(total / payload['limit'])

            with Progress(
                    MofNCompleteColumn(),
                    SpinnerColumn(),
                    *Progress.get_default_columns(),
                    TimeElapsedColumn(),
            ) as progress:
                progress_task = progress.add_task("[green bold]Reading product Ids", total=(pages - 1) * i)
                for page in range(2, pages + 1):
                    payload['page'] = page
                    response = self.generate_admin_request('POST', f'https://{self.target}/api/search/product', payload)
                    data = response.json()
                    products = data['data']
                    all_products.extend(products)
                    progress.update(progress_task, advance=i)

            with open(f'{self.target} - all product ids.json', 'w') as product_file:
                product_file.write(json.dumps(all_products))

        return all_products

    def reduce_prices(self, discount: int = 20, ending: int = 95) -> None:
        all_products = self.get_all_products()
        id_price_map = {
            x['id']: x['attributes']['price'][0]['gross'] for x in all_products
        }

        factor = 1 - discount / 100
        substract = 1 - ending / 100


        datas = [
            {
                'id': uuid,
                'price': [
                    {
                        'currencyId': self.currency_id,
                        'gross': math.ceil(price * factor) - substract,
                        'net': (math.ceil(price * factor) - substract) / 1.19,
                        'linked': True,
                    }
                ],

            } for uuid, price in id_price_map.items()
        ]

        step = s = 100
        chunks = [
            datas[x:x + s] for x in range(0, len(datas), s)
        ]
        with Progress(
                MofNCompleteColumn(),
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
        ) as progress:
            progress_task = progress.add_task("[green bold]Updating product prices", total=len(datas))

            for batch in chunks:
                payload = {
                    "update_prices": {
                        "entity": "product",
                        "action": 'upsert',
                        'payload': batch
                    }
                }

                product_push = self.generate_admin_request('POST', f'https://{self.target}/api/_action/sync', payload)
                progress.update(progress_task, advance=len(batch))

    def create_products(self, datas: list[dict]) -> tuple:
        """
        create a product with shopware 6 API

        datas is a list of dicts containing payload data
        dict is a data container
        use like:
        for data in datas:

            :data is a dict with the following keys:
                :category: []  # list of categories
                :product_number: ''
                :ean: ''
                :manufacturer_number: ''  # MPN
                :strike_price: ''
                :purchase_price: ''
                :description_html: ''  # main description text
                :description_tail: ''  # main description text, 2nd part
                :short_description: ''  # main short_description text
                :properties: {propery_name: property_value}  # grouping property groups in subgroups TODO
                :manufacturer: ''  # or brand, supplier...
                :manufacturer_image_url: ''
                :name: '' # (or title)
                :children: []  # (['child_data'] list of children-dicts with the following keys:
                    :product_number: ''
                    :ean: ''
                    :manufacturer_number: ''  # MPN
                    :name: ''
                    :description_html: ''  # if child product has its own description
                    :description_tail: ''  # if child product has its own description
                    :strike_price: ''
                    :purchase_price: ''
                    :options: {key:value, key2:value2}  # dict represents key:value pairs for options, e.g. color:red, size:M
                    :images: []  # list of child_image urls

        TODO: check existing products to avoid unnessecery overwriting (not within controller, but within grab main()
        TODO: grouping property groups in subgroups
        TODO: develop property handling and "wesentliche Merkmale" handling
        TODO: add metrics like weight, width, height, shipping methods etc.
        TODO: add reviews writing
        TODO: add better docstring lol
        """
        product_datas = []
        all_product_images = set()
        all_manufacturer_images = {}
        for data in datas:

            full_category = data['category']
            product_number = data['product_number']
            name = data['product_name']
            ean = data['ean']
            description = data['description_html']
            description_tail = data['description_tail']  # if 'description_tail' in data else ''
            short_description = data['short_description']  # if 'short_description' in data else ''
            manufacturer_number = data['manufacturer_number']  # if 'manufacturer_number' in data else ''
            manufacturer_name = data['manufacturer_name']
            manufacturer_image_url = data['manufacturer_image_url']
            strike_price = float(str(data['strike_price']).replace(',', '.'))
            purchase_price = float(str(data['purchase_price']).replace(',', '.'))  # if data['price'] != '' else 0
            energy_class = data['energy_class']  # if 'energy_class' in data else ''
            energy_icon_filename = data['energy_icon_filename']  # if 'energy_icon_filename' in data else ''
            energy_label_filename = data['energy_label_filename']  # if 'energy_label_filename' in data else ''
            energy_pdf_filename = data['energy_pdf_filename']  # if 'energy_datasheet_filename' in data else ''
            image_urls = data['image_urls']
            properties = data['properties']
            children = data['children']

            all_manufacturer_images[manufacturer_name] = manufacturer_image_url
            all_product_images.update(image_urls)
            for child_data in children:
                all_product_images.update(child_data['images'])

            product_id = md5(product_number.encode()).hexdigest()
            manufacturer_media_id = md5(manufacturer_image_url.encode()).hexdigest()

            # images
            product_image_payload_data = [
                {
                    'id': md5((product_id + md5(image_url.encode()).hexdigest()).encode()).hexdigest(),
                    'media': {
                        'id': md5(image_url.encode()).hexdigest(),
                        'mediaFolder':
                            {
                                'id': md5('API Product Media'.encode()).hexdigest(),
                                'name': 'API Product Media',
                                'configurationId': '381fbd435a594aafa817a9c207a77f9f',
                            }
                    },
                    'position': i,
                } for i, image_url in enumerate(image_urls)
            ]

            # categories
            product_category_payload_data = {}
            new_level = product_category_payload_data
            for i, category_name in enumerate(full_category[:-1]):
                category_tree = ''.join(full_category[:i + 1])
                child_category_tree = ''.join(full_category[:i + 2])
                new_level['id'] = md5(category_tree.encode()).hexdigest()
                new_level['name'] = full_category[i]
                new_level['cmsPageId'] = '0c8f4e3f5975446581e996e66528214a'
                new_level['children'] = [
                    {
                        'name': full_category[i + 1],
                        'cmsPageId': '0c8f4e3f5975446581e996e66528214a',
                        'id': md5(child_category_tree.encode()).hexdigest()
                    }
                ]
                new_level = new_level['children'][0]

            custom_fields = {
                'grab_add_short_description': short_description,
                'grab_add_description_tail': description_tail,
                'grab_add_energy_class': energy_class,
                'grab_add_energy_icon_filename': energy_icon_filename,
                'grab_add_energy_label_filename': energy_label_filename,
                'grab_add_energy_datasheet_filename': energy_pdf_filename,
            }
            custom_field_sets_payload_data = [
                {
                    'name': field_name,
                    'id': md5(field_name.encode()).hexdigest(),
                    'type': 'html',
                    'config': {
                        'componentName': "sw-text-editor",
                        'customFieldPosition': 1,
                        'customFieldType': "textEditor",
                        'label': {
                            'en-GB': field_name,
                        }
                    }
                } for field_name in custom_fields
            ]
            custom_fields_payload_data = {name: value for name, value in custom_fields.items()}
            properties_payload_data = [
                {
                    'group':
                        {
                            'id': md5(name.encode()).hexdigest(),
                            'name': name
                        },
                    'id': md5((name + value).encode()).hexdigest(),
                    'name': value
                } for name, value in properties.items()
            ]
            children_payload_data = [
                {
                    'name': child_data['name'],
                    'id': md5(child_data['product_number'].encode()).hexdigest(),
                    'price': [
                        {
                            'currencyId': self.currency_id,
                            'gross': float(str(child_data['purchase_price']).replace(',', '.')),
                            'net': float(str(child_data['purchase_price']).replace(',', '.')) / 1.19,
                            'linked': True,
                            'listPrice':
                                {
                                    'currencyId': self.currency_id,
                                    'gross': float(str(child_data['strike_price']).replace(',', '.')),
                                    'net': float(str(child_data['strike_price']).replace(',', '.')) / 1.19,
                                    'linked': True
                                }
                        }
                    ],
                    'productNumber': child_data['product_number'],
                    'ean': child_data['ean'],
                    'manufacturerNumber': child_data['mpn'],
                    'stock': 1000,
                    'options': [
                        {
                            'group':
                                {
                                    'id': md5(option.encode()).hexdigest(),
                                    'name': option,
                                },
                            'id': md5((option + value).encode()).hexdigest(),
                            'name': value,
                        } for option, value in child_data['options'].items()
                    ],
                    'properties': properties_payload_data,
                    'customFields': {'grab_add_description_tail': child_data['description_tail']},
                    'media': [
                        {
                            'id': md5((md5(child_data['product_number'].encode()).hexdigest() + md5(image_url.encode()).hexdigest()).encode()).hexdigest(),
                            'media': {
                                'id': md5(image_url.encode()).hexdigest(),
                                'mediaFolder':
                                    {
                                        'name': 'Product Images',
                                        'id': md5('Product Images'.encode()).hexdigest(),
                                        'configurationId': '381fbd435a594aafa817a9c207a77f9f',
                                    }
                            },
                            'position': i,
                        } for i, image_url in enumerate(child_data['images'])
                    ],
                    'cover':
                        {
                            'mediaId': md5(child_data['images'][0].encode()).hexdigest(),
                        },
                    'categories': [product_category_payload_data],

                } for child_data in children
            ]
            configurator_settings_payload_data = [
                json.loads(x) for x in set(
                    [
                        json.dumps(
                            {
                                'id': md5((data['product_number'] + value).encode()).hexdigest(),
                                'optionId': md5((option + value).encode()).hexdigest()
                            }
                        ) for child_data in children for option, value in child_data['options'].items()
                    ]
                )
            ]
            configurator_group_config_payload_data = [
                json.loads(x) for x in set(
                    [
                        json.dumps(
                            {
                                'id': md5(option.encode()).hexdigest(),
                                'representation': 'box',
                                # 'expressionForListings': True if option == 'Farbe' else False
                                'expressionForListings': False
                            }
                        ) for child_data in children for option, value in child_data['options'].items()
                    ]
                )
            ]

            product_data = {
                'children': children_payload_data,
                'configuratorSettings': configurator_settings_payload_data,
                'configuratorGroupConfig': configurator_group_config_payload_data,
                'taxId': self.tax_id,
                'stock': 1000,
                'id': product_id,
                'productNumber': product_number,
                'price': [
                    {
                        'currencyId': self.currency_id,
                        'gross': purchase_price,
                        'net': purchase_price / 1.19,
                        'linked': True,
                        'listPrice':
                            {
                                'currencyId': self.currency_id,
                                'gross': strike_price,
                                'net': strike_price / 1.19,
                                'linked': True
                            }
                    }
                ],
                'name': name,
                'properties': properties_payload_data,
                'customFieldSets': [
                    {
                        'name': 'additional_product_data',
                        'id': md5('additional_product_data'.encode()).hexdigest(),
                        'relations': [
                            {
                                'id': md5(f'customFieldSetsProductRelationsadditional_product_data'.encode()).hexdigest(),
                                'entityName': "product"
                            }
                        ],
                        'customFields': custom_field_sets_payload_data
                    },
                ],
                'customFields': custom_fields_payload_data,
                'cmsPageId': self.product_cms_page_id,
                'visibilities': [
                    {
                        'id': md5((product_number + 'visibility').encode()).hexdigest(),
                        'salesChannelId': self.sales_channel_id,
                        'visibility': 30
                    }
                ],
                'ean': ean,
                'deliveryTimeId': self.delivery_time_id,
                'manufacturerNumber': manufacturer_number,
                'description': description,
                'manufacturer': {
                    'name': manufacturer_name,
                    'id': md5(manufacturer_name.encode()).hexdigest(),
                    'media': {
                        'id': manufacturer_media_id,
                        'mediaFolder':
                            {
                                'id': md5('API Manufacurer Media'.encode()).hexdigest(),
                                'name': 'API Manufacurer Media',
                                'configurationId': '381fbd435a594aafa817a9c207a77f9f',
                            }
                    }
                },
                'media': product_image_payload_data,
                'coverId': product_image_payload_data[0]['id'],
                'categories': [product_category_payload_data],
            }

            product_datas.append(product_data)

        payload = {
            "create_product": {
                "entity": "product",
                "action": 'upsert',
                'payload': product_datas
            }
        }

        # upload product
        product_push = self.generate_admin_request('POST', f'https://{self.target}/api/_action/sync', payload)
        product_resp_data = json.loads(product_push.text) if product_push.text != '' else 'no response => success'

        # upload product images
        if self.upload_product_images:
            all_product_images = set(all_product_images)
            tasks = []
            with ThreadPoolExecutor(max_workers=12) as executor:

                for i, image_url in enumerate(all_product_images):
                    # fileextension = image_url.split('.')[-1]
                    tasks.append(
                        executor.submit(
                            self.generate_admin_request,
                            'POST',
                            f'https://{self.target}/api/_action/media/{md5(image_url.encode()).hexdigest()}'
                            f'/upload?extension=webp&fileName={product_number}_Produktbild_{i + 1}',
                            {'url': image_url}
                        )
                    )

        # upload manufacturer images

        for name, url in all_manufacturer_images.items():
            manufacturer_media_id = md5(url.encode()).hexdigest()
            manufacturer_image_payload = {'url': url}
            manufacturor_media_push = self.generate_admin_request(
                'POST', f'https://{self.target}/api/_action/media/{manufacturer_media_id}/upload?extension=webp&fileName={name}_Herstellerbild',
                manufacturer_image_payload)

        manufacturor_resp_data = json.loads(manufacturor_media_push.text) if manufacturor_media_push.text != '' else 'no response => success'
        if not product_resp_data['success']:
            print(product_resp_data)
        return product_resp_data, manufacturor_resp_data

    def delete_all_products(self) -> None:
        all_products = self.get_all_product_ids()

        all_ids = [{"id": x['id']} for x in all_products]
        i = 100
        chunks = [all_ids[x:x + i] for x in range(0, len(all_ids), i)]

        # with ThreadPoolExecutor() as executor:
        #     with Progress() as progress:
        #         progress_task = progress.add_task("[red bold]Deleting products...", total=len(all_ids))
        #
        #         tasks = [
        #             executor.submit(
        #                 self.generate_admin_request,
        #                 'DELETE',
        #                 f'https://{self.target}/api/product/{id}')
        #             for id in all_ids
        #         ]
        #
        #         [progress.update(progress_task, advance=1) for _ in futures.as_completed(tasks)]
        with Progress(
                MofNCompleteColumn(),
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
        ) as progress:
            progress_task = progress.add_task("[red bold]Deleting products", total=len(chunks))
            for batch in chunks:
                payload = {
                    'delete_products': {
                        "action": "delete",
                        "entity": "product",
                        "payload": batch,
                    },
                }
                response = self.generate_admin_request('POST', f'https://{self.target}/api/_action/sync', payload)
                if response.status_code != 200:
                    print(response)
                progress.update(progress_task, advance=1)

    def edit_cms_pages(self, sites_contents: dict) -> None:

        pages_payload = {
            'associations': {
                'sections': {
                    'associations': {
                        'blocks': {
                            'associations': {
                                'slots': {}
                            }
                        }
                    }
                }
            }
        }
        url = f'https://{self.target}/api/search/cms-page'
        response = self.generate_admin_request('POST', url, payload=pages_payload).json()
        result = response
        pages = result['data']
        sections = [line for line in result['included'] if line['type'] == 'cms_section']
        blocks = [line for line in result['included'] if line['type'] == 'cms_block']
        slots = [line for line in result['included'] if line['type'] == 'cms_slot']

        for content in pages:
            for name in sites_contents.keys():
                for value in content['attributes'].values():
                    if name.lower() in str(value).lower():
                        sites_contents[name]['id'] = content['id']

        for name, value in sites_contents.copy().items():
            if 'id' not in value:
                del sites_contents[name]

        for name, value in sites_contents.items():
            for section in sections:
                if value['id'] == section['attributes']['pageId']:
                    sites_contents[name]['section_id'] = section['id']

        for name, value in sites_contents.items():
            for block in blocks:
                if value['section_id'] == block['attributes']['sectionId'] and block['attributes']['position'] == 0:
                    sites_contents[name]['block_id'] = block['id']

        for name, value in sites_contents.items():
            for slot in slots:
                if value['block_id'] == slot['attributes']['blockId']:
                    sites_contents[name]['slot_id'] = slot['id']

        for name, data in sites_contents.items():
            patch_payload = {
                "id": data['id'],
                "sections": [
                    {
                        "id": data['section_id'],
                        "blocks": [
                            {
                                "id": data['block_id'],
                                "slots": [
                                    {
                                        "id": data['slot_id'],
                                        "config": {
                                            "content": {
                                                "source": "static",
                                                "value": data['content']
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            self.generate_admin_request('PATCH', f'https://{self.target}/api/cms-page/{data["id"]}', payload=patch_payload)


    def edit_snippets(self, snippets_contents: dict) -> None:

        payload = {
            'limit': 100,
            'filter': [
                {
                    'type': 'multi',
                    'operator': 'or',
                    'queries': [
                        {
                            'type': 'equals',
                            'field': 'translationKey',
                            'value': name,
                        } for name in snippets_contents.keys()
                    ],
                },
            ],
            'associations': {
                'set': {}
            }
        }
        url = f'https://{self.target}/api/search/snippet'
        response = self.generate_admin_request('POST', url, payload)
        result = response.json()
        snippets = result['data']
        snippet_sets = result['included']
        for snippet_set in snippet_sets:
            if snippet_set['attributes']['name'] == 'BASE de-DE':
                snippet_set_id = snippet_set['id']

        for snippet in snippets:
            for name, value in snippets_contents.items():
                if name == snippet['attributes']['translationKey'] and snippet_set_id == snippet['attributes']['setId']:
                    value['id'] = snippet['id']


        for snippet in snippets_contents.values():
            # update snippet
            payload = {
                'value': snippet['content'],
            }
            url = f'https://{self.target}/api/snippet/{snippet["id"]}'
            response = self.generate_admin_request('PATCH', url, payload)
            resp = json.loads(response.text) if response.text != '' else 'no response => success'

    def edit_sales_channel(self, shop_name=None) -> None:

        # update sales channel domains
        update_domains_list = [
            f'http://{self.target}',
            f'https://{self.target}',
            f'http://www.{self.target}',
            f'https://www.{self.target}',
        ]
        domains = self.generate_admin_request(
            'GET', f'https://{self.target}/api/sales-channel/{self.sales_channel_id}/domains')
        result = [uuid['id'] for uuid in domains.json()['data']]
        domain_id_url_map = dict(zip(result, update_domains_list))
        for uuid, url in domain_id_url_map.items():
            payload = {'url': url}
            result = self.generate_admin_request(
                'PATCH', f'https://{self.target}/api/sales-channel-domain/{uuid}', payload=payload)

        # update sales channel name
        self.generate_admin_request(
            'PATCH', f'https://{self.target}/api/sales-channel/{self.sales_channel_id}', payload={'name': shop_name})

    def edit_base_data(self, shop_name, shop_mail):

        payload = {
            None: {
                'core.basicInformation.shopName': shop_name,
                'core.basicInformation.email': shop_mail,

            }
        }

        result = self.generate_admin_request(
            'POST', f'https://{self.target}/api/_action/system-config/batch', payload=payload)

    def edit_invoice_data(self, company):
        """ No handling for delivery countries yet"""
        payload = {
            'filter': [
                {
                    'type': 'equals',
                    'field': 'name',
                    'value': 'invoice'
                }
            ]
        }

        invoice_id = self.generate_admin_request(
            'POST', f'https://{self.target}/api/search/document-base-config', payload=payload).json()['data'][0]['id']

        payload = {
            "id": self.sales_channel_id,
            "config": {
                "displayPrices": True,
                "displayFooter": True,
                "displayHeader": True,
                "displayLineItems": True,
                "diplayLineItemPosition": True,
                "displayPageCount": True,
                "displayCompanyAddress": True,
                "pageOrientation": "portrait",
                "pageSize": "a4",
                "itemsPerPage": 10,
                "companyName": company['firma'],
                "taxNumber": company['tax_number'],
                "vatId": company['ust_id'],
                "taxOffice": company['city'],
                "bankName": "BANKNAME",
                "bankIban": "DE1810000000000000000",
                "bankBic": "BICXXXXXXXX",
                "placeOfJurisdiction": f"Deutschland <br /> {company['amtsgericht']}, {company['hrb']}",
                "placeOfFulfillment": company['city'],
                "executiveDirector": "KONTOINHABER",
                "companyAddress": f"{company['street']}, {company['postcode']} {company['city']}",
                # "deliveryCountries": [
                #     "15e1a20b831b4fdd8d539ec09b37c43d","197fd9c171984084a5032d0a9d4b878b","3bcd3dee17554c42a9f9da7c604c6837","4296382b6a3d4114bfb9b4f8315fa317","4366ec2484f34410991d97e7903597d7","4c228f18910f4157a37654a4e8cd24fc","4cb1c7cabd9b4382ab2d2067d42a448f","4e12f2144385437b91e5a75036d606a7","4ef46e1e8f3f475ab5397413e488e667","5bbec0b270d5413292bd5fa772d2d251","732c8274910f4759858a182b45a45784","7949898777e44cca9e0df28b1dd37d85","8094e4bc251a445e98e66ff82ee40888","8d010ab933d2418bb22fdf3acd8e8356","9c97ae27e50b4b3abe1fc24a16243482","9dce4ff9be6643baacab1b3aefda7377","9f4161fa7c894c2d8382318a91666545","bd863884c3df46e9bccafb47558a21d1","c358ae0f074a4e9188dc0fba3510babe","c6d98d188c6c4e45a191fa256958404e","d5e71cad4a214842a10b367edb69f5cb","dd19a1a17f12475f86ddecd166eb5277","ddeb318373474dcab1dcd313e7260c49","e0b7086a73d446aeb1c36e80c18723a5","e2eb313ed4c84ec388f118e5c6f496ee","e5a16dcb84cb45ec839a2261d523eeb6","eb8783e7755148739dc53a56b66782a1","ef7a924c6e0240f2820dc9d226be2e3d"
                # ],
                "companyUrl": f"www.{self.target}",
                "companyEmail": f"{company['pre']}@{self.target}",
                "companyPhone": company['phone']
            }
        }

        result = self.generate_admin_request(
            'PATCH', f'https://{self.target}/api/document-base-config/{invoice_id}', payload=payload)

# def delete_images_with_no_folder(target, username, password):
#     all_images = []
#     payload = {
#         'total-count-mode': 1,
#         'page': 1,
#         'limit': 100,
#     }
#     response = generate_admin_request('POST', f'https://{target}/api/search/media', username, password, payload)
#     data = response.json()
#     total = data['meta']['total']
#     images = data['data']
#     all_images.extend(images)
#     payload['total-count-mode'] = 0
#     pages = math.ceil(total / payload['limit'])
#     for page in range(2, pages + 1):
#         payload['page'] = page
#         response = generate_admin_request('POST', f'https://{target}/api/search/media', password, password, payload)
#         data = response.json()
#         images = data['data']
#         all_images.extend(images)
#         print(f'page {page}/{pages} done')
#
#     no_folder_ids = [x['id'] for x in all_images if x['attributes']['mediaFolderId'] is None]
#
#     tasks = []
#     with ThreadPoolExecutor(max_workers=10) as executor:
#         tasks = []
#         for uuid in no_folder_ids:
#             tasks.append(executor.submit(generate_admin_request, 'DELETE', f'https://{target}/api/media/{uuid}', password, password))
#
#         for job in futures.as_completed(tasks):
#             print(f'{job} deleted')
#
#     # for uuid in no_folder_ids:
#     #     response = generate_admin_request('DELETE', f'https://{HOST}/api/media/{uuid}', password, password)
#     #     print(f'{uuid} deleted')
#
#     return response
#
# def get_products_with_empty_media(target, username, password):
#     empty_media_products = []
#     payload = {
#         'total-count-mode': 1,
#         'page': 1,
#         'limit': 100,
#         "filter": [
#             {
#                 'field': "media.id",
#                 'type': "equals",
#                 'value': None,
#             }
#         ]
#     }
#
#     response = generate_admin_request('POST', f'https://{target}/api/search/product', username, password, payload)
#     data = response.json()
#     total = data['meta']['total']
#     product_numbers = [
#         p['attributes']['productNumber'] for p in data['data']
#     ]
#     empty_media_products.extend(product_numbers)
#     payload['total-count-mode'] = 0
#     pages = math.ceil(total / payload['limit'])
#     for page in range(2, pages + 1):
#         payload['page'] = page
#         response = generate_admin_request('POST', f'https://{target}/api/search/product', password, password, payload)
#         data = response.json()
#         product_numbers = [
#             p['attributes']['productNumber'] for p in data['data']
#         ]
#         empty_media_products.extend(product_numbers)
#         print(f'page {page}/{pages} done')
#
#
# def upload_product_images(rootfolder, target, username, password):
#     all_product_images = set(open(f'{rootfolder}/cache/all_images.txt', 'r').read().splitlines())
#     all_image_urls_list = [
#         u for img_data in list(all_product_images) for image_urls in json.loads(img_data).values() for u in image_urls
#     ]
#     count = 0
#     tasks = []
#     with ThreadPoolExecutor(max_workers=10) as executor:
#
#         for img_data in list(all_product_images):
#             raw_line = img_data
#             img_data = json.loads(raw_line)
#             for product_number, image_urls in img_data.items():
#                 for i, image_url in enumerate(image_urls):
#                     if 'youtube' in image_url:
#                         continue
#                     count += 1
#                     product_media_id = md5(image_url.encode()).hexdigest()
#                     product_media_data_payload = {'url': image_url}
#                     fileextension = image_url.split('.')[-1]
#                     url = f'https://{target}/api/_action/media/{product_media_id}/upload?extension={fileextension}&fileName={product_number}_Produktbild_{i + 1}'
#                     tasks.append(executor.submit(generate_admin_request, 'POST', url, target, username, password, product_media_data_payload))
#
#                 for future in futures.as_completed(tasks):
#                     status = future.result().status_code
#                     print(future.result(), f'{count}/{len(all_image_urls_list)} uploaded')
#
#                 if status == 204:
#                     all_product_images.remove(raw_line)
#                     with open(f'{rootfolder}/cache/all_images.txt', 'w') as imagefile:
#                         [imagefile.write(line + '\n') for line in all_product_images]


if __name__ == '__main__':
    self = SW6Shop(
        target='go-e-bike.com',
        username='D#r#eB)lNMzIo%**',
        password='D#r#eB)lNMzIo%**',
        upload_product_images=False,
    )
