from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Cpdw:
	"""Cpdw commands group definition. 22 total commands, 2 Subgroups, 13 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cpdw", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	@property
	def group(self):
		"""group commands group. 1 Sub-classes, 7 commands."""
		if not hasattr(self, '_group'):
			from .Group import Group
			self._group = Group(self._core, self._cmd_group)
		return self._group

	def get_alias(self) -> str:
		"""SCPI: SCENario:CPDW:ALIas \n
		Snippet: value: str = driver.scenario.cpdw.get_alias() \n
		Enters an alias name. \n
			:return: alias: string
		"""
		response = self._core.io.query_str('SCENario:CPDW:ALIas?')
		return trim_str_response(response)

	def set_alias(self, alias: str) -> None:
		"""SCPI: SCENario:CPDW:ALIas \n
		Snippet: driver.scenario.cpdw.set_alias(alias = '1') \n
		Enters an alias name. \n
			:param alias: string
		"""
		param = Conversions.value_to_quoted_str(alias)
		self._core.io.write(f'SCENario:CPDW:ALIas {param}')

	def clear(self) -> None:
		"""SCPI: SCENario:CPDW:CLEar \n
		Snippet: driver.scenario.cpdw.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCENario:CPDW:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:CPDW:CLEar \n
		Snippet: driver.scenario.cpdw.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:CPDW:CLEar', opc_timeout_ms)

	def delete(self, delete: float) -> None:
		"""SCPI: SCENario:CPDW:DELete \n
		Snippet: driver.scenario.cpdw.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SCENario:CPDW:DELete {param}')

	def get_enable(self) -> bool:
		"""SCPI: SCENario:CPDW:ENABle \n
		Snippet: value: bool = driver.scenario.cpdw.get_enable() \n
		If enabled, the PDW list is included in the output file. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CPDW:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:CPDW:ENABle \n
		Snippet: driver.scenario.cpdw.set_enable(enable = False) \n
		If enabled, the PDW list is included in the output file. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:CPDW:ENABle {param}')

	def get_freq(self) -> float:
		"""SCPI: SCENario:CPDW:FREQ \n
		Snippet: value: float = driver.scenario.cpdw.get_freq() \n
		Sets the frequency for the selected emitter. \n
			:return: freq: float Range: -1000 to 4.4e+10
		"""
		response = self._core.io.query_str('SCENario:CPDW:FREQ?')
		return Conversions.str_to_float(response)

	def set_freq(self, freq: float) -> None:
		"""SCPI: SCENario:CPDW:FREQ \n
		Snippet: driver.scenario.cpdw.set_freq(freq = 1.0) \n
		Sets the frequency for the selected emitter. \n
			:param freq: float Range: -1000 to 4.4e+10
		"""
		param = Conversions.decimal_value_to_str(freq)
		self._core.io.write(f'SCENario:CPDW:FREQ {param}')

	def get_interleaving(self) -> bool:
		"""SCPI: SCENario:CPDW:INTerleaving \n
		Snippet: value: bool = driver.scenario.cpdw.get_interleaving() \n
		If enabled, multiple PDW lists are interleaved into a single output file using a priority-based dropping algorithm. Set
		the priority with the command method RsPulseSeq.Scenario.Cpdw.priority. \n
			:return: interleaving: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CPDW:INTerleaving?')
		return Conversions.str_to_bool(response)

	def set_interleaving(self, interleaving: bool) -> None:
		"""SCPI: SCENario:CPDW:INTerleaving \n
		Snippet: driver.scenario.cpdw.set_interleaving(interleaving = False) \n
		If enabled, multiple PDW lists are interleaved into a single output file using a priority-based dropping algorithm. Set
		the priority with the command method RsPulseSeq.Scenario.Cpdw.priority. \n
			:param interleaving: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(interleaving)
		self._core.io.write(f'SCENario:CPDW:INTerleaving {param}')

	def get_ldelay(self) -> float:
		"""SCPI: SCENario:CPDW:LDELay \n
		Snippet: value: float = driver.scenario.cpdw.get_ldelay() \n
		If interleaving is enabled, shifts the processing of the selected PDW list in time. \n
			:return: ldelay: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:CPDW:LDELay?')
		return Conversions.str_to_float(response)

	def set_ldelay(self, ldelay: float) -> None:
		"""SCPI: SCENario:CPDW:LDELay \n
		Snippet: driver.scenario.cpdw.set_ldelay(ldelay = 1.0) \n
		If interleaving is enabled, shifts the processing of the selected PDW list in time. \n
			:param ldelay: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(ldelay)
		self._core.io.write(f'SCENario:CPDW:LDELay {param}')

	def get_level(self) -> float:
		"""SCPI: SCENario:CPDW:LEVel \n
		Snippet: value: float = driver.scenario.cpdw.get_level() \n
		Adds a level offset. \n
			:return: level: float Range: -200 to 0
		"""
		response = self._core.io.query_str('SCENario:CPDW:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, level: float) -> None:
		"""SCPI: SCENario:CPDW:LEVel \n
		Snippet: driver.scenario.cpdw.set_level(level = 1.0) \n
		Adds a level offset. \n
			:param level: float Range: -200 to 0
		"""
		param = Conversions.decimal_value_to_str(level)
		self._core.io.write(f'SCENario:CPDW:LEVel {param}')

	def get_lvabs(self) -> float:
		"""SCPI: SCENario:CPDW:LVABs \n
		Snippet: value: float = driver.scenario.cpdw.get_lvabs() \n
		Sets the absolute level for the selected PDW list. \n
			:return: lvabs: float Range: -130 to 30
		"""
		response = self._core.io.query_str('SCENario:CPDW:LVABs?')
		return Conversions.str_to_float(response)

	def set_lvabs(self, lvabs: float) -> None:
		"""SCPI: SCENario:CPDW:LVABs \n
		Snippet: driver.scenario.cpdw.set_lvabs(lvabs = 1.0) \n
		Sets the absolute level for the selected PDW list. \n
			:param lvabs: float Range: -130 to 30
		"""
		param = Conversions.decimal_value_to_str(lvabs)
		self._core.io.write(f'SCENario:CPDW:LVABs {param}')

	def get_name(self) -> str:
		"""SCPI: SCENario:CPDW:NAME \n
		Snippet: value: str = driver.scenario.cpdw.get_name() \n
		Selects the waveform element, used to import the PDW list. Query the list of waveform elements with the command method
		RsPulseSeq.Waveform.catalog. \n
			:return: name: string
		"""
		response = self._core.io.query_str('SCENario:CPDW:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: SCENario:CPDW:NAME \n
		Snippet: driver.scenario.cpdw.set_name(name = '1') \n
		Selects the waveform element, used to import the PDW list. Query the list of waveform elements with the command method
		RsPulseSeq.Waveform.catalog. \n
			:param name: string
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'SCENario:CPDW:NAME {param}')

	def get_priority(self) -> float:
		"""SCPI: SCENario:CPDW:PRIority \n
		Snippet: value: float = driver.scenario.cpdw.get_priority() \n
		Sets the priority of the selected PDW list , where the higher the value the higher the priority. \n
			:return: priority: float Range: 1 to 100
		"""
		response = self._core.io.query_str('SCENario:CPDW:PRIority?')
		return Conversions.str_to_float(response)

	def set_priority(self, priority: float) -> None:
		"""SCPI: SCENario:CPDW:PRIority \n
		Snippet: driver.scenario.cpdw.set_priority(priority = 1.0) \n
		Sets the priority of the selected PDW list , where the higher the value the higher the priority. \n
			:param priority: float Range: 1 to 100
		"""
		param = Conversions.decimal_value_to_str(priority)
		self._core.io.write(f'SCENario:CPDW:PRIority {param}')

	def get_select(self) -> float:
		"""SCPI: SCENario:CPDW:SELect \n
		Snippet: value: float = driver.scenario.cpdw.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:CPDW:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:CPDW:SELect \n
		Snippet: driver.scenario.cpdw.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:CPDW:SELect {param}')

	def get_threshold(self) -> float:
		"""SCPI: SCENario:CPDW:THReshold \n
		Snippet: value: float = driver.scenario.cpdw.get_threshold() \n
		Sets a threshold. Pulses at levels below this threshold are omitted. \n
			:return: threshold: float Range: -100 to 0
		"""
		response = self._core.io.query_str('SCENario:CPDW:THReshold?')
		return Conversions.str_to_float(response)

	def set_threshold(self, threshold: float) -> None:
		"""SCPI: SCENario:CPDW:THReshold \n
		Snippet: driver.scenario.cpdw.set_threshold(threshold = 1.0) \n
		Sets a threshold. Pulses at levels below this threshold are omitted. \n
			:param threshold: float Range: -100 to 0
		"""
		param = Conversions.decimal_value_to_str(threshold)
		self._core.io.write(f'SCENario:CPDW:THReshold {param}')

	def clone(self) -> 'Cpdw':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Cpdw(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
