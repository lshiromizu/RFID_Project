from module import RFIDReader
import numpy as np
import pandas as pd

def main():
    # Initialize the RFID reader with the correct serial port number
    device = RFIDReader(port='COM21', baudrate=115200)
    device.connect()

    # -------- IMPLEMENT ALGORITHM HERE --------



    # ------------------------------------------

    

    device.software_reset()
    device.disconnect()


if __name__ == "__main__":
    main()
