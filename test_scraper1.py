import pytest
import scraper1 as s
import bs4

def test_extract_listings():
    html, encoding = s.read_search_results('apartments2.html')
    doc = s.parse_source(html, encoding)
    listings = s.extract_listings(doc)
    assert str(listings)[0] == '<'

def  test_add_address():
    html, encoding = s.read_search_results('apartments2.html')
    doc = s.parse_source(html, encoding)
    listings = s.extract_listings(doc)
    json_result =  s.fetch_json_results(minAsk=0, maxAsk=4000, bedrooms=3 )
    search = {j['PostingID']:j for j in json_result[0]}
    for listing in listings:
        if (s.add_location(listing, search)):
            listing = s.add_address(listing)
            assert "longitude" in str(listing)


def test_add_location():
    html, encoding = s.read_search_results('apartments2.html')
    doc = s.parse_source(html, encoding)
    json_result =  s.fetch_json_results(minAsk=0, maxAsk=4000, bedrooms=3 )
    search = {j['PostingID']:j for j in json_result[0]}
    listings = s.extract_listings(doc)
    for l in listings:
        assert  str(s.add_location(l, search)) is not None

def test_fetch_json_results():
    json_result = s.fetch_json_results(minAsk=0, maxAsk=4000, bedrooms=3)
    assert 'Ask' in str(json_result[0])

def test_parse_source():
    html, encoding = s.read_search_results('apartments2.html')
    doc = s.parse_source(html, encoding)
    query = '<'
    assert query in str(doc)

def test_read_search_results():
    html, encoding = s.read_search_results('apartments2.html')
    query = '<!DOCTYPE html>'
    assert query in html

def  test_fetch_search_results():
    html, encoding = s.fetch_search_results('beautiful+view', 0, 4000, 3)
    assert html
    assert type(html)
