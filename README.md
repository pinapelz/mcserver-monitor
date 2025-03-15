# mcserver-monitor
A Minecraft server monitor for Linux for the following oddly specific conditions:
- You need the server every X interval
- You don't want the server running when there are no players, but anyone who wants to join must be able to turn the server back on
- You don't want to run a proxy between players and the server to detect players joining to turn the server back on (for various reasons), and instead prefer to use an HTTP request

Ok well this does that. However, you must bring your own `start.sh` and `stop.sh` scripts which should be shell scripts that starts and stops the server accordingly.
