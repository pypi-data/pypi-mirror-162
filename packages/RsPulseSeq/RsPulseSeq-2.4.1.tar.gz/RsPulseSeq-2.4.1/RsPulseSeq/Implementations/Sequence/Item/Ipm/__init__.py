from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Ipm:
	"""Ipm commands group definition. 14 total commands, 4 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ipm", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	@property
	def random(self):
		"""random commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_random'):
			from .Random import Random
			self._random = Random(self._core, self._cmd_group)
		return self._random

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_source'):
			from .Source import Source
			self._source = Source(self._core, self._cmd_group)
		return self._source

	@property
	def target(self):
		"""target commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_target'):
			from .Target import Target
			self._target = Target(self._core, self._cmd_group)
		return self._target

	def get_count(self) -> float:
		"""SCPI: SEQuence:ITEM:IPM:COUNt \n
		Snippet: value: float = driver.sequence.item.ipm.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: SEQuence:ITEM:IPM:DELete \n
		Snippet: driver.sequence.item.ipm.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SEQuence:ITEM:IPM:DELete {param}')

	def get_equation(self) -> str:
		"""SCPI: SEQuence:ITEM:IPM:EQUation \n
		Snippet: value: str = driver.sequence.item.ipm.get_equation() \n
		Defines output value of the IPM mathematically. \n
			:return: equation: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:EQUation?')
		return trim_str_response(response)

	def set_equation(self, equation: str) -> None:
		"""SCPI: SEQuence:ITEM:IPM:EQUation \n
		Snippet: driver.sequence.item.ipm.set_equation(equation = '1') \n
		Defines output value of the IPM mathematically. \n
			:param equation: string
		"""
		param = Conversions.value_to_quoted_str(equation)
		self._core.io.write(f'SEQuence:ITEM:IPM:EQUation {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.IpmMode:
		"""SCPI: SEQuence:ITEM:IPM:MODE \n
		Snippet: value: enums.IpmMode = driver.sequence.item.ipm.get_mode() \n
		Defines the way the variations are applied on repeating pulses. \n
			:return: mode: INDividual| SAME
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.IpmMode)

	def set_mode(self, mode: enums.IpmMode) -> None:
		"""SCPI: SEQuence:ITEM:IPM:MODE \n
		Snippet: driver.sequence.item.ipm.set_mode(mode = enums.IpmMode.INDividual) \n
		Defines the way the variations are applied on repeating pulses. \n
			:param mode: INDividual| SAME
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.IpmMode)
		self._core.io.write(f'SEQuence:ITEM:IPM:MODE {param}')

	def get_restart(self) -> bool:
		"""SCPI: SEQuence:ITEM:IPM:RESTart \n
		Snippet: value: bool = driver.sequence.item.ipm.get_restart() \n
		Restarts the IPM for this sequence line item. \n
			:return: restart: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:RESTart?')
		return Conversions.str_to_bool(response)

	def set_restart(self, restart: bool) -> None:
		"""SCPI: SEQuence:ITEM:IPM:RESTart \n
		Snippet: driver.sequence.item.ipm.set_restart(restart = False) \n
		Restarts the IPM for this sequence line item. \n
			:param restart: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(restart)
		self._core.io.write(f'SEQuence:ITEM:IPM:RESTart {param}')

	def get_select(self) -> float:
		"""SCPI: SEQuence:ITEM:IPM:SELect \n
		Snippet: value: float = driver.sequence.item.ipm.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SEQuence:ITEM:IPM:SELect \n
		Snippet: driver.sequence.item.ipm.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SEQuence:ITEM:IPM:SELect {param}')

	def clone(self) -> 'Ipm':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Ipm(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
