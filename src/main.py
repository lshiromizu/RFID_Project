from module import RFIDReader
import numpy as np


def main():
    # Initialize the RFID reader with the correct serial port number
    device = RFIDReader(port='COM21', baudrate=115200)
    device.connect()

    # -------- IMPLEMENT ALGORITHM HERE --------




    # ------------------------------------------    
    # Uncomment the following lines to run examples:

    #import examples

    #examples.example1(device)

    #examples.example2(device)
    
    #-------------------------------------------
    device.read_stop()
    device.software_reset()
    device.disconnect()


if __name__ == "__main__":
    main()
