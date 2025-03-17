from mcrcon import MCRcon
import re
import subprocess

def execute_shell_command(command: str):
    """
    Execute a given shell command and return the output
    """
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def start_server(script_path: str):
    """
    Execute some shell script that turns the server on
    """
    print("Triggered server start routine!")
    execute_shell_command(script_path)

def stop_server(script_path: str):
    """
    Execute some shell script that stops the server on
    """
    print("Triggered server stop routine!")
    execute_shell_command(script_path)

def announce_to_server(message: str, host: str, password:str,port: str):
    with MCRcon(host, password, port) as mcr:
        resp = mcr.command("say " + message)
    return resp

def get_player_count(host, password, port):
    with MCRcon(host, password, port=port) as mcr:
        response = mcr.command("list")
        print(response)
        match = re.search(r"There are (\d+) of a max of \d+ players online", response)
    if match:
        return int(match.group(1))
    else:
        print("Error: Could not parse player count from response.")
        return None
