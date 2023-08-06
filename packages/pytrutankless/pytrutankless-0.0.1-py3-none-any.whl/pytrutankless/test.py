import asyncio
import logging
import getpass

from pytrutankless.api import TruTanklessApiInterface

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

async def main():
    email = input("Enter your email: ").strip()
    password = getpass.getpass(prompt='Enter your password: ')
    api = await TruTanklessApiInterface.login(email, password)
    all_locations = await api._get_locations()
    print(all_locations)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())