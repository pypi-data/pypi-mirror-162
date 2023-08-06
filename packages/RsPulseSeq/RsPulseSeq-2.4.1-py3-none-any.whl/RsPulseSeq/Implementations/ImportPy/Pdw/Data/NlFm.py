from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NlFm:
	"""NlFm commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("nlFm", core, parent)

	def get_cubic(self) -> float:
		"""SCPI: IMPort:PDW:DATA:NLFM:CUBic \n
		Snippet: value: float = driver.importPy.pdw.data.nlFm.get_cubic() \n
		Queries the pulse parameter. \n
			:return: cubic: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:NLFM:CUBic?')
		return Conversions.str_to_float(response)

	def get_linear(self) -> float:
		"""SCPI: IMPort:PDW:DATA:NLFM:LINear \n
		Snippet: value: float = driver.importPy.pdw.data.nlFm.get_linear() \n
		Queries the pulse parameter. \n
			:return: linear: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:NLFM:LINear?')
		return Conversions.str_to_float(response)

	def get_quadratic(self) -> float:
		"""SCPI: IMPort:PDW:DATA:NLFM:QUADratic \n
		Snippet: value: float = driver.importPy.pdw.data.nlFm.get_quadratic() \n
		Queries the pulse parameter. \n
			:return: quadratic: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:NLFM:QUADratic?')
		return Conversions.str_to_float(response)
