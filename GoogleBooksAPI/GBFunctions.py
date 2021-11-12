import json
import urllib
from urllib.request import urlopen
import PubVar


def fetch_query(qtype, query):
    if qtype == 'isbn':
        resp = urlopen(PubVar.API + PubVar.ISBNQUERY + query)
    else:
        query = urllib.parse.quote(query)
        resp = urlopen(PubVar.API + PubVar.TITLEQUERY + query)

    book_data = json.load(resp)
    volume_info = book_data["items"][0]["volumeInfo"]

    return volume_info
