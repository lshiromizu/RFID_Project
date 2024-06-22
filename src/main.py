from module import RFIDReader
import numpy as np
import pandas as pd

def main():
    # Initialize the RFID reader with the correct serial port number
    device = RFIDReader(port='COM21', baudrate=115200)
    device.connect()

    # -------- IMPLEMENT ALGORITHM HERE --------

    device.set_power(15)
    
    device.set_antenna(0,0,1,1)
    
    res = device.read_start(10)

    device.read_stop()

    df =pd.DataFrame(res)

    res_fltr=[]
    for i in range(len(res)):
        for j in range(len(res_fltr)):
            data= res[i[1]]
            if res[i[1]]!=res_fltr[j[1]]:
                res_fltr.append(i)
                if (len(res_fltr[j][1])==3):
                    (res_fltr[i]).append(1)
                else:
                    (res_fltr[3]) = (res_fltr[3]+1)
    print(df)
    
    print(res_fltr)
    
    #device.read_stop()
    
    #print("Length:", len(res))
    # ------------------------------------------

    

    device.software_reset()
    device.disconnect()


if __name__ == "__main__":
    main()
