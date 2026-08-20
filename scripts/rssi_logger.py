from scapy.all import sniff
from scapy.layers.dot11 import Dot11, RadioTap
import csv
import time

# === CONFIGURATION ===
CSV_FILE = "/home/tamer/rssi_log.csv"   # Where the data will be saved
MONITOR_IFACE = "wlan0mon"           # Your monitor-mode interface
TARGET_BSSID = "8c:86:dd:03:7d:93"   # Replace with your TX MAC address
SAMPLE_RATE_HZ = 5                   # Number of samples per second
# =====================

sample_interval = 1 / SAMPLE_RATE_HZ
last_time = 0

# Open CSV file in append mode so data persists
with open(CSV_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    # Write header if file is empty
    f.seek(0, 2)  # move to end of file
    if f.tell() == 0:
        writer.writerow(["timestamp", "bssid", "rssi", "channel"])

    # Packet handler for sniff()
    def packet_handler(pkt):
        global last_time
        now = time.time()

        # Limit sample rate
        if now - last_time < sample_interval:
            return
        last_time = now

        # Filter for 802.11 packets with our target BSSID
        if pkt.haslayer(Dot11):
            pkt_bssid = pkt.addr2
            if pkt_bssid and pkt_bssid.lower() == TARGET_BSSID.lower():
                # Read RSSI from radiotap header (dBm)
                rssi = getattr(pkt, "dBm_AntSignal", None)
                # Optional: channel info if available
                channel = getattr(pkt[RadioTap], "ChannelFrequency", None)
                timestamp = now

                # Write to CSV
                writer.writerow([timestamp, pkt_bssid, rssi, channel])
                f.flush()  # ensure data is saved immediately

                # Print to terminal for live monitoring
                print(f"{timestamp:.2f} | {pkt_bssid} | RSSI={rssi} dBm | channel={channel}")
    sniff(iface=MONITOR_IFACE, prn=packet_handler, store=False)
