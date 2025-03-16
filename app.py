from flask import Flask, render_template
from flask_cors import CORS
import file_util
import server_handler
import os
from dotenv import load_dotenv
import time
import random
import threading

load_dotenv()
app = Flask(__name__)
CORS(app)

ALREADY_ON_MESSAGE = os.getenv('ALREADY_ON_MESSAGE', "The server is already on")
TURNING_ON_MESSAGE = os.getenv('TURNING_ON_MESSAGE', "Now turning server on")
STATE_FILE_PATH = 'state_running'  # static file that is in same dir as script
RCON_IP = os.getenv("RCON_IP")
RCON_PORT = int(os.getenv("RCON_PORT", 25575))
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
WARNING_MSG_1 = os.getenv("FIRST_WARNING", "This is the first warning")
WARNING_MSG_2 = os.getenv("SECOND_WARNING", "This is the second warning")
WARNING_MSG_FINAL = os.getenv("FINAL_WARNING", "This is the final warning")
TIME_TO_ACTION = int(os.getenv("TIME_TO_ACTION", 7200))  # 2 hours in seconds
WARNING_TIME_1 = int(os.getenv("FIRST_WARNING_TIME", TIME_TO_ACTION / 4))
WARNING_TIME_2 = int(os.getenv("SECOND_WARNING_TIME", TIME_TO_ACTION / 16))
WARNING_TIME_FINAL = int(os.getenv("FINAL_WARNING_TIME", 5))
PLAYER_CHECK_INTERVAL =int(os.getenv("PLAYER_CHECK_INTERVAL", 500)) # check every 5 seconds
START_SCRIPT_PATH = os.getenv("START_SCRIPT_PATH", "start.sh")
STOP_SCRIPT_PATH = os.getenv("STOP_SCRIPT_PATH", "stop.sh")
SERVER_NAME = os.getenv("SERVER_NAME", "My Server")

file_util.create_file(STATE_FILE_PATH, default_val='false')
timer = 0


def server_monitor():
    global timer
    timer = TIME_TO_ACTION
    time.sleep(30)
    print("[Monitor] READY now announcing start time we will restart every ", TIME_TO_ACTION)
    server_handler.announce_to_server(f"We will restart every {TIME_TO_ACTION} seconds ok?", RCON_IP, RCON_PASSWORD, RCON_PORT)
    while True:
        time.sleep(1)
        timer -= 1
        if timer == WARNING_TIME_1:
            print(WARNING_MSG_1)
            server_handler.announce_to_server(WARNING_MSG_1, RCON_IP, RCON_PASSWORD, RCON_PORT)
        elif timer == WARNING_TIME_2:
            print(WARNING_MSG_2)
            server_handler.announce_to_server(WARNING_MSG_2, RCON_IP, RCON_PASSWORD, RCON_PORT)
        elif timer == WARNING_TIME_FINAL:
            print(WARNING_MSG_FINAL)
            server_handler.announce_to_server(WARNING_MSG_FINAL, RCON_IP, RCON_PASSWORD, RCON_PORT)
        elif timer % PLAYER_CHECK_INTERVAL == 0:
            print("Current Time Remaining: ", timer)
            player_count = server_handler.get_player_count(RCON_IP, RCON_PASSWORD, RCON_PORT)
            if player_count == 0:
                print("NO PLAYERS! Shutting down...")
                server_handler.stop_server(STOP_SCRIPT_PATH)
                file_util.set_file_contents(STATE_FILE_PATH, 'false')
                break
            print("Check Passes. There is at least 1 player on")
        elif timer == 0:
            file_util.set_file_contents(STATE_FILE_PATH, 'false')
            server_handler.stop_server(STOP_SCRIPT_PATH)
            server_handler.start_server(START_SCRIPT_PATH)
            print("[Monitor] Giving the server some time to startup 30 sec")
            time.sleep(30)
            file_util.set_file_contents(STATE_FILE_PATH, 'true')
            timer = TIME_TO_ACTION


@app.route('/state', methods=['GET'])
def get_state():
    return file_util.get_file_contents(STATE_FILE_PATH)


@app.route('/request_on', methods=['GET'])
def request_on():
    if file_util.get_file_contents(STATE_FILE_PATH) == 'true':
        message = ALREADY_ON_MESSAGE
    else:
        server_handler.start_server(START_SCRIPT_PATH)
        file_util.set_file_contents(STATE_FILE_PATH, 'true')
        message = TURNING_ON_MESSAGE
    return render_template('request_on.html', server_name=SERVER_NAME, message=message)


@app.route('/')
def home():
    global timer
    state = file_util.get_file_contents(STATE_FILE_PATH)
    return render_template("index.html", status=state, server_name=SERVER_NAME, time_remaining=timer, player_interval=PLAYER_CHECK_INTERVAL)

def monitor_loop():
    print("[Monitor] Allowing for some startup time... (30 sec)")
    if file_util.get_file_contents(STATE_FILE_PATH) == 'false':
        server_handler.start_server(START_SCRIPT_PATH)
        file_util.set_file_contents(STATE_FILE_PATH, 'true')
    while True:
        if file_util.get_file_contents(STATE_FILE_PATH) == 'true':
            print("[Monitor Loop] Starting server monitor...")
            server_monitor()
        else:
            time.sleep(1)

def run_flask():
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    monitor_loop()
