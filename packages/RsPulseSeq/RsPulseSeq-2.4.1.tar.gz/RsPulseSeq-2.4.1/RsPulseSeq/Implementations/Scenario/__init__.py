from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Scenario:
	"""Scenario commands group definition. 459 total commands, 17 Subgroups, 13 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scenario", core, parent)

	@property
	def cemit(self):
		"""cemit commands group. 7 Sub-classes, 14 commands."""
		if not hasattr(self, '_cemit'):
			from .Cemit import Cemit
			self._cemit = Cemit(self._core, self._cmd_group)
		return self._cemit

	@property
	def destination(self):
		"""destination commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_destination'):
			from .Destination import Destination
			self._destination = Destination(self._core, self._cmd_group)
		return self._destination

	@property
	def df(self):
		"""df commands group. 14 Sub-classes, 14 commands."""
		if not hasattr(self, '_df'):
			from .Df import Df
			self._df = Df(self._core, self._cmd_group)
		return self._df

	@property
	def localized(self):
		"""localized commands group. 13 Sub-classes, 14 commands."""
		if not hasattr(self, '_localized'):
			from .Localized import Localized
			self._localized = Localized(self._core, self._cmd_group)
		return self._localized

	@property
	def cache(self):
		"""cache commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_cache'):
			from .Cache import Cache
			self._cache = Cache(self._core, self._cmd_group)
		return self._cache

	@property
	def calculate(self):
		"""calculate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_calculate'):
			from .Calculate import Calculate
			self._calculate = Calculate(self._core, self._cmd_group)
		return self._calculate

	@property
	def cpdw(self):
		"""cpdw commands group. 2 Sub-classes, 13 commands."""
		if not hasattr(self, '_cpdw'):
			from .Cpdw import Cpdw
			self._cpdw = Cpdw(self._core, self._cmd_group)
		return self._cpdw

	@property
	def csequence(self):
		"""csequence commands group. 1 Sub-classes, 7 commands."""
		if not hasattr(self, '_csequence'):
			from .Csequence import Csequence
			self._csequence = Csequence(self._core, self._cmd_group)
		return self._csequence

	@property
	def emitter(self):
		"""emitter commands group. 2 Sub-classes, 2 commands."""
		if not hasattr(self, '_emitter'):
			from .Emitter import Emitter
			self._emitter = Emitter(self._core, self._cmd_group)
		return self._emitter

	@property
	def generator(self):
		"""generator commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_generator'):
			from .Generator import Generator
			self._generator = Generator(self._core, self._cmd_group)
		return self._generator

	@property
	def ilCache(self):
		"""ilCache commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_ilCache'):
			from .IlCache import IlCache
			self._ilCache = IlCache(self._core, self._cmd_group)
		return self._ilCache

	@property
	def interleave(self):
		"""interleave commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_interleave'):
			from .Interleave import Interleave
			self._interleave = Interleave(self._core, self._cmd_group)
		return self._interleave

	@property
	def output(self):
		"""output commands group. 7 Sub-classes, 11 commands."""
		if not hasattr(self, '_output'):
			from .Output import Output
			self._output = Output(self._core, self._cmd_group)
		return self._output

	@property
	def pdw(self):
		"""pdw commands group. 2 Sub-classes, 5 commands."""
		if not hasattr(self, '_pdw'):
			from .Pdw import Pdw
			self._pdw = Pdw(self._core, self._cmd_group)
		return self._pdw

	@property
	def sequence(self):
		"""sequence commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_sequence'):
			from .Sequence import Sequence
			self._sequence = Sequence(self._core, self._cmd_group)
		return self._sequence

	@property
	def trigger(self):
		"""trigger commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_trigger'):
			from .Trigger import Trigger
			self._trigger = Trigger(self._core, self._cmd_group)
		return self._trigger

	@property
	def volatile(self):
		"""volatile commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_volatile'):
			from .Volatile import Volatile
			self._volatile = Volatile(self._core, self._cmd_group)
		return self._volatile

	def get_catalog(self) -> str:
		"""SCPI: SCENario:CATalog \n
		Snippet: value: str = driver.scenario.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('SCENario:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: SCENario:COMMent \n
		Snippet: value: str = driver.scenario.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('SCENario:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: SCENario:COMMent \n
		Snippet: driver.scenario.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'SCENario:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: SCENario:CREate \n
		Snippet: driver.scenario.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'SCENario:CREate {param}')

	def get_id(self) -> float:
		"""SCPI: SCENario:ID \n
		Snippet: value: float = driver.scenario.get_id() \n
		Queries the database identifier of the selected scenario. \n
			:return: idn: float
		"""
		response = self._core.io.query_str('SCENario:ID?')
		return Conversions.str_to_float(response)

	def get_name(self) -> str:
		"""SCPI: SCENario:NAME \n
		Snippet: value: str = driver.scenario.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('SCENario:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: SCENario:NAME \n
		Snippet: driver.scenario.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'SCENario:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: SCENario:REMove \n
		Snippet: driver.scenario.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'SCENario:REMove {param}')

	def set_sanitize(self, sanitize: enums.SanitizeScenario) -> None:
		"""SCPI: SCENario:SANitize \n
		Snippet: driver.scenario.set_sanitize(sanitize = enums.SanitizeScenario.ALL) \n
		Removes uploaded waveforms from the hard disk of the signal generator. \n
			:param sanitize: SCENario| REPository| ALL SCENario Removes the current scenario waveforms REPository Removes the waveforms of all scenarios from the current repository ALL Removes all waveforms created by the R&S Pulse Sequencer
		"""
		param = Conversions.enum_scalar_to_str(sanitize, enums.SanitizeScenario)
		self._core.io.write(f'SCENario:SANitize {param}')

	def get_select(self) -> str:
		"""SCPI: SCENario:SELect \n
		Snippet: value: str = driver.scenario.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('SCENario:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: SCENario:SELect \n
		Snippet: driver.scenario.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'SCENario:SELect {param}')

	def start(self) -> None:
		"""SCPI: SCENario:STARt \n
		Snippet: driver.scenario.start() \n
		Starts/stops signal generation. \n
		"""
		self._core.io.write(f'SCENario:STARt')

	def start_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:STARt \n
		Snippet: driver.scenario.start_with_opc() \n
		Starts/stops signal generation. \n
		Same as start, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:STARt', opc_timeout_ms)

	# noinspection PyTypeChecker
	def get_state(self) -> enums.State:
		"""SCPI: SCENario:STATe \n
		Snippet: value: enums.State = driver.scenario.get_state() \n
		Queries the current scenario status. \n
			:return: state: IDLE| RUN
		"""
		response = self._core.io.query_str('SCENario:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.State)

	def stop(self) -> None:
		"""SCPI: SCENario:STOP \n
		Snippet: driver.scenario.stop() \n
		Starts/stops signal generation. \n
		"""
		self._core.io.write(f'SCENario:STOP')

	def stop_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:STOP \n
		Snippet: driver.scenario.stop_with_opc() \n
		Starts/stops signal generation. \n
		Same as stop, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:STOP', opc_timeout_ms)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.ScenarioType:
		"""SCPI: SCENario:TYPE \n
		Snippet: value: enums.ScenarioType = driver.scenario.get_type_py() \n
		Sets the scenario type. \n
			:return: type_py: SEQuence| CSEQuence| EMITter| CEMitter| LOCalized| DF| PDW | WAVeform
		"""
		response = self._core.io.query_str('SCENario:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ScenarioType)

	def set_type_py(self, type_py: enums.ScenarioType) -> None:
		"""SCPI: SCENario:TYPE \n
		Snippet: driver.scenario.set_type_py(type_py = enums.ScenarioType.CEMitter) \n
		Sets the scenario type. \n
			:param type_py: SEQuence| CSEQuence| EMITter| CEMitter| LOCalized| DF| PDW | WAVeform
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.ScenarioType)
		self._core.io.write(f'SCENario:TYPE {param}')

	def get_waveform(self) -> str:
		"""SCPI: SCENario:WAVeform \n
		Snippet: value: str = driver.scenario.get_waveform() \n
		Specify the name of the 'Signal Generation' output file. \n
			:return: waveform: string
		"""
		response = self._core.io.query_str('SCENario:WAVeform?')
		return trim_str_response(response)

	def set_waveform(self, waveform: str) -> None:
		"""SCPI: SCENario:WAVeform \n
		Snippet: driver.scenario.set_waveform(waveform = '1') \n
		Specify the name of the 'Signal Generation' output file. \n
			:param waveform: string
		"""
		param = Conversions.value_to_quoted_str(waveform)
		self._core.io.write(f'SCENario:WAVeform {param}')

	def clone(self) -> 'Scenario':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Scenario(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
