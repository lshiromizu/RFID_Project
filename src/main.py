from module import RFIDReader
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import examples


def main():
    # Initialize the RFID reader with the correct serial port number
    device = RFIDReader(port='COM21', baudrate=115200)
    device.connect()

    # -------- IMPLEMENT ALGORITHM HERE --------





    # ------------------------------------------
    # Uncomment the following lines to run examples:

    #examples.example1(device)

    #examples.example2(device)
    
    #examples.distance_vs_RSSI(device)

    #-------------------------------------------
    device.read_stop()
    device.software_reset()
    device.disconnect()


if __name__ == "__main__":
    main()
