from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Cph:
	"""Cph commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cph", core, parent)

	def get_chip_count(self) -> float:
		"""SCPI: IMPort:PDW:DATA:CPH:CHIPcount \n
		Snippet: value: float = driver.importPy.pdw.data.cph.get_chip_count() \n
		Queries the pulse parameter. \n
			:return: chip_count: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:CPH:CHIPcount?')
		return Conversions.str_to_float(response)

	def get_values(self) -> str:
		"""SCPI: IMPort:PDW:DATA:CPH:VALues \n
		Snippet: value: str = driver.importPy.pdw.data.cph.get_values() \n
		Queries the pulse parameter. \n
			:return: values: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:CPH:VALues?')
		return trim_str_response(response)

	def set_values(self, values: str) -> None:
		"""SCPI: IMPort:PDW:DATA:CPH:VALues \n
		Snippet: driver.importPy.pdw.data.cph.set_values(values = '1') \n
		Queries the pulse parameter. \n
			:param values: No help available
		"""
		param = Conversions.value_to_quoted_str(values)
		self._core.io.write(f'IMPort:PDW:DATA:CPH:VALues {param}')
