from typing import ClassVar, List

from .Internal.Core import Core
from .Internal.InstrumentErrors import RsInstrException
from .Internal.CommandsGroup import CommandsGroup
from .Internal.VisaSession import VisaSession
from datetime import datetime, timedelta


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RsPulseSeq:
	"""1291 total commands, 31 Subgroups, 0 group commands"""
	_driver_options = "SupportedInstrModels = PulseSequencer, SupportedIdnPatterns = Pulse\\s*Sequencer, SkipStatusSystemSettings = 1, SimulationIdnString = 'Rohde&Schwarz,PulseSequencer,100001,2.4.1.0024'"
	_global_logging_relative_timestamp: ClassVar[datetime] = None
	_global_logging_target_stream: ClassVar = None

	def __init__(self, resource_name: str, id_query: bool = True, reset: bool = False, options: str = None, direct_session: object = None):
		"""Initializes new RsPulseSeq session. \n
		Parameter options tokens examples:
			- ``Simulate=True`` - starts the session in simulation mode. Default: ``False``
			- ``SelectVisa=socket`` - uses no VISA implementation for socket connections - you do not need any VISA-C installation
			- ``SelectVisa=rs`` - forces usage of RohdeSchwarz Visa
			- ``SelectVisa=ivi`` - forces usage of National Instruments Visa
			- ``QueryInstrumentStatus = False`` - same as ``driver.utilities.instrument_status_checking = False``. Default: ``True``
			- ``WriteDelay = 20, ReadDelay = 5`` - Introduces delay of 20ms before each write and 5ms before each read. Default: ``0ms`` for both
			- ``OpcWaitMode = OpcQuery`` - mode for all the opc-synchronised write/reads. Other modes: StbPolling, StbPollingSlow, StbPollingSuperSlow. Default: ``StbPolling``
			- ``AddTermCharToWriteBinBLock = True`` - Adds one additional LF to the end of the binary data (some instruments require that). Default: ``False``
			- ``AssureWriteWithTermChar = True`` - Makes sure each command/query is terminated with termination character. Default: Interface dependent
			- ``TerminationCharacter = "\\r"`` - Sets the termination character for reading. Default: ``\\n`` (LineFeed or LF)
			- ``DataChunkSize = 10E3`` - Maximum size of one write/read segment. If transferred data is bigger, it is split to more segments. Default: ``1E6`` bytes
			- ``OpcTimeout = 10000`` - same as driver.utilities.opc_timeout = 10000. Default: ``30000ms``
			- ``VisaTimeout = 5000`` - same as driver.utilities.visa_timeout = 5000. Default: ``10000ms``
			- ``ViClearExeMode = Disabled`` - viClear() execution mode. Default: ``execute_on_all``
			- ``OpcQueryAfterWrite = True`` - same as driver.utilities.opc_query_after_write = True. Default: ``False``
			- ``StbInErrorCheck = False`` - if true, the driver checks errors with *STB? If false, it uses SYST:ERR?. Default: ``True``
			- ``LoggingMode = On`` - Sets the logging status right from the start. Default: ``Off``
			- ``LoggingName = 'MyDevice'`` - Sets the name to represent the session in the log entries. Default: ``'resource_name'``
			- ``LogToGlobalTarget = True`` - Sets the logging target to the class-property previously set with RsPulseSeq.set_global_logging_target() Default: ``False``
			- ``LoggingToConsole = True`` - Immediately starts logging to the console. Default: False
			- ``LoggingToUdp = True`` - Immediately starts logging to the UDP port. Default: False
			- ``LoggingUdpPort = 49200`` - UDP port to log to. Default: 49200
		:param resource_name: VISA resource name, e.g. 'TCPIP::192.168.2.1::INSTR'
		:param id_query: if True, the instrument's model name is verified against the models supported by the driver and eventually throws an exception.
		:param reset: Resets the instrument (sends *RST command) and clears its status sybsystem.
		:param options: string tokens alternating the driver settings.
		:param direct_session: Another driver object or pyVisa object to reuse the session instead of opening a new session."""
		self._core = Core(resource_name, id_query, reset, RsPulseSeq._driver_options, options, direct_session)
		self._core.driver_version = '2.4.1.0024'
		self._options = options
		self._add_all_global_repcaps()
		self._custom_properties_init()
		self.utilities.default_instrument_setup()
		# noinspection PyTypeChecker
		self._cmd_group = CommandsGroup("ROOT", self._core, None)

	@classmethod
	def from_existing_session(cls, session: object, options: str = None) -> 'RsPulseSeq':
		"""Creates a new RsPulseSeq object with the entered 'session' reused. \n
		:param session: can be another driver or a direct pyvisa session.
		:param options: string tokens alternating the driver settings."""
		# noinspection PyTypeChecker
		return cls(None, False, False, options, session)
		
	@classmethod
	def set_global_logging_target(cls, target) -> None:
		"""Sets global common target stream that each instance can use. To use it, call the following: io.utilities.logger.set_logging_target_global().
		If an instance uses global logging target, it automatically uses the global relative timestamp (if set).
		You can set the target to None to invalidate it."""
		cls._global_logging_target_stream = target

	@classmethod
	def get_global_logging_target(cls):
		"""Returns global common target stream."""
		return cls._global_logging_target_stream

	@classmethod
	def set_global_logging_relative_timestamp(cls, timestamp: datetime) -> None:
		"""Sets global common relative timestamp for log entries. To use it, call the following: io.utilities.logger.set_relative_timestamp_global()"""
		cls._global_logging_relative_timestamp = timestamp

	@classmethod
	def set_global_logging_relative_timestamp_now(cls) -> None:
		"""Sets global common relative timestamp for log entries to this moment.
		To use it, call the following: io.utilities.logger.set_relative_timestamp_global()."""
		cls._global_logging_relative_timestamp = datetime.now()

	@classmethod
	def clear_global_logging_relative_timestamp(cls) -> None:
		"""Clears the global relative timestamp. After this, all the instances using the global relative timestamp continue logging with the absolute timestamps."""
		cls._global_logging_relative_timestamp = None

	@classmethod
	def get_global_logging_relative_timestamp(cls) -> datetime or None:
		"""Returns global common relative timestamp for log entries."""
		return cls._global_logging_relative_timestamp

	def __str__(self) -> str:
		if self._core.io:
			return f"RsPulseSeq session '{self._core.io.resource_name}'"
		else:
			return f"RsPulseSeq with session closed"

	def get_total_execution_time(self) -> timedelta:
		"""Returns total time spent by the library on communicating with the instrument.
		This time is always shorter than get_total_time(), since it does not include gaps between the communication.
		You can reset this counter with reset_time_statistics()."""
		return self._core.io.total_execution_time

	def get_total_time(self) -> timedelta:
		"""Returns total time spent by the library on communicating with the instrument.
		This time is always shorter than get_total_time(), since it does not include gaps between the communication.
		You can reset this counter with reset_time_statistics()."""
		return datetime.now() - self._core.io.total_time_startpoint

	def reset_time_statistics(self) -> None:
		"""Resets all execution and total time counters. Affects the results of get_total_time() and get_total_execution_time()"""
		self._core.io.reset_time_statistics()

	@staticmethod
	def assert_minimum_version(min_version: str) -> None:
		"""Asserts that the driver version fulfills the minimum required version you have entered.
		This way you make sure your installed driver is of the entered version or newer."""
		min_version_list = min_version.split('.')
		curr_version_list = '2.4.1.0024'.split('.')
		count_min = len(min_version_list)
		count_curr = len(curr_version_list)
		count = count_min if count_min < count_curr else count_curr
		for i in range(count):
			minimum = int(min_version_list[i])
			curr = int(curr_version_list[i])
			if curr > minimum:
				break
			if curr < minimum:
				raise RsInstrException(f"Assertion for minimum RsPulseSeq version failed. Current version: '2.4.1.0024', minimum required version: '{min_version}'")

	@staticmethod
	def list_resources(expression: str = '?*::INSTR', visa_select: str = None) -> List[str]:
		"""Finds all the resources defined by the expression
			- '?*' - matches all the available instruments
			- 'USB::?*' - matches all the USB instruments
			- 'TCPIP::192?*' - matches all the LAN instruments with the IP address starting with 192
		:param expression: see the examples in the function
		:param visa_select: optional parameter selecting a specific VISA. Examples: '@ivi', '@rs'
		"""
		rm = VisaSession.get_resource_manager(visa_select)
		resources = rm.list_resources(expression)
		rm.close()
		# noinspection PyTypeChecker
		return resources

	def close(self) -> None:
		"""Closes the active RsPulseSeq session."""
		self._core.io.close()

	def get_session_handle(self) -> object:
		"""Returns the underlying session handle."""
		return self._core.get_session_handle()

	def _add_all_global_repcaps(self) -> None:
		"""Adds all the repcaps defined as global to the instrument's global repcaps dictionary."""

	def _custom_properties_init(self):
		"""Adds all the interfaces that are custom for the driver."""
		from .CustomFiles.utilities import Utilities
		self.utilities = Utilities(self._core)
		from .CustomFiles.events import Events
		self.events = Events(self._core)

	@property
	def repository(self):
		"""repository commands group. 2 Sub-classes, 15 commands."""
		if not hasattr(self, '_repository'):
			from .Implementations.Repository import Repository
			self._repository = Repository(self._core, self._cmd_group)
		return self._repository

	@property
	def assignment(self):
		"""assignment commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_assignment'):
			from .Implementations.Assignment import Assignment
			self._assignment = Assignment(self._core, self._cmd_group)
		return self._assignment

	@property
	def destination(self):
		"""destination commands group. 1 Sub-classes, 6 commands."""
		if not hasattr(self, '_destination'):
			from .Implementations.Destination import Destination
			self._destination = Destination(self._core, self._cmd_group)
		return self._destination

	@property
	def emitter(self):
		"""emitter commands group. 1 Sub-classes, 8 commands."""
		if not hasattr(self, '_emitter'):
			from .Implementations.Emitter import Emitter
			self._emitter = Emitter(self._core, self._cmd_group)
		return self._emitter

	@property
	def lserver(self):
		"""lserver commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_lserver'):
			from .Implementations.Lserver import Lserver
			self._lserver = Lserver(self._core, self._cmd_group)
		return self._lserver

	@property
	def platform(self):
		"""platform commands group. 1 Sub-classes, 7 commands."""
		if not hasattr(self, '_platform'):
			from .Implementations.Platform import Platform
			self._platform = Platform(self._core, self._cmd_group)
		return self._platform

	@property
	def program(self):
		"""program commands group. 15 Sub-classes, 1 commands."""
		if not hasattr(self, '_program'):
			from .Implementations.Program import Program
			self._program = Program(self._core, self._cmd_group)
		return self._program

	@property
	def scenario(self):
		"""scenario commands group. 17 Sub-classes, 13 commands."""
		if not hasattr(self, '_scenario'):
			from .Implementations.Scenario import Scenario
			self._scenario = Scenario(self._core, self._cmd_group)
		return self._scenario

	@property
	def antenna(self):
		"""antenna commands group. 1 Sub-classes, 6 commands."""
		if not hasattr(self, '_antenna'):
			from .Implementations.Antenna import Antenna
			self._antenna = Antenna(self._core, self._cmd_group)
		return self._antenna

	@property
	def adjustment(self):
		"""adjustment commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_adjustment'):
			from .Implementations.Adjustment import Adjustment
			self._adjustment = Adjustment(self._core, self._cmd_group)
		return self._adjustment

	@property
	def cpanel(self):
		"""cpanel commands group. 6 Sub-classes, 3 commands."""
		if not hasattr(self, '_cpanel'):
			from .Implementations.Cpanel import Cpanel
			self._cpanel = Cpanel(self._core, self._cmd_group)
		return self._cpanel

	@property
	def dialog(self):
		"""dialog commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_dialog'):
			from .Implementations.Dialog import Dialog
			self._dialog = Dialog(self._core, self._cmd_group)
		return self._dialog

	@property
	def dsrc(self):
		"""dsrc commands group. 1 Sub-classes, 7 commands."""
		if not hasattr(self, '_dsrc'):
			from .Implementations.Dsrc import Dsrc
			self._dsrc = Dsrc(self._core, self._cmd_group)
		return self._dsrc

	@property
	def generator(self):
		"""generator commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_generator'):
			from .Implementations.Generator import Generator
			self._generator = Generator(self._core, self._cmd_group)
		return self._generator

	@property
	def importPy(self):
		"""importPy commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_importPy'):
			from .Implementations.ImportPy import ImportPy
			self._importPy = ImportPy(self._core, self._cmd_group)
		return self._importPy

	@property
	def instrument(self):
		"""instrument commands group. 1 Sub-classes, 18 commands."""
		if not hasattr(self, '_instrument'):
			from .Implementations.Instrument import Instrument
			self._instrument = Instrument(self._core, self._cmd_group)
		return self._instrument

	@property
	def ipm(self):
		"""ipm commands group. 9 Sub-classes, 9 commands."""
		if not hasattr(self, '_ipm'):
			from .Implementations.Ipm import Ipm
			self._ipm = Ipm(self._core, self._cmd_group)
		return self._ipm

	@property
	def msgLog(self):
		"""msgLog commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_msgLog'):
			from .Implementations.MsgLog import MsgLog
			self._msgLog = MsgLog(self._core, self._cmd_group)
		return self._msgLog

	@property
	def plot(self):
		"""plot commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_plot'):
			from .Implementations.Plot import Plot
			self._plot = Plot(self._core, self._cmd_group)
		return self._plot

	@property
	def plugin(self):
		"""plugin commands group. 1 Sub-classes, 7 commands."""
		if not hasattr(self, '_plugin'):
			from .Implementations.Plugin import Plugin
			self._plugin = Plugin(self._core, self._cmd_group)
		return self._plugin

	@property
	def preview(self):
		"""preview commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_preview'):
			from .Implementations.Preview import Preview
			self._preview = Preview(self._core, self._cmd_group)
		return self._preview

	@property
	def pulse(self):
		"""pulse commands group. 9 Sub-classes, 8 commands."""
		if not hasattr(self, '_pulse'):
			from .Implementations.Pulse import Pulse
			self._pulse = Pulse(self._core, self._cmd_group)
		return self._pulse

	@property
	def receiver(self):
		"""receiver commands group. 1 Sub-classes, 7 commands."""
		if not hasattr(self, '_receiver'):
			from .Implementations.Receiver import Receiver
			self._receiver = Receiver(self._core, self._cmd_group)
		return self._receiver

	@property
	def repmanager(self):
		"""repmanager commands group. 1 Sub-classes, 4 commands."""
		if not hasattr(self, '_repmanager'):
			from .Implementations.Repmanager import Repmanager
			self._repmanager = Repmanager(self._core, self._cmd_group)
		return self._repmanager

	@property
	def scan(self):
		"""scan commands group. 10 Sub-classes, 8 commands."""
		if not hasattr(self, '_scan'):
			from .Implementations.Scan import Scan
			self._scan = Scan(self._core, self._cmd_group)
		return self._scan

	@property
	def script(self):
		"""script commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_script'):
			from .Implementations.Script import Script
			self._script = Script(self._core, self._cmd_group)
		return self._script

	@property
	def sequence(self):
		"""sequence commands group. 3 Sub-classes, 7 commands."""
		if not hasattr(self, '_sequence'):
			from .Implementations.Sequence import Sequence
			self._sequence = Sequence(self._core, self._cmd_group)
		return self._sequence

	@property
	def setup(self):
		"""setup commands group. 4 Sub-classes, 8 commands."""
		if not hasattr(self, '_setup'):
			from .Implementations.Setup import Setup
			self._setup = Setup(self._core, self._cmd_group)
		return self._setup

	@property
	def status(self):
		"""status commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_status'):
			from .Implementations.Status import Status
			self._status = Status(self._core, self._cmd_group)
		return self._status

	@property
	def system(self):
		"""system commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_system'):
			from .Implementations.System import System
			self._system = System(self._core, self._cmd_group)
		return self._system

	@property
	def waveform(self):
		"""waveform commands group. 8 Sub-classes, 8 commands."""
		if not hasattr(self, '_waveform'):
			from .Implementations.Waveform import Waveform
			self._waveform = Waveform(self._core, self._cmd_group)
		return self._waveform

	def clone(self) -> 'RsPulseSeq':
		"""Creates a deep copy of the RsPulseSeq object. Also copies:
			- All the existing Global repeated capability values
			- All the default group repeated capabilities setting \n
		Does not check the *IDN? response, and does not perform Reset.
		After cloning, you can set all the repeated capabilities settings independentely from the original group.
		Calling close() on the new object does not close the original VISA session"""
		cloned = RsPulseSeq.from_existing_session(self.get_session_handle(), self._options)
		self._cmd_group.synchronize_repcaps(cloned)
		
		return cloned

	def restore_all_repcaps_to_default(self) -> None:
		"""Sets all the Group and Global repcaps to their initial values"""
		self._cmd_group.restore_repcaps()
