import serial
import time
import pandas as pd


class RFIDReader:

    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate)

    def connect(self):
        if not self.ser.is_open:
            self.ser.open()

    def disconnect(self):
        if self.ser.is_open:
            self.ser.close()

    def send_command(self, cmd):
        '''
        Builds and sends a command to the serial port.
    
        Parameters:
        self (serial.Serial): The serial port object.
        cmd (bytearray): The command to send.

        :return: The device response (byte array)
        '''
        SOF = b'\xA5\x5A'
        EOF = b'\x0D\x0A'

        timeout = 10 # Timeout in seconds

        length = len(cmd) + 7
        crc = calculate_crc(length.to_bytes(2, byteorder='big') + cmd)
        cmd = SOF + length.to_bytes(2, byteorder='big') + cmd + crc + EOF
        self.ser.write(cmd)

        start_time = time.time()
        while not self.ser.in_waiting:
            if (time.time() - start_time) > timeout:
                print("Timeout waiting for response")
                return b''

        response = self.ser.read_until(b'\r\n')
        while (len(response) > 4) and (response[4] != (cmd[4]+1)):
            response = self.ser.read_until(b'\r\n')

        return response

    
    def set_power(self, pwr, save=False):
        """
        Set device read power in dBm.

        Parameters: 
        pwr (float): The power value in dBm (range 1.0dBm to 30.0dBm).
        save (bool): If True, saves the configuration to NVM. Defaults to False.

        Returns:
        response: The device response, bytearray.
        """
        if not (1.0 <= pwr <= 30.0):
            raise ValueError("Power level must be between 1.0 and 30.0 dBm")

        cmd = b'\x10'
        if save:
            NVM = b'\x20\x01'
        else:
            NVM = b'\x00\x01'
        
        read_pwr = dbm_to_hex(pwr)

        cmd = cmd + NVM + read_pwr + read_pwr
        
        response = self.send_command(cmd)

        if response[4:6] == b'\x11\x01':
            print("Power set. ")
        else:
            print("Error. ")
        
        return response
    
    def get_power(self):
        """
        Get the device read power configuration.

        Parameters: 
        None

        Returns:
        pwr (float): The device power configuration in dBm.
        """
        cmd = b'\x12'
        response = self.send_command(cmd)

        pwr = hex_to_dbm(response[7:9])

        return pwr
    
    def set_antenna(self, ant_1=True, ant_2=True, ant_3=True, ant_4=True, save=False):
        """
        Activate/deactivate antennas.

        Parameters: 
        ant_1, ant_2, ant_3, ant_4 (bool): Antenna on/off values. All activated by default.
        save (bool): save (bool): If True, saves the configuration to NVM. Defaults to False.

        Returns:
        response: The device response, bytearray.
        """
        cmd = b'\x28'
        ant = bytes([(ant_1 << 0) | (ant_2 << 1) | (ant_3 << 2) | (ant_4 << 3)])
        cmd = cmd + b'\x00\x00' + ant

        response = self.send_command(cmd)

        return response

    def set_gen2_params(self, target, action):
        """
        **TODO**
        Set the device Gen2 parameters.

        Parameters: 
        None

        Returns:
        response: The device response, bytearray.
        """
        cmd = b'\x20'

        response = self.send_command(cmd)

        return response


    def get_gen2_params(self):
        """
        Set the device Gen2 parameters.

        Parameters: 
        None

        Returns:
        response: The device Gen2 configuration.
        """
        cmd = b'\x22'

        response = self.send_command(cmd)

        return response

    def set_RF_mode(self, mode, save=False):
        """
        Set device RF link mode.

        Parameters: 
        mode (int): 0 -> DSB_ASK /FM0/ 40 KHz
                    1 -> PR _ASK /Miller4/ 250KHz
                    2 -> PR _ASK /Miller4/ 300KHz
                    3 -> DSB_ASK /FM0/ 400KHz
        save (bool): If True, saves the configuration to NVM. Defaults to False.

        Returns:
        response: The device response, bytearray.
        """
        cmd = b'\x52'
        
        if save:
            cmd = cmd + b'\x00\x01'
        else:
            cmd = cmd + b'\x00\x00'

        match mode:
            case 0:
                cmd = cmd + b'\x00'
            case 1:
                cmd = cmd + b'\x01'
            case 2:
                cmd = cmd + b'\x02'
            case 3:
                cmd = cmd + b'\x03'      

        response = self.send_command(cmd)

        return response

    def get_RF_mode(self):
        """
        Get device RF link mode.

        Parameters: 
        None

        Returns:
        response (str): The device RF configuration.
        """
        cmd = b'\x54\x00\x00'
        
        response = self.send_command(cmd)

        mode = int(response[7])

        return mode

    def read_start(self, cycles):
        """
        Perform multiple Tag reads.
        Note: Device will not receive other commands while performing an inventory read. 

        Parameters: 
        cycles (int): The number of cycles to perform. If NONE, the device will read indefinitely. Defaults to NONE. 

        Returns:
        inventory (dataframe): Detected tags, data: PC, EPC, RSSI, Antenna number. 
        """
        cmd = b'\x82'

        if cycles is None:
            num = b'\x00\x00'
        else:
            num = int(cycles).to_bytes(2, byteorder='big')

        cmd += num

        self.send_command(cmd)
        self.ser.read_until(b'\r\n')
        response = self.ser.read_until(b'\r\n')
        loop = 0
        while loop < (cycles-1):
            response = response + self.ser.read_until(b'\r\n')
            loop +=1

        self.read_stop()
        time.sleep(0.1)
        self.ser.flush()

        inventory = parse_tag_data(response)

        print("Done reading.")

        return inventory

    def read_stop(self):
        """
        Stop reading.

        Parameters: 
        None

        Returns:
        response: The device response, bytearray.
        """
        cmd = b'\x8C'

        response = self.send_command(cmd)

        return response

    def software_reset(self):
        """
        Reset device settings to default.  

        Parameters: 
        None

        Returns:
        response: response: The device response, bytearray.
        """
        cmd = b'\x2A'

        response = self.send_command(cmd)
        
        return response


