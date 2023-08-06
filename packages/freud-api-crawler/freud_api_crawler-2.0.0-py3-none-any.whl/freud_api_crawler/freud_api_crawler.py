import os
import json
import re
import time
from collections import defaultdict

import requests
import lxml.etree as ET
import jinja2

from freud_api_crawler.string_utils import clean_markup, extract_page_nr, always_https, normalize_white_space

from xml.sax.saxutils import escape

# from freud_api_crawler.tei_utils import make_pb

FRD_BASE = "https://www.freud-edition.net"
FRD_API = os.environ.get('FRD_API', f'{FRD_BASE}/jsonapi/')
FRD_WORK_LIST = f"{FRD_API}node/werk?filter[field_status_umschrift]=2"
FRD_WORK_SIGNATUR_EP = f"{FRD_API}taxonomy_term/signatur_fe/"
FRD_USER = os.environ.get('FRD_USER', False)
FRD_PW = os.environ.get('FRD_PW', False)
FULL_MANIFEST = "228361d0-4cda-4805-a2f8-a05ee58119b6"
HISTORISCHE_AUSGABE = "5b8d9c77-99d0-4a80-92d8-4a9de06ac7ca"

MANIFEST_DEFAULT_FILTER = {
    "field_doc_component.id": FULL_MANIFEST,
    "field_manifestation_typ.id": HISTORISCHE_AUSGABE,
    "field_status_umschrift": 2
}


def get_auth_items(username, password):
    """ helper function to fetch auth-cookie

    :param username: Drupal-User Username
    :type username: str
    :param password: Drupal-User Password
    :type password: str

    :return: A dict with auth-items `'cookie', 'current_user', 'csrf_token', 'logout_token'`
    :rtype: dict
    """

    url = "https://www.freud-edition.net/user/login?_format=json"
    payload = {
        "name": username,
        "pass": password
    }
    headers = {
        'Content-Type': 'application/json',
    }
    r = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload)
    )
    auth_items = {
        'cookie': r.cookies,
    }
    for key, value in r.json().items():
        auth_items[key] = value
    return auth_items


AUTH_ITEMS = get_auth_items(FRD_USER, FRD_PW)

XSLT_FILE = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
    "make_tei.xslt"
)

XSL_DOC = ET.parse(XSLT_FILE)

TEI_DUMMY = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
    "tei_dummy.xml"
)

CUR_LOC = os.path.dirname(os.path.abspath(__file__))


class FrdClient():

    """Main Class to interact with freud.net-API """

    def tei_dummy(self):
        doc = ET.parse(TEI_DUMMY)
        return doc

    def list_endpoints(self):
        """ returns a list of existing API-Endpoints
        :return: A PyLobidPerson instance
        """

        time.sleep(1)
        r = requests.get(
            self.endpoint,
            cookies=self.cookie,
            allow_redirects=True
        )
        result = r.json()
        d = defaultdict(list)
        for key, value in result['links'].items():
            url = value['href']
            node_type = url.split('/')[-2]
            d[node_type].append(url)
        return d

    def __init__(
        self,
        out_dir=CUR_LOC,
        endpoint=FRD_API,
        browser_endpoint=FRD_BASE,
        xsl_doc=XSL_DOC,
        auth_items={},
        limit=10,
    ):

        """ initializes the class

        :param out_dir: The directory to save processed Manifestations
        :type out_dir: str
        :param endpoint: The API Endpoint
        :type endpoint: str
        :param xsl_doc: A `lxml.etree._ElementTree` object (i.e. a parsed XSL-Stylesheet)
        :type xsl_doc: lxml.etree._ElementTree
        :param auth_items: The result dict of a successfull drupal api login action
        :type auth_items: dict
        :param limit: After how many next-loads the loop should stop
        :type pw: int

        :return: A FrdClient instance
        """
        super().__init__()
        self.endpoint = endpoint
        self.browser = browser_endpoint
        self.auth_items = auth_items
        self.cookie = self.auth_items['cookie']
        self.limit = limit
        self.werk_ep = f"{self.endpoint}node/werk"
        self.manifestation_ep = f"{self.endpoint}node/manifestation"
        self.nsmap = {
            "tei": "http://www.tei-c.org/ns/1.0",
            "xml": "http://www.w3.org/XML/1998/namespace",
        }
        self.tei_dummy = self.tei_dummy()
        self.out_dir = out_dir
        self.xsl_doc = xsl_doc


