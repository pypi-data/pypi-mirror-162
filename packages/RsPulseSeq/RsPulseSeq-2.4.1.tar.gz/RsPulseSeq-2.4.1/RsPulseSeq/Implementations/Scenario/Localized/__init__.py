from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Localized:
	"""Localized commands group definition. 146 total commands, 13 Subgroups, 14 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("localized", core, parent)

	@property
	def interleaving(self):
		"""interleaving commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_interleaving'):
			from .Interleaving import Interleaving
			self._interleaving = Interleaving(self._core, self._cmd_group)
		return self._interleaving

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	@property
	def direction(self):
		"""direction commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_direction'):
			from .Direction import Direction
			self._direction = Direction(self._core, self._cmd_group)
		return self._direction

	@property
	def emitter(self):
		"""emitter commands group. 2 Sub-classes, 2 commands."""
		if not hasattr(self, '_emitter'):
			from .Emitter import Emitter
			self._emitter = Emitter(self._core, self._cmd_group)
		return self._emitter

	@property
	def group(self):
		"""group commands group. 1 Sub-classes, 7 commands."""
		if not hasattr(self, '_group'):
			from .Group import Group
			self._group = Group(self._core, self._cmd_group)
		return self._group

	@property
	def location(self):
		"""location commands group. 3 Sub-classes, 9 commands."""
		if not hasattr(self, '_location'):
			from .Location import Location
			self._location = Location(self._core, self._cmd_group)
		return self._location

	@property
	def maps(self):
		"""maps commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_maps'):
			from .Maps import Maps
			self._maps = Maps(self._core, self._cmd_group)
		return self._maps

	@property
	def marker(self):
		"""marker commands group. 1 Sub-classes, 8 commands."""
		if not hasattr(self, '_marker'):
			from .Marker import Marker
			self._marker = Marker(self._core, self._cmd_group)
		return self._marker

	@property
	def mchg(self):
		"""mchg commands group. 1 Sub-classes, 7 commands."""
		if not hasattr(self, '_mchg'):
			from .Mchg import Mchg
			self._mchg = Mchg(self._core, self._cmd_group)
		return self._mchg

	@property
	def movement(self):
		"""movement commands group. 2 Sub-classes, 23 commands."""
		if not hasattr(self, '_movement'):
			from .Movement import Movement
			self._movement = Movement(self._core, self._cmd_group)
		return self._movement

	@property
	def receiver(self):
		"""receiver commands group. 2 Sub-classes, 7 commands."""
		if not hasattr(self, '_receiver'):
			from .Receiver import Receiver
			self._receiver = Receiver(self._core, self._cmd_group)
		return self._receiver

	@property
	def subitem(self):
		"""subitem commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_subitem'):
			from .Subitem import Subitem
			self._subitem = Subitem(self._core, self._cmd_group)
		return self._subitem

	@property
	def waveform(self):
		"""waveform commands group. 0 Sub-classes, 6 commands."""
		if not hasattr(self, '_waveform'):
			from .Waveform import Waveform
			self._waveform = Waveform(self._core, self._cmd_group)
		return self._waveform

	def get_alias(self) -> str:
		"""SCPI: SCENario:LOCalized:ALIas \n
		Snippet: value: str = driver.scenario.localized.get_alias() \n
		Enters an alias name. \n
			:return: alias: string
		"""
		response = self._core.io.query_str('SCENario:LOCalized:ALIas?')
		return trim_str_response(response)

	def set_alias(self, alias: str) -> None:
		"""SCPI: SCENario:LOCalized:ALIas \n
		Snippet: driver.scenario.localized.set_alias(alias = '1') \n
		Enters an alias name. \n
			:param alias: string
		"""
		param = Conversions.value_to_quoted_str(alias)
		self._core.io.write(f'SCENario:LOCalized:ALIas {param}')

	def clear(self) -> None:
		"""SCPI: SCENario:LOCalized:CLEar \n
		Snippet: driver.scenario.localized.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCENario:LOCalized:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:LOCalized:CLEar \n
		Snippet: driver.scenario.localized.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:LOCalized:CLEar', opc_timeout_ms)

	def get_current(self) -> float:
		"""SCPI: SCENario:LOCalized:CURRent \n
		Snippet: value: float = driver.scenario.localized.get_current() \n
		Sets the sequence/emitter that is used by the scenario. \n
			:return: current: float Number of the sequence/emitter in the list with multiple sequences
		"""
		response = self._core.io.query_str('SCENario:LOCalized:CURRent?')
		return Conversions.str_to_float(response)

	def set_current(self, current: float) -> None:
		"""SCPI: SCENario:LOCalized:CURRent \n
		Snippet: driver.scenario.localized.set_current(current = 1.0) \n
		Sets the sequence/emitter that is used by the scenario. \n
			:param current: float Number of the sequence/emitter in the list with multiple sequences
		"""
		param = Conversions.decimal_value_to_str(current)
		self._core.io.write(f'SCENario:LOCalized:CURRent {param}')

	def delete(self, delete: float) -> None:
		"""SCPI: SCENario:LOCalized:DELete \n
		Snippet: driver.scenario.localized.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SCENario:LOCalized:DELete {param}')

	def get_distance(self) -> float:
		"""SCPI: SCENario:LOCalized:DISTance \n
		Snippet: value: float = driver.scenario.localized.get_distance() \n
		Sets the distance to the receiver. \n
			:return: distance: float Range: 0 to 1e+09, Unit: m
		"""
		response = self._core.io.query_str('SCENario:LOCalized:DISTance?')
		return Conversions.str_to_float(response)

	def set_distance(self, distance: float) -> None:
		"""SCPI: SCENario:LOCalized:DISTance \n
		Snippet: driver.scenario.localized.set_distance(distance = 1.0) \n
		Sets the distance to the receiver. \n
			:param distance: float Range: 0 to 1e+09, Unit: m
		"""
		param = Conversions.decimal_value_to_str(distance)
		self._core.io.write(f'SCENario:LOCalized:DISTance {param}')

	def get_enable(self) -> bool:
		"""SCPI: SCENario:LOCalized:ENABle \n
		Snippet: value: bool = driver.scenario.localized.get_enable() \n
		If enabled, the PDW list is included in the output file. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:LOCalized:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:LOCalized:ENABle \n
		Snippet: driver.scenario.localized.set_enable(enable = False) \n
		If enabled, the PDW list is included in the output file. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:LOCalized:ENABle {param}')

	def get_frequency(self) -> float:
		"""SCPI: SCENario:LOCalized:FREQuency \n
		Snippet: value: float = driver.scenario.localized.get_frequency() \n
		Sets the frequency for the selected emitter. \n
			:return: frequency: No help available
		"""
		response = self._core.io.query_str('SCENario:LOCalized:FREQuency?')
		return Conversions.str_to_float(response)

	def get_ldelay(self) -> float:
		"""SCPI: SCENario:LOCalized:LDELay \n
		Snippet: value: float = driver.scenario.localized.get_ldelay() \n
		If interleaving is enabled, shifts the processing of the selected PDW list in time. \n
			:return: ldelay: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:LOCalized:LDELay?')
		return Conversions.str_to_float(response)

	def set_ldelay(self, ldelay: float) -> None:
		"""SCPI: SCENario:LOCalized:LDELay \n
		Snippet: driver.scenario.localized.set_ldelay(ldelay = 1.0) \n
		If interleaving is enabled, shifts the processing of the selected PDW list in time. \n
			:param ldelay: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(ldelay)
		self._core.io.write(f'SCENario:LOCalized:LDELay {param}')

	def get_level(self) -> float:
		"""SCPI: SCENario:LOCalized:LEVel \n
		Snippet: value: float = driver.scenario.localized.get_level() \n
		Adds a level offset. \n
			:return: level: float Range: -200 to 0
		"""
		response = self._core.io.query_str('SCENario:LOCalized:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, level: float) -> None:
		"""SCPI: SCENario:LOCalized:LEVel \n
		Snippet: driver.scenario.localized.set_level(level = 1.0) \n
		Adds a level offset. \n
			:param level: float Range: -200 to 0
		"""
		param = Conversions.decimal_value_to_str(level)
		self._core.io.write(f'SCENario:LOCalized:LEVel {param}')

	def get_priority(self) -> float:
		"""SCPI: SCENario:LOCalized:PRIority \n
		Snippet: value: float = driver.scenario.localized.get_priority() \n
		Sets the priority of the selected PDW list , where the higher the value the higher the priority. \n
			:return: priority: float Range: 1 to 100
		"""
		response = self._core.io.query_str('SCENario:LOCalized:PRIority?')
		return Conversions.str_to_float(response)

	def set_priority(self, priority: float) -> None:
		"""SCPI: SCENario:LOCalized:PRIority \n
		Snippet: driver.scenario.localized.set_priority(priority = 1.0) \n
		Sets the priority of the selected PDW list , where the higher the value the higher the priority. \n
			:param priority: float Range: 1 to 100
		"""
		param = Conversions.decimal_value_to_str(priority)
		self._core.io.write(f'SCENario:LOCalized:PRIority {param}')

	def get_select(self) -> float:
		"""SCPI: SCENario:LOCalized:SELect \n
		Snippet: value: float = driver.scenario.localized.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:LOCalized:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:LOCalized:SELect \n
		Snippet: driver.scenario.localized.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:LOCalized:SELect {param}')

	def get_sequence(self) -> str:
		"""SCPI: SCENario:LOCalized:SEQuence \n
		Snippet: value: str = driver.scenario.localized.get_sequence() \n
		Assigns a sequence to the background signal. \n
			:return: sequence: string
		"""
		response = self._core.io.query_str('SCENario:LOCalized:SEQuence?')
		return trim_str_response(response)

	def set_sequence(self, sequence: str) -> None:
		"""SCPI: SCENario:LOCalized:SEQuence \n
		Snippet: driver.scenario.localized.set_sequence(sequence = '1') \n
		Assigns a sequence to the background signal. \n
			:param sequence: string
		"""
		param = Conversions.value_to_quoted_str(sequence)
		self._core.io.write(f'SCENario:LOCalized:SEQuence {param}')

	def get_threshold(self) -> float:
		"""SCPI: SCENario:LOCalized:THReshold \n
		Snippet: value: float = driver.scenario.localized.get_threshold() \n
		Sets a threshold. Pulses at levels below this threshold are omitted. \n
			:return: threshold: float Range: -100 to 0
		"""
		response = self._core.io.query_str('SCENario:LOCalized:THReshold?')
		return Conversions.str_to_float(response)

	def set_threshold(self, threshold: float) -> None:
		"""SCPI: SCENario:LOCalized:THReshold \n
		Snippet: driver.scenario.localized.set_threshold(threshold = 1.0) \n
		Sets a threshold. Pulses at levels below this threshold are omitted. \n
			:param threshold: float Range: -100 to 0
		"""
		param = Conversions.decimal_value_to_str(threshold)
		self._core.io.write(f'SCENario:LOCalized:THReshold {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.DfType:
		"""SCPI: SCENario:LOCalized:TYPE \n
		Snippet: value: enums.DfType = driver.scenario.localized.get_type_py() \n
		Defines whether an emitter/interferer is configured. \n
			:return: type_py: EMITter | | WAVeform
		"""
		response = self._core.io.query_str('SCENario:LOCalized:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.DfType)

	def set_type_py(self, type_py: enums.DfType) -> None:
		"""SCPI: SCENario:LOCalized:TYPE \n
		Snippet: driver.scenario.localized.set_type_py(type_py = enums.DfType.BACKground) \n
		Defines whether an emitter/interferer is configured. \n
			:param type_py: EMITter | | WAVeform
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.DfType)
		self._core.io.write(f'SCENario:LOCalized:TYPE {param}')

	def clone(self) -> 'Localized':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Localized(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
