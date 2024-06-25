from module import RFIDReader
import numpy as np


def main():
    # Initialize the RFID reader with the correct serial port number
    device = RFIDReader(port='COM12', baudrate=115200)
    device.connect()

    # -------- IMPLEMENT ALGORITHM HERE --------



    # ------------------------------------------    

    device.software_reset()
    device.disconnect()


if __name__ == "__main__":
    main()
