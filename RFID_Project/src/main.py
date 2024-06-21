from module import RFIDReader

def main():
    # Initialize the RFID reader with the correct serial port number
    device = RFIDReader(port='COM21', baudrate=115200)
    device.connect()

    device.set_power(5.0)

    response = device.get_power()
    print(response, 'dBm')

    res = device.inventory_read(10)
    device.read_stop()

    device.software_reset()
    device.disconnect()


if __name__ == "__main__":
    main()
