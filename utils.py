from os import uname
from netifaces import interfaces, ifaddresses, AF_INET


#
# def is_root():
#     return os.geteuid() == 0

def is_rpi():
    try:
        import RPi.GPIO as GPIO
        # import serial
        test_environment = False
    except (ImportError, RuntimeError):
        test_environment = True
    return uname()[4][:3] == 'arm' and test_environment


is_rpi = is_rpi()

ip_addresses = {interface: ifaddresses(interface).get(AF_INET)
                for interface in interfaces()}.get('enp4s0', [{'addr': '192.168.1.110'}])[0].get('addr')
