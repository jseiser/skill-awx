from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import aiohttp
import datetime


class AWXSkill(Skill):
    async def _get_inventories(self, deployment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][deployment]["username"],
            password=self.config["sites"][deployment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = f"{self.config['sites'][deployment]['url']}/api/v2/inventories/"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                return_text = f"*{deployment} - Inventories*\n"
                data = await resp.json()
                for i in data["results"]:
                    return_text = (
                        f"{return_text}```ID: {i['id']} Name: {i['name']}```\n"
                    )
                return return_text

    async def _update_inventory(self, deployment, inventory):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][deployment]["username"],
            password=self.config["sites"][deployment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = f"{self.config['sites'][deployment]['url']}/api/v2/inventories/{inventory}/update_inventory_sources/"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.post(api_url) as resp:
                return_text = f"*{deployment} - Inventory Update* \n"
                data = await resp.json()
                result = data[0]
                return_text = f"{return_text}```Status: {resp.status} State: {result['status']}```"
                return return_text

    async def _get_running_jobs(self, deployment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][deployment]["username"],
            password=self.config["sites"][deployment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = (
            f"{self.config['sites'][deployment]['url']}/api/v2/jobs/?status=running"
        )

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                if data["count"] > 0:
                    return_text = f"*{deployment} - Running Jobs*\n"
                    for i in data["results"]:
                        return_text = f"{return_text}```Date: {i['started']} ID: {i['id']} Name: {i['name']} Playbook: {i['playbook']}```\n"
                else:
                    return_text = f"*{deployment} - No Running Jobs*"
                return return_text

    async def _get_failed_jobs(self, deployment, num=5, yesterday=None):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][deployment]["username"],
            password=self.config["sites"][deployment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        if yesterday:
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            start_time = yesterday.isoformat()
            api_url = f"{self.config['sites'][deployment]['url']}/api/v2/jobs/?status=failed&order_by=-started&started__gt={start_time}&page_size=100"
        else:
            api_url = f"{self.config['sites'][deployment]['url']}/api/v2/jobs/?status=failed&order_by=-started&page_size={num}"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                if data["count"] > 0:
                    return_text = f"*{deployment} - Failed Jobs*\n"
                    for i in data["results"]:
                        return_text = f"{return_text}```Date: {i['started']} ID: {i['id']} Name: {i['name']} Playbook: {i['playbook']}```\n"
                else:
                    return_text = f"*{deployment} - No Failed Jobs*"
                return return_text

    async def _get_scheduled_jobs(self, deployment, num=5):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][deployment]["username"],
            password=self.config["sites"][deployment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        api_url = f"{self.config['sites'][deployment]['url']}/api/v2/schedules/?enabled=true&order_by=next_run&page_size={num}"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                if data["count"] > 0:
                    return_text = f"*{deployment} - Next 5 Scheduled Jobs*\n"
                    for i in data["results"]:
                        return_text = f"{return_text}```Next Run: {i['next_run']} ID: {i['id']} Name: {i['name']}```\n"
                else:
                    return_text = f"*{deployment} - No Scheduled Jobs*"
                return return_text

    async def _get_scheduled_jobs_past(self, deployment):
        auth = aiohttp.BasicAuth(
            login=self.config["sites"][deployment]["username"],
            password=self.config["sites"][deployment]["password"],
        )
        timeout = aiohttp.ClientTimeout(total=60)
        today = datetime.datetime.now()
        next_run = today.isoformat()
        api_url = f"{self.config['sites'][deployment]['url']}/api/v2/schedules/?enabled=true&order_by=next_run&next_run__lt={next_run}&page_size=20"

        async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                if data["count"] > 0:
                    return_text = f"*{deployment} - Past Scheduled Jobs*\n"
                    for i in data["results"]:
                        return_text = f"{return_text}```Next Run: {i['next_run']} ID: {i['id']} Name: {i['name']}```\n"
                else:
                    return_text = f"*{deployment} - No Scheduled Jobs*"
                return return_text

    async def _get_deployments(self):
        sites = self.config["sites"]
        return_text = f"*AWX Deployments*\n"
        for site in sites:
            return_text = f"{return_text}```Deployment: {site} URL: {self.config['sites'][site]['url']}```\n"
        return return_text

    async def _get_help(self):
        return_text = f"*Help*\n"
        return_text = f"{return_text}```awx help - returns this help screen```\n"
        return_text = f"{return_text}```awx list deployments - Returns Deployment keywords and urls```\n"
        return_text = f"{return_text}```awx <deployment> list inventory  - Returns name and id for all inventories in specific deployment```\n"
        return_text = f"{return_text}```awx <deployment> update inventory  <id> - Updates inventory sources for inventory in specific deployment```\n"
        return_text = f"{return_text}```awx <deployment> list running jobs  - Returns information about running jobs for specific deployment```\n"
        return_text = f"{return_text}```awx <deployment> list failed jobs  - Returns information about last 5 failed jobs for specific deployment```\n"
        return_text = f"{return_text}```awx <deployment> list failed jobs yesterday  - Returns information about last 24 hours of failed jobs for specific deployment```\n"
        return_text = f"{return_text}```awx <deployment> list failed jobs  num:<#> - Returns information about last # failed jobs for specific deployment```\n"
        return_text = f"{return_text}```awx <deployment> list scheduled jobs  - Returns information about next 5 scheduled jobs for specific deployment```\n"
        return_text = f"{return_text}```awx <deployment> list scheduled jobs num:<#> - Returns information about next # scheduled jobs for specific deployment```\n"
        return_text = f"{return_text}```awx <deployment> list scheduled jobs past - Returns information about  scheduled jobs with next_run in the past```\n"
        return return_text

    # being Matching Functions

    @match_regex(r"^awx (?P<deployment>\w+-\w+|\w+) list inventory$")
    async def list_inventory(self, message):
        deployment = message.regex.group("deployment")
        inventories = await self._get_inventories(deployment)

        await message.respond(f"{inventories}")

    @match_regex(
        r"^awx (?P<deployment>\w+-\w+|\w+) update inventory (?P<inventory>\d+)$"
    )
    async def update_inventory(self, message):
        deployment = message.regex.group("deployment")
        inventory = message.regex.group("inventory")
        update = await self._update_inventory(deployment, inventory)

        await message.respond(f"{update}")

    @match_regex(r"^awx (?P<deployment>\w+-\w+|\w+) list running jobs$")
    async def list_running_jobs(self, message):
        deployment = message.regex.group("deployment")
        inventories = await self._get_running_jobs(deployment)

        await message.respond(f"{inventories}")

    @match_regex(r"^awx (?P<deployment>\w+-\w+|\w+) list failed jobs$")
    async def list_failed_jobs(self, message):
        deployment = message.regex.group("deployment")
        inventories = await self._get_failed_jobs(deployment)

        await message.respond(f"{inventories}")

    @match_regex(r"^awx (?P<deployment>\w+-\w+|\w+) list failed jobs yesterday$")
    async def list_failed_jobs_yesterday(self, message):
        deployment = message.regex.group("deployment")
        inventories = await self._get_failed_jobs(deployment, yesterday=True)

        await message.respond(f"{inventories}")

    @match_regex(
        r"^awx (?P<deployment>\w+-\w+|\w+) list failed jobs num: (?P<num>\d+)$"
    )
    async def list_failed_jobs_num(self, message):
        deployment = message.regex.group("deployment")
        num = message.regex.group("num")
        inventories = await self._get_failed_jobs(deployment, num)

        await message.respond(f"{inventories}")

    @match_regex(r"^awx (?P<deployment>\w+-\w+|\w+) list scheduled jobs$")
    async def list_scheduled_jobs(self, message):
        deployment = message.regex.group("deployment")
        inventories = await self._get_scheduled_jobs(deployment)

        await message.respond(f"{inventories}")

    @match_regex(
        r"^awx (?P<deployment>\w+-\w+|\w+) list scheduled jobs num: (?P<num>\d+)$"
    )
    async def list_scheduled_jobs_num(self, message):
        deployment = message.regex.group("deployment")
        num = message.regex.group("num")
        inventories = await self._get_scheduled_jobs(deployment, num)

        await message.respond(f"{inventories}")

    @match_regex(r"^awx (?P<deployment>\w+-\w+|\w+) list scheduled jobs past$")
    async def list_scheduled_jobs_past(self, message):
        deployment = message.regex.group("deployment")
        inventories = await self._get_scheduled_jobs_past(deployment)

        await message.respond(f"{inventories}")

    @match_regex(r"^awx list deployments$")
    async def list_deployments(self, message):
        inventories = await self._get_deployments()

        await message.respond(f"{inventories}")

    @match_regex(r"^awx help$")
    async def list_help(self, message):
        inventories = await self._get_help()

        await message.respond(f"{inventories}")
