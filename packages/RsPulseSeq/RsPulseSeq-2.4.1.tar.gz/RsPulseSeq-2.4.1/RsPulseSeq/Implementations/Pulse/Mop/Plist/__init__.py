from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Plist:
	"""Plist commands group definition. 7 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("plist", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def clear(self) -> None:
		"""SCPI: PULSe:MOP:PLISt:CLEar \n
		Snippet: driver.pulse.mop.plist.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'PULSe:MOP:PLISt:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PULSe:MOP:PLISt:CLEar \n
		Snippet: driver.pulse.mop.plist.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PULSe:MOP:PLISt:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: PULSe:MOP:PLISt:COUNt \n
		Snippet: value: float = driver.pulse.mop.plist.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('PULSe:MOP:PLISt:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: PULSe:MOP:PLISt:DELete \n
		Snippet: driver.pulse.mop.plist.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'PULSe:MOP:PLISt:DELete {param}')

	def set_insert(self, insert: float) -> None:
		"""SCPI: PULSe:MOP:PLISt:INSert \n
		Snippet: driver.pulse.mop.plist.set_insert(insert = 1.0) \n
		Inserts a new item before the selected one. \n
			:param insert: float
		"""
		param = Conversions.decimal_value_to_str(insert)
		self._core.io.write(f'PULSe:MOP:PLISt:INSert {param}')

	def get_select(self) -> float:
		"""SCPI: PULSe:MOP:PLISt:SELect \n
		Snippet: value: float = driver.pulse.mop.plist.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('PULSe:MOP:PLISt:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: PULSe:MOP:PLISt:SELect \n
		Snippet: driver.pulse.mop.plist.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'PULSe:MOP:PLISt:SELect {param}')

	def get_value(self) -> float:
		"""SCPI: PULSe:MOP:PLISt:VALue \n
		Snippet: value: float = driver.pulse.mop.plist.get_value() \n
		Sets the phase. \n
			:return: value: float Range: -180 to 180, Unit: degree
		"""
		response = self._core.io.query_str('PULSe:MOP:PLISt:VALue?')
		return Conversions.str_to_float(response)

	def set_value(self, value: float) -> None:
		"""SCPI: PULSe:MOP:PLISt:VALue \n
		Snippet: driver.pulse.mop.plist.set_value(value = 1.0) \n
		Sets the phase. \n
			:param value: float Range: -180 to 180, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(value)
		self._core.io.write(f'PULSe:MOP:PLISt:VALue {param}')

	def clone(self) -> 'Plist':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Plist(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
