from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FmStep:
	"""FmStep commands group definition. 8 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fmStep", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def clear(self) -> None:
		"""SCPI: PULSe:MOP:FMSTep:CLEar \n
		Snippet: driver.pulse.mop.fmStep.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'PULSe:MOP:FMSTep:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PULSe:MOP:FMSTep:CLEar \n
		Snippet: driver.pulse.mop.fmStep.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PULSe:MOP:FMSTep:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: PULSe:MOP:FMSTep:COUNt \n
		Snippet: value: float = driver.pulse.mop.fmStep.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('PULSe:MOP:FMSTep:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: PULSe:MOP:FMSTep:DELete \n
		Snippet: driver.pulse.mop.fmStep.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'PULSe:MOP:FMSTep:DELete {param}')

	def get_duration(self) -> float:
		"""SCPI: PULSe:MOP:FMSTep:DURation \n
		Snippet: value: float = driver.pulse.mop.fmStep.get_duration() \n
		Sets the step time. \n
			:return: duration: float Range: 0 to 3600, Unit: s
		"""
		response = self._core.io.query_str('PULSe:MOP:FMSTep:DURation?')
		return Conversions.str_to_float(response)

	def set_duration(self, duration: float) -> None:
		"""SCPI: PULSe:MOP:FMSTep:DURation \n
		Snippet: driver.pulse.mop.fmStep.set_duration(duration = 1.0) \n
		Sets the step time. \n
			:param duration: float Range: 0 to 3600, Unit: s
		"""
		param = Conversions.decimal_value_to_str(duration)
		self._core.io.write(f'PULSe:MOP:FMSTep:DURation {param}')

	def get_frequency(self) -> float:
		"""SCPI: PULSe:MOP:FMSTep:FREQuency \n
		Snippet: value: float = driver.pulse.mop.fmStep.get_frequency() \n
		Sets the step frequency. \n
			:return: frequency: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:FMSTep:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: PULSe:MOP:FMSTep:FREQuency \n
		Snippet: driver.pulse.mop.fmStep.set_frequency(frequency = 1.0) \n
		Sets the step frequency. \n
			:param frequency: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'PULSe:MOP:FMSTep:FREQuency {param}')

	def set_insert(self, insert: float) -> None:
		"""SCPI: PULSe:MOP:FMSTep:INSert \n
		Snippet: driver.pulse.mop.fmStep.set_insert(insert = 1.0) \n
		Inserts a new item before the selected one. \n
			:param insert: float
		"""
		param = Conversions.decimal_value_to_str(insert)
		self._core.io.write(f'PULSe:MOP:FMSTep:INSert {param}')

	def get_select(self) -> float:
		"""SCPI: PULSe:MOP:FMSTep:SELect \n
		Snippet: value: float = driver.pulse.mop.fmStep.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('PULSe:MOP:FMSTep:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: PULSe:MOP:FMSTep:SELect \n
		Snippet: driver.pulse.mop.fmStep.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'PULSe:MOP:FMSTep:SELect {param}')

	def clone(self) -> 'FmStep':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FmStep(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
