import time
import pandas as pd
import matplotlib.pyplot as plt


target_epcs = {
        "e2801160600002083e75ba94",
        "e2801160600002083e756ab6",
        "e2801160600002083e75baa4",
        "e2801160600002083e756ac6"
    }

def example1(device):

    print("Running example 1")

    device.set_RF_mode(mode=3)
    device.set_power(pwr=3.0, save=False)

    device.set_antenna(ant_1=1, ant_2=1, ant_3=0, ant_4=0, save=False)

    inventory1 = device.read_start(cycles=100)

    device.set_antenna(ant_1=0, ant_2=0, ant_3=1, ant_4=1, save=False)

    inventory2 = device.read_start(cycles=100)

    # Merge DataFrames keeping all rows (including duplicates)
    merged_df = pd.concat([inventory1, inventory2], sort=False)

    # Get the set of EPCs from each dataframe
    df1 = set(inventory1['EPC'])
    df2 = set(inventory2['EPC'])

    # Find EPCs present in both DataFrames
    both_df_tags = df1.intersection(df2)

    # Filter merged dataframe based on EPCs in both DataFrames and RSSI >= -50
    df_filtered = merged_df[merged_df['EPC'].isin(both_df_tags) & (merged_df['RSSI'] >= -50)]

    # Group by EPC, get max RSSI and count occurrences
    df_grouped = df_filtered.groupby('EPC').agg(RSSI=('RSSI', max), count=('EPC', 'count'))

    # Sort by count
    df_grouped = df_grouped.sort_values(by='count', ascending=False)

    print("\nItems inside the portal:")
    print(df_grouped)

    # Find EPCs unique to each DataFrame
    unique_epcs = (df1 - df2).union(df2 - df1)

    # Filter the merged dataframe for unique EPCs or RSSI < -50
    outside_tags = merged_df[(merged_df['EPC'].isin(unique_epcs)) | (merged_df['RSSI'] < -50)].drop_duplicates(subset=['EPC']).reset_index(drop=True)

    print("\nItems outside the portal:")
    print(outside_tags)


def example2(device):

    print("Running example 2")

    device.set_RF_mode(mode=3)
    device.set_antenna(ant_1=True, ant_2=True, ant_3=True, ant_4=True, save=False)

    RSSI = []
    Read_Power = []

    for i in range(1, 30 + 1, 1):
        device.set_power(pwr=i, save=False)
        rpwr = device.get_power()
        Read_Power.append(rpwr)
        time.sleep(0.1)
        tag = device.read_start(1)
        RSSI.append(tag['RSSI'].max())

    #print(RSSI)
    #print(Read_Power)

    # Plot RSSI vs reading power
    plt.plot(Read_Power, RSSI)
    plt.xlabel("Reader Output Power (dBm)")
    plt.ylabel("RSSI (dBm)")
    plt.title('Reader Output Power vs. RSSI')
    plt.grid(True)
    plt.show()
    '''
    #bar plot
    plt.bar(Read_Power, RSSI)
    plt.xlabel('Reader Output Power (dBm)')
    plt.ylabel('RSSI (dBm)')
    plt.title('Reader Output Power vs. RSSI')
    plt.grid(axis='y')
    plt.show()
    '''


def get_target_epcs():
    return {
        "e2801160600002083e75ba94",
        "e2801160600002083e756ab6",
        "e2801160600002083e75baa4",
        "e2801160600002083e756ac6"
    }
