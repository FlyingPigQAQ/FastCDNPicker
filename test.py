import geoip2.database

with geoip2.database.Reader('db/GeoLite2-Country.mmdb') as reader:
    resp=reader.country("101.200.142.87")
    print(resp.country.iso_code)