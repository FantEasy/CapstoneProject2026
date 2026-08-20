import subprocess
import csv
import re
import time

INTERFACE = "wlan0mon"
ROUTER_MAC = "32:ab:6a:68:e2:4a"
CSV_FILE = "rssi_log.csv"
SAMPLE_INTERVAL = 0.2 #5Hz

cmd = [
    "sudo",
    "tcpdump",
    "-l",
    "-i", INTERFACE,
    "-e",
    "-vvv",
    f"wlan type mgt subtype beacon and wlan addr3 {ROUTER_MAC}"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

pattern = re.compile(r"(-?\d+)dBm signal")

last_rssi = None
last_sample_time = time.time()

with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "rssi_dbm"])

    print("Logging RSSI... Press CTRL+C to stop")

    while True:
        # read line if available
        line = proc.stdout.readline()
        if line:
            match = pattern.search(line)
            if match:
                last_rssi = int(match.group(1))

        now = time.time()
        if now - last_sample_time >= SAMPLE_INTERVAL and last_rssi is not None:
            ts_str = time.strftime("%H:%M:%S", time.localtime(now)) + f".{int((now%1)*1000):03d}"
            writer.writerow([ts_str, last_rssi])
            f.flush()
            print(f"{ts_str} RSSI {last_rssi} dBm")

            last_sample_time = now
