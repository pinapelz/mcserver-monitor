from flask import Flask, render_template
from flask_cors import CORS
import file_util
import server_handler
import os
from dotenv import dotenv_values, load_dotenv
import time
import random
import threading

load_dotenv()
app = Flask(__name__)
CORS(app)


ALREADY_ON_MESSAGE = os.getenv('ALREADY_ON_MESSAGE') or "The server is already on"
TURNING_ON_MESSAGE = os.getenv('TURNING_ON_MESSAGE') or "Now turning server on"
STATE_FILE_PATH = 'state_running' # static file that is in same dir as script
RCON_IP = os.getenv("RCON_IP")
RCON_PORT = os.getenv("RCON_PORT")
WARNING_MSG_1 = os.getenv("FIRST_WARNING") or "This is the first warning"
WARNING_MSG_2 = os.getenv("SECOND_WARNING") or "This is the second warning"
WARNING_MSG_FINAL = os.getenv("FINAL_WARNING") or "This is the final warning"
# Note that the time value is SECONDS UNTIL THE ACTION
TIME_TO_ACTION = int(os.getenv("TIME_TO_ACTION")) or 7200  # 2 hours in seconds
WARNING_TIME_1 = int(os.getenv("FIRST_WARNING_TIME")) or 1800
WARNING_TIME_2 = int(os.getenv("SECOND_WARNING_TIME")) or 600
WARNING_TIME_FINAL = int(os.getenv("SECOND_WARNING_TIME")) or 300
RANDOM_CHECK_TIME = random.randint(1, TIME_TO_ACTION)

file_util.create_file(STATE_FILE_PATH, default_val='false')


def server_monitor():
    timer = TIME_TO_ACTION
    print("Allowing for some startup time... (60 sec)")
    time.sleep(60)
    server_handler.announce_to_server("Now Listening....", RCON_IP, RCON_PORT)
    while True:
        time.sleep(1)
        timer = timer - 1
        if timer == WARNING_TIME_1:
            print(WARNING_MSG_1)
            server_handler.announce_to_server(WARNING_MSG_1, RCON_IP, RCON_PORT)
        elif timer == WARNING_TIME_2:
            print(WARNING_MSG_2)
            server_handler.announce_to_server(WARNING_MSG_2, RCON_IP, RCON_PORT)
        elif timer == WARNING_TIME_FINAL:
            print(WARNING_MSG_FINAL)
            server_handler.announce_to_server(WARNING_MSG_FINAL, RCON_IP, RCON_PORT)
        elif timer == RANDOM_CHECK_TIME:
            player_count = server_handler.get_player_count()
            if player_count == 0:
                server_handler.stop_server()
                file_util.set_file_contents(STATE_FILE_PATH, 'false')
                break
            print("Check Passes. There is at least 1 player on")
        elif timer == 0:
            file_util.set_file_contents(STATE_FILE_PATH, 'restarting')
            server_handler.execute_server_restart_routine()
            file_util.set_file_contents(STATE_FILE_PATH, 'start')
            timer = TIME_TO_ACTION

task_thread = threading.Thread(target=server_monitor)
task_thread.daemon = True


@app.route('/state', methods=['GET'])
def get_state():
    return file_util.get_file_contents()

@app.route('/request_on', methods=['GET'])
def request_on():
    if file_util.get_file_contents() == 'true':
        return ALREADY_ON_MESSAGE
    server_handler.start_server()
    file_util.set_file_contents(STATE_FILE_PATH, 'true')
    task_thread.start()
    return TURNING_ON_MESSAGE

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
