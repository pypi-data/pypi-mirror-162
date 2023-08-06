from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Item:
	"""Item commands group definition. 7 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("item", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	def get_count(self) -> float:
		"""SCPI: IPM:LIST:ITEM:COUNt \n
		Snippet: value: float = driver.ipm.listPy.item.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('IPM:LIST:ITEM:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: IPM:LIST:ITEM:DELete \n
		Snippet: driver.ipm.listPy.item.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'IPM:LIST:ITEM:DELete {param}')

	def get_repetition(self) -> float:
		"""SCPI: IPM:LIST:ITEM:REPetition \n
		Snippet: value: float = driver.ipm.listPy.item.get_repetition() \n
		Sets the number of times a list item is repeated. \n
			:return: repetition: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('IPM:LIST:ITEM:REPetition?')
		return Conversions.str_to_float(response)

	def set_repetition(self, repetition: float) -> None:
		"""SCPI: IPM:LIST:ITEM:REPetition \n
		Snippet: driver.ipm.listPy.item.set_repetition(repetition = 1.0) \n
		Sets the number of times a list item is repeated. \n
			:param repetition: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(repetition)
		self._core.io.write(f'IPM:LIST:ITEM:REPetition {param}')

	def get_select(self) -> float:
		"""SCPI: IPM:LIST:ITEM:SELect \n
		Snippet: value: float = driver.ipm.listPy.item.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('IPM:LIST:ITEM:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: IPM:LIST:ITEM:SELect \n
		Snippet: driver.ipm.listPy.item.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'IPM:LIST:ITEM:SELect {param}')

	def get_time(self) -> float:
		"""SCPI: IPM:LIST:ITEM:TIME \n
		Snippet: value: float = driver.ipm.listPy.item.get_time() \n
		Sets how long a list item is repeated. \n
			:return: time: float Range: 0 to 1e+09
		"""
		response = self._core.io.query_str('IPM:LIST:ITEM:TIME?')
		return Conversions.str_to_float(response)

	def set_time(self, time: float) -> None:
		"""SCPI: IPM:LIST:ITEM:TIME \n
		Snippet: driver.ipm.listPy.item.set_time(time = 1.0) \n
		Sets how long a list item is repeated. \n
			:param time: float Range: 0 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(time)
		self._core.io.write(f'IPM:LIST:ITEM:TIME {param}')

	def get_value(self) -> float:
		"""SCPI: IPM:LIST:ITEM:VALue \n
		Snippet: value: float = driver.ipm.listPy.item.get_value() \n
		Sets the value of the selected list item. \n
			:return: value: float Range: -1e+11 to 1e+11
		"""
		response = self._core.io.query_str('IPM:LIST:ITEM:VALue?')
		return Conversions.str_to_float(response)

	def set_value(self, value: float) -> None:
		"""SCPI: IPM:LIST:ITEM:VALue \n
		Snippet: driver.ipm.listPy.item.set_value(value = 1.0) \n
		Sets the value of the selected list item. \n
			:param value: float Range: -1e+11 to 1e+11
		"""
		param = Conversions.decimal_value_to_str(value)
		self._core.io.write(f'IPM:LIST:ITEM:VALue {param}')

	def clone(self) -> 'Item':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Item(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
