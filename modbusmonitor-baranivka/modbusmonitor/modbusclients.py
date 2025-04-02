import json
from pathlib import Path
from typing import TypedDict


class ModbusClient(TypedDict):
    name: str
    tcpHost: str
    tcpPort: str


def get_ip_addresses() -> list[ModbusClient]:
    current_dir = Path(__file__).parent
    file_path = current_dir / "modbus-clients.json"

    with file_path.open('r', encoding='utf-8') as clients_json:
        clients = json.load(clients_json)
        return clients
