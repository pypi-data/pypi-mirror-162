from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Marker:
	"""Marker commands group definition. 7 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("marker", core, parent)

	@property
	def condition(self):
		"""condition commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_condition'):
			from .Condition import Condition
			self._condition = Condition(self._core, self._cmd_group)
		return self._condition

	def get_all(self) -> float:
		"""SCPI: SEQuence:ITEM:MARKer:ALL \n
		Snippet: value: float = driver.sequence.item.marker.get_all() \n
		Enables up to four markers of the corresponding type. \n
			:return: all_py: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		response = self._core.io.query_str('SEQuence:ITEM:MARKer:ALL?')
		return Conversions.str_to_float(response)

	def set_all(self, all_py: float) -> None:
		"""SCPI: SEQuence:ITEM:MARKer:ALL \n
		Snippet: driver.sequence.item.marker.set_all(all_py = 1.0) \n
		Enables up to four markers of the corresponding type. \n
			:param all_py: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(all_py)
		self._core.io.write(f'SEQuence:ITEM:MARKer:ALL {param}')

	def get_first(self) -> float:
		"""SCPI: SEQuence:ITEM:MARKer:FIRSt \n
		Snippet: value: float = driver.sequence.item.marker.get_first() \n
		Enables up to four markers of the corresponding type. \n
			:return: first: No help available
		"""
		response = self._core.io.query_str('SEQuence:ITEM:MARKer:FIRSt?')
		return Conversions.str_to_float(response)

	def set_first(self, first: float) -> None:
		"""SCPI: SEQuence:ITEM:MARKer:FIRSt \n
		Snippet: driver.sequence.item.marker.set_first(first = 1.0) \n
		Enables up to four markers of the corresponding type. \n
			:param first: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(first)
		self._core.io.write(f'SEQuence:ITEM:MARKer:FIRSt {param}')

	def get_last(self) -> float:
		"""SCPI: SEQuence:ITEM:MARKer:LAST \n
		Snippet: value: float = driver.sequence.item.marker.get_last() \n
		Enables up to four markers of the corresponding type. \n
			:return: last: No help available
		"""
		response = self._core.io.query_str('SEQuence:ITEM:MARKer:LAST?')
		return Conversions.str_to_float(response)

	def set_last(self, last: float) -> None:
		"""SCPI: SEQuence:ITEM:MARKer:LAST \n
		Snippet: driver.sequence.item.marker.set_last(last = 1.0) \n
		Enables up to four markers of the corresponding type. \n
			:param last: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(last)
		self._core.io.write(f'SEQuence:ITEM:MARKer:LAST {param}')

	def clone(self) -> 'Marker':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Marker(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
