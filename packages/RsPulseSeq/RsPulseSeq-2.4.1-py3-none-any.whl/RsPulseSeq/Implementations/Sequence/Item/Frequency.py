from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Frequency:
	"""Frequency commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	def get_offset(self) -> float:
		"""SCPI: SEQuence:ITEM:FREQuency:OFFSet \n
		Snippet: value: float = driver.sequence.item.frequency.get_offset() \n
		Enables a frequency offset. \n
			:return: offset: float Range: -1e+09 to 1e+09, Unit: Hz
		"""
		response = self._core.io.query_str('SEQuence:ITEM:FREQuency:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, offset: float) -> None:
		"""SCPI: SEQuence:ITEM:FREQuency:OFFSet \n
		Snippet: driver.sequence.item.frequency.set_offset(offset = 1.0) \n
		Enables a frequency offset. \n
			:param offset: float Range: -1e+09 to 1e+09, Unit: Hz
		"""
		param = Conversions.decimal_value_to_str(offset)
		self._core.io.write(f'SEQuence:ITEM:FREQuency:OFFSet {param}')
