import config
from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
from google.protobuf.internal import encoder
from s2sphere import CellId
from s2sphere import LatLng
import math
from math import radians, cos, sin, asin, sqrt
import struct


LATITUDE = 0
LONGITUDE = 0
ALTITUDE = 0
FLOAT_LAT = 0
FLOAT_LONG = 0


def get_location_coords():
    return (LATITUDE, LONGITUDE, ALTITUDE)


def get_lat():
    return LATITUDE


def get_lot():
    return LONGITUDE


def set_lat(new):
    global LATITUDE
    LATITUDE = f2i(new)


def set_lot(new):
    global LONGITUDE
    LONGITUDE = f2i(new)


def set_location(location_name):
    geolocator = GoogleV3()
    loc = geolocator.geocode(location_name)

    print('[!] Your given location: {}'.format(loc.address.encode('utf-8')))
    set_location_coords(loc.latitude, loc.longitude, loc.altitude)


def set_location_coords(lat, long, alt):
    if config.debug:
        print('[!] lat/long/alt: {} {} {}'.format(lat, long, alt))
    global LATITUDE, LONGITUDE, ALTITUDE
    global FLOAT_LAT, FLOAT_LONG
    FLOAT_LAT = lat
    FLOAT_LONG = long
    LATITUDE = f2i(lat)
    LONGITUDE = f2i(long)
    ALTITUDE = f2i(alt)


def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)


def getNeighbors():
    origin = CellId.from_lat_lng(LatLng.from_degrees(FLOAT_LAT,
                                                     FLOAT_LONG)).parent(15)
    walk = [origin.id()]
    # 10 before and 10 after
    next = origin.next()
    prev = origin.prev()
    for i in range(10):
        walk.append(prev.id())
        walk.append(next.id())
        next = next.next()
        prev = prev.prev()
    return walk


def i2f(int):
    return struct.unpack('<Q', struct.pack('<d', int))[0]


def f2h(float):
    return hex(struct.unpack('<Q', struct.pack('<d', float))[0])


def f2i(float):
    return struct.unpack('<Q', struct.pack('<d', float))[0]


def l2f(float):
    return struct.unpack('d', struct.pack('Q', int(bin(float), 0)))[0]


def h2f(hex):
    return struct.unpack('<d', struct.pack('<Q', int(hex, 16)))[0]


def get_near(map):
    ms = []
    ms.append(('start', get_lat(), get_lot(),
               get_distance(get_lat(), get_lot(), LATITUDE, LONGITUDE)))
    for cell in [map]:
        for block in cell.b:
            for obj in block.c:
                for stop in obj.s:
                    ms.append((stop.name, stop.lat, stop.lon,
                               get_distance(stop.lat, stop.lon, LATITUDE,
                                            LONGITUDE)))
    return ms


def get_near_p(map):
    ms = []
    ms.append(('start', get_lat(), get_lot(), 'start', 'start',
               get_distance(get_lat(), get_lot(), LATITUDE, LONGITUDE)))
    for cell in [map]:
        for block in cell.b:
            for obj in block.c:
                for stop in obj.p:
                    ms.append((stop.t.type, stop.lat, stop.lon,
                               stop.name, stop.hash, get_distance(stop.lat,
                                                                  stop.lon,
                                                                  LATITUDE,
                                                                  LONGITUDE)))
    return ms


def move_to(lat1, lot1, lat2, lot2):
    if (lat1 > lat2):
        while(lat1 < lat2):
            lat1 = lat1 - 0.000095
    else:
        while(lat1 < lat2):
            lat1 = lat1 + 0.000095
    if (lot1 > lot2):
        while(lot1 > lot2):
            lot1 = lot1 - 0.000095
    else:
        while(lot2 > lot1):
            lot1 = lot1 + 0.000095
    return lat1, lot1, lat2, lot2


def distance(lat1, lon1, lat2, lon2):
    lat1 = l2f(lat1)
    lon1 = l2f(lon1)
    lat2 = l2f(lat2)
    lon2 = l2f(lon2)
    radius = 6371  # km *1000 m
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) \
        + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) \
        * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c * 1000
    return d < config.distance


def get_distance(lat1, lon1, lat2, lon2):
    lat1 = l2f(lat1)
    lon1 = l2f(lon1)
    lat2 = l2f(lat2)
    lon2 = l2f(lon2)
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    meter = 6367000 * c
    return meter


def haversine(lon1, lat1, lon2, lat2):
    lat1 = l2f(lat1)
    lon1 = l2f(lon1)
    lat2 = l2f(lat2)
    lon2 = l2f(lon2)
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r * 1000


def is_near(locx, locy, myx, myy):
    tmp1 = (l2f(locx), l2f(locy))
    tmp2 = (l2f(myx), l2f(myy))
    res = vincenty(tmp1, tmp2).meters
    return res < config.distance
