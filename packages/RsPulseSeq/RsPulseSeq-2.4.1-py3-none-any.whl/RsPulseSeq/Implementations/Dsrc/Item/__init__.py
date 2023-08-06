from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Item:
	"""Item commands group definition. 10 total commands, 2 Subgroups, 6 group commands"""

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

	@property
	def prbs(self):
		"""prbs commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_prbs'):
			from .Prbs import Prbs
			self._prbs = Prbs(self._core, self._cmd_group)
		return self._prbs

	def get_bits(self) -> float:
		"""SCPI: DSRC:ITEM:BITS \n
		Snippet: value: float = driver.dsrc.item.get_bits() \n
		Sets the length of the selected item in bits. \n
			:return: bits: float Range: 0 to 4096
		"""
		response = self._core.io.query_str('DSRC:ITEM:BITS?')
		return Conversions.str_to_float(response)

	def set_bits(self, bits: float) -> None:
		"""SCPI: DSRC:ITEM:BITS \n
		Snippet: driver.dsrc.item.set_bits(bits = 1.0) \n
		Sets the length of the selected item in bits. \n
			:param bits: float Range: 0 to 4096
		"""
		param = Conversions.decimal_value_to_str(bits)
		self._core.io.write(f'DSRC:ITEM:BITS {param}')

	def get_data(self) -> str:
		"""SCPI: DSRC:ITEM:DATA \n
		Snippet: value: str = driver.dsrc.item.get_data() \n
		Sets the user defined data pattern. \n
			:return: data: string
		"""
		response = self._core.io.query_str('DSRC:ITEM:DATA?')
		return trim_str_response(response)

	def set_data(self, data: str) -> None:
		"""SCPI: DSRC:ITEM:DATA \n
		Snippet: driver.dsrc.item.set_data(data = '1') \n
		Sets the user defined data pattern. \n
			:param data: string
		"""
		param = Conversions.value_to_quoted_str(data)
		self._core.io.write(f'DSRC:ITEM:DATA {param}')

	def delete(self, delete: float) -> None:
		"""SCPI: DSRC:ITEM:DELete \n
		Snippet: driver.dsrc.item.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'DSRC:ITEM:DELete {param}')

	# noinspection PyTypeChecker
	def get_pattern(self) -> enums.ItemPattern:
		"""SCPI: DSRC:ITEM:PATTern \n
		Snippet: value: enums.ItemPattern = driver.dsrc.item.get_pattern() \n
		Sets the data pattern of the selected item. \n
			:return: pattern: ZERO| ONE| ALT| R2A| R2B| R3| R4A| R4B| R5| R7| R11| R13 ZERO|ONE Binary 0 and 1 ALT Variable bit strings ('1010') with alternating 0 and 1 and a maximum length of 999 bits R2A|R2B|R3|R4A|R4B|R5|R7|R11|R13 Barker codes
		"""
		response = self._core.io.query_str('DSRC:ITEM:PATTern?')
		return Conversions.str_to_scalar_enum(response, enums.ItemPattern)

	def set_pattern(self, pattern: enums.ItemPattern) -> None:
		"""SCPI: DSRC:ITEM:PATTern \n
		Snippet: driver.dsrc.item.set_pattern(pattern = enums.ItemPattern.ALT) \n
		Sets the data pattern of the selected item. \n
			:param pattern: ZERO| ONE| ALT| R2A| R2B| R3| R4A| R4B| R5| R7| R11| R13 ZERO|ONE Binary 0 and 1 ALT Variable bit strings ('1010') with alternating 0 and 1 and a maximum length of 999 bits R2A|R2B|R3|R4A|R4B|R5|R7|R11|R13 Barker codes
		"""
		param = Conversions.enum_scalar_to_str(pattern, enums.ItemPattern)
		self._core.io.write(f'DSRC:ITEM:PATTern {param}')

	def get_select(self) -> float:
		"""SCPI: DSRC:ITEM:SELect \n
		Snippet: value: float = driver.dsrc.item.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('DSRC:ITEM:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: DSRC:ITEM:SELect \n
		Snippet: driver.dsrc.item.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'DSRC:ITEM:SELect {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.ItemTypeB:
		"""SCPI: DSRC:ITEM:TYPE \n
		Snippet: value: enums.ItemTypeB = driver.dsrc.item.get_type_py() \n
		Sets the data type of selected item. \n
			:return: type_py: PATTern| PRBS| USER
		"""
		response = self._core.io.query_str('DSRC:ITEM:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ItemTypeB)

	def set_type_py(self, type_py: enums.ItemTypeB) -> None:
		"""SCPI: DSRC:ITEM:TYPE \n
		Snippet: driver.dsrc.item.set_type_py(type_py = enums.ItemTypeB.PATTern) \n
		Sets the data type of selected item. \n
			:param type_py: PATTern| PRBS| USER
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.ItemTypeB)
		self._core.io.write(f'DSRC:ITEM:TYPE {param}')

	def clone(self) -> 'Item':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Item(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
