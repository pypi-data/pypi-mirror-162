from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Cemit:
	"""Cemit commands group definition. 52 total commands, 7 Subgroups, 14 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cemit", core, parent)

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
		"""direction commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_direction'):
			from .Direction import Direction
			self._direction = Direction(self._core, self._cmd_group)
		return self._direction

	@property
	def emitter(self):
		"""emitter commands group. 1 Sub-classes, 2 commands."""
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

	def get_alias(self) -> str:
		"""SCPI: SCENario:CEMit:ALIas \n
		Snippet: value: str = driver.scenario.cemit.get_alias() \n
		Enters an alias name. \n
			:return: alias: string
		"""
		response = self._core.io.query_str('SCENario:CEMit:ALIas?')
		return trim_str_response(response)

	def set_alias(self, alias: str) -> None:
		"""SCPI: SCENario:CEMit:ALIas \n
		Snippet: driver.scenario.cemit.set_alias(alias = '1') \n
		Enters an alias name. \n
			:param alias: string
		"""
		param = Conversions.value_to_quoted_str(alias)
		self._core.io.write(f'SCENario:CEMit:ALIas {param}')

	def clear(self) -> None:
		"""SCPI: SCENario:CEMit:CLEar \n
		Snippet: driver.scenario.cemit.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCENario:CEMit:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:CEMit:CLEar \n
		Snippet: driver.scenario.cemit.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:CEMit:CLEar', opc_timeout_ms)

	def get_current(self) -> float:
		"""SCPI: SCENario:CEMit:CURRent \n
		Snippet: value: float = driver.scenario.cemit.get_current() \n
		No command help available \n
			:return: current: No help available
		"""
		response = self._core.io.query_str('SCENario:CEMit:CURRent?')
		return Conversions.str_to_float(response)

	def set_current(self, current: float) -> None:
		"""SCPI: SCENario:CEMit:CURRent \n
		Snippet: driver.scenario.cemit.set_current(current = 1.0) \n
		No command help available \n
			:param current: No help available
		"""
		param = Conversions.decimal_value_to_str(current)
		self._core.io.write(f'SCENario:CEMit:CURRent {param}')

	def delete(self, delete: float) -> None:
		"""SCPI: SCENario:CEMit:DELete \n
		Snippet: driver.scenario.cemit.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SCENario:CEMit:DELete {param}')

	def get_enable(self) -> bool:
		"""SCPI: SCENario:CEMit:ENABle \n
		Snippet: value: bool = driver.scenario.cemit.get_enable() \n
		If enabled, the PDW list is included in the output file. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CEMit:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:CEMit:ENABle \n
		Snippet: driver.scenario.cemit.set_enable(enable = False) \n
		If enabled, the PDW list is included in the output file. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:CEMit:ENABle {param}')

	def get_fq_qffset(self) -> float:
		"""SCPI: SCENario:CEMit:FQOFfset \n
		Snippet: value: float = driver.scenario.cemit.get_fq_qffset() \n
		Sets the frequency offset for the selected emitter. \n
			:return: fq_offset: float Range: -2e+09 to 2e+09
		"""
		response = self._core.io.query_str('SCENario:CEMit:FQOFfset?')
		return Conversions.str_to_float(response)

	def set_fq_qffset(self, fq_offset: float) -> None:
		"""SCPI: SCENario:CEMit:FQOFfset \n
		Snippet: driver.scenario.cemit.set_fq_qffset(fq_offset = 1.0) \n
		Sets the frequency offset for the selected emitter. \n
			:param fq_offset: float Range: -2e+09 to 2e+09
		"""
		param = Conversions.decimal_value_to_str(fq_offset)
		self._core.io.write(f'SCENario:CEMit:FQOFfset {param}')

	def get_frequency(self) -> float:
		"""SCPI: SCENario:CEMit:FREQuency \n
		Snippet: value: float = driver.scenario.cemit.get_frequency() \n
		Sets the frequency for the selected emitter. \n
			:return: frequency: No help available
		"""
		response = self._core.io.query_str('SCENario:CEMit:FREQuency?')
		return Conversions.str_to_float(response)

	def get_ldelay(self) -> float:
		"""SCPI: SCENario:CEMit:LDELay \n
		Snippet: value: float = driver.scenario.cemit.get_ldelay() \n
		If interleaving is enabled, shifts the processing of the selected PDW list in time. \n
			:return: ldelay: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:CEMit:LDELay?')
		return Conversions.str_to_float(response)

	def set_ldelay(self, ldelay: float) -> None:
		"""SCPI: SCENario:CEMit:LDELay \n
		Snippet: driver.scenario.cemit.set_ldelay(ldelay = 1.0) \n
		If interleaving is enabled, shifts the processing of the selected PDW list in time. \n
			:param ldelay: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(ldelay)
		self._core.io.write(f'SCENario:CEMit:LDELay {param}')

	def get_level(self) -> float:
		"""SCPI: SCENario:CEMit:LEVel \n
		Snippet: value: float = driver.scenario.cemit.get_level() \n
		Adds a level offset. \n
			:return: level: float Range: -200 to 0
		"""
		response = self._core.io.query_str('SCENario:CEMit:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, level: float) -> None:
		"""SCPI: SCENario:CEMit:LEVel \n
		Snippet: driver.scenario.cemit.set_level(level = 1.0) \n
		Adds a level offset. \n
			:param level: float Range: -200 to 0
		"""
		param = Conversions.decimal_value_to_str(level)
		self._core.io.write(f'SCENario:CEMit:LEVel {param}')

	def get_lvabs(self) -> float:
		"""SCPI: SCENario:CEMit:LVABs \n
		Snippet: value: float = driver.scenario.cemit.get_lvabs() \n
		Sets the absolute level for the selected PDW list. \n
			:return: lvabs: float Range: -130 to 30
		"""
		response = self._core.io.query_str('SCENario:CEMit:LVABs?')
		return Conversions.str_to_float(response)

	def set_lvabs(self, lvabs: float) -> None:
		"""SCPI: SCENario:CEMit:LVABs \n
		Snippet: driver.scenario.cemit.set_lvabs(lvabs = 1.0) \n
		Sets the absolute level for the selected PDW list. \n
			:param lvabs: float Range: -130 to 30
		"""
		param = Conversions.decimal_value_to_str(lvabs)
		self._core.io.write(f'SCENario:CEMit:LVABs {param}')

	def get_priority(self) -> float:
		"""SCPI: SCENario:CEMit:PRIority \n
		Snippet: value: float = driver.scenario.cemit.get_priority() \n
		Sets the priority of the selected PDW list , where the higher the value the higher the priority. \n
			:return: priority: float Range: 1 to 100
		"""
		response = self._core.io.query_str('SCENario:CEMit:PRIority?')
		return Conversions.str_to_float(response)

	def set_priority(self, priority: float) -> None:
		"""SCPI: SCENario:CEMit:PRIority \n
		Snippet: driver.scenario.cemit.set_priority(priority = 1.0) \n
		Sets the priority of the selected PDW list , where the higher the value the higher the priority. \n
			:param priority: float Range: 1 to 100
		"""
		param = Conversions.decimal_value_to_str(priority)
		self._core.io.write(f'SCENario:CEMit:PRIority {param}')

	def get_scn_delay(self) -> float:
		"""SCPI: SCENario:CEMit:SCNDelay \n
		Snippet: value: float = driver.scenario.cemit.get_scn_delay() \n
		Sets the scan delay for the selected emitter. \n
			:return: scn_delay: float Range: -3600 to 3600
		"""
		response = self._core.io.query_str('SCENario:CEMit:SCNDelay?')
		return Conversions.str_to_float(response)

	def set_scn_delay(self, scn_delay: float) -> None:
		"""SCPI: SCENario:CEMit:SCNDelay \n
		Snippet: driver.scenario.cemit.set_scn_delay(scn_delay = 1.0) \n
		Sets the scan delay for the selected emitter. \n
			:param scn_delay: float Range: -3600 to 3600
		"""
		param = Conversions.decimal_value_to_str(scn_delay)
		self._core.io.write(f'SCENario:CEMit:SCNDelay {param}')

	def get_select(self) -> float:
		"""SCPI: SCENario:CEMit:SELect \n
		Snippet: value: float = driver.scenario.cemit.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:CEMit:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:CEMit:SELect \n
		Snippet: driver.scenario.cemit.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:CEMit:SELect {param}')

	def get_threshold(self) -> float:
		"""SCPI: SCENario:CEMit:THReshold \n
		Snippet: value: float = driver.scenario.cemit.get_threshold() \n
		Sets a threshold. Pulses at levels below this threshold are omitted. \n
			:return: threshold: float Range: -100 to 0
		"""
		response = self._core.io.query_str('SCENario:CEMit:THReshold?')
		return Conversions.str_to_float(response)

	def set_threshold(self, threshold: float) -> None:
		"""SCPI: SCENario:CEMit:THReshold \n
		Snippet: driver.scenario.cemit.set_threshold(threshold = 1.0) \n
		Sets a threshold. Pulses at levels below this threshold are omitted. \n
			:param threshold: float Range: -100 to 0
		"""
		param = Conversions.decimal_value_to_str(threshold)
		self._core.io.write(f'SCENario:CEMit:THReshold {param}')

	def clone(self) -> 'Cemit':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Cemit(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
