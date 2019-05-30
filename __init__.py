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

    async def _get_scheduled_jobs(self, environment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][environment]["username"],
            password=self.config["sites"][environment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = f"{self.config['sites'][environment]['url']}/api/v2/schedules/?enabled=true&order_by=next_run&page_size=5"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                if data["count"] > 0:
                    return_text = f"*{environment} - Next 5 Scheduled Jobs*\n"
                    for i in data["results"]:
                        return_text = f"{return_text}```Next Run: {i['next_run']} ID: {i['id']} Name: {i['name']}```\n"
                else:
                    return_text = f"*{environment} - No Scheduled Jobs*"
                return return_text

    async def _get_environments(self):
        sites = self.config["sites"]
        return_text = f"*AWX Environments*\n"
        for site in sites:
            return_text = f"{return_text}```Environment: {site} URL: {self.config['sites'][site]['url']}```\n"
        return return_text

    async def _get_help(self):
        return_text = f"*Help*\n"
        return_text = f"{return_text}```awx help - returns this help screen```\n"
        return_text = f"{return_text}```awx list environments - Returns Environment keywords and urls```\n"
        return_text = f"{return_text}```awx list inventory <environment> - Returns name and id for all inventories in specific environment```\n"
        return_text = f"{return_text}```awx update inventory <environment> <id> - Updates inventory sources for inventory in specific environment```\n"
        return_text = f"{return_text}```awx list running jobs <environment> - Returns information about running jobs for specific environment```\n"
        return_text = f"{return_text}```awx list failed jobs <environment> - Returns information about last 5 failed jobs for specific environment```\n"
        return_text = f"{return_text}```awx list scheduled jobs <environment> - Returns information about next 5 scheduled jobs for specific environment```\n"
        return return_text

    @match_regex(r"^awx list inventory (?P<environment>\w+-\w+|\w+)$")
    async def list_inventory(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_inventories(environment)

        await message.respond(f"{inventories}")

    @match_regex(
        r"^awx update inventory (?P<environment>\w+-\w+|\w+) (?P<inventory>\d+)$"
    )
    async def update_inventory(self, message):
        environment = message.regex.group("environment")
        inventory = message.regex.group("inventory")
        update = await self._update_inventory(environment, inventory)

        await message.respond(f"{update}")

    @match_regex(r"^awx list running jobs (?P<environment>\w+-\w+|\w+)$")
    async def list_running_jobs(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_running_jobs(environment)

        await message.respond(f"{inventories}")

    @match_regex(r"^awx list failed jobs (?P<environment>\w+-\w+|\w+)$")
    async def list_failed_jobs(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_failed_jobs(environment)

        await message.respond(f"{inventories}")

    @match_regex(r"^awx list scheduled jobs (?P<environment>\w+-\w+|\w+)$")
    async def list_scheduled_jobs(self, message):
        environment = message.regex.group("environment")
        inventories = await self._get_scheduled_jobs(environment)

        await message.respond(f"{inventories}")

    @match_regex(r"^awx list environments$")
    async def list_environments(self, message):
        inventories = await self._get_environments()

        await message.respond(f"{inventories}")

    @match_regex(r"^awx help$")
    async def list_help(self, message):
        inventories = await self._get_help()

        await message.respond(f"{inventories}")
