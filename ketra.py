import subprocess
import json
import os
from datetime import datetime
import time
import socket

class AndroidInfoGatherer:
    def __init__(self):
        self.device = None
        self.info = {}
        self.log_file = "android_info.log"

    def check_adb(self):
        """Check if ADB is installed and a device is connected"""
        try:
            devices = subprocess.check_output(['adb', 'devices']).decode().strip().split('\n')[1:]
            if len(devices) > 0 and devices[0]:
                self.device = devices[0].split('\t')[0]
                return True
            print("[!] No device connected")
            return False
        except:
            print("[!] Error: ADB not found. Please install Android SDK platform tools.")
            return False

    def get_basic_info(self):
        """Get basic device information"""
        try:
            info = {}
            
            # Android version
            info["android_version"] = subprocess.check_output(
                ['adb', 'shell', 'getprop', 'ro.build.version.release']
            ).decode().strip()
            
            # Device model
            info["model"] = subprocess.check_output(
                ['adb', 'shell', 'getprop', 'ro.product.model']
            ).decode().strip()
            
            # Brand
            info["brand"] = subprocess.check_output(
                ['adb', 'shell', 'getprop', 'ro.product.brand']
            ).decode().strip()
            
            # Device name
            info["device"] = subprocess.check_output(
                ['adb', 'shell', 'getprop', 'ro.product.device']
            ).decode().strip()
            
            # Security patch level
            info["security_patch"] = subprocess.check_output(
                ['adb', 'shell', 'getprop', 'ro.build.version.security_patch']
            ).decode().strip()
            
            self.info["basic_info"] = info
            return info
        except Exception as e:
            print(f"[!] Error getting basic info: {str(e)}")
            return None

    def get_system_info(self):
        """Get system information"""
        try:
            info = {}
            
            # CPU info
            info["cpu"] = subprocess.check_output(
                ['adb', 'shell', 'cat', '/proc/cpuinfo']
            ).decode().strip()
            
            # Memory info
            info["memory"] = subprocess.check_output(
                ['adb', 'shell', 'cat', '/proc/meminfo']
            ).decode().strip()
            
            # Storage info
            info["storage"] = subprocess.check_output(
                ['adb', 'shell', 'df']
            ).decode().strip()
            
            # Battery info
            info["battery"] = subprocess.check_output(
                ['adb', 'shell', 'dumpsys', 'battery']
            ).decode().strip()
            
            self.info["system_info"] = info
            return info
        except Exception as e:
            print(f"[!] Error getting system info: {str(e)}")
            return None

    def get_network_info(self):
        """Get network information"""
        try:
            info = {}
            
            # WiFi info
            info["wifi"] = subprocess.check_output(
                ['adb', 'shell', 'dumpsys', 'wifi']
            ).decode().strip()
            
            # IP address
            info["ip"] = subprocess.check_output(
                ['adb', 'shell', 'ip', 'addr', 'show']
            ).decode().strip()
            
            # Network stats
            info["network_stats"] = subprocess.check_output(
                ['adb', 'shell', 'dumpsys', 'netstats']
            ).decode().strip()
            
            self.info["network_info"] = info
            return info
        except Exception as e:
            print(f"[!] Error getting network info: {str(e)}")
            return None

    def get_installed_apps(self):
        """Get list of installed applications"""
        try:
            apps = subprocess.check_output(
                ['adb', 'shell', 'pm', 'list', 'packages', '-f']
            ).decode().strip().split('\n')
            
            self.info["installed_apps"] = apps
            return apps
        except Exception as e:
            print(f"[!] Error getting installed apps: {str(e)}")
            return None

    def get_security_info(self):
        """Get security information"""
        try:
            info = {}
            
            # SELinux status
            info["selinux"] = subprocess.check_output(
                ['adb', 'shell', 'getenforce']
            ).decode().strip()
            
            # Root status
            info["root"] = self.check_root_status()
            
            # Encryption status
            info["encryption"] = subprocess.check_output(
                ['adb', 'shell', 'getprop', 'ro.crypto.state']
            ).decode().strip()
            
            self.info["security_info"] = info
            return info
        except Exception as e:
            print(f"[!] Error getting security info: {str(e)}")
            return None

    def check_root_status(self):
        """Check if device is rooted"""
        try:
            # Check for su binary
            result = subprocess.run(
                ['adb', 'shell', 'which su'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.returncode == 0
        except:
            return False

    def save_info(self):
        """Save gathered information to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ketra_report_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(self.info, f, indent=4)
            print(f"[+] Information saved to {filename}")
            return True
        except Exception as e:
            print(f"[!] Error saving information: {str(e)}")
            return False

    def get_battery_info(self):
        """Get detailed battery information"""
        try:
            info = {}
            
            # Get battery stats
            battery_stats = subprocess.check_output(
                ['adb', 'shell', 'dumpsys', 'battery']
            ).decode().strip()
            
            # Parse important battery information
            for line in battery_stats.split('\n'):
                if 'level:' in line:
                    info['level'] = line.split(':')[1].strip() + '%'
                elif 'status:' in line:
                    info['status'] = line.split(':')[1].strip()
                elif 'health:' in line:
                    info['health'] = line.split(':')[1].strip()
                elif 'temperature:' in line:
                    # Convert temperature to Celsius
                    temp = float(line.split(':')[1].strip()) / 10
                    info['temperature'] = f"{temp}°C"
                elif 'technology:' in line:
                    info['technology'] = line.split(':')[1].strip()
                elif 'voltage:' in line:
                    voltage = float(line.split(':')[1].strip()) / 1000
                    info['voltage'] = f"{voltage}V"
                elif 'plugged:' in line:
                    info['charging'] = line.split(':')[1].strip() != '0'
                    
            self.info["battery_info"] = info
            return info
        except Exception as e:
            print(f"[!] Error getting battery info: {str(e)}")
            return None

    def get_open_ports(self):
        """Get information about open ports on the device"""
        try:
            info = {}
            
            # Get TCP ports
            tcp_ports = subprocess.check_output(
                ['adb', 'shell', 'netstat', '-tln']
            ).decode().strip()
            
            # Get UDP ports
            udp_ports = subprocess.check_output(
                ['adb', 'shell', 'netstat', '-uln']
            ).decode().strip()
            
            # Parse TCP ports
            tcp_list = []
            for line in tcp_ports.split('\n'):
                if 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        local_address = parts[3]
                        if ':' in local_address:
                            port = local_address.split(':')[-1]
                            try:
                                service = socket.getservbyport(int(port), 'tcp')
                            except:
                                service = 'unknown'
                            tcp_list.append({
                                'port': port,
                                'protocol': 'TCP',
                                'service': service,
                                'state': 'LISTENING'
                            })
            
            # Parse UDP ports
            udp_list = []
            for line in udp_ports.split('\n'):
                if ':' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        local_address = parts[3]
                        if ':' in local_address:
                            port = local_address.split(':')[-1]
                            try:
                                service = socket.getservbyport(int(port), 'udp')
                            except:
                                service = 'unknown'
                            udp_list.append({
                                'port': port,
                                'protocol': 'UDP',
                                'service': service,
                                'state': 'OPEN'
                            })
            
            info['tcp'] = tcp_list
            info['udp'] = udp_list
            self.info["open_ports"] = info
            return info
        except Exception as e:
            print(f"[!] Error getting port information: {str(e)}")
            return None

    def show_help(self):
        """Display help information and ADB connection instructions"""
        help_text = """
╔════════════════════ HELP ════════════════════╗
║                                              ║
║  ADB Connection Instructions:                ║
║  ────────────────────────────                ║
║  1. Enable Developer Options:                ║
║     • Go to Settings                         ║
║     • About Phone                            ║
║     • Tap Build Number 7 times               ║
║                                              ║
║  2. Enable USB Debugging:                    ║
║     • Go to Developer Options                ║
║     • Enable USB Debugging                   ║
║     • Enable USB debugging (Security)        ║
║                                              ║
║  3. Connect Device:                          ║
║     • Connect device via USB                 ║
║     • Accept USB debugging prompt            ║
║                                              ║
║  4. Verify Connection:                       ║
║     • Run 'adb devices'                      ║
║     • Device should be listed                ║
║                                              ║
║  Common ADB Commands:                        ║
║  ─────────────────────                       ║
║  • adb devices         - List devices        ║
║  • adb kill-server    - Reset ADB server     ║
║  • adb start-server   - Start ADB server     ║
║  • adb tcpip 5555     - Enable WiFi debug    ║
║                                              ║
║  Troubleshooting:                           ║
║  ────────────────                           ║
║  • Ensure USB debugging is enabled           ║
║  • Try different USB ports                   ║
║  • Restart ADB server                        ║
║  • Check USB cable                           ║
║  • Install ADB drivers                       ║
║                                              ║
╚══════════════════════════════════════════════╝
"""
        print(help_text)

def main():
    print("""
╔═══════════════════════════════════════════╗
║                 K E T R A                  ║
║         Android Information Tool           ║
║                                           ║
║  Author: kcyb3r                           ║
║  Version: 1.0                             ║
╚═══════════════════════════════════════════╝
    """)

    gatherer = AndroidInfoGatherer()
    
    if not gatherer.check_adb():
        return

    while True:
        print("\nKetra - Android Information Gatherer")
        print("==================================")
        print("1. Get Basic Device Info")
        print("2. Get System Info")
        print("3. Get Network Info")
        print("4. Get Installed Apps")
        print("5. Get Security Info")
        print("6. Check Battery Status")
        print("7. Check Open Ports")
        print("8. Get & Save All Information")
        print("9. Help")
        print("10. Exit")
        print("\nKetra > ", end='')
        
        choice = input()
        
        if choice == '1':
            info = gatherer.get_basic_info()
            if info:
                print("\nBasic Device Information:")
                for key, value in info.items():
                    print(f"{key}: {value}")
                    
        elif choice == '2':
            info = gatherer.get_system_info()
            if info:
                print("\nSystem Information:")
                print(f"CPU Info:\n{info['cpu']}\n")
                print(f"Memory Info:\n{info['memory']}\n")
                print(f"Storage Info:\n{info['storage']}\n")
                print(f"Battery Info:\n{info['battery']}")
                
        elif choice == '3':
            info = gatherer.get_network_info()
            if info:
                print("\nNetwork Information:")
                print(f"IP Configuration:\n{info['ip']}\n")
                
        elif choice == '4':
            apps = gatherer.get_installed_apps()
            if apps:
                print("\nInstalled Applications:")
                for app in apps:
                    print(app)
                    
        elif choice == '5':
            info = gatherer.get_security_info()
            if info:
                print("\nSecurity Information:")
                print(f"SELinux Status: {info['selinux']}")
                print(f"Root Status: {'Rooted' if info['root'] else 'Not Rooted'}")
                print(f"Encryption Status: {info['encryption']}")
                
        elif choice == '6':
            info = gatherer.get_battery_info()
            if info:
                print("\nBattery Information:")
                print("=" * 20)
                print(f"Battery Level: {info['level']}")
                print(f"Status: {info['status']}")
                print(f"Health: {info['health']}")
                print(f"Temperature: {info['temperature']}")
                print(f"Technology: {info['technology']}")
                print(f"Voltage: {info['voltage']}")
                print(f"Charging: {'Yes' if info['charging'] else 'No'}")
                
        elif choice == '7':
            info = gatherer.get_open_ports()
            if info:
                print("\nOpen Ports Information:")
                print("=" * 50)
                
                print("\nTCP Ports:")
                print("-" * 20)
                if info['tcp']:
                    for port in info['tcp']:
                        print(f"Port: {port['port']}/TCP")
                        print(f"Service: {port['service']}")
                        print(f"State: {port['state']}")
                        print("-" * 20)
                else:
                    print("No TCP ports found")
                
                print("\nUDP Ports:")
                print("-" * 20)
                if info['udp']:
                    for port in info['udp']:
                        print(f"Port: {port['port']}/UDP")
                        print(f"Service: {port['service']}")
                        print(f"State: {port['state']}")
                        print("-" * 20)
                else:
                    print("No UDP ports found")
                
        elif choice == '8':
            print("\n[*] Gathering all information...")
            
            # Gather all information
            basic = gatherer.get_basic_info()
            system = gatherer.get_system_info()
            network = gatherer.get_network_info()
            apps = gatherer.get_installed_apps()
            security = gatherer.get_security_info()
            battery = gatherer.get_battery_info()
            ports = gatherer.get_open_ports()
            
            # Save information
            if gatherer.save_info():
                print("[+] All information gathered and saved successfully")
                
                # Display summary
                print("\n=== Information Summary ===")
                if basic:
                    print(f"\nDevice: {basic.get('model', 'Unknown')} ({basic.get('brand', 'Unknown')})")
                    print(f"Android Version: {basic.get('android_version', 'Unknown')}")
                if security:
                    print(f"Root Status: {'Rooted' if security.get('root') else 'Not Rooted'}")
                if battery:
                    print(f"Battery Level: {battery.get('level', 'Unknown')}")
                    print(f"Charging: {'Yes' if battery.get('charging') else 'No'}")
                if ports:
                    print(f"Open TCP Ports: {len(ports['tcp'])}")
                    print(f"Open UDP Ports: {len(ports['udp'])}")
                if apps:
                    print(f"Installed Apps: {len(apps)}")
            else:
                print("[!] Error saving information")
            
        elif choice == '9':
            gatherer.show_help()
            
        elif choice == '10':
            print("\nExiting...")
            break
            
        else:
            print("\n[!] Invalid option")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Program interrupted by user")
    except Exception as e:
        print(f"\n[!] Error: {str(e)}")
