import subprocess

class NetworkConfig:
    def __init__(self):
        pass

    def get_interfaces(self):
        try:
            result = subprocess.run(["ls", "/sys/class/net"], capture_output=True, text=True, check=True)
            interfaces = result.stdout.split()
            return interfaces
        except subprocess.CalledProcessError as e:
            return []

    def set_static_ip(self, interface, ip_address, netmask, gateway):
        try:
            subprocess.run(["sudo", "ifconfig", interface, ip_address, "netmask", netmask], check=True)
            subprocess.run(["sudo", "route", "add", "default", "gw", gateway, interface], check=True)
            return f"Static IP {ip_address} set on interface {interface}"
        except subprocess.CalledProcessError as e:
            return f"Failed to set static IP: {e}"

    def set_dhcp(self, interface):
        try:
            subprocess.run(["sudo", "dhclient", interface], check=True)
            return f"DHCP configured on interface {interface}"
        except subprocess.CalledProcessError as e:
            return f"Failed to set DHCP: {e}"

    def set_dns(self, dns_servers):
        try:
            resolv_conf = "/etc/resolv.conf"
            with open(resolv_conf, "w") as f:
                for dns in dns_servers:
                    f.write(f"nameserver {dns}\n")
            return f"DNS servers set: {', '.join(dns_servers)}"
        except Exception as e:
            return f"Failed to set DNS servers: {e}"
