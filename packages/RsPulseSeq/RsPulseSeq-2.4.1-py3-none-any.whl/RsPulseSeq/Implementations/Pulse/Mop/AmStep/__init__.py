from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AmStep:
	"""AmStep commands group definition. 8 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("amStep", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def clear(self) -> None:
		"""SCPI: PULSe:MOP:AMSTep:CLEar \n
		Snippet: driver.pulse.mop.amStep.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'PULSe:MOP:AMSTep:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PULSe:MOP:AMSTep:CLEar \n
		Snippet: driver.pulse.mop.amStep.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PULSe:MOP:AMSTep:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: PULSe:MOP:AMSTep:COUNt \n
		Snippet: value: float = driver.pulse.mop.amStep.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('PULSe:MOP:AMSTep:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: PULSe:MOP:AMSTep:DELete \n
		Snippet: driver.pulse.mop.amStep.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'PULSe:MOP:AMSTep:DELete {param}')

	def get_duration(self) -> float:
		"""SCPI: PULSe:MOP:AMSTep:DURation \n
		Snippet: value: float = driver.pulse.mop.amStep.get_duration() \n
		Sets the step time. \n
			:return: duration: float Range: 0 to 3600, Unit: s
		"""
		response = self._core.io.query_str('PULSe:MOP:AMSTep:DURation?')
		return Conversions.str_to_float(response)

	def set_duration(self, duration: float) -> None:
		"""SCPI: PULSe:MOP:AMSTep:DURation \n
		Snippet: driver.pulse.mop.amStep.set_duration(duration = 1.0) \n
		Sets the step time. \n
			:param duration: float Range: 0 to 3600, Unit: s
		"""
		param = Conversions.decimal_value_to_str(duration)
		self._core.io.write(f'PULSe:MOP:AMSTep:DURation {param}')

	def set_insert(self, insert: float) -> None:
		"""SCPI: PULSe:MOP:AMSTep:INSert \n
		Snippet: driver.pulse.mop.amStep.set_insert(insert = 1.0) \n
		Inserts a new item before the selected one. \n
			:param insert: float
		"""
		param = Conversions.decimal_value_to_str(insert)
		self._core.io.write(f'PULSe:MOP:AMSTep:INSert {param}')

	def get_level(self) -> float:
		"""SCPI: PULSe:MOP:AMSTep:LEVel \n
		Snippet: value: float = driver.pulse.mop.amStep.get_level() \n
		Sets the step level. \n
			:return: level: float Range: -100 to 0
		"""
		response = self._core.io.query_str('PULSe:MOP:AMSTep:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, level: float) -> None:
		"""SCPI: PULSe:MOP:AMSTep:LEVel \n
		Snippet: driver.pulse.mop.amStep.set_level(level = 1.0) \n
		Sets the step level. \n
			:param level: float Range: -100 to 0
		"""
		param = Conversions.decimal_value_to_str(level)
		self._core.io.write(f'PULSe:MOP:AMSTep:LEVel {param}')

	def get_select(self) -> float:
		"""SCPI: PULSe:MOP:AMSTep:SELect \n
		Snippet: value: float = driver.pulse.mop.amStep.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('PULSe:MOP:AMSTep:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: PULSe:MOP:AMSTep:SELect \n
		Snippet: driver.pulse.mop.amStep.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'PULSe:MOP:AMSTep:SELect {param}')

	def clone(self) -> 'AmStep':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AmStep(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
