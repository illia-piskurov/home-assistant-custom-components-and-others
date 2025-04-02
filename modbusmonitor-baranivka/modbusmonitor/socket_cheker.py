import asyncio
from modbusclients import ModbusClient

class SocketChecker:
    async def check_failed(self, ip_addresses: list[ModbusClient]) -> list[ModbusClient]:
        check_results = await self.check(ip_addresses)
        return [address for (address, flag) in check_results if not flag]

    async def check(self, ip_addresses: list[ModbusClient]) -> list[tuple[ModbusClient, bool]]:
        check_results = []
        for address in ip_addresses:
            result = await self._is_port_open(address['tcpHost'], address['tcpPort'])
            check_results.append((address, result))
        return check_results

    async def _is_port_open(self, ip: str, port: int, timeout: float = 5.0) -> bool:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False