import random

import os
from pycaenhv.wrappers import init_system, deinit_system, get_board_parameters, get_crate_map, get_channel_parameters
from pycaenhv import get_channel_parameter as caen_get_channel_parameter
from pycaenhv.enums import CAENHV_SYSTEM_TYPE, LinkType
from pycaenhv.errors import CAENHVError

def get_available_ports():
    """Get list of available ttyACM ports."""
    ports = []
    for i in range(10):  # Scan up to ttyACM9, can extend if needed
        port = f'/dev/ttyACM{i}'
        if os.path.exists(port):
            ports.append(f'ttyACM{i}')
    return ports


class HVControl:
    def __init__(self):
        """Initialize the controller with arbitrary number of devices and dynamic channels."""
        # First, get the available ports and their serial numbers
        available_ports = get_available_ports()

        if not available_ports:
            print("No CAEN devices found!")
            return
            
        print(f"Found {len(available_ports)} possible CAEN devices.")

        # Dictionary to store serial numbers and corresponding handles and numbers of channels
        self.device_numbers = []
        self.handles = dict()
        self.channels_per_device = dict()
        
        # Initialize systems for each available device and gather serial numbers
        for port in available_ports:
            print(f"Connecting to device on {port}...")
            system_type = CAENHV_SYSTEM_TYPE["DT55XXE"]
            link_type = LinkType["USB_VCP"]
            handle = init_system(system_type, link_type, f"{port}_115200_8_1_N_0")
            try:
                crate_map = get_crate_map(handle)
                serial_number = crate_map["serial_numbers"][0]
                num_channels = crate_map["channels"][0]
                self.device_numbers.append(serial_number)
                print(f"Got handle for device with serial number {serial_number} with {num_channels} channels: {handle}")
                self.handles[serial_number] = handle  # Store the handle using serial number as key
                self.channels_per_device[serial_number] = num_channels
            except CAENHVError as err:
                print(f"Got error: {err}\nExiting ...")
            finally:
                pass

        self.device_numbers = sorted(self.device_numbers)
        
    def get_channels_per_device(self, device_number):
        """Returns the number of channels for a specific device."""
        return self.channels_per_device[device_number] 

    def get_channel_parameter(self, device_number, channel, param):
        """Getter method for a specific channel parameter."""
        return caen_get_channel_parameter(self.handles[device_number], 0, channel, param)
        if param in ['VMon', 'IMon', 'ChStatus', 'Polarity']:
            # Randomly generate these parameters if they are being accessed
            if param == 'VMon':
                return round(random.uniform(0.0, 500.0), 2)
            elif param == 'IMon':
                return round(random.uniform(0.0, 5.0), 2)
            elif param == 'ChStatus':
                return "On" if random.random() > 0.5 else "Off"
            elif param == 'Polarity':
                return "Positive" if random.random() > 0.5 else "Negative"
        else:
            # Return the stored value for other parameters
            return 0

    def set_channel_parameter(self, device_number, channel, param, value):
        """Setter method for a specific channel parameter."""
        if param in ['VMon', 'IMon', 'ChStatus', 'Polarity']:
            # These parameters are read-only for simulation, do nothing
            print(f"{param} is read-only and cannot be set.")
        else:
            # Store the value for other parameters
            print(f"{param} is set to {value} for Channel {channel} on device {device_number}")

    def __del__(self):
        for serial_number in self.device_numbers:
            print(f"Deinitializing device with serial number {serial_number}.")
            deinit_system(handle=self.handles[serial_number])

