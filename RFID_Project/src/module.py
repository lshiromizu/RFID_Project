import serial

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

        length = len(cmd) + 7
        crc = calculate_crc(length.to_bytes(2, byteorder='big') + cmd)
        cmd = SOF + length.to_bytes(2, byteorder='big') + cmd + crc + EOF
        self.ser.write(cmd)

        response = self.ser.readline()

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

        if response[5]:
            print("Power set. \r\n")
        else:
            print("Error. \r\n")
        
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
        cmd += ant

        response = self.send_command(cmd)


        return response
    
    def get_antenna(self):
        """
        Get Activated/deactivated antennas.

        Parameters: 
        None

        Returns:
        ant: Hex byte array,

        """
        cmd = b'\x2A'

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
        **TODO**
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
        **TODO**
        Set device RF mode.

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

        response = self.send_command(cmd)

        return response

    def get_RF_mode():
        """
        **TODO**
        Get device RF configuration.

        Parameters: 
        None

        Returns:
        response (str): The device RF configuration.
        """

    def set_dwell_time(self, time_on, time_off, save=False):
        """
        Set the device dwell (work and wait) time.

        Parameters: 
        time_on (int): Work time in ms (range 0 to 65535). 
        time_off (int): Wait time in ms (range 0 to 65535). 
        save (bool): If True, saves the configuration to NVM. Defaults to False.

        Returns:
        response: The device response, bytearray.
        """
        cmd = b'\x3C'

        if save:
            NVM = b'\x01'
        else:
            NVM = b'\x00'

        work = int(time_on).to_bytes(2, byteorder='big')
        wait = int(time_off).to_bytes(2, byteorder='big')

        cmd = cmd + NVM + work + wait

        response = self.send_command(cmd)
        
        return response

    def get_dwell_time(self):
        """
        Get the device dwell (work and wait) time.

        Parameters: 
        None. 

        Returns:
        time_on, time_off: The device dwell (work and wait) time in ms.
        """
        cmd = b'\x3E'

        response = self.send_command(cmd)

        time_on = int.from_bytes(response[6:8])
        time_off = int.from_bytes(response[8:10])

        return time_on, time_off

    def inventory_read(self, cycles=None):
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

        stop=False
        response = self.send_command(cmd)

        loop = 0
        while not stop:
            response += self.ser.readline()
            loop +=1
            if cycles is not None and loop > cycles:
                stop=True
        
        inventory = parse_tag_data(response)

        return inventory


    def read_stop(self):
        """
        Stop reading.

        Parameters: 
        None

        Returns:
        response: The device response, bytearray.
        """
        global stop
        stop=True

        cmd = b'\x8C'

        response = self.send_command(cmd)

        return response

    def single_read(self, timeout):
        """
        Perform a single Tag read.

        Parameters: 
        timeout (int): Timeout value in ms. Reading stops as soon as a tag is detected or timeout occurs. 

        Returns:
        response: Detected Tag, data: EPC (str), RSSI (float), Antenna number. 
        """
        cmd = b'\x80'

        time = int(timeout).to_bytes(2, byteorder='big')

        cmd += time

        response = self.send_command(cmd)

        EPC = response[7:(len(response)-6)].decode()
        RSSI = 10 * hex_to_dbm(response[(len(response)-6):(len(response)-4)])
        ant = int.from_bytes(response[(len(response)-4)], byteorder='big')

        return EPC, RSSI, ant

    def timed_read(self, time):
        """
        Perform a timed inventory read.

        Parameters: 
        time (int): Reading time value in ms (range 10 to 30000ms). Reading until time runs out. 

        Returns:
        tag_count: Number of tags detected.
        """
        if not (10 <= time <= 30000):
            raise ValueError("Time must be between 10 and 30000")

        cmd = b'\x90'
        timeout = int(time).to_bytes(2, byteorder='big')
        cmd += timeout

        response = self.send_command(cmd)

        tag_count = int.from_bytes(response[5:9], byteorder='big')

        return tag_count

    def get_timed_read(self):
        """
        **TODO**
        Get Tags detected during timed read. 

        Parameters: 
        None

        Returns:
        response: Detected tags, data: PC+EPC, RSSI, Antenna number
        """
        cmd = b'\x92'

        response = self.send_command(cmd)

        inventory = parse_tag_data(response)

        return inventory

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

        print('Reset succeeded. \r\n')
        
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
            parsed_data.append({
                'EPC': epc.decode('utf-8'),
                'RSSI': 10 * hex_to_dbm(rssi),
                'Antenna': int.from_bytes(antenna, byteorder='big')
            })
            index = antenna_end + 3
        else:
            index += 1

    return parsed_data
