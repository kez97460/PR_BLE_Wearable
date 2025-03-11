from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import asyncio
import time

async def BLE_scan(print_results : bool = False) -> list:
    res = []
    devices = await BleakScanner.discover()
    if (print_results) :
        print("---Found---")
    for d in devices:
        if (d.name != None) :
            if (print_results) :
                print(f"Found : {d.name}")
            res.append(d)
    if (print_results) :
        print("---End---")
    return res

def Vcc_val_to_V(Vcc_val : int) -> float:
    Vcc_mV = (Vcc_val * 1.85 + 1000) * 2.5
    return Vcc_mV / 1000

async def BLE_connect(device_name : str, print_results : bool = False) :
    stop_event = asyncio.Event()

    def detectionCallback(device : BLEDevice, advertising_data : AdvertisementData) :
        if (device.name != device_name) :
            return
        
        data = advertising_data.manufacturer_data[0x0505]
        if (print_results) :
            print("---Data BEGIN---\n", advertising_data.manufacturer_data, "\n---Data END---")
            print(f"Vcc = {Vcc_val_to_V(data[0])}")

        stop_event.set()
        time.sleep(1)


    async with BleakScanner(detection_callback=detectionCallback) as scanner :
        await stop_event.wait()