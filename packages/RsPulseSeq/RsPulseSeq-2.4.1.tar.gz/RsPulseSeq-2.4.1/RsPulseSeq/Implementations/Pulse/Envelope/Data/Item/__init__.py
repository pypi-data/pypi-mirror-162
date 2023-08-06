from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Item:
	"""Item commands group definition. 5 total commands, 1 Subgroups, 4 group commands"""

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
		"""SCPI: PULSe:ENVelope:DATA:ITEM:COUNt \n
		Snippet: value: float = driver.pulse.envelope.data.item.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('PULSe:ENVelope:DATA:ITEM:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: PULSe:ENVelope:DATA:ITEM:DELete \n
		Snippet: driver.pulse.envelope.data.item.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'PULSe:ENVelope:DATA:ITEM:DELete {param}')

	def get_select(self) -> float:
		"""SCPI: PULSe:ENVelope:DATA:ITEM:SELect \n
		Snippet: value: float = driver.pulse.envelope.data.item.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('PULSe:ENVelope:DATA:ITEM:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: PULSe:ENVelope:DATA:ITEM:SELect \n
		Snippet: driver.pulse.envelope.data.item.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'PULSe:ENVelope:DATA:ITEM:SELect {param}')

	def get_value(self) -> float:
		"""SCPI: PULSe:ENVelope:DATA:ITEM:VALue \n
		Snippet: value: float = driver.pulse.envelope.data.item.get_value() \n
		Sets the value of the selected item. \n
			:return: value: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:ENVelope:DATA:ITEM:VALue?')
		return Conversions.str_to_float(response)

	def set_value(self, value: float) -> None:
		"""SCPI: PULSe:ENVelope:DATA:ITEM:VALue \n
		Snippet: driver.pulse.envelope.data.item.set_value(value = 1.0) \n
		Sets the value of the selected item. \n
			:param value: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(value)
		self._core.io.write(f'PULSe:ENVelope:DATA:ITEM:VALue {param}')

	def clone(self) -> 'Item':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Item(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
