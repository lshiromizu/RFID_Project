import pandas as pd
import matplotlib.pyplot as plt


def example1(device):

    print("Running example 1")

    device.set_RF_mode(mode=3)
    device.set_power(pwr=10.0, save=False)

    device.set_antenna(ant_1=1, ant_2=1, ant_3=0, ant_4=0, save=False)

    inventory1 = device.read_start(cycles=100)
    device.read_stop()

    device.set_antenna(ant_1=0, ant_2=0, ant_3=1, ant_4=1, save=False)

    inventory2 = device.read_start(cycles=100)
    device.read_stop()

    print(inventory1)
    print(inventory2)

    # Merge DataFrames keeping all rows (including duplicates)
    merged_df = pd.concat([inventory1, inventory2], sort=False)

    # Get the set of EPCs from each dataframe
    df1_epcs = set(inventory1['EPC'])
    df2_epcs = set(inventory2['EPC'])

    # Find EPCs present in both DataFrames
    both_df_epcs = df1_epcs.intersection(df2_epcs)

    # Filter merged dataframe based on EPCs in both DataFrames
    df_filtered = merged_df[merged_df['EPC'].isin(both_df_epcs)]

    # Group by EPC, get max RSSI and count occurrences
    df_grouped = df_filtered.groupby('EPC').agg(RSSI=('RSSI', max), count=('EPC', 'count'))

    # Sort by count
    df_grouped = df_grouped.sort_values(by='count', ascending=False)

    print(df_grouped)




def example2(device):

    print("Running example 2")

    device.set_RF_mode(mode=3)
    device.set_antenna(ant_1=1, ant_2=1, ant_3=1, ant_4=1, save=False)

    RSSI = []
    Read_Power = []

    for pwr in range(3, 30 + 1, 3):
        device.set_power(pwr=pwr, save=False)
        Read_Power.append(device.get_power())
        tag = device.read_start(1)
        device.read_stop()
        RSSI.append(tag.RSSI)


    # Plot RSSI vs reading power
    plt.plot(Read_Power, RSSI)
    plt.xlabel("Reading Power (dBm)")
    plt.ylabel("RSSI (dB)")
    plt.title("RSSI vs Reading Power")
    plt.grid(True)
    plt.show()
