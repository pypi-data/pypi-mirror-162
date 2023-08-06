import json
import aiohttp
from aiohttp import web
import configparser


async def get_url(config: configparser.ConfigParser):
    result = {"Healthy": True}

    async with aiohttp.ClientSession() as session:

        for section in config.sections():
            url = config[section]["url"]
            success_codes = json.loads(config.get(section, "success_codes"))
            return_message = config[section].getboolean("return_message")
            allow_redirects = config[section].getboolean("allow_redirects")
            timeout = config[section].getint("timeout")
            try:
                async with session.get(url, allow_redirects=allow_redirects, timeout=timeout) as resp:
                    body = await resp.read()
                    status_code = resp.status
                    if return_message == True:
                        result[section] = {"msg": body.decode(
                            'utf-8'), "status_code": status_code}
                    if not (resp.status in success_codes):
                        result["Healthy"] = False
            except web.HTTPException as e:
                print(e)
                result["Healthy"] = False
                if return_message == True:
                    result[section] = {"msg": e.text,
                                       "status_code": e.status_code}
            except Exception as e:
                print(e)
                result["Healthy"] = False
                if return_message == True:
                    result[section] = {"msg": str(e)}
    return result
