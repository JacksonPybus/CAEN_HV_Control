#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from HVsemi import HVControl  # Import the HVControl class from HVsim.py

class HVControlUI:
    def __init__(self, root, hv_control):
        self.root = root
        self.root.title("HV Control Interface")
        self.hv_control = hv_control

        # Store previous values to support the Cancel button
        self.previous_values = {}

        # Create a frame for the channel parameters table
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=20, pady=20)

        # Create a Frame for the table of editable parameters
        self.table_frame = tk.Frame(self.frame)
        self.table_frame.grid(row=0, column=0)

        # Add buttons for Apply Changes, Cancel, and Refresh
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.apply_button = tk.Button(self.button_frame, text="Apply Changes", command=self.apply_changes)
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.cancel_changes)
        self.refresh_button = tk.Button(self.button_frame, text="Refresh", command=self.refresh_table)

        # Place the buttons in a horizontal row, equally spaced
        self.apply_button.grid(row=0, column=0, padx=5, pady=5)
        self.cancel_button.grid(row=0, column=1, padx=5, pady=5)
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5)

        # Initially populate the table with all channels (from all devices)
        self.update_table()

        # Continuously update read-only parameters every 100ms (10 Hz)
        self.continuous_update()

    def continuous_update(self):
        """Continuously update the read-only parameters (VMon, IMon, ChStatus, Polarity)."""
        self.update_read_only_cells()  # Only update the read-only cells
        self.root.after(100, self.continuous_update)  # Schedule the next update in 100 ms (10 Hz)

    def update_table(self, _=None):
        """Update the table to display all channels from all devices."""
        # Column labels for the table, with Pw being a boolean
        headers = ["Channel", "VSet", "VMon", "ISet", "IMon", "Pw", "ChStatus", "Polarity", "MaxV", "RUp", "RDwn", "Trip", "PDwn"]

        # Clear the existing table
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Create the headers dynamically based on the "headers" list
        for col_index, header in enumerate(headers):
            label = tk.Label(self.table_frame, text=header, width=8, borderwidth=2, relief="solid")
            label.grid(row=0, column=col_index, sticky="nsew")

        # Loop through all channels from all devices (2 devices, 4 channels each by default)
        row_index = 1
        for device_number in self.hv_control.device_numbers:
            for channel in range(self.hv_control.get_channels_per_device(device_number)):
                # Create a label for the channel number (non-editable)
                tk.Label(self.table_frame, text=f"{device_number}-{channel}", width=8, borderwidth=2, relief="solid").grid(row=row_index, column=0)

                # Create editable fields for the other parameters
                for col_index, param in enumerate(headers[1:]):
                    param_value = self.hv_control.get_channel_parameter(device_number, channel, param)

                    if param in ['VMon', 'IMon', 'ChStatus', 'Polarity']:  # These parameters are read-only
                        value = tk.Label(self.table_frame, text=f"{param_value:.1f}", width=8, borderwidth=2, relief="solid")
                        value.grid(row=row_index, column=col_index + 1)
                        # Store the label widget for later access
                        setattr(self, f"label_{device_number}_{channel}_{param}", value)

                    elif param == "Pw":  # Boolean field - "On" or "Off"
                        pw_value = "On" if param_value == 1 else "Off"

                        pw_button = tk.Button(self.table_frame, text=pw_value, width=8, command=lambda device=device_number, ch=channel, p=param: self.toggle_pw(device, ch, p))
                        pw_button.grid(row=row_index, column=col_index + 1)

                        # Store the button widget for later access
                        setattr(self, f"button_{device_number}_{channel}_{param}", pw_button)

                        # Save the initial value of the editable field to allow "Cancel" functionality
                        self.save_previous_values(device_number, channel, param, param_value)

                    else:
                        entry = tk.Entry(self.table_frame, width=8)  # Reduced width for alignment
                        entry.insert(0, param_value)
                        entry.grid(row=row_index, column=col_index + 1)
                        # Store the entry widget in a dictionary for later access
                        setattr(self, f"entry_{device_number}_{channel}_{param}", entry)

                        # Save the initial value of the editable field to allow "Cancel" functionality
                        self.save_previous_values(device_number, channel, param, param_value)

                row_index += 1

    def update_read_only_cells(self):
        """Update only the read-only cells (VMon, IMon, ChStatus, Polarity)."""
        for device_number in self.hv_control.device_numbers:
            for channel in range(self.hv_control.get_channels_per_device(device_number)):
                for param in ['VMon', 'IMon', 'ChStatus', 'Polarity']:
                    param_value = self.hv_control.get_channel_parameter(device_number, channel, param)
                    # Find the corresponding label widget for the read-only parameter and update its text
                    label_widget = getattr(self, f"label_{device_number}_{channel}_{param}", None)
                    if label_widget:
                        label_widget.config(text=f"{param_value:.1f}")

    def save_previous_values(self, device_number, channel, param, value):
        """Save the initial value of writable fields to allow cancellation of changes."""
        if device_number not in self.previous_values:
            self.previous_values[device_number] = {}
        if channel not in self.previous_values[device_number]:
            self.previous_values[device_number][channel] = {}
        self.previous_values[device_number][channel][param] = value

    def apply_changes(self):
        """Apply changes from the writable fields to the HVControl device."""
        # Loop through each channel and parameter and update the values
        for device_number in self.hv_control.device_numbers:
            for channel in range(self.hv_control.get_channels_per_device(device_number)):
                for param in ["VSet", "ISet", "MaxV", "RUp", "RDwn", "Trip", "PDwn", "Pw"]:
                    entry_widget = getattr(self, f"entry_{device_number}_{channel}_{param}", None)
                    button_widget = getattr(self, f"button_{device_number}_{channel}_{param}", None)

                    if entry_widget:
                        new_value = entry_widget.get()
                        if new_value != "":  # Skip empty entries
                            try:
                                new_value = float(new_value)
                                self.hv_control.set_channel_parameter(device_number, channel, param, new_value)
                            except ValueError:
                                messagebox.showerror("Invalid Input", f"Invalid input for {param} on Channel {channel}. Please enter a numeric value.")
                    elif button_widget:
                        new_value = button_widget.cget("text")  # Get the selected value ("On" or "Off")
                        self.hv_control.set_channel_parameter(device_number, channel, param, 1 if new_value == "On" else 0)

        self.update_table()

    def cancel_changes(self):
        """Cancel changes by reverting to the previous values."""
        for device_number in self.hv_control.device_numbers:
            for channel in range(self.hv_control.get_channels_per_device(device_number)):
                for param in ["VSet", "ISet", "MaxV", "RUp", "RDwn", "Trip", "PDwn", "Pw"]:
                    entry_widget = getattr(self, f"entry_{device_number}_{channel}_{param}", None)
                    button_widget = getattr(self, f"button_{device_number}_{channel}_{param}", None)
                    if entry_widget:
                        prev_value = self.previous_values.get(device_number, {}).get(channel, {}).get(param, None)
                        if prev_value is not None:
                            entry_widget.delete(0, tk.END)
                            entry_widget.insert(0, prev_value)
                    elif button_widget:
                        prev_value = self.previous_values.get(device_number, {}).get(channel, {}).get(param, None)
                        if prev_value is not None:
                            # For the button, we update the associated StringVar
                            button_var = getattr(self, f"button_{device_number}_{channel}_{param}", None)
                            print(button_var,prev_value)
                            if button_var:
                                prev_text = "On" if prev_value else "Off"
                                getattr(self, f"button_{device_number}_{channel}_{param}").config(text=prev_text)

    def refresh_table(self):
        """Refresh the entire table by pulling values from HVControl."""
        self.update_table()

    def toggle_pw(self, device_number, channel, param):
        # Retrieve the current button text
        current_value = getattr(self, f"button_{device_number}_{channel}_{param}").cget("text")
        
        # Toggle the value
        new_value = "Off" if current_value == "On" else "On"
        
        # Update the button's text to reflect the new value
        getattr(self, f"button_{device_number}_{channel}_{param}").config(text=new_value)
        
        # Save the new value to the device or the control system
        # You should update the parameter with the new value here
        #self.hv_control.set_channel_parameter(device_number, channel, param, 1 if new_value == "On" else 0)
        
        # Optionally, update internal tracking of the value
        #self.save_previous_values(device_number, channel, param, new_value == "On")


# Initialize the application
if __name__ == "__main__":
    root = tk.Tk()
    hv_control = HVControl()  # Create an HVControl object
    app = HVControlUI(root, hv_control)  # Pass the HVControl object to the UI
    root.mainloop()
