#
# Aidlab_peripheral.py
# Aidlab-SDK
# Created by Szymon Gesicki on 10.05.2020.
#

from Aidlab.AidlabCharacteristicsUUID import AidlabCharacteristicsUUID
from Aidlab.AidlabNotificationHandler import AidlabNotificationHandler
from Aidlab.Signal import Signal
from bleak import BleakClient, discover, BleakError
import asyncio
from multiprocessing import Process
import sys
import logging
from packaging import version

logging.getLogger("bleak").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class AidlabPeripheral():
    connected_aidlab = []

    def __init__(self, aidlab_delegate):
        self.aidlab_delegate = aidlab_delegate
        self.queue_to_send = []
        self.max_cmd_length = 20

    async def scan_for_aidlab(self):
        devices = await discover()
        # Container for Aidlab's MAC addresses (these were found during the scan process)
        aidlabMACs = []

        for dev in devices:
            # Device found with dev.name
            if dev.name == "Aidlab" and dev.address not in self.connected_aidlab:
                aidlabMACs.append(dev.address)
        return aidlabMACs

    def run(self, real_time_signal, sync_signal, aidlabs_address=None):
        
        loop = asyncio.get_event_loop()
        self.connect(real_time_signal, sync_signal, loop, aidlabs_address)

    def connect(self, real_time_signal, sync_signal, loop, aidlabs_address=None):

        # Connect to all Aidlabs from `aidlabsMAC` list
        if aidlabs_address:
            logging.info("Connecting to %s", aidlabs_address)
            self.create_task(real_time_signal, sync_signal, aidlabs_address, loop, False)
            # All Aidlabs connected, end the loop
            return

        # Connect to every discoverable Aidlab
        else:
            print("Scanning ...")

            while True:
                aidlabs_address = loop.run_until_complete(self.scan_for_aidlab())

                if aidlabs_address != []:
                    logging.info("Connecting to %s",aidlabs_address)
                    self.create_task(real_time_signal, sync_signal, aidlabs_address, loop, True)

    def create_task(self, real_time_signal, sync_signal, aidlabs_address, loop, should_scan):

        if 'linux' in sys.platform:
            # during my testing, this method seemed to work relatively stable, but can connect to one aidlab at the time
            # it requires more testing though - leaving the previous approach below (and creating task on trello)
            loop.run_until_complete(self.connect_to_aidlab(real_time_signal, sync_signal, aidlabs_address[0], loop, 0.5))
            #for aidlab_address in aidlabs_address:
            #    Process(target=self.between, args=(real_time_signal, sync_signal, aidlab_address, loop)).start()
            #    self.connected_aidlab.append(aidlab_address)
        else:
            for aidlab_address in aidlabs_address:
                try:
                    loop.create_task(self.connect_to_aidlab(real_time_signal, sync_signal, aidlab_address, loop))
                except:
                    pass
                finally:
                    self.connected_aidlab.append(aidlab_address)

            if should_scan:
                # task to look for more aidlabs
                loop.create_task(self.connect(real_time_signal, sync_signal, loop))

            loop.run_forever()

    def between(self, real_time_signal, sync_signal, aidlab_address, loop):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.connect_to_aidlab(real_time_signal, sync_signal, aidlab_address, loop))
        except:
            pass

    async def connect_to_aidlab(self, real_time_signal, sync_signal, aidlab_address, loop, command_send_delay_sec = 0):
        client = BleakClient(aidlab_address, loop=loop)

        try:
            await client.connect(timeout=10)

            self.aidlab_delegate.create_aidlabSDK(aidlab_address)

            # Harvest Device Information
            firmware_revision = (await client.read_gatt_char("00002a26-0000-1000-8000-00805f9b34fb")).decode('ascii')
            self.aidlab_delegate.did_receive_raw_firmware_revision(firmware_revision, aidlab_address)

            self.aidlab_delegate.did_receive_raw_hardware_revision(
                (await client.read_gatt_char("00002a27-0000-1000-8000-00805f9b34fb")).decode('ascii'), aidlab_address)

            self.aidlab_delegate.did_receive_raw_manufacture_name(
                (await client.read_gatt_char("00002a29-0000-1000-8000-00805f9b34fb")).decode('ascii'), aidlab_address)

            self.aidlab_delegate.did_receive_raw_serial_number(
                (await client.read_gatt_char("00002a25-0000-1000-8000-00805f9b34fb")).decode('ascii'), aidlab_address)

            self.aidlab_delegate.did_connect_aidlab(aidlab_address)

            self.aidlabCharacteristicsUUID = AidlabCharacteristicsUUID(firmware_revision)

            aidlabNotificationHandler = AidlabNotificationHandler(aidlab_address,  self.aidlab_delegate, self.aidlabCharacteristicsUUID)

            for characteristic in self.converter_to_uuids(real_time_signal, aidlab_address):
                try:
                    await client.start_notify(characteristic, aidlabNotificationHandler.handle_notification)
                except BleakError as e:
                    logger.debug(str(e) + " (this might be due to compatibility with older aidlabs)")
                    pass

            if version.parse("3.6.0") < version.parse(firmware_revision):
                logger.debug("Version later than 3.6 start collect data")
                await self.start_collect_data(client, aidlab_address, real_time_signal, sync_signal)
            else:
                logger.debug("Version older than 3.6")

            while True:
                await asyncio.sleep(command_send_delay_sec)
                await self.send_command_if_needed(client)
                if not client.is_connected:
                    self.aidlab_delegate.did_disconnect_aidlab(aidlab_address)
                    self.aidlab_delegate.destroy(aidlab_address)
                    self.connected_aidlab.remove(aidlab_address)
                    break

        except Exception as e:
            logging.info("Exception " + str(e))
            if aidlab_address in self.connected_aidlab: self.connected_aidlab.remove(aidlab_address)


    def start_synchronization(self, address):
        self.queue_to_send.append({"address": address, "command": "sync start"})

    def stop_synchronization(self, address):
        self.queue_to_send.append({"address": address, "command": "sync stop"})
    
    def send(self, address, command):
        self.queue_to_send.append({"address": address, "command": command})

    async def send_command_if_needed(self, client):
        while self.queue_to_send:
            command = self.queue_to_send.pop(0)
            await self.send_command(client, command["address"], command["command"])
            await asyncio.sleep(1)

    async def send_command(self, client, aidlab_address, command):
        write_value = self.aidlab_delegate.get_command(aidlab_address, command)
        size = write_value[3] | (write_value[4] << 8)
        message = [write_value[i] for i in range(size)]
        await self.send_to_aidlab(client, message, size)

    async def send_to_aidlab(self, client, message, size):
        logger.debug("will send msg" + str(message) + " len " + str(size))
        for i in range(round(int(size/self.max_cmd_length) + (size%self.max_cmd_length > 0))):
            message_byte = bytearray(message[i*self.max_cmd_length:(i+1)*self.max_cmd_length])
            logger.debug("sending bytes\n" + str(message_byte))
            await client.write_gatt_char(self.aidlabCharacteristicsUUID.cmdUUID["uuid"], message_byte, True)

    def signal_list_to_int_list(self, signals):
        int_list = []
        for signal in signals:
            int_list.append(signal.value)
        return int_list

    async def start_collect_data(self, client, aidlab_address, real_time_signal, sync_signal):
        write_value = self.aidlab_delegate.get_collect_command(
            aidlab_address, 
            self.signal_list_to_int_list(real_time_signal), 
            self.signal_list_to_int_list(sync_signal)
        )
        size = write_value[3] | (write_value[4] << 8)
        message = [write_value[i] for i in range(size)]
        await self.send_to_aidlab(client, message, size)    

    def converter_to_uuids(self, signals, aidlab_address):
        # We always want to notify the command line
        out = [self.aidlabCharacteristicsUUID.cmdUUID["uuid"]]

        for signal in signals:
            if signal == Signal.temperature:
                out.append(self.aidlabCharacteristicsUUID.temperatureUUID["uuid"])
            elif signal == Signal.ecg:
                out.append(self.aidlabCharacteristicsUUID.ecgUUID["uuid"])
            elif signal == Signal.battery:
                out.append(self.aidlabCharacteristicsUUID.batteryUUID["uuid"])
                out.append(self.aidlabCharacteristicsUUID.batteryLevelUUID["uuid"])
            elif signal == Signal.respiration:
                out.append(self.aidlabCharacteristicsUUID.respirationUUID["uuid"])
            elif signal == Signal.motion:
                out.append(self.aidlabCharacteristicsUUID.motionUUID["uuid"])
            elif signal == Signal.activity:
                out.append(self.aidlabCharacteristicsUUID.activityUUID["uuid"])
            elif signal == Signal.steps:
                out.append(self.aidlabCharacteristicsUUID.stepsUUID["uuid"])
            elif signal == Signal.orientation:
                out.append(self.aidlabCharacteristicsUUID.orientationUUID["uuid"])
            elif signal == Signal.sound_volume:
                out.append(self.aidlabCharacteristicsUUID.soundVolumeUUID["uuid"])
            elif signal == Signal.heart_rate:
                out.append(self.aidlabCharacteristicsUUID.heartRateUUID["uuid"])
            elif signal == Signal.rr:
                out.append(self.aidlabCharacteristicsUUID.heartRateUUID["uuid"])
            elif signal == Signal.pressure:
                pass
            elif signal == Signal.respiration_rate:
                pass
            elif signal == Signal.body_position:
                pass
            else:
                logging.error(f"Signal {signal} not supported")
                self.aidlab_delegate.did_disconnect_aidlab(aidlab_address)
                exit()
        return out
