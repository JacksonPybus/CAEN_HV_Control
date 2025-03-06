import random

class HVControl:
    def __init__(self):
        """Initialize the device with arbitrary number of devices and dynamic channels."""
        self.device_numbers = [1, 3]  # Example device serial numbers
        self.channels_per_device = {device: 4 for device in self.device_numbers}  # Default to 4 channels per device
        
        # Create a dictionary for each device and its channels
        self.channels = {
            device_number: {
                channel: {
                    'VSet': 0,
                    'VMon': 0,
                    'ISet': 0,
                    'IMon': 0,
                    'ImonRange': 0,
                    'MaxV': 0,
                    'RUp': 0,
                    'RDwn': 0,
                    'Trip': 0,
                    'PDwn': 0,
                    'Polarity': 0,
                    'ChStatus': 0,
                    'Pw': 0
                }
                for channel in range(self.get_channels_per_device(device_number))
            }
            for device_number in self.device_numbers
        }

    def get_channels_per_device(self, device_number):
        """Returns the number of channels for a specific device."""
        # For now, always return 4 channels per device (can be modified for different devices)
        return self.channels_per_device.get(device_number, 4)  # Default to 4 channels if device is not found

    def get_channel_parameter(self, device_number, channel, param):
        """Getter method for a specific channel parameter."""
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
            return self.channels[device_number][channel].get(param, 0)

    def set_channel_parameter(self, device_number, channel, param, value):
        """Setter method for a specific channel parameter."""
        if param in ['VMon', 'IMon', 'ChStatus', 'Polarity']:
            # These parameters are read-only for simulation, do nothing
            print(f"{param} is read-only and cannot be set.")
        else:
            # Store the value for other parameters
            print(f"{param} is set to {value} for Channel {channel} on device {device_number}")
            self.channels[device_number][channel][param] = value
