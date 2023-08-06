from enum import Enum, Flag, IntFlag
from typing import *
from typing import BinaryIO
import struct
import io
import numpy as np


class SenseX1000Base(object):
    USB_VID: int = 0x1FC9
    USB_PID: int = 0x8271

    class IPVersion(Enum):
        IPV4 = 4
        IPV6 = 6

    class IPv4AutoconfStatus(Enum):
        OFF = 0
        PROBING = 1
        ANNOUNCING = 2
        BOUND = 3

    class IPv6AutoconfStatus(Enum):
        NOTIMPLEMENTED = 0

    class IPv4DHCPStatus(Enum):
        OFF = 0
        REQUESTING = 1
        INIT = 2
        REBOOTING = 3
        REBINDING = 4
        RENEWING = 5
        SELECTING = 6
        INFORMING = 7
        CHECKING = 8
        PERMANENT = 9
        BOUND = 10
        RELEASING = 11
        BACKINGOFF = 12

    class IPv6DHCPStatus(Enum):
        NOTIMPLEMENTED = 0

    class PowerLevel(Enum):
        UNKNOWN = 0
        LOW = 1
        MEDIUM = 2
        HIGH = 3
        AUTO = 4

    class RadarState(Enum):
        OFF = 0
        STANDBY = 11
        IDLE = 12
        BUSY = 15
        DETECTFAIL = 40
        MAGICFAIL = 45

    # Enums for CONTrol subsystem
    class RampMode(Enum):
        """Ramp mode used with CONTrol:RADAR:MPLL:RMODe"""
        SINGLE = 0
        """Perform single ramps on each trigger"""
        DOUBLE = 1
        """Perform double ramps on each trigger"""
        ALTERNATING = 2
        """Perform alternating ramps on each trigger"""

    class ChannelCoupling(Enum):
        """Frontend coupling of receive channel used with CONTrol:RADAR:FRONtend:CHANnel#:COUPling"""
        GND = 0
        """Set GND channel coupling"""
        DC = 1
        """Set DC channel coupling"""
        AC = 2
        """Set AC channel coupling (R^2 compensation)"""

    class ChannelForce(Enum):
        """Frontend channel force used with CONTrol:RADAR:FRONtend:CHANnel#:FORCe"""
        NONE = 0
        """Do not force channel state"""
        ON = 1,
        """Force channel to always-on"""
        OFF = 2
        """Force channel to always-off"""

    # Enums for SENSe subsystem
    class FrequencyMode(Enum):
        """Frequency mode used with SENSe:FREQuency:MODE"""
        CW = 0
        """Operate in continuous wave mode on a single frequency (aka zero-span)"""
        SWEEP = 1
        """Operate in swept mode (normal)"""

    class SweepDirection(Enum):
        """Sweep direction used with SENSe:SWEep:DIRection"""
        DOWN = -1
        """Sweep slope of (first) sweep is down"""
        UP = 1
        """Sweep slope of (first) sweep is up"""

    class SweepMode(Enum):
        """Sweep mode used with SENSe:SWEep:MODE"""
        NORMAL = 0
        """Sweep slope is constant with jump back to start frequency at the end of sweep"""
        ALTERNATING = 1
        """Sweep slope is alternating in consecutive sweeps"""

    class RefOscSource(Enum):
        """Reference Oscillator source used with SENSe:ROSCillator:SOURCE"""
        NONE = 0
        """No reference oscillator, free running"""
        INTERNAL = 1
        """Internal reference oscillator source (if available)"""
        EXTERNAL = 2
        """External reference oscillator source (if available)"""

    class RefOscStatus(Enum):
        """Status of reference oscillator used with SENSe:ROSCillator:STATus"""
        OFF = 0
        """Reference oscillator PLL is disabled, i.e. during power-off"""
        HOLDOVER = 1
        """Reference oscillator PLL is in holdover mode (source lost)"""
        LOCKING = 2
        """Reference oscillator PLL is trying to lock to selected reference"""
        LOCKED = 3
        """Reference oscillator PLL is locked to selected reference"""
        LOCK = 3
        """Deprecated"""

    # Enums for TRIGger subsystem
    class TrigSource(Enum):
        """Trigger source used with TRIGger:SOURce"""
        IMMEDIATE = 0
        """A trigger will commence immediately after the device is initiated"""
        EXTERNAL = 1
        """An external trigger input is used for triggering the acquisition"""
        INTERNAL = 2
        """An internal trigger signal is used for triggering the acquisition"""

    # Data type information container
    class AcqDTypeInfo(NamedTuple):
        min: Union[int, complex]
        max: Union[int, complex]
        mag: int
        np: np.dtype

    # Enums/Flags for AcquisitionHeader
    class AcqDType(Enum):
        """Acquisition Datatype used in acquisition header"""
        S16RLE = 0
        """Signed 16 bit (real), little endian"""
        S16RILE = 4
        """Signed 16 bit (real, imaginary), little endian"""
        S32RLE = 8
        """Signed 32 bit (real), little endian"""
        S32RILE = 12
        """Signed 32 bit (real, imaginary), little endian"""

        @property
        def info(self) -> 'SenseX1000Base.AcqDTypeInfo':
            """Information about data type as AcqDTypeInfo object"""
            return {
                self.S16RLE.value: SenseX1000Base.AcqDTypeInfo(
                    min=-32768, max=32767, mag=32768, np=np.dtype('<i2')),
                self.S16RILE.value: SenseX1000Base.AcqDTypeInfo(
                    min=-32768-32768j, max=32767+32767j, mag=32768, np=np.dtype([('re', '<i2'), ('im', '<i2')])),
                self.S32RLE.value: SenseX1000Base.AcqDTypeInfo(
                    min=-2147483648, max=2147483647, mag=2147483648, np=np.dtype('<i4')),
                self.S32RILE.value: SenseX1000Base.AcqDTypeInfo(
                    min=-2147483648-2147483648j, max=2147483647+2147483647j, mag=2147483648, np=np.dtype([('re', '<i4'), ('im', '<i4')])),
            }[self.value]

    class AcqFlags(Flag):
        """Acquisition flags used in acquisition header"""
        SDOMAIN = 1 << 4
        """Sweep Domain data"""
        RDOMAIN = 1 << 5
        """Range Domain data"""
        DIRECTION = 1 << 8
        """Falling (0) or rising (1) slope of first sweep in acquisition"""
        ALTERNATING = 1 << 9
        """Constant (0) or alternating (1) sweep slope for multiple sweep acquisitions"""

    class AcqSubheaderFlags(IntFlag):
        """Acquisition subheader flags"""
        ACQTIMING = 1 << 4
        """Header includes timestamp information"""
        TIMEAXIS = 1 << 8
        """Header includes time axis information"""
        FREQAXIS = 1 << 9
        """Header includes frequency axis information"""
        SUPPDATA = 1 << 12
        """Header includes supplemental data information"""

    class AcqSubheaderAcqTiming(NamedTuple):
        """Class representing a timing subheader"""
        # header fields as named tuple entries.
        # Note that the order of these entries must match the binary header format
        trigger_timestamp: int
        """Timestamp of trigger in nanoseconds UTC since 1970-01-01 00:00:00"""
        trigger_delay: int
        """Delay between trigger event and acquisition start in nanoseconds"""
        sweep_period: int
        """The period with which sweeps are carried out in nanoseconds"""

        @classmethod
        def struct(cls) -> struct.Struct:
            return struct.Struct('<8xQQQ')

        @classmethod
        def flag(cls) -> 'SenseX1000Base.AcqSubheaderFlags':
            return SenseX1000Base.AcqSubheaderFlags.ACQTIMING

        @classmethod
        def from_stream(cls, stream: BinaryIO) -> 'SenseX1000Base.AcqSubheaderAcqTiming':
            # Get struct object, unpack binary data and create the NamedTuple object
            s = cls.struct()
            buffer = stream.read(s.size)
            return cls(*s.unpack(buffer))

    class AcqSubheaderTimeAxis(NamedTuple):
        """Class representing a time axis subheader"""
        # header fields as named tuple entries.
        # Note that the order of these entries must match the binary header format
        start: float
        """Start value of the axis"""
        stop: float
        """Stop value of the axis"""

        @classmethod
        def struct(cls) -> struct.Struct:
            return struct.Struct('<8xd8xd')

        @classmethod
        def flag(cls) -> 'SenseX1000Base.AcqSubheaderFlags':
            return SenseX1000Base.AcqSubheaderFlags.TIMEAXIS

        @property
        def delta(self) -> float:
            return self.stop - self.start

        @classmethod
        def from_stream(cls, stream: BinaryIO) -> 'SenseX1000Base.AcqSubheaderTimeAxis':
            # Get struct object, unpack binary data and create the NamedTuple object
            s = cls.struct()
            buffer = stream.read(s.size)
            return cls(*s.unpack(buffer))

    class AcqSubheaderFreqAxis(NamedTuple):
        """Class representing a time axis subheader"""
        # header fields as named tuple entries.
        # Note that the order of these entries must match the binary header format
        start: float
        """Start value of the axis"""
        stop: float
        """Stop value of the axis"""

        @classmethod
        def struct(cls) -> struct.Struct:
            return struct.Struct('<8xd8xd')

        @classmethod
        def flag(cls) -> 'SenseX1000Base.AcqSubheaderFlags':
            return SenseX1000Base.AcqSubheaderFlags.FREQAXIS

        @property
        def delta(self) -> float:
            return self.stop - self.start

        @classmethod
        def from_stream(cls, stream: BinaryIO) -> 'SenseX1000Base.AcqSubheaderFreqAxis':
            # Get struct object, unpack binary data and create the NamedTuple object
            s = cls.struct()
            buffer = stream.read(s.size)
            return cls(*s.unpack(buffer))

    class AcqSubheaderSupplementalData(NamedTuple):
        """Class representing supplemental data subheader"""
        class AcqSubHeaderSupplementalDataItem(NamedTuple):
            data_points: int
            data_size: int
            data_type: int
            data_flags: int

            @classmethod
            def struct(cls) -> struct.Struct:
                return struct.Struct('<LBBH')

            @property
            def dtype(self) -> 'SenseX1000Base.AcqDType':
                return SenseX1000Base.AcqDType(self.data_type)

            @classmethod
            def from_stream(cls, stream: BinaryIO) -> 'SenseX1000Base.AcqSubheaderSupplementalData.AcqSubHeaderSupplementalDataItem':
                # Get struct object, unpack binary data and create the NamedTuple object
                s = cls.struct()
                buffer = stream.read(s.size)
                return cls(*s.unpack(buffer))

        items: List[AcqSubHeaderSupplementalDataItem]

        @classmethod
        def struct(cls) -> struct.Struct:
            return struct.Struct(b'<' + cls.AcqSubHeaderSupplementalDataItem.struct().format.lstrip(b'<') * 4)

        @classmethod
        def flag(cls) -> 'SenseX1000Base.AcqSubheaderFlags':
            return SenseX1000Base.AcqSubheaderFlags.SUPPDATA


        @classmethod
        def from_stream(cls, stream: BinaryIO) -> 'SenseX1000Base.AcqSubheaderSupplementalData':
            # Get struct object, unpack binary data and create the NamedTuple object
            n_items = 4
            buffer = stream.read(cls.AcqSubHeaderSupplementalDataItem.struct().size * n_items)
            bytesio = io.BytesIO(buffer)
            items = []

            for i in range(n_items):
                item = cls.AcqSubHeaderSupplementalDataItem.from_stream(bytesio)
                if item.data_size != 0 and item.data_points != 0:
                    items.append(item)

            return cls(items)

    class AcqBaseHeader(NamedTuple):
        """Class representing the header prepended to every acquisition"""
        # header fields as named tuple entries.
        # Note that the order of these entries must match the binary header format
        header_length: int
        """Binary header size"""
        header_id: int
        """Binary header identifier"""
        header_version: int
        """Binary header version"""
        flags: int
        """Acquisition flags as integer"""
        bytes_total: int
        """Total number of bytes in acquisition"""
        sweep_count: int
        """Number of sweeps in acquisition"""
        trace_mask: int
        """Bitmask of enabled traces in acquisition"""
        data_points: int
        """Number of points per trace"""
        data_size: int
        """Size of datatype in bytes"""
        data_type: int
        """Datatype identifier"""
        acq_index: int
        """Index of acquisition"""
        subheader_flags: int
        """Indication of included subheaders"""
        subhdr_acq_timing: 'SenseX1000Base.AcqSubheaderAcqTiming' = None
        """Acquisition timing subheader"""
        subhdr_time_axis: 'SenseX1000Base.AcqSubheaderTimeAxis' = None
        """Time axis subheader"""
        subhdr_freq_axis: 'SenseX1000Base.AcqSubheaderFreqAxis' = None
        """Frequency axis subheader"""
        subhdr_supp_data: 'SenseX1000Base.AcqSubheaderSupplementalData' = None
        """Supplemental data subheader"""

        @classmethod
        def struct(cls) -> struct.Struct:
            # Return a Python struct object for parsing the binary header into the named tuple
            return struct.Struct('<HBBLLLLLBBLH')

        @classmethod
        def version(cls) -> int:
            # Return version supported by this NamedTuple
            return 1

        @classmethod
        def from_stream(cls, stream: BinaryIO) -> 'SenseX1000Base.AcqBaseHeader':
            # Get struct object, unpack binary data and create the NamedTuple object
            s = cls.struct()
            buffer = stream.read(s.size)
            header = cls(*s.unpack(buffer))
            assert header.header_version == cls.version(), f'Unsupported header version: {header.header_version:x}'
            return header

    class AcqHeader(AcqBaseHeader):
        @classmethod
        def subheaders(cls) -> dict:
            return {
                # The order of this subheader list matters.
                # They must be in the order they would be occuring in the header
                'subhdr_acq_timing': SenseX1000Base.AcqSubheaderAcqTiming,
                'subhdr_time_axis': SenseX1000Base.AcqSubheaderTimeAxis,
                'subhdr_freq_axis': SenseX1000Base.AcqSubheaderFreqAxis,
                'subhdr_supp_data': SenseX1000Base.AcqSubheaderSupplementalData
            }

        @classmethod
        def from_stream(cls, stream: BinaryIO) -> 'SenseX1000Base.AcqHeader':
            # Create the base header object
            baseheader = SenseX1000Base.AcqBaseHeader.from_stream(stream)
            subheaders_dict = {}

            # Read all subheaders
            subheaders_length = baseheader.header_length - baseheader.struct().size
            if subheaders_length > 0:
                subheaders_buffer = stream.read(subheaders_length)
                subheaders_iostream = io.BytesIO(subheaders_buffer)

                # Build a list of subheader objects from the subheader table, when they
                # are indicated in the baseheader.subheader_flags attribute
                subheaders_dict = {a: c.from_stream(subheaders_iostream) for a, c in cls.subheaders().items()
                                   if baseheader.subheader_flags & c.flag()}

            # Combine baseheader and subheaders
            header_dict = baseheader._asdict()
            header_dict.update(subheaders_dict)

            # Return new AcqHeader object, created from baseheader and subheaders
            return cls(**header_dict)

        @property
        def trace_list(self) -> List[int]:
            """List of traces enabled in this acquisition"""
            mask = self.trace_mask
            lst = []
            i = 0
            while mask > 0:
                if mask & (1 << i):
                    lst += [i]
                    mask = mask & ~(1 << i)
                i += 1
            return lst

        @property
        def trace_count(self) -> int:
            """Number of traces enabled in this acquisition"""
            return len(self.trace_list)

        @property
        def trace_size(self) -> int:
            """Total size of single trace in bytes"""
            size = self.data_points * self.data_size
            if self.subhdr_supp_data is not None:
                # Add size of supplemental data if it exists
                size += sum([i.data_points * i.data_size for i in self.subhdr_supp_data.items])
            return size

        @property
        def sweep_size(self) -> int:
            """Total size of sweep in bytes"""
            return self.trace_count * self.trace_size

        @property
        def acq_dtype(self) -> 'SenseX1000Base.AcqDType':
            """Acqusition data type as AcqDType object"""
            return SenseX1000Base.AcqDType(self.data_type)

        @property
        def acq_flags(self) -> 'SenseX1000Base.AcqFlags':
            """Acquisition flags as AcqFlags object"""
            return SenseX1000Base.AcqFlags(self.flags)

        @property
        def trig_timestamp(self) -> np.datetime64:
            timestamp = self.subhdr_acq_timing.trigger_timestamp if self.subhdr_acq_timing is not None else None
            return np.datetime64(timestamp, 'ns')

        @property
        def trig_delay(self) -> np.datetime64:
            delay = self.subhdr_acq_timing.trigger_delay if self.subhdr_acq_timing is not None else None
            return np.timedelta64(delay, 'ns')

        @property
        def sweep_period(self) -> np.timedelta64:
            timedelta = self.subhdr_acq_timing.sweep_period if self.subhdr_acq_timing is not None else None
            return np.timedelta64(timedelta, 'ns')

        @property
        def time_axis(self) -> Optional[np.ndarray]:
            if self.subhdr_time_axis is None:
                return None
            start, stop = self.subhdr_time_axis.start, self.subhdr_time_axis.stop
            return np.linspace(start, stop, self.data_points)

        @property
        def freq_axis(self) -> Optional[np.ndarray]:
            if self.subhdr_freq_axis is None:
                return None
            start, stop = self.subhdr_freq_axis.start, self.subhdr_freq_axis.stop
            return np.linspace(start, stop, self.data_points)

        @property
        def time_step(self) -> Optional[float]:
            """Returns delta-time per point"""
            if self.subhdr_time_axis is None:
                return None
            return self.subhdr_time_axis.delta / self.data_points

        @property
        def freq_step(self) -> Optional[float]:
            """Returns delta-frequency per point"""
            if self.subhdr_freq_axis is None:
                return None
            return self.subhdr_freq_axis.delta / self.data_points

    class AcqData(object):
        """Class representing an acquisition data object holding data for one or more consecutive sweeps"""
        header: 'SenseX1000Base.AcqHeader'
        """Copy of the acquisition header to which this data container belongs"""
        array: np.ndarray
        """Acquisition data as numpy array with shape N_sweeps x N_traces x N_points"""
        n_sweeps: int
        """Number of sweeps in this container"""
        n_traces: int
        """Number of traces per sweep"""
        n_points: int
        """Number of points per trace"""
        trace_list: list
        """Mapping of the trace index in the data array to the respective trace number"""
        seq_nums: list
        """List of sweep sequence numbers with respect to entire acquisition for each sweep in data array"""
        sweep_dir: int
        """Direction of first sweep in acquisition as sign value (-1, +1)"""
        sweep_dirs: list
        """List of sweep directions for each sweep in data array as sign value (-1, +1)"""
        timestamps: List[np.datetime64]
        """List of timestamps for each sweep in data array as UTC since 1970-01-01 00:00:00 in 1 ns resolution"""
        time_axes: List[np.ndarray]
        """List of time axes for each sweep in data array"""
        freq_axes: List[np.ndarray]
        """List of frequency axes for each sweep in data array"""
        supplemental_data: List[np.ndarray]
        """List of supplemental data arrays that is attached to the acquisition data"""

        @classmethod
        def from_stream(cls, stream: BinaryIO, header: 'SenseX1000Base.AcqHeader', seq_num: int, n_sweeps: int):
            # Calculate and read requested number of bytes from stream and create an AcqData object
            data = stream.read(n_sweeps * header.trace_count * header.trace_size)
            return SenseX1000Base.AcqData(data, header, seq_num, n_sweeps)

        def __init__(self, data: bytes, header: 'SenseX1000Base.AcqHeader', seq_num: int, n_sweeps: int) -> None:
            # Construct object from binary data, current header and sweep sequence number/number of sweeps
            self.header = header
            self.n_sweeps = n_sweeps
            self.n_traces = header.trace_count
            self.n_points = header.data_points
            self.trace_list = header.trace_list
            self.seq_nums = list(range(seq_num, seq_num + n_sweeps))

            # Calculate directions (alternating sign if ALTERNATING flag is set, otherwise constant sign)
            self.sweep_dir = 1 if header.acq_flags & SenseX1000Base.AcqFlags.DIRECTION else -1
            self.sweep_dirs = [(-self.sweep_dir if seq_num % 2 else self.sweep_dir)
                               if header.acq_flags & SenseX1000Base.AcqFlags.ALTERNATING
                               else self.sweep_dir for seq_num in self.seq_nums]
            self.timestamps = [header.trig_timestamp + header.trig_delay + seq_num * header.sweep_period for seq_num in self.seq_nums]
            self.time_axes = [header.time_axis for seq_num in self.seq_nums]
            self.freq_axes = [(np.flip(header.freq_axis) if seq_num % 2 else header.freq_axis)
                              if header.acq_flags & SenseX1000Base.AcqFlags.ALTERNATING and
                                 header.acq_flags & SenseX1000Base.AcqFlags.SDOMAIN else header.freq_axis
                              for seq_num in self.seq_nums]

            # use binary data buffer to construct numpy array and put into correct shape
            array = np.frombuffer(data, dtype=header.acq_dtype.info.np)
            shape = [n_sweeps, header.trace_count, header.data_points]
            strides = [header.sweep_size, header.trace_size, header.data_size]
            self.array = np.lib.stride_tricks.as_strided(array, shape, strides)

            # Extract supplemental data if exist
            if header.subhdr_supp_data is not None:
                offset = header.data_points * header.data_size
                supplemental_data = []
                for item in header.subhdr_supp_data.items:
                    # Create new numpy array and set up strides
                    array = np.frombuffer(data, offset=offset, dtype=item.dtype.info.np)
                    shape = [n_sweeps, header.trace_count, item.data_points]
                    strides = [header.sweep_size, header.trace_size, item.data_size]
                    supplemental_data.append(np.lib.stride_tricks.as_strided(array, shape, strides))

                    # Advance to next supplemental data element
                    offset += item.data_points * item.data_size
                self.supplemental_data = supplemental_data


    class Acquisition(object):
        """Container class representing an entire acquisition"""
        _header: 'SenseX1000Base.AcqHeader'
        _stream: BinaryIO

        @classmethod
        def from_stream(cls, stream: BinaryIO) -> 'SenseX1000Base.Acquisition':
            """Create acquisition header from the device data stream and instantiate an Acquisition object"""
            header = SenseX1000Base.AcqHeader.from_stream(stream)
            return SenseX1000Base.Acquisition(header=header, stream=stream)

        def __init__(self, header: 'SenseX1000Base.AcqHeader', stream: BinaryIO):
            # Initialize variables required acquisition logic
            self._header = header
            self._stream = stream
            self._sweeps_remaining = header.sweep_count
            self._seq_num = 0

        @property
        def header(self):
            """The header object associated with this acquisition"""
            return self._header

        @property
        def sweeps_remaining(self):
            """The number of sweeps that can still be read from this acquisition"""
            return self._sweeps_remaining

        @property
        def seq_num(self):
            """The sequence number of the acquisition next to be read"""
            return self._seq_num

        def read(self, n_sweeps=-1) -> 'SenseX1000Base.AcqData':
            """Read given number of sweeps (or all sweeps by default) from device"""
            # Determine actual number of sweeps available to be read
            # Create data object from device stream
            # Advance variables
            n = self._sweeps_remaining if n_sweeps < 0 else min(n_sweeps, self._sweeps_remaining)
            data = SenseX1000Base.AcqData.from_stream(self._stream, self._header, self._seq_num, n)
            self._sweeps_remaining -= n
            self._seq_num += n
            return data

        def data(self, n_sweeps=1):
            """Returns a generator object producing an AcqData object with given number of sweeps per iteration"""

            # generator syntax
            while self._sweeps_remaining > 0:
                yield self.read(n_sweeps=n_sweeps)
