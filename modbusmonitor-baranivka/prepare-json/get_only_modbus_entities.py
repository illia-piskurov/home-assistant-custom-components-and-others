import json

modbus_client_nodes = []

with open('flows.json', 'r', encoding='utf-8') as flows_data:
    nodes = json.load(flows_data)
    modbus_client_nodes = [node for node in nodes if node["type"] == 'modbus-client']

assert len(modbus_client_nodes) != 0, 'Count of modbus clients must be > 0'

with open('modbus-clients.json', 'w', encoding='utf-8') as f:
    json.dump(modbus_client_nodes, f, ensure_ascii=False, indent=4)

print(f'Count of modbus clients: {len(modbus_client_nodes)}')