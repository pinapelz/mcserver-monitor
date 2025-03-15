from mcrcon import MCRcon
import re

def start_server():
    """
    Execute some shell script that turns the server on
    """
    pass # TODO: currently stubbed

def stop_server():
    """
    Execute some shell script that stops the server on
    """
    pass # TODO: currently stubbed


def execute_server_restart_routine():
    """
    Some routine to restart the server
    """
    pass

def announce_to_server(message: str, host: str, password:str,port: str):
    with MCRcon(host, password, port) as mcr:
        resp = mcr.command("say " + message)

def get_player_count(host, password, port):
    with MCRcon(host, password, port=port) as mcr:
        response = mcr.command("list")
    match = re.search(r"There are (\d+) of a maximum", response)
    if match:
        return int(match.group(1))
    else:
        print("Error: Could not parse player count from response.")
        return None
