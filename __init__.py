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
                return_text = f"*{environment} - Inventories*\n"
                data = await resp.json()
                for i in data["results"]:
                    return_text = (
                        f"{return_text}```ID: {i['id']} Name: {i['name']}```\n"
                    )
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
                return_text = f"*{environment} - Inventory Update* \n"
                data = await resp.json()
                result = data[0]
                return_text = f"{return_text}```Status: {resp.status} State: {result['status']}```"
                return return_text

    async def _get_running_jobs(self, environment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][environment]["username"],
            password=self.config["sites"][environment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = (
            f"{self.config['sites'][environment]['url']}/api/v2/jobs/?status=running"
        )

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                if data["count"] > 0:
                    return_text = f"*{environment} - Running Jobs*\n"
                    for i in data["results"]:
                        return_text = f"{return_text}```Date: {i['started']} ID: {i['id']} Name: {i['name']} Playbook: {i['playbook']}```\n"
                else:
                    return_text = f"*{environment} - No Running Jobs*"
                return return_text

    async def _get_failed_jobs(self, environment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][environment]["username"],
            password=self.config["sites"][environment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = f"{self.config['sites'][environment]['url']}/api/v2/jobs/?status=failed&order_by=-started&page_size=5"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                if data["count"] > 0:
                    return_text = f"*{environment} - Last 5 Failed Jobs*\n"
                    for i in data["results"]:
                        return_text = f"{return_text}```Date: {i['started']} ID: {i['id']} Name: {i['name']} Playbook: {i['playbook']}```\n"
                else:
                    return_text = f"*{environment} - No Failed Jobs*"
                return return_text

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

    @match_regex(r"^list running jobs (?P<environment>\w+-\w+|\w+)")
    async def list_running_jobs(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_running_jobs(environment)

        await message.respond(f"{inventories}")

    @match_regex(r"^list failed jobs (?P<environment>\w+-\w+|\w+)")
    async def list_failed_jobs(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_failed_jobs(environment)

        await message.respond(f"{inventories}")
