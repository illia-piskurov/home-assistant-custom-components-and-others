import json
from typing import TypedDict


class ModbusClient(TypedDict):
    name: str
    tcpHost: str
    tcpPort: str


def get_ip_addresses() -> list[ModbusClient]:
    with open('modbus-clients.json', 'r', encoding='utf-8') as clients_json:
        clients = json.load(clients_json)
        return clients