def dbm_to_hex(dbm):
    """
    Convert a power value in dBm x100 to a hex byte array in signed 2's complement format.

    Parameters:
    dbm (float): The dBm value to convert.

    Returns:
    hex_value (bytearray): The resulting hex bytes array.
    """
    value = int(dbm * 100)
    hex_value = value.to_bytes(2, byteorder='big', signed=True)
    return hex_value

def hex_to_dbm(hex_value):
    """
    Convert a hex bytes array in signed 2's complement format to a dBm value.

    Parameters:
    hex_value (bytearray): The hex bytes array to convert.

    Returns:
    float: The resulting dBm value.
    """
    value = int.from_bytes(hex_value, byteorder='big', signed=True)
    dbm = value / 100.0
    return dbm

def calculate_crc(data):
    """
    Calculate the CRC for the given data using bitwise XOR.

    Parameters:
    data (bytes): The data for which to calculate the CRC.

    Returns:
    int: The calculated CRC value.
    """
    crc = 0
    for byte in data:
        crc ^= byte
    return bytes([crc])

def parse_tag_data(data):
    """
    Parse EPC, RSSI and antenna id from a byte array.

    Parameters:
    data (bytearray): The encoded data.

    Returns:
    EPC (str), RSSI (float), ant_id (int).
    """
    index = 0
    SOF = b'\xA5\x5A'
    parsed_data = []
    while index < len(data):
        if data[index:index+2] == SOF:
            index += 5
            pc = int.from_bytes(data[index:index+2], byteorder='big')
            epc_length = ((pc >> 11) & 0x1F) * 2
            epc_start = index + 2
            epc_end = epc_start + epc_length
            rssi_start = epc_end
            rssi_end = rssi_start + 2
            antenna_start = rssi_end
            antenna_end = antenna_start + 1
            epc = data[epc_start:epc_end]
            rssi = data[rssi_start:rssi_end]
            antenna = data[antenna_start:antenna_end]
            parsed_data.append([
                epc.hex(),
                10 * hex_to_dbm(rssi),
                int.from_bytes(antenna, byteorder='big')
            ])
            index = antenna_end + 3
        else:
            index += 1
    df = pd.DataFrame(parsed_data, columns=['EPC', 'RSSI', 'Antenna'])
    return df

