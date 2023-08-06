from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Ovl:
	"""Ovl commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ovl", core, parent)

	def get_variable(self) -> str:
		"""SCPI: SEQuence:ITEM:OVL:VARiable \n
		Snippet: value: str = driver.sequence.item.ovl.get_variable() \n
		Sets a variable. \n
			:return: variable: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:OVL:VARiable?')
		return trim_str_response(response)

	def set_variable(self, variable: str) -> None:
		"""SCPI: SEQuence:ITEM:OVL:VARiable \n
		Snippet: driver.sequence.item.ovl.set_variable(variable = '1') \n
		Sets a variable. \n
			:param variable: string
		"""
		param = Conversions.value_to_quoted_str(variable)
		self._core.io.write(f'SEQuence:ITEM:OVL:VARiable {param}')

	def get_wtime(self) -> float:
		"""SCPI: SEQuence:ITEM:OVL:WTIMe \n
		Snippet: value: float = driver.sequence.item.ovl.get_wtime() \n
		Sets the duration of the overlay. \n
			:return: wtime: float Range: 0 to 3600, Unit: sec
		"""
		response = self._core.io.query_str('SEQuence:ITEM:OVL:WTIMe?')
		return Conversions.str_to_float(response)

	def set_wtime(self, wtime: float) -> None:
		"""SCPI: SEQuence:ITEM:OVL:WTIMe \n
		Snippet: driver.sequence.item.ovl.set_wtime(wtime = 1.0) \n
		Sets the duration of the overlay. \n
			:param wtime: float Range: 0 to 3600, Unit: sec
		"""
		param = Conversions.decimal_value_to_str(wtime)
		self._core.io.write(f'SEQuence:ITEM:OVL:WTIMe {param}')
