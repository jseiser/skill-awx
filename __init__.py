from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import aiohttp


class AWXSkill(Skill):
    async def _get_inventories(self, environment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][environment]["username"],
            password=self.config["sites"][environment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = f"{self.config['sites'][environment]['url']}/api/v2/inventories/"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                return_text = "*Inventories*\n"
                data = await resp.json()
                for i in data["results"]:
                    return_text = f"{return_text}```{i['id']}{i['name']}```\n"
                return return_text

    async def _update_inventory(self, environment, inventory):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][environment]["username"],
            password=self.config["sites"][environment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = f"{self.config['sites'][environment]['url']}/api/v2/inventories/{inventory}/update_inventory_sources/"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.post(api_url) as resp:
                data = await resp.json()
                print(data)
                return data

    @match_regex(r"^list inventory (?P<environment>\w+-\w+|\w+)")
    async def list_inventory(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_inventories(environment)

        await message.respond(f"{inventories}")

    @match_regex(r"^update inventory (?P<environment>\w+-\w+|\w+) (?P<inventory>\d+)")
    async def update_inventory(self, message):
        environment = message.regex.group("environment")
        inventory = message.regex.group("inventory")
        update = await self._update_inventory(environment, inventory)

        await message.respond(f"{update}")
