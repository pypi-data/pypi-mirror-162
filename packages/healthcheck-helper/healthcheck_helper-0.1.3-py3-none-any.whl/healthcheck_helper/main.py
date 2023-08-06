#! /usr/bin/env python
import typer
import os
import uvicorn
import configparser
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from healthcheck_helper.lib.service import get_url

COMMAND_CONFIG_DIR = os.path.abspath(
    os.path.join(os.getcwd(), 'healthcheck.ini'))
RELATIVE_CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(
    __file__), 'healthcheck.ini'))

config_parser = configparser.ConfigParser()

app = FastAPI()


@app.get("/")
async def read_healthcheck():
    result = await get_url(config_parser)

    status_code = 200
    if result["Healthy"] == False:
        status_code = 503

    return JSONResponse(content=result, status_code=status_code)


def start_server(
        config: str = typer.Option(
            RELATIVE_CONFIG_DIR, help="Configuration file location."),
        host: str = typer.Option(
            "0.0.0.0", help="The host ip address to run the healthcheck."),
        port: int = typer.Option(8000, help="The port to run the healthcheck.")):
    """
    Run queries to multiple urls and return the results as healthcheck.
    """

    CLI_CONFIG_DIR = os.path.abspath(config)
    if not os.path.exists(CLI_CONFIG_DIR):
        print(CLI_CONFIG_DIR + " not found.")

    configs_read = config_parser.read([COMMAND_CONFIG_DIR, CLI_CONFIG_DIR])
    print("Using configuration from the following files: " + str(configs_read))

    sections = config_parser.sections()
    print("running queries to the following endpoints " + str(sections))
    uvicorn.run(app, host=host, port=port)


def main():
    typer.run(start_server)


if __name__ == "__main__":
    typer.run(main)
