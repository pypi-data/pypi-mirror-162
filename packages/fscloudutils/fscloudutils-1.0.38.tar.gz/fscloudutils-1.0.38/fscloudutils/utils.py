"""
This module holds various useful tools
"""
import enum
import traceback
from datetime import datetime
from os import times

import pandas as pd
from typing import Tuple
import fscloudutils.exceptions as exceptions


class NMEASentectID(enum.Enum):
    GGA = "GGA"
    RMC = "RMC"
    VTG = "VTG"


class NavRowData:
    def __init__(self, lat, long):
        self._lat = lat
        self._long = long
        self._satellites_count = 0
        self._speed_kmh = 0
        self._direction_mag = None
        self._direction_true = None
        self._talkerID = None
        self._timestamp = None

    def get_lat(self):
        return self._lat

    def get_long(self):
        return self._long

    def set_talkerID(self, talkerID):
        self._talkerID = talkerID

    def get_talkerID(self):
        return self._talkerID

    def set_direction_true(self, direction_true):
        self._direction_true = direction_true

    def get_direction_true(self):
        return self._direction_true

    def set_direction_mag(self, direction_mag):
        self._direction_mag = direction_mag

    def get_direction_mag(self):
        return self._direction_mag

    def set_speed_kmh(self, speed_kmh):
        self._speed_kmh = speed_kmh

    def get_speed_kmh(self):
        return self._speed_kmh

    def set_timestamp(self, timestamp):
        self._timestamp = timestamp

    def get_timestamp(self):
        return self._timestamp

    def set_satellites_count(self, satellites_count):
        self._satellites_count = satellites_count

    def get_satellites_count(self):
        return self._satellites_count

    def has_all_data(self) -> bool:
        return self._satellites_count and self._speed_kmh and self._direction_mag \
               and self._direction_true and self._timestamp


class NavParser:
    """ nav_reader is a class implementing methods to read .nav files in NMEA format """

    def __init__(self, nmea: str, is_file=False):
        """
        :param path:
        """
        super()
        self._nmea_block_buffer = ""
        self._nmea_buffer_flags = {
            NMEASentectID.RMC.value: False,
            NMEASentectID.GGA.value: False,
            NMEASentectID.VTG.value: False
        }
        self._points = dict()
        if is_file:
            self.read_file(nmea)
        else:
            self.read_string(nmea)
        self._most_recent = max(self._points, default=None)
        self._most_accurate = max(self._points, key=lambda s: self._points[s].get_satellites_count(), default=None)

    @staticmethod
    def get_final_lat_long(lat_before_conversion, long_before_conversion, lat_dir, long_dir) -> Tuple[float, float]:
        lat_dec = lat_before_conversion // 100
        long_dec = long_before_conversion // 100
        lat_partial = ((lat_before_conversion / 100 - lat_dec) * 100) / 60
        long_partial = ((long_before_conversion / 100 - long_dec) * 100) / 60
        final_lat = lat_dec + lat_partial
        final_long = long_dec + long_partial
        if lat_dir == 'S':
            final_lat = final_lat * -1
        if long_dir == 'W':
            final_long = final_long * -1
        return final_lat, final_long

    def read_file(self, path: str) -> None:
        if not path.split('.')[-1] == 'nav':
            raise exceptions.FileExtensionError('nav')
        else:
            with open(path, 'r') as f:
                read_data = f.readlines()
                nmea_blocks = self.break_NMEA_into_blocks(read_data)
                for block in nmea_blocks:
                    self.process_NMEA_block(block)

    def read_string(self, nmea: str) -> None:
        read_data = nmea.splitlines()
        nmea_blocks = self.break_NMEA_into_blocks(read_data)
        for block in nmea_blocks:
            self.process_NMEA_block(block)

    def break_NMEA_into_blocks(self, nmea_lines):
        blocks = []
        for line in nmea_lines:
            self._nmea_block_buffer += f'{line}\n'
            self._nmea_buffer_flags = {k: True if k in line else v for k, v in self._nmea_buffer_flags.items()}
            for flag in self._nmea_buffer_flags:
                self._nmea_buffer_flags[flag] = True if flag in line else self._nmea_buffer_flags[flag]
            if all(v for v in self._nmea_buffer_flags.values()):
                self._nmea_buffer_flags = {flag: False for flag in self._nmea_buffer_flags}
                blocks.append(self._nmea_block_buffer)
                self._nmea_block_buffer = ""
        return blocks

    def process_NMEA_block(self, block):
        GGA = RMC = VTG = None
        lines = block.splitlines()
        for line in lines:
            data = line.split(',')
            if len(data) <= 6:
                continue
            sentenceID = data[0][3:]  # $GPGGA -> GGA
            if sentenceID == NMEASentectID.GGA.value:
                GGA = data
            if sentenceID == NMEASentectID.RMC.value:
                RMC = data
            if sentenceID == NMEASentectID.VTG.value:
                VTG = data
        if not (GGA and RMC and VTG and GGA[0][1:3] == RMC[0][1:3] == VTG[0][1:3]):
            raise exceptions.InputError("illegal NMEA block")

        talkerID = GGA[0][1:3]  # $GPGGA -> GP

        lat_before_conversion = float(GGA[2])
        long_before_conversion = float(GGA[4])
        lat_dir, long_dir = GGA[3], GGA[5]
        GGA_lat, GGA_long = NavParser.get_final_lat_long(lat_before_conversion, long_before_conversion,
                                                         lat_dir, long_dir)

        lat_before_conversion = float(RMC[3])
        long_before_conversion = float(RMC[5])
        lat_dir, long_dir = RMC[4], RMC[6]
        RMC_lat, RMC_long = NavParser.get_final_lat_long(lat_before_conversion, long_before_conversion,
                                                         lat_dir, long_dir)

        satellites_count = int(GGA[7])
        timestamp = datetime.strptime(f"{RMC[9]} {RMC[1]}", "%d%m%y %H%M%S.%f")
        speed_kmh = 1.852 * float(RMC[7])
        direction_true = VTG[1]
        direction_mag = VTG[3]

        if GGA_lat != RMC_lat or GGA_long != RMC_long:
            raise exceptions.InputError("illegal NMEA block")

        lat, long = RMC_lat, RMC_long
        if timestamp not in self._points:
            self._points[timestamp] = NavRowData(lat, long)

        self._points[timestamp].set_talkerID(talkerID)
        self._points[timestamp].set_speed_kmh(speed_kmh)
        self._points[timestamp].set_timestamp(timestamp)
        self._points[timestamp].set_satellites_count(satellites_count)
        self._points[timestamp].set_direction_true(direction_true)
        self._points[timestamp].set_direction_mag(direction_mag)

        if self._most_recent is None or timestamp > self._most_recent:
            self._most_recent = timestamp
        if self._most_accurate is None or satellites_count > self._points[self._most_accurate].get_satellites_count():
            self._most_accurate = timestamp

    def get_points(self) -> dict:
        return self._points

    def get_most_accurate_point(self) -> NavRowData or None:
        if self._most_accurate is not None:
            return self._points[self._most_accurate]
        return None

    def get_most_recent_point(self) -> NavRowData or None:
        if self._most_recent is not None:
            return self._points[self._most_recent]
        return None
