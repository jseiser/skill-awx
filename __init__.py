from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import aiohttp


class AWXSkill(Skill):
    async def _get_inventories(self, environment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][environment]["username"],
            password=self.config["sites"][environment]["username"],
        )
        api_url = self.config["sites"][environment]["url"]

        async with aiohttp.ClientSession(auth=auth) as session:
            response = await session.get(api_url)
        return response.json()

    @match_regex(r"^list inventory (?P<environment>\w+-\w+|\w+)")
    async def list_inventory(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_inventories(environment)

        await message.respond(f"{inventories}")
