import pokemon_pb2
from random import randint
import location
from google.protobuf.internal import encoder
from s2sphere import CellId
from s2sphere import LatLng


def simulate_walking(ses, cur_session):
    walk = pokemon_pb2.walk()
    walk.time = 2
    walk.rpc_id = 2212820743501119519-randint(0, 999)
    walk.unk1 = cur_session[1]
    walk.unk2 = cur_session[2]
    walk.unk3 = 0x4049000000000000
    # TODO:
    walk.sess.ses1 = ses.session_hash
    walk.sess.time = ses.session_live
    walk.sess.ses2 = ses.session_id
    walk.unknown12 = randint(0, 999999)

    req1 = walk.requests.add()
    req1.type = 106
    req1.message.unknown6 = cur_session[1]
    req1.message.unknown7 = cur_session[2]
    req2 = walk.requests.add()
    req2.type = 126
    req5 = walk.requests.add()
    req5.type = 4
    req3 = walk.requests.add()
    req3.type = 129
    req4 = walk.requests.add()
    req4.type = 5
    req4.message.unknown4 = '05daf51635c82611d1aac95c0b051d3ec088a930'
    return walk.SerializeToString()


def gen_stop_data_pre(ses, cur_session):
    stop_request = pokemon_pb2.stop_request()
    stop_request.time = 2
    stop_request.rpc_id = 2212820743501119519-randint(0, 999)
    stop_request.unk1 = cur_session[1]
    stop_request.unk2 = cur_session[2]
    stop_request.unk3 = 0x4049000000000000
    stop_request.sess.ses1 = ses.session_hash
    stop_request.sess.time = ses.session_live
    stop_request.sess.ses2 = ses.session_id
    stop_request.unknown12 = randint(0, 999999)

    req1 = stop_request.requests.add()
    req1.type = 104
    req1.message.unknown4 = cur_session[0]
    req1.message.unknown5 = cur_session[1]
    req1.message.unknown6 = cur_session[2]
    req2 = stop_request.requests.add()
    req2.type = 126
    req5 = stop_request.requests.add()
    req5.type = 4
    req3 = stop_request.requests.add()
    req3.type = 129
    req4 = stop_request.requests.add()
    req4.type = 5
    req4.message.unknown4 = '05daf51635c82611d1aac95c0b051d3ec088a930'
    return stop_request.SerializeToString()


def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)


def getNeighbors():
    origin = CellId.from_lat_lng(LatLng.from_degrees(
                 location.FLOAT_LAT, location.FLOAT_LONG)).parent(15)
    walk = [origin.id()]

    next = origin.next()
    prev = origin.prev()
    for i in range(10):
        walk.append(prev.id())
        walk.append(next.id())
        next = next.next()
        prev = prev.prev()
    return walk


def all_stops(cur_session):
    get_all = pokemon_pb2.get_all()
    walk = sorted(getNeighbors())
    get_all.unk1 = 2
    get_all.unk3 = 2212820743501119519 - randint(0, 999)
    get_all.unk12 = randint(0, 999999)
    lat, lon, fl = location.get_location_coords()

    req1 = get_all.b.add()
    req1.id = 106
    req1.c.msg = ''.join(map(encode, walk))
    req1.c.lat = lat
    req1.c.lon = lon
    req2 = get_all.b.add()
    req2.id = 126
    req5 = get_all.b.add()
    req5.id = 4
    req3 = get_all.b.add()
    req3.id = 129
    req4 = get_all.b.add()
    req4.id = 5
    req4.c.msg = '05daf51635c82611d1aac95c0b051d3ec088a930'

    get_all.sess.session_hash = cur_session.ses.session_hash
    get_all.sess.session_live = cur_session.ses.session_live
    get_all.sess.session_id = cur_session.ses.session_id
    get_all.unk7 = lat
    get_all.unk8 = lon
    get_all.unk9 = 0x4049000000000000
    return get_all.SerializeToString()


def gen_stop_data(ses, cur_session):
    stop_request = pokemon_pb2.stop_request()
    stop_request.time = 2
    stop_request.rpc_id = 2212820743501119519 - randint(0, 999)
    stop_request.unk1 = cur_session[1]
    stop_request.unk2 = cur_session[2]
    stop_request.unk3 = 0x4049000000000000
    stop_request.unknown12 = randint(0, 999999)
    stop_request.sess.ses1 = ses.session_hash
    stop_request.sess.time = ses.session_live
    stop_request.sess.ses2 = ses.session_id

    req1 = stop_request.requests.add()
    req1.type = 101
    req1.message.unknown4 = cur_session[0]
    req1.message.unknown5 = cur_session[1]
    req1.message.unknown6 = cur_session[2]
    req1.message.unknown7 = cur_session[1]
    req1.message.unknown8 = cur_session[2]
    req2 = stop_request.requests.add()
    req2.type = 126
    req5 = stop_request.requests.add()
    req5.type = 4
    req3 = stop_request.requests.add()
    req3.type = 129
    req4 = stop_request.requests.add()
    req4.type = 5
    req4.message.unknown4 = '05daf51635c82611d1aac95c0b051d3ec088a930'
    location.set_location_coords(location.l2f(cur_session[1]),
                                 location.l2f(cur_session[2]),
                                 location.l2f(0x4049000000000000))
    return stop_request.SerializeToString()


def gen_first_data(access_token, ltype):
    login_request = pokemon_pb2.login_request()
    login_request.time = 2
    login_request.unknown12 = randint(0, 999999)
    login_request.rpc_id = 72185515343874 - randint(0, 999)
    login_request.auth.provider = ltype
    login_request.auth.token.contents = access_token

    req1 = login_request.requests.add()
    req1.type = 2
    req2 = login_request.requests.add()
    req2.type = 126
    req3 = login_request.requests.add()
    req3.type = 4
    req4 = login_request.requests.add()
    req4.type = 129
    req5 = login_request.requests.add()
    req5.type = 5
    return login_request.SerializeToString()
