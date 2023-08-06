from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Loop:
	"""Loop commands group definition. 6 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("loop", core, parent)

	@property
	def count(self):
		"""count commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_count'):
			from .Count import Count
			self._count = Count(self._core, self._cmd_group)
		return self._count

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.LoopType:
		"""SCPI: SEQuence:ITEM:LOOP:TYPE \n
		Snippet: value: enums.LoopType = driver.sequence.item.loop.get_type_py() \n
		Sets how the loop repetition is defined. \n
			:return: type_py: FIXed| VARiable
		"""
		response = self._core.io.query_str('SEQuence:ITEM:LOOP:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.LoopType)

	def set_type_py(self, type_py: enums.LoopType) -> None:
		"""SCPI: SEQuence:ITEM:LOOP:TYPE \n
		Snippet: driver.sequence.item.loop.set_type_py(type_py = enums.LoopType.FIXed) \n
		Sets how the loop repetition is defined. \n
			:param type_py: FIXed| VARiable
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.LoopType)
		self._core.io.write(f'SEQuence:ITEM:LOOP:TYPE {param}')

	def get_variable(self) -> str:
		"""SCPI: SEQuence:ITEM:LOOP:VARiable \n
		Snippet: value: str = driver.sequence.item.loop.get_variable() \n
		Sets a loop variable. \n
			:return: variable: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:LOOP:VARiable?')
		return trim_str_response(response)

	def set_variable(self, variable: str) -> None:
		"""SCPI: SEQuence:ITEM:LOOP:VARiable \n
		Snippet: driver.sequence.item.loop.set_variable(variable = '1') \n
		Sets a loop variable. \n
			:param variable: string
		"""
		param = Conversions.value_to_quoted_str(variable)
		self._core.io.write(f'SEQuence:ITEM:LOOP:VARiable {param}')

	def clone(self) -> 'Loop':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Loop(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
