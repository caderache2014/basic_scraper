import requests
from bs4 import BeautifulSoup
import sys

def fetch_search_results(
        query=None, minAsk=None, maxAsk=None, bedrooms=None
        ):
        search_params = {
            key: val for key, val in locals().items() if val is not None
        }

        if not search_params:
            raise ValueError("No valid keywords")
        base = 'http://seattle.craigslist.org/search/apa'
        resp = requests.get(base, params=search_params, timeout=3)
        resp.raise_for_status() #no-op if status == 200
        return resp.content, resp.encoding

def read_search_results(fileName=None):
        with open(fileName, 'r') as infile:
            results = infile.read()
        encoding =  results.split('<')[0]
        content  = results
        return content, encoding

def parse_source(html, encoding='utf-8'):
        parsed = BeautifulSoup(html, from_encoding=encoding)
        return parsed

def fetch_json_results(**kwargs):
    base = 'http://seattle.craigslist.org/jsonsearch/apa'
    resp = requests.get(base, params=kwargs)
    resp.raise_for_status()
    return resp.json()

def add_location(listing, search):
    """True if listing can be located, False if not"""
    if listing['pid'] in search:
        match = search[listing['pid']]
        listing['location'] = {
            'data-latitude': match.get('Latitude', ''),
            'data-longitude': match.get('Longitude', ''),
        }
        return True
    return False

def add_address(listing):
    api_url = 'http://maps.googleapis.com/maps/api/geocode/json'
    loc = listing['location']
    latlng_tmpl = "{data-latitude},{data-longitude}"
    parameters = {
        'sensor': 'false',
        'latlng': latlng_tmpl.format(**loc),
    }
    resp = requests.get(api_url, params=parameters)
    resp.raise_for_status()  # <- this is a no-op if all is well
    data = resp.json()
    if data['status'] == 'OK':
        best = data['results'][0]
        listing['address'] = best['formatted_address']
    else:
        listing['address'] = 'unavailable'
    return listing

def extract_listings(parsed):
    listings = parsed.find_all('p', class_='row')
    for listing in listings:
        link = listing.find('span', class_='pl').find('a')
        price_span = listing.find('span', class_='price')
        this_listing = {
            'pid': listing.attrs.get('data-pid', ''),
            'link': link.attrs['href'],
            'description': link.string.strip(),
            'price': price_span.string.strip(),
            'size': price_span.next_sibling.strip(' \n-/')
        }
        yield this_listing

if __name__ == '__main__':
        import pprint
        if len(sys.argv) > 1 and sys.argv[1] == 'test':
            html, encoding = read_search_results('apartments.html')
        else:
            html, encoding = fetch_search_results(
                minAsk=500, maxAsk=3000, bedrooms=3
                )
        doc = parse_source(html, encoding)
        json_result = fetch_json_results(minAsk=500, maxAsk=3000, bedrooms=3)
        search = {j['PostingID']:j for j in json_result[0]}

        for listing in extract_listings(doc):
            if (add_location(listing, search)):
                listing = add_address(listing)
                print listing
                break
                pprint.pprint(listing)