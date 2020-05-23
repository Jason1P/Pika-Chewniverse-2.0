import asyncio
import threading

import Logger
from AuthServer.Auth import Auth
from CLI import CLI
from CharacterServer.Character import Character
from ZoneServer.Zone import Zone

if __name__ == "__main__":
    Logger.logmanage()
    world_dict = {}
    auth = Auth(bind_ip="0.0.0.0", port=1001, max_connections=32, incoming_password=b"3.25 ND1", ssl=None)
    char = Character(bind_ip="0.0.0.0", port=1002, max_connections=32, incoming_password=b"3.25 ND1", ssl=None)

    avant_zone = Zone(bind_ip="0.0.0.0", port=2100, max_connections=32, incoming_password=b"3.25 ND1", ssl=None, zone_id="1100")
    world_dict['1100'] = avant_zone

    nimbus_zone = Zone(bind_ip="0.0.0.0", port=2200, max_connections=32, incoming_password=b"3.25 ND1", ssl=None, zone_id="1200")
    world_dict['1200'] = nimbus_zone

    chantey_zone = Zone(bind_ip="0.0.0.0", port=2350, max_connections=32, incoming_password=b"3.25 ND1", ssl=None, zone_id="1350")
    world_dict['1350'] = chantey_zone

    freeze_zone = Zone(bind_ip="0.0.0.0", port=2601, max_connections=32, incoming_password=b"3.25 ND1", ssl=None, zone_id="1601")
    world_dict['1601'] = freeze_zone

    cli = threading.Thread(target=CLI, args=(world_dict,))
    cli.start()

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
