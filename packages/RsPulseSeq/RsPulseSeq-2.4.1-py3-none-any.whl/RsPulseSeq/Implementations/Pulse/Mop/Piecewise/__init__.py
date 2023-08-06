from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Piecewise:
	"""Piecewise commands group definition. 9 total commands, 1 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("piecewise", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def clear(self) -> None:
		"""SCPI: PULSe:MOP:PIECewise:CLEar \n
		Snippet: driver.pulse.mop.piecewise.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'PULSe:MOP:PIECewise:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PULSe:MOP:PIECewise:CLEar \n
		Snippet: driver.pulse.mop.piecewise.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PULSe:MOP:PIECewise:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: PULSe:MOP:PIECewise:COUNt \n
		Snippet: value: float = driver.pulse.mop.piecewise.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('PULSe:MOP:PIECewise:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: PULSe:MOP:PIECewise:DELete \n
		Snippet: driver.pulse.mop.piecewise.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'PULSe:MOP:PIECewise:DELete {param}')

	def get_duration(self) -> float:
		"""SCPI: PULSe:MOP:PIECewise:DURation \n
		Snippet: value: float = driver.pulse.mop.piecewise.get_duration() \n
		Set the length of the chirp interval as a percentage of the duration the MOP is applied on. \n
			:return: duration: float Range: 0 to 100
		"""
		response = self._core.io.query_str('PULSe:MOP:PIECewise:DURation?')
		return Conversions.str_to_float(response)

	def set_duration(self, duration: float) -> None:
		"""SCPI: PULSe:MOP:PIECewise:DURation \n
		Snippet: driver.pulse.mop.piecewise.set_duration(duration = 1.0) \n
		Set the length of the chirp interval as a percentage of the duration the MOP is applied on. \n
			:param duration: float Range: 0 to 100
		"""
		param = Conversions.decimal_value_to_str(duration)
		self._core.io.write(f'PULSe:MOP:PIECewise:DURation {param}')

	def set_insert(self, insert: float) -> None:
		"""SCPI: PULSe:MOP:PIECewise:INSert \n
		Snippet: driver.pulse.mop.piecewise.set_insert(insert = 1.0) \n
		Inserts a new item before the selected one. \n
			:param insert: float
		"""
		param = Conversions.decimal_value_to_str(insert)
		self._core.io.write(f'PULSe:MOP:PIECewise:INSert {param}')

	def get_offset(self) -> float:
		"""SCPI: PULSe:MOP:PIECewise:OFFSet \n
		Snippet: value: float = driver.pulse.mop.piecewise.get_offset() \n
		Offsets the start frequency of the chirp. \n
			:return: offset: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:PIECewise:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, offset: float) -> None:
		"""SCPI: PULSe:MOP:PIECewise:OFFSet \n
		Snippet: driver.pulse.mop.piecewise.set_offset(offset = 1.0) \n
		Offsets the start frequency of the chirp. \n
			:param offset: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(offset)
		self._core.io.write(f'PULSe:MOP:PIECewise:OFFSet {param}')

	def get_rate(self) -> float:
		"""SCPI: PULSe:MOP:PIECewise:RATE \n
		Snippet: value: float = driver.pulse.mop.piecewise.get_rate() \n
		Set the chirp rate. \n
			:return: rate: float Range: -1e+15 to 1e+15, Unit: Hz/s
		"""
		response = self._core.io.query_str('PULSe:MOP:PIECewise:RATE?')
		return Conversions.str_to_float(response)

	def set_rate(self, rate: float) -> None:
		"""SCPI: PULSe:MOP:PIECewise:RATE \n
		Snippet: driver.pulse.mop.piecewise.set_rate(rate = 1.0) \n
		Set the chirp rate. \n
			:param rate: float Range: -1e+15 to 1e+15, Unit: Hz/s
		"""
		param = Conversions.decimal_value_to_str(rate)
		self._core.io.write(f'PULSe:MOP:PIECewise:RATE {param}')

	def get_select(self) -> float:
		"""SCPI: PULSe:MOP:PIECewise:SELect \n
		Snippet: value: float = driver.pulse.mop.piecewise.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('PULSe:MOP:PIECewise:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: PULSe:MOP:PIECewise:SELect \n
		Snippet: driver.pulse.mop.piecewise.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'PULSe:MOP:PIECewise:SELect {param}')

	def clone(self) -> 'Piecewise':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Piecewise(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
