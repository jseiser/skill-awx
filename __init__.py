from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import aiohttp


class AWXSkill(Skill):
    async def _get_inventories(self, environment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][environment]["username"],
            password=self.config["sites"][environment]["password"],
        )
        api_url = f"{self.config['sites'][environment]['url']}/api/v2/inventories/"

        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                for i in data["results"]:
                    print(i["id"])
                    print(i["name"])
                return "testing"

    @match_regex(r"^list inventory (?P<environment>\w+-\w+|\w+)")
    async def list_inventory(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_inventories(environment)
        data = {
            "text": "I am a test message http://slack.com",
            "attachments": [{"text": "And here’s an attachment!"}],
        }
        await message.respond(data)
