from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import asyncio
from datetime import datetime
import os
import time
import pathlib

CSV_HEADERS = "id, timestamp, rssi, vcc_V, accx, accy, accz\n"

def Vcc_val_to_V(Vcc_val : int) -> float:
    Vcc_mV = (Vcc_val * 1.85 + 1000) * 2.5
    return Vcc_mV / 1000

def count_lines(file_path) -> int:
    if (file_path == "" or file_path == None or not os.path.exists(file_path)):
        return 0

    with open(file_path, "r", encoding="utf-8") as file:
        return sum(1 for _ in file)
    
def create_empty_csv(file_path):
    if (not os.path.exists(file_path)) :
        with open(file_path, "w+") as f:
            f.write(CSV_HEADERS)

def get_12bitInt(MSB, LSB) -> int:
    value = ((MSB << 8) | (LSB)) & 0xFFF  # Extract 12 bits

    # Check if the number is negative (if bit 11 is set)
    if value & 0x800:  # 0x800 = 0b100000000000 (sign bit is set)
        value -= 0x1000  # Convert to negative using two's complement

    return value

    
async def IN100_getAddress(device_name : str, print_results : bool = False) -> str : 
    device : BLEDevice= BleakScanner.find_device_by_name(device_name)
    return device.address

def IN100_writePayloadToCSV(advertising_data : AdvertisementData, file_path : str) -> str:
    """
    Decodes a BLE payload and generates a string to be written into a .csv containing the data. 
    Returns the strings and writes it in the given file (if file_path == "", will not write to the file)
    The headers of the csv file (column names) are in the CSV_HEADERS global variable.
    """

    # Get the specific data we need
    data = advertising_data.manufacturer_data[0x0505]
    rssi = advertising_data.rssi

    # Extract data for each column
    id : int = count_lines(file_path) # DO NOT REMOVE THIS ONE. Should always be the first column, named id.
    timestamp : int = time.time()
    vcc_V : float = Vcc_val_to_V(data[0]) # TODO: adapt data values : 12 bit int.
    acc_x : int = get_12bitInt(data[2], data[1])
    acc_y : int = get_12bitInt(data[4], data[3])
    acc_z : int = get_12bitInt(data[6], data[5])

    # Write the data in a csv format. 
    formatted_data = f"{id}, {timestamp}, {rssi}, {vcc_V}, {acc_x}, {acc_y}, {acc_z}\n"

    #--------------DO NOT MODIFY BELOW THIS--------------------------

    if (file_path == "" or file_path == None) :
        return formatted_data

    with open(file_path, "+a") as f :
        if (id == 0) :
            id = 1
            f.write(CSV_HEADERS)
            
        f.write(formatted_data)

    return formatted_data

async def IN100_connect(device_name : str, print_results : bool = False) :
    stop_event = asyncio.Event()

    #------------------------BEGIN Callback--------------------------------
    def detectionCallback(device : BLEDevice, advertising_data : AdvertisementData) :
        if (device.name != device_name) :
            return
        
        if (print_results) :
            print("---Data BEGIN---\n", advertising_data.manufacturer_data, "\n---Data END---")

        date = datetime.date(datetime.today())
        APP_PATH = str(pathlib.Path(__file__).parent.resolve())
        file_path = os.path.join(APP_PATH, "data", f"ble_data_{date}.csv")

        IN100_writePayloadToCSV(advertising_data, file_path)
    #------------------------END Callback---------------------------------

    async with BleakScanner(detection_callback=detectionCallback) as scanner :
        await stop_event.wait()

if __name__ == "__main__" : 
    asyncio.run(IN100_connect("IN100"))