import time
import requests
import freud_api_crawler.freud_api_crawler as frd
from freud_api_crawler.string_utils import always_https


class FrdPerson(frd.FrdClient):

    """class to interact with person endpoint"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.person_ep = f"{self.endpoint}taxonomy_term/personen"

    def yield_persons(self):
        """ iterates through person endpoint and yields dict with some data """
        counter = 1
        url = self.person_ep
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
                item = {}
                item['id'] = f"frd_person_{counter:05}"
                item['drupal_hash'] = x['id']
                for y in [
                    'drupal_internal__tid',
                    'name',
                ]:
                    item[y] = x['attributes'][y]
                counter += 1
                yield(item)
