from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Am:
	"""Am commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("am", core, parent)

	def get_depth(self) -> float:
		"""SCPI: IMPort:PDW:DATA:AM:DEPTh \n
		Snippet: value: float = driver.importPy.pdw.data.am.get_depth() \n
		Queries the pulse parameter. \n
			:return: depth: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:AM:DEPTh?')
		return Conversions.str_to_float(response)

	def get_mod_freq(self) -> float:
		"""SCPI: IMPort:PDW:DATA:AM:MODFreq \n
		Snippet: value: float = driver.importPy.pdw.data.am.get_mod_freq() \n
		Queries the pulse parameter. \n
			:return: mod_freq: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:AM:MODFreq?')
		return Conversions.str_to_float(response)
