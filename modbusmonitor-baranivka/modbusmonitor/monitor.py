import asyncio
import logging
from homeassistant.core import HomeAssistant
from .modbusclients import ModbusClient, get_ip_addresses
from .socket_cheker import SocketChecker
from .telegram_bot import TelegramBot
from httpx import HTTPStatusError
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)

failed_devices = set()

async def monitor(hass: HomeAssistant):
    config = hass.data[DOMAIN]
    tg_bot_token = config["tg_bot_token"]
    chat_id = config["chat_id"]
    message_fail = config["message_fail"]
    message_success = config["message_success"]

    checker = SocketChecker()
    bot = TelegramBot(tg_bot_token, hass)

    try:
        ip_addresses = get_ip_addresses()
        failed_list = await checker.check_failed(ip_addresses)

        current_failed_ips = {addr.get('tcpHost') for addr in failed_list}
        new_failures = [addr for addr in failed_list if addr.get('tcpHost') not in failed_devices]
        
        recovered_ips = failed_devices - current_failed_ips
        recovered_devices = [addr for addr in ip_addresses if addr.get('tcpHost') in recovered_ips]

        if new_failures:
            await send_messages(new_failures, message_fail, bot, chat_id)
            failed_devices.update(addr.get('tcpHost') for addr in new_failures)

        if recovered_devices:
            await send_messages(recovered_devices, message_success, bot, chat_id)
            failed_devices.difference_update(recovered_ips)

    except HTTPStatusError as e:
        _LOGGER.debug(f"HTTP error occurred: {e}")
    except Exception as e:
        _LOGGER.debug(f"An error occurred: {e}")

async def send_messages(addresses: list[ModbusClient], msg: str, bot: TelegramBot, chat_id: str) -> str:
    for address in addresses:
        message = f"{address.get('tcpHost')} - {address.get('name')} - {msg}"
        await bot.send_telegram_message(message, chat_id)

    return msg

# async def main():
#     while True:
#         await monitor({})
#         await asyncio.sleep(10)

# asyncio.run(main())