class FrdWerk(FrdClient):
    """class to deal with Werke
    :param werk_id: The hash ID of a Werk Node
    :type werk_id: str

    :return: A FrdWork instance
    :rtype: class:`freud_api_crawler.freud_api_crawler.FrdWerk`
    """

    def get_werk(self):
        """ returns the werk json as python dict

        :return: a Werk representation
        :rtype: dict
        """
        time.sleep(1)
        r = requests.get(
            self.ep,
            cookies=self.cookie,
            allow_redirects=True
        )
        result = r.json()
        return result

    def get_manifestations(
        self,
        filters={}
    ):
        """ retuns a list of dicts of related manifestation
        :param filters: a dictionary holding query filter params, see e.g. `MANIFEST_DEFAULT_FILTER`
        :type werk_id: dict

        :return: A list of dicts with ids and titles of the related manifestations
        :rtype: list
        """
        man_col = []
        fields_param = "fields[node--manifestation]=id,title"
        url = f"{self.manifestation_ep}{self.filtered_url}&{fields_param}"
        for key, value in filters.items():
            if value is not None:
                url += f"&filter[{key}]={value}"
        next_page = True
        while next_page:
            print(url)
            response = None
            result = None
            x = None
            time.sleep(1)
            response = requests.get(
                url,
                cookies=self.cookie,
                allow_redirects=True
            )
            result = response.json()
            links = result['links']
            if links.get('next', False):
                orig_url = links['next']['href']
                url = always_https(orig_url)
            else:
                next_page = False
            for x in result['data']:
                item = {
                    "man_id": x['id'],
                    "man_title": x['attributes']['title']
                }
                man_col.append(item)
        return man_col

    def get_fe_signatur(self):
        r = requests.get(
            f"{FRD_WORK_SIGNATUR_EP}{self.signatur_hash}",
            cookies=self.cookie,
            allow_redirects=True
        )
        result = r.json()
        return result['data']['attributes']['name']

    def __init__(
        self,
        werk_id=None,
        filter_finished=True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.werk_id = werk_id
        self.ep = f"{self.werk_ep}/{self.werk_id}"
        self.werk = self.get_werk()
        self.signatur_hash = self.werk['data']['relationships']['field_signatur_sfe']['data']['id']
        self.signatur = self.get_fe_signatur()
        self.werk_attrib = self.werk['data']['attributes']
        self.filter_finished = filter_finished
        if filter_finished:
            self.filtered_url = f"?filter[field_werk.id]={self.werk_id}"
        else:
            self.filtered_url = f"?filter[field_werk.id]={self.werk_id}"
        for x in self.werk_attrib.keys():
            value = self.werk_attrib[x]
            if isinstance(value, dict):
                for y in value.keys():
                    dict_key = f"{x}__{y}"
                    setattr(self, f"md__{dict_key}", value[y])
            else:
                setattr(self, f"md__{x}", value)
        self.meta_attributes = [x for x in dir(self) if x.startswith('md__')]
        print("fetching related manifestations")
        self.manifestations = self.get_manifestations()
        self.manifestations_count = len(self.manifestations)


class FrdManifestation(FrdClient):

    """class to deal with Manifestations
    :param manifestation_id: The hash ID of a Manifestation Node
    :type manifestation_id: str

    :return: A FrdManifestation instance
    :rtype: class:`freud_api_crawler.freud_api_crawler.FrdManifestation`
    """

    def get_manifest(self):
        """ returns the manifest json as python dict

        :return: a Manifestation representation
        :rtype: dict
        """
        fields_to_include = [
            'field_werk',
            'field_werk.field_signature_sfg',
            'field_chapters'
        ]
        url = f"{self.manifestation_endpoint}?include={','.join(fields_to_include)}"
        time.sleep(1)
        r = requests.get(
            url,
            cookies=self.cookie,
            allow_redirects=True
        )
        print(url)
        result = r.json()
        return result

    def get_pages(self):
        """ method returning related page-ids/urls

        :return: a list of dicts `[{'id': 'hash-id', 'url': 'page_url'}]`
        :rtype: list
        """
        page_list = []
        if self.manifestation['data']['relationships']['field_chapters']['data']:
            print("looks like there are chapters")
            for y in self.manifestation['included']:
                try:
                    pages = y['relationships']['field_seiten']['data']
                except KeyError:
                    continue
                for x in pages:
                    node_type = x['type'].split('--')[1]
                    page = {
                        'id': x['id'],
                        'url': f"{self.endpoint}node/{node_type}/{x['id']}"
                    }
                    page_list.append(page)
        else:
            for x in self.manifestation['data']['relationships']['field_seiten']['data']:
                node_type = x['type'].split('--')[1]
                page = {
                    'id': x['id'],
                    'url': f"{self.endpoint}node/{node_type}/{x['id']}"
                }
                page_list.append(page)
        return page_list

    def get_page(self, page_id):
        """ fetches a page matching the given id or url and returns the manifestation_seite json

        :param page_id: A hash-id or url to a manifestation_seite endpoint
        :type page_id: string

        :return: A manifestation_seite dict
        :rtype: dict
        """

        if not page_id.startswith('http'):
            url = f"{self.endpoint}node/manifestation_seite/{page_id}"
        else:
            url = page_id

        print(url)

        time.sleep(1)
        r = requests.get(
            f"{url}?include=field_faksimile",
            cookies=self.cookie,
            allow_redirects=True
        )

        result = r.json()
        return result

    def process_page(self, page_json):
        """ processes a page_json to something more useful

        :param page_json: The API response of a manifestation_seite endpoint
        :type page_json: dict

        :return: A dict containing a cleaned body with needed metatdata\

        {
            'id': page_id,
            'body': <div xml:id=page_id><p>lorem ipsum</p></div>
        }

        :rtype: dict
        """
        page_attributes = page_json['data']['attributes']
        page_id = page_json['data']['id']
        try:
            body = page_attributes['body']['processed']
        except:  # noqa: E722
            print("\n#####################")
            print(f"no content for manifestation_seite/{page_id}")
            print("#####################\n")
            body = "<p>BLANK</p>"
        # wrapped_body = f'<div xmlns="http://www.tei-c.org/ns/1.0" xml:id="page__{page_id}">{body}</div>'
        cleaned_body = clean_markup(body)
        cleaned_body = normalize_white_space(cleaned_body)
        faks = page_json['included'][0]
        page_nr = extract_page_nr(page_attributes['title'])
        result = {
            'id': page_id,
            'title': page_attributes['title'],
            'page_nr': page_nr,
            'attr': page_attributes,
            'body': cleaned_body,
            'faks': faks,
            'faks__id': faks['id'],
            'faks__url': faks['links']['self']['href'],
            'faks__payload': faks['attributes']['uri']['url']
        }
        return result

    def make_xml(self, save=False, limit=True, dump=False):

        """serializes a manifestation as XML/TEI document

        :param save: if set, a XML/TEI file `{self.save_path}` is saved
        :param type: bool

        :return: A lxml.etree
        """
        json_dump = self.get_man_json_dump(lmt=limit, dmp=dump)
        templateLoader = jinja2.PackageLoader(
            "freud_api_crawler", "templates"
        )
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template('./tei.xml')
        tei = template.render({"objects": [json_dump]})
        tei = re.sub(r'\s+$', '', tei, flags=re.MULTILINE)
        tei = ET.fromstring(tei)
        transform = ET.XSLT(self.xsl_doc)
        tei = transform(tei)
        if save:
            with open(self.save_path, 'wb') as f:
                f.write(ET.tostring(tei, pretty_print=True, encoding="utf-8"))
        return tei

    def get_man_json_dump(self, lmt=True, dmp=False):
        if dmp:
            json_dump = {}
            json_dump["id"] = f"bibl__{self.manifestation_id}"
            json_dump["browser_url"] = f"{self.browser}{self.manifestation_folder}"
            man_type = self.manifestation['data']['type'].replace('--', '/')
            json_dump["url"] = f"{self.endpoint}{man_type}/{self.manifestation_id}"
            json_dump['man_title'] = self.md__title
            json_dump['signature'] = self.manifestation_signatur
            try:
                s_title_t = self.manifestation['data']['attributes']['field_shorttitle']
                json_dump['man_shorttitle'] = escape(s_title_t['value'])
            except (KeyError, TypeError):
                json_dump['man_shorttitle'] = None
                print("No short title found!")
            try:
                field_date = self.manifestation['data']['attributes']['field_datum']
                json_dump['date'] = {
                    "value": field_date['value'],
                    "end_value": field_date['end_value']
                }
            except(KeyError, TypeError):
                json_dump['date'] = {}
                print("manifestation has no field_datum.")
            try:
                field_reihe = self.manifestation['data']['attributes']['field_reihe']
                field_reihe_no = self.manifestation['data']['attributes']['field_reihe_nummer']
                json_dump['reihe'] = {
                    "name": field_reihe,
                    "number": field_reihe_no
                }
            except(KeyError, TypeError):
                json_dump['reihe'] = {}
                print("manifestation has no field_reihe")
            try:
                field_pages = self.manifestation['data']['attributes']['field_pages']
                json_dump['page_num'] = []
                for idx, x in enumerate(field_pages):
                    page_num = x['value']
                    if idx == 0:
                        name = "start"
                    else:
                        name = "end"
                    json_dump['page_num'] = {
                        name: page_num
                    }
            except (KeyError, TypeError):
                json_dump['page_num'] = {}
                print("manifestation has no field_pages")
            try:
                man_art = self.art['data']['attributes']['name']
                json_dump['man_type'] = man_art
            except (KeyError, TypeError):
                json_dump['man_type'] = None
                print("manifestation has no field_art")
            try:
                json_dump['man_font'] = []
                for x in self.font:
                    man_font = x['data']['attributes']['name']
                    json_dump['man_font'].append({
                        "name": man_font
                    })
            except (KeyError, TypeError):
                json_dump['man_font'] = {}
                print("manifestation has no field_font")
            try:
                man_format = self.format['data']['attributes']['name']
                json_dump['man_format'] = man_format
            except (KeyError, TypeError):
                json_dump['man_format'] = None
                print("manifestation has no field_font")
            try:
                man_mediatype = self.mediatype['data']['attributes']['name']
                json_dump['man_mediatype'] = man_mediatype
            except (KeyError, TypeError):
                json_dump['man_mediatype'] = None
                print("manifestation has no field_mediatype")
            try:
                json_dump["type"] = escape(self.type['data']['attributes']['name'])
            except (KeyError, TypeError):
                json_dump["type"] = None
                print("Manifestation has no attribute field_publication_type.")
            try:
                man_sprache = self.sprache['data']['attributes']['name']
                man_langcode = self.sprache['data']['attributes']['langcode']
                json_dump['man_lang'] = {
                    "name": man_sprache,
                    "langcode": man_langcode
                }
            except (KeyError, TypeError):
                json_dump['man_lang'] = {}
                print("manifestation has no field_sprache")
            try:
                man_edition = self.edition['data']['attributes']['name']
                json_dump['man_edition'] = {
                    "name": man_edition
                }
            except (KeyError, TypeError):
                json_dump['man_edition'] = None
                print("manifestation has no field_edition")
            try:
                attr = self.author['data']['attributes']
                json_dump["author"] = {
                    "name": escape(attr['name']),
                    "id": f"p__{self.author['data']['id']}",
                    "tid": attr['drupal_internal__tid'],
                    "rev_id": attr['drupal_internal__revision_id'],
                    "url": f"{self.endpoint}taxonomy_term/personen/{self.author['data']['id']}",
                    "browser_url": f"{self.browser}/taxonomy/term/{attr['drupal_internal__revision_id']}"
                }
            except (KeyError, TypeError):
                json_dump["author"] = {
                    "name": "Freud, Sigmund",
                    "id": "p__80f26163-0581-4079-a0ce-4f2417f09b97",
                    "tid": "111",
                    "rev_id": "111",
                    "url": f"{self.endpoint}taxonomy_term/personen/80f26163-0581-4079-a0ce-4f2417f09b97",
                    "browser_url": f"{self.browser}/taxonomy/term/111"
                }
            # work level
            json_dump["work"] = {}
            json_dump["work"]["id"] = f"bibl__{self.werk['id']}"
            json_dump["work"]["title"] = escape(self.werk['attributes']['title'])
            json_dump["work"]["url"] = f"{self.endpoint}werk/{self.werk['id']}"
            json_dump["work"]["browser_url"] = f"{self.browser}{self.werk_folder}"
            # publication level 1
            init_methods = {
                "manifestation": self.manifestation_id,
                "publication": self.publication,
                "publisher": self.pub_publisher,
                "pub_herausgeber": self.pub_herausgeber,
                "pub_author": self.pub_author,
                "pub_edition": self.pub_edition,
                "pub_advisors": self.pub_advisors,
                "pub_editors": self.pub_editors,
                "pub_type": self.pub_type,
                "endpoint": self.endpoint,
                "browser": self.browser,
            }
            publication = self.get_publication_md(init_methods)
            json_dump["publication"] = publication
            # publication level 2
            init_methods = {
                "manifestation": self.manifestation_id,
                "publication": self.publication2,
                "publisher": self.pub2_publisher,
                "pub_herausgeber": self.pub2_herausgeber,
                "pub_author": self.pub2_author,
                "pub_edition": self.pub2_edition,
                "pub_advisors": self.pub2_advisors,
                "pub_editors": self.pub2_editors,
                "pub_type": self.pub2_type,
                "endpoint": self.endpoint,
                "browser": self.browser,
            }
            publication = self.get_publication_md(init_methods)
            if publication["id"]:
                json_dump["publication"]["publication"] = publication
            # publication level 3
            init_methods = {
                "manifestation": self.manifestation_id,
                "publication": self.publication3,
                "publisher": self.pub3_publisher,
                "pub_herausgeber": self.pub3_herausgeber,
                "pub_author": self.pub3_author,
                "pub_edition": self.pub3_edition,
                "pub_advisors": self.pub3_advisors,
                "pub_editors": self.pub3_editors,
                "pub_type": self.pub3_type,
                "endpoint": self.endpoint,
                "browser": self.browser,
            }
            publication = self.get_publication_md(init_methods)
            if publication["id"]:
                json_dump["publication"]["publication"]["publication"] = publication
            # repository
            try:
                msType = self.repository['data']['type'].replace('--', '/')
                json_dump["repository"] = {
                    "id": f"rep__{self.repository['data']['id']}",
                    "name": escape(self.repository['data']['attributes']['name']),
                    "url": f"{self.endpoint}{msType}/{self.repository['data']['id']}"
                }
            except (KeyError, TypeError):
                json_dump["repository"] = {}
                print("It seems there is no 'filed_aufbewahrungsort'")
            try:
                repo_container = self.manifestation['data']['attributes']['field_aufbewahrungsort_container']
                json_dump["repository"]["orig_archiv_id"] = repo_container['value']
            except (KeyError, TypeError):
                print("It seems there is no 'filed_aufbewahrungsort_container'")
            json_dump["pages"] = []
            pages = self.pages
            if lmt:
                actual_pages = pages[:2]
            else:
                actual_pages = pages
            for x in actual_pages:
                page_json = self.get_page(x['id'])
                pp = self.process_page(page_json)
                json_dump["pages"].append(pp)
            os.makedirs(os.path.join(self.save_dir, self.werk_signatur, 'data'), exist_ok=True)
            with open(self.save_path_json, 'w', encoding='utf8') as f:
                json.dump(json_dump, f)
        else:
            try:
                with open(self.save_path_json, 'r', encoding='utf8') as f:
                    json_dump = json.load(f)
            except FileNotFoundError:
                print(f"file {self.save_path_json} not found, switching dump=True and restarting")
                json_dump = self.get_man_json_dump(lmt=lmt, dmp=True)
        return json_dump

    def get_fe_werk_signatur(self):
        r = requests.get(
            f"{FRD_WORK_SIGNATUR_EP}{self.werk_signatur_hash}",
            cookies=self.cookie,
            allow_redirects=True
        )
        result = r.json()
        return result['data']['attributes']['name']

    def get_fields_any(self, field_type):
        """requests manifestation 'relationships' fields

        :param field_type: takes a string refering to the correct field e.g. 'field_published_in'

        :return: json
        """
        try:
            item = self.manifestation['data']['relationships'][field_type]['data']
        except (KeyError, TypeError):
            print(f"looks like there is no {field_type}")
            return {}
        if type(item) is list:
            result = []
            for x in item:
                try:
                    item_id = x['id']
                except (KeyError, TypeError):
                    print(f"looks like there is no ID for {field_type}")
                    return {}
                node_type = x['type'].split('--')[1]
                taxonomy = x['type'].split('--')[0]
                url = f"{self.endpoint}{taxonomy}/{node_type}/{item_id}"
                r = requests.get(
                    url,
                    cookies=self.cookie,
                    allow_redirects=True
                )
                res = r.json()
                result.append(res)
            return result
        else:
            try:
                item_id = item['id']
            except (KeyError, TypeError):
                print(f"looks like there is no ID for {field_type}")
                return {}
            node_type = item['type'].split('--')[1]
            taxonomy = item['type'].split('--')[0]
            url = f"{self.endpoint}{taxonomy}/{node_type}/{item_id}"
            r = requests.get(
                url,
                cookies=self.cookie,
                allow_redirects=True
            )
            result = r.json()
        return result

    def get_fields_any_any(self, field_type, get_fields):
        """requests manifestation 'relationships' fields

        :param field_type: takes a string refering to the correct field e.g. 'field_published_in'

        :return: json
        """
        try:
            get_fields['data']['id']
        except (KeyError, TypeError):
            print("looks like there is no ID for get_fields")
            return {}
        try:
            item = get_fields['data']['relationships'][field_type]['data']
        except (KeyError, TypeError):
            print(f"looks like there is no {field_type}")
            return {}
        if type(item) is list:
            result = []
            for x in item:
                try:
                    item_id = x['id']
                except (KeyError, TypeError):
                    print(f"looks like there is no ID for {field_type}")
                    return {}
                node_type = x['type'].split('--')[1]
                taxonomy = x['type'].split('--')[0]
                url = f"{self.endpoint}{taxonomy}/{node_type}/{item_id}"
                r = requests.get(
                    url,
                    cookies=self.cookie,
                    allow_redirects=True
                )
                res = r.json()
                result.append(res)
            return result
        else:
            try:
                item_id = item['id']
            except (KeyError, TypeError):
                print(f"looks like there is no ID for {field_type}")
                return {}
            node_type = item['type'].split('--')[1]
            taxonomy = item['type'].split('--')[0]
            url = f"{self.endpoint}{taxonomy}/{node_type}/{item_id}"
            r = requests.get(
                url,
                cookies=self.cookie,
                allow_redirects=True
            )
            result = r.json()
            return result

    def get_publication_md(self, init_methods):
        obj = {}
        try:
            obj["id"] = f"bibl__{init_methods['publication']['data']['id']}"
        except (KeyError, TypeError):
            obj["id"] = None
        try:
            obj["title"] = escape(init_methods['publication']['data']['attributes']['title'])
        except (KeyError, TypeError):
            obj["title"] = None
        try:
            obj["type"] = escape(init_methods['pub_type']['data']['attributes']['name'])
        except (KeyError, TypeError):
            print("Publication has no attribute field_publication_type.")
        try:
            field_reihe = init_methods['publication']['data']['attributes']['field_reihe']
            field_reihe_no = init_methods['publication']['data']['attributes']['field_reihe_nummer']
            obj['reihe'] = {
                "name": field_reihe,
                "number": field_reihe_no
            }
        except(KeyError, TypeError):
            print("publication has no field_reihe")
        try:
            edition = init_methods['pub_edition']['data']['attributes']['name']
            obj['edition'] = {
                "name": edition
            }
        except (KeyError, TypeError):
            print("publication has no field_edition")
        try:
            bibl_type = init_methods['publication']['data']['type'].replace('--', '/')
            obj["id"] = f"bibl__{init_methods['publication']['data']['id']}"
            obj["url"] = f"{init_methods['endpoint']}{bibl_type}/{init_methods['publication']['data']['id']}"
        except (KeyError, TypeError):
            print("No publication ID found!")
        try:
            bibl_title_obj = init_methods['publication']['data']['attributes']['field_titel']
            obj["title_main"] = escape(bibl_title_obj['value'])
        except (KeyError, TypeError):
            print("No publication main title found!")
        try:
            bibl_title_obj = init_methods['publication']['data']['attributes']['field_secondary_title']
            obj["title_sub"] = escape(bibl_title_obj['value'])
        except (KeyError, TypeError):
            print("No publication secodnary title found!")
        try:
            bibl_title_obj = init_methods['publication']['data']['attributes']['field_shorttitle']
            obj["title_short"] = escape(bibl_title_obj['value'])
        except (KeyError, TypeError):
            print("No publication short title found!")
        try:
            bibl_jahrgang = init_methods['publication']['data']['attributes']['field_jahrgang']
            obj["jahrgang"] = bibl_jahrgang['value']
        except (KeyError, TypeError):
            print("No publication jahrgang found!")
        try:
            bibl_orig_year = init_methods['publication']['data']['attributes']['field_original_publication_year']
            obj["original_publication_year"] = bibl_orig_year
        except (KeyError, TypeError):
            print("No original publication year found!")
        try:
            places = init_methods['publication']['data']['attributes']['field_publication_place']
            for x in places:
                place = escape(x["value"])
                obj["places"] = []
                obj["places"].append({"name": place})
        except (KeyError, TypeError):
            print("No publication place(s) found!")
        try:
            bibl_date_obj = init_methods['publication']['data']['attributes']['field_publication_year']
            obj["date"] = bibl_date_obj
        except (KeyError, TypeError):
            print("No publication year found!")
        try:
            bibl_scope_obj = init_methods['publication']['data']['attributes']['field_band']
            bibl_scope_no = init_methods['publication']['data']['attributes']['field_band_nr']
            obj["band"] = {
                "name": escape(bibl_scope_obj['value']),
                "number": bibl_scope_no
            }
        except (KeyError, TypeError):
            print("No publication field band found!")
        try:
            if type(init_methods['pub_publisher']) is list:
                for x in init_methods['pub_publisher']:
                    pub_type = x['data']['type'].replace('--', '/')
                    obj["publisher"] = []
                    attr = x['data']['attributes']
                    browser = f"{init_methods['browser']}/taxonomy/term/"
                    obj["publisher"].append(
                        {
                            "id": f"p__{x['data']['id']}",
                            "name": f"{escape(x['data']['attributes']['name'])}",
                            "url": f"{init_methods.endpoint}{pub_type}/{x['data']['id']}",
                            "tid": attr['drupal_internal__tid'],
                            "rev_id": attr['drupal_internal__revision_id'],
                            "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                        }
                    )
            else:
                pub_type = init_methods['pub_publisher']['data']['type'].replace('--', '/')
                obj["publisher"] = []
                attr = init_methods['pub_publisher']['data']['attributes']
                browser = f"{init_methods['browser']}/taxonomy/term/"
                obj["publisher"] = [
                    {
                        "id": f"p__{init_methods['pub_publisher']['data']['id']}",
                        "name": f"{escape(attr['name'])}",
                        "url": f"{init_methods['endpoint']}{pub_type}/{init_methods['pub_publisher']['data']['id']}",
                        "tid": attr['drupal_internal__tid'],
                        "rev_id": attr['drupal_internal__revision_id'],
                        "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                    }
                ]
        except (KeyError, TypeError):
            print("No publication publisher found!")
        try:
            if type(init_methods['pub_herausgeber']) is list:
                for x in init_methods['pub_herausgeber']:
                    pub_type = x['data']['type'].replace('--', '/')
                    obj["herausgeber"] = []
                    attr = x['data']['attributes']
                    browser = f"{init_methods['browser']}/taxonomy/term/"
                    obj["herausgeber"].append(
                        {
                            "id": f"p__{x['data']['id']}",
                            "name": f"{escape(x['data']['attributes']['name'])}",
                            "url": f"{init_methods['endpoint']}{pub_type}/{x['data']['id']}",
                            "tid": attr['drupal_internal__tid'],
                            "rev_id": attr['drupal_internal__revision_id'],
                            "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                        }
                    )
            else:
                pub_type = init_methods['pub_herausgeber']['data']['type'].replace('--', '/')
                obj["herausgeber"] = []
                attr = init_methods['pub_herausgeber']['data']['attributes']
                browser = f"{init_methods['browser']}/taxonomy/term/"
                obj["herausgeber"].append(
                    {
                        "id": f"p__{init_methods['pub_herausgeber']['data']['id']}",
                        "name": f"{escape(attr['name'])}",
                        "url": f"{init_methods['endpoint']}{pub_type}/{init_methods['pub_herausgeber']['data']['id']}",
                        "tid": attr['drupal_internal__tid'],
                        "rev_id": attr['drupal_internal__revision_id'],
                        "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                    }
                )
        except (KeyError, TypeError):
            print("No publication herausgeber found!")
        try:
            if type(init_methods['pub_author']) is list:
                for x in init_methods['pub_author']:
                    pub_type = x['data']['type'].replace('--', '/')
                    obj["author"] = []
                    attr = x['data']['attributes']
                    browser = f"{init_methods['browser']}/taxonomy/term/"
                    obj["author"].append(
                        {
                            "id": f"p__{x['data']['id']}",
                            "name": f"{escape(x['data']['attributes']['name'])}",
                            "url": f"{init_methods['endpoint']}{pub_type}/{x['data']['id']}",
                            "tid": attr['drupal_internal__tid'],
                            "rev_id": attr['drupal_internal__revision_id'],
                            "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                        }
                    )
            else:
                pub_type = init_methods['pub_author']['data']['type'].replace('--', '/')
                obj["author"] = []
                attr = init_methods['pub_author']['data']['attributes']
                browser = f"{init_methods['browser']}/taxonomy/term/"
                obj["author"].append(
                    {
                        "id": f"p__{init_methods['pub_author']['data']['id']}",
                        "name": f"{escape(attr['attributes']['name'])}",
                        "url": f"{init_methods['endpoint']}{pub_type}/{init_methods['pub_author']['data']['id']}",
                        "tid": attr['drupal_internal__tid'],
                        "rev_id": attr['drupal_internal__revision_id'],
                        "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                    }
                )
        except (KeyError, TypeError):
            print("No publication author(s) found!")
        try:
            if type(init_methods['pub_editors']) is list:
                for x in init_methods['pub_editors']:
                    pub_type = x['data']['type'].replace('--', '/')
                    obj["editor"] = []
                    browser = f"{init_methods['browser']}/taxonomy/term/"
                    attr = x['data']['attributes']
                    obj["editor"].append(
                        {
                            "id": f"p__{x['data']['id']}",
                            "name": f"{escape(x['data']['attributes']['name'])}",
                            "url": f"{init_methods['endpoint']}{pub_type}/{x['data']['id']}",
                            "tid": x['data']['attributes']['drupal_internal__tid'],
                            "rev_id": x['data']['attributes']['drupal_internal__revision_id'],
                            "browser_url": f"{browser}{x['drupal_internal__revision_id']}"
                        }
                    )
            else:
                pub_type = init_methods['pub_editors']['data']['type'].replace('--', '/')
                obj["editor"] = []
                attr = init_methods['pub_editors']['data']['attributes']
                browser = f"{init_methods['browser']}/taxonomy/term/"
                obj["editor"].append(
                    {
                        "id": f"p__{init_methods['pub_editors']['data']['id']}",
                        "name": f"{escape(init_methods['pub_editors']['data']['attributes']['name'])}",
                        "url": f"{init_methods['endpoint']}{pub_type}/{init_methods['pub_editors']['data']['id']}",
                        "tid": attr['drupal_internal__tid'],
                        "rev_id": attr['drupal_internal__revision_id'],
                        "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                    }
                )
        except (KeyError, TypeError):
            print("No publication editor(s) found!")
        try:
            if type(init_methods['pub_advisors']) is list:
                for x in init_methods['pub_advisors']:
                    pub_type = x['data']['type'].replace('--', '/')
                    obj["advisor"] = []
                    attr = x['data']['attributes']
                    browser = f"{init_methods['browser']}/taxonomy/term/"
                    obj["advisor"].append(
                        {
                            "id": f"p__{x['data']['id']}",
                            "name": f"{escape(attr['name'])}",
                            "url": f"{init_methods['endpoint']}{pub_type}/{x['data']['id']}",
                            "tid": attr['drupal_internal__tid'],
                            "rev_id": attr['drupal_internal__revision_id'],
                            "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                        }
                    )
            else:
                pub_type = init_methods['pub_advisors']['data']['type'].replace('--', '/')
                obj["advisor"] = []
                attr = init_methods['pub_advisors']['data']['attributes']
                browser = f"{init_methods['browser']}/taxonomy/term/"
                obj["advisor"].append(
                    {
                        "id": f"p__{init_methods['pub_advisors']['data']['id']}",
                        "name": f"{escape(init_methods['pub_advisors']['data']['attributes']['name'])}",
                        "url": f"{init_methods['endpoint']}{pub_type}/{init_methods['pub_advisors']['data']['id']}",
                        "tid": attr['drupal_internal__tid'],
                        "rev_id": attr['drupal_internal__revision_id'],
                        "browser_url": f"{browser}{attr['drupal_internal__revision_id']}"
                    }
                )
        except (KeyError, TypeError):
            print("No publication advisors(s) found!")
        return obj

    def __init__(
        self,
        manifestation_id=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        # level manifestation
        self.manifestation_id = manifestation_id
        self.manifestation_endpoint = f"{self.endpoint}node/manifestation/{manifestation_id}"
        self.manifestation = self.get_manifest()
        self.werk = self.manifestation['included'][0]
        self.author = self.get_fields_any('field_authors')
        self.repository = self.get_fields_any('field_aufbewahrungsort')
        self.repository_orig = self.get_fields_any('field_archive_original')
        self.advisors = self.get_fields_any('field_advisors')
        self.editors = self.get_fields_any('field_editors')
        self.herausgeber = self.get_fields_any('field_herausgeber')
        self.art = self.get_fields_any('field_art')
        self.font = self.get_fields_any('field_font')
        self.format = self.get_fields_any('field_format')
        self.mediatype = self.get_fields_any('field_mediatype')
        self.sprache = self.get_fields_any('field_sprache')
        self.type = self.get_fields_any('field_publication_type')
        self.edition = self.get_fields_any('field_edition')
        # first level publication
        self.publication = self.get_fields_any('field_published_in')
        self.pub_publisher = self.get_fields_any_any('field_publisher', self.publication)
        self.pub_herausgeber = self.get_fields_any_any('field_herausgeber', self.publication)
        self.pub_author = self.get_fields_any_any('field_authors', self.publication)
        self.pub_edition = self.get_fields_any_any('field_edition', self.publication)
        self.pub_advisors = self.get_fields_any_any('field_advisor', self.publication)
        self.pub_editors = self.get_fields_any_any('field_editors', self.publication)
        self.pub_type = self.get_fields_any_any('field_publication_type', self.publication)
        # 2nd level publication
        self.publication2 = self.get_fields_any_any('field_published_in', self.publication)
        self.pub2_publisher = self.get_fields_any_any('field_publisher', self.publication2)
        self.pub2_herausgeber = self.get_fields_any_any('field_herausgeber', self.publication2)
        self.pub2_author = self.get_fields_any_any('field_authors', self.publication2)
        self.pub2_edition = self.get_fields_any_any('field_edition', self.publication2)
        self.pub2_advisors = self.get_fields_any_any('field_advisor', self.publication2)
        self.pub2_editors = self.get_fields_any_any('field_editors', self.publication2)
        self.pub2_type = self.get_fields_any_any('field_publication_type', self.publication2)
        # 3rd level publication
        self.publication3 = self.get_fields_any_any('field_published_in', self.publication2)
        self.pub3_publisher = self.get_fields_any_any('field_publisher', self.publication3)
        self.pub3_herausgeber = self.get_fields_any_any('field_herausgeber', self.publication3)
        self.pub3_author = self.get_fields_any_any('field_authors', self.publication3)
        self.pub3_edition = self.get_fields_any_any('field_edition', self.publication3)
        self.pub3_advisors = self.get_fields_any_any('field_advisor', self.publication3)
        self.pub3_editors = self.get_fields_any_any('field_editors', self.publication3)
        self.pub3_type = self.get_fields_any_any('field_publication_type', self.publication3)
        self.werk_folder = self.werk['attributes']['path']['alias']
        self.manifestation_folder = self.manifestation['data']['attributes']['path']['alias']
        self.man_attrib = self.manifestation['data']['attributes']
        for x in self.man_attrib.keys():
            value = self.man_attrib[x]
            if isinstance(value, dict):
                for y in value.keys():
                    dict_key = f"{x}__{y}"
                    setattr(self, f"md__{dict_key}", value[y])
            else:
                setattr(self, f"md__{x}", value)
        self.meta_attributes = [x for x in dir(self) if x.startswith('md__')]
        self.pages = self.get_pages()
        self.page_count = len(self.pages)
        self.save_dir = os.path.join(self.out_dir)
        self.werk_signatur_hash = self.werk['relationships']['field_signatur_sfe']['data']['id']
        self.werk_signatur = self.get_fe_werk_signatur()
        self.manifestation_signatur = f"{self.werk_signatur}{self.man_attrib['field_signatur_sfe_type']}"
        self.file_name = f"sfe-{self.manifestation_signatur.replace('/', '__').replace('.', '_')}.xml"
        self.file_name_json = f"sfe-{self.manifestation_signatur.replace('/', '__').replace('.', '_')}.json"
        self.save_path = os.path.join(
            self.save_dir, self.werk_signatur, self.file_name
        )
        self.save_path_json = os.path.join(
            self.save_dir, self.werk_signatur, "data", self.file_name_json
        )


class FrdIndex(FrdClient):

    def make_index(self, save, dump, index_type):
        """serializes a person index as XML/TEI document

        :param save: if set, a XML/TEI file `{self.save_path}` is saved
        :param type: bool

        :return: A lxml.etree
        """
        index = self.get_index(dmp=dump, index_type=index_type)
        templateLoader = jinja2.PackageLoader(
            "freud_api_crawler", "templates"
        )
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(f'./{index_type}.xml')
        tei = template.render({"objects": [index]})
        tei = re.sub(r'\s+$', '', tei, flags=re.MULTILINE)
        tei = ET.fromstring(tei)
        if save:
            with open(os.path.join(self.save_dir, f'{index_type}.xml'), 'wb') as f:
                f.write(ET.tostring(tei, pretty_print=True, encoding="utf-8"))
        return tei

    def get_index(self, dmp, index_type):
        if dmp:
            r = requests.get(
                f"{self.endpoint}taxonomy_term/{index_type}",
                cookies=self.cookie,
                allow_redirects=True
            )
            result = r.json()
            data = result['data']
            index = {
                "data": []
            }
            if index_type == "personen":
                for x in data:
                    index['data'].append(
                        {
                            "name": escape(x['attributes']['name']),
                            "birthdate": x['attributes']['field_birthdate'],
                            "birthplace": x['attributes']['field_birthplace'],
                            "birthname": x['attributes']['field_birthname'],
                            "deathdate": x['attributes']['field_deathdate'],
                            "deathplace": x['attributes']['field_deathplace'],
                            "id": f"p__{x['id']}",
                            "tid": x['attributes']['drupal_internal__tid'],
                            "rev_id": x['attributes']['drupal_internal__revision_id'],
                            "field_name_id": x['attributes']['field_name_id'],
                            "url": f"{self.endpoint}taxonomy_term/personen/{x['id']}",
                            "browser_url": f"{self.browser}/taxonomy/term/{x['attributes']['drupal_internal__tid']}"
                        }
                    )
            elif index_type == "publisher":
                for x in data:
                    index['data'].append(
                        {
                            "name": escape(x['attributes']['name']),
                            "id": f"org__{x['id']}",
                            "tid": x['attributes']['drupal_internal__tid'],
                            "rev_id": x['attributes']['drupal_internal__revision_id'],
                            "url": f"{self.endpoint}taxonomy_term/personen/{x['id']}",
                            "browser_url": f"{self.browser}/taxonomy/term/{x['attributes']['drupal_internal__tid']}"
                        }
                    )
            elif index_type == "ort":
                for x in data:
                    index['data'].append(
                        {
                            "name": escape(x['attributes']['name']),
                            "id": f"place__{x['id']}",
                            "tid": x['attributes']['drupal_internal__tid'],
                            "rev_id": x['attributes']['drupal_internal__revision_id'],
                            "url": f"{self.endpoint}taxonomy_term/personen/{x['id']}",
                            "browser_url": f"{self.browser}/taxonomy/term/{x['attributes']['drupal_internal__tid']}"
                        }
                    )
            else:
                for x in data:
                    index['data'].append(
                        {
                            "name": escape(x['attributes']['name']),
                            "id": f"{index_type}__{x['id']}",
                            "tid": x['attributes']['drupal_internal__tid'],
                            "rev_id": x['attributes']['drupal_internal__revision_id'],
                            "url": f"{self.endpoint}taxonomy_term/personen/{x['id']}",
                            "browser_url": f"{self.browser}/taxonomy/term/{x['attributes']['drupal_internal__tid']}"
                        }
                    )
            os.makedirs(os.path.join(self.save_dir, "data"), exist_ok=True)
            with open(os.path.join(self.save_dir, 'data', f'{index_type}.json'), 'w', encoding='utf8') as f:
                json.dump(index, f)
        else:
            try:
                with open(os.path.join(self.save_dir, 'data', f'{index_type}.json'), 'r', encoding='utf8') as f:
                    index = json.load(f)
            except FileNotFoundError:
                print(f"file {os.path.join(self.save_dir, 'data', f'{index_type}.json')} not found, switching \
                    dump=True and restarting")
                index = self.get_index(dmp=True, index_type=index_type)
        return index

    def __init__(
        self,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.save_dir = os.path.join(self.out_dir)


def yield_works(url, simple=True):
    """ yields basic metadata from works

        :param url: The API-endpoint
        :param type: string

        :param simple: If True a processed dict is returned, otherwise the full data object
        :param type: bool

        :return: Yields a dict
        """
    next_page = True
    while next_page:
        print(url)
        response = None
        result = None
        x = None
        time.sleep(1)
        response = requests.get(
            url,
            cookies=AUTH_ITEMS['cookie'],
            allow_redirects=True
        )
        result = response.json()
        links = result['links']
        if links.get('next', False):
            orig_url = links['next']['href']
            url = always_https(orig_url)
        else:
            next_page = False
        for x in result['data']:
            if simple:
                yield x
            else:
                item = {}
                item['id'] = x['id']
                item['title'] = x['attributes']['title']
                item['nid'] = x['attributes']['drupal_internal__nid']
                item['vid'] = x['attributes']['drupal_internal__vid']
                item['path'] = x['attributes']['path']['alias']
                item['umschrift'] = x['attributes']['field_status_umschrift']
                yield item
