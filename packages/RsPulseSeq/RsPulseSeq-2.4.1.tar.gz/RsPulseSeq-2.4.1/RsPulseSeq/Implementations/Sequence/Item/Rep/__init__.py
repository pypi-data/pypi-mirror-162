from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Rep:
	"""Rep commands group definition. 7 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rep", core, parent)

	@property
	def count(self):
		"""count commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_count'):
			from .Count import Count
			self._count = Count(self._core, self._cmd_group)
		return self._count

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.RepetitionType:
		"""SCPI: SEQuence:ITEM:REP:TYPE \n
		Snippet: value: enums.RepetitionType = driver.sequence.item.rep.get_type_py() \n
		Sets how the repetition number is defined. \n
			:return: type_py: FIXed| VARiable| DURation
		"""
		response = self._core.io.query_str('SEQuence:ITEM:REP:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.RepetitionType)

	def set_type_py(self, type_py: enums.RepetitionType) -> None:
		"""SCPI: SEQuence:ITEM:REP:TYPE \n
		Snippet: driver.sequence.item.rep.set_type_py(type_py = enums.RepetitionType.DURation) \n
		Sets how the repetition number is defined. \n
			:param type_py: FIXed| VARiable| DURation
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.RepetitionType)
		self._core.io.write(f'SEQuence:ITEM:REP:TYPE {param}')

	def get_variable(self) -> str:
		"""SCPI: SEQuence:ITEM:REP:VARiable \n
		Snippet: value: str = driver.sequence.item.rep.get_variable() \n
		Seta a repetition variable. \n
			:return: variable: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:REP:VARiable?')
		return trim_str_response(response)

	def set_variable(self, variable: str) -> None:
		"""SCPI: SEQuence:ITEM:REP:VARiable \n
		Snippet: driver.sequence.item.rep.set_variable(variable = '1') \n
		Seta a repetition variable. \n
			:param variable: string
		"""
		param = Conversions.value_to_quoted_str(variable)
		self._core.io.write(f'SEQuence:ITEM:REP:VARiable {param}')

	def clone(self) -> 'Rep':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Rep(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
