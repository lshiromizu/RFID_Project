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

    


def example2(device):

    print("Running example 2")
    device.set_power(pwr=10.0, save=False)