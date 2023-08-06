from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class State:
	"""State commands group definition. 9 total commands, 1 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def clear(self) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:CLEar \n
		Snippet: driver.scenario.localized.emitter.state.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCENario:LOCalized:EMITter:STATe:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:CLEar \n
		Snippet: driver.scenario.localized.emitter.state.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:LOCalized:EMITter:STATe:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:COUNt \n
		Snippet: value: float = driver.scenario.localized.emitter.state.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('SCENario:LOCalized:EMITter:STATe:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:DELete \n
		Snippet: driver.scenario.localized.emitter.state.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SCENario:LOCalized:EMITter:STATe:DELete {param}')

	def get_duration(self) -> float:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:DURation \n
		Snippet: value: float = driver.scenario.localized.emitter.state.get_duration() \n
		Sets the duration during that the emitter remains in the current state. \n
			:return: duration: float Range: -1e+06 to 1e+06
		"""
		response = self._core.io.query_str('SCENario:LOCalized:EMITter:STATe:DURation?')
		return Conversions.str_to_float(response)

	def set_duration(self, duration: float) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:DURation \n
		Snippet: driver.scenario.localized.emitter.state.set_duration(duration = 1.0) \n
		Sets the duration during that the emitter remains in the current state. \n
			:param duration: float Range: -1e+06 to 1e+06
		"""
		param = Conversions.decimal_value_to_str(duration)
		self._core.io.write(f'SCENario:LOCalized:EMITter:STATe:DURation {param}')

	def get_enable(self) -> bool:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:ENABle \n
		Snippet: value: bool = driver.scenario.localized.emitter.state.get_enable() \n
		Enables that an emitter can use on and off states. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:LOCalized:EMITter:STATe:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:ENABle \n
		Snippet: driver.scenario.localized.emitter.state.set_enable(enable = False) \n
		Enables that an emitter can use on and off states. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:LOCalized:EMITter:STATe:ENABle {param}')

	def set_insert(self, insert: float) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:INSert \n
		Snippet: driver.scenario.localized.emitter.state.set_insert(insert = 1.0) \n
		Inserts a new item before the selected one. \n
			:param insert: float
		"""
		param = Conversions.decimal_value_to_str(insert)
		self._core.io.write(f'SCENario:LOCalized:EMITter:STATe:INSert {param}')

	def get_select(self) -> float:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:SELect \n
		Snippet: value: float = driver.scenario.localized.emitter.state.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:LOCalized:EMITter:STATe:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:SELect \n
		Snippet: driver.scenario.localized.emitter.state.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:LOCalized:EMITter:STATe:SELect {param}')

	def get_value(self) -> bool:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:VALue \n
		Snippet: value: bool = driver.scenario.localized.emitter.state.get_value() \n
		Sets the emitter state during the selected period. \n
			:return: value: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:LOCalized:EMITter:STATe:VALue?')
		return Conversions.str_to_bool(response)

	def set_value(self, value: bool) -> None:
		"""SCPI: SCENario:LOCalized:EMITter:STATe:VALue \n
		Snippet: driver.scenario.localized.emitter.state.set_value(value = False) \n
		Sets the emitter state during the selected period. \n
			:param value: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(value)
		self._core.io.write(f'SCENario:LOCalized:EMITter:STATe:VALue {param}')

	def clone(self) -> 'State':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = State(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
