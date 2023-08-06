from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Fm:
	"""Fm commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fm", core, parent)

	def get_deviation(self) -> float:
		"""SCPI: IMPort:PDW:DATA:FM:DEViation \n
		Snippet: value: float = driver.importPy.pdw.data.fm.get_deviation() \n
		Queries the pulse parameter. \n
			:return: deviation: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:FM:DEViation?')
		return Conversions.str_to_float(response)

	def get_mod_freq(self) -> float:
		"""SCPI: IMPort:PDW:DATA:FM:MODFreq \n
		Snippet: value: float = driver.importPy.pdw.data.fm.get_mod_freq() \n
		Queries the pulse parameter. \n
			:return: mod_freq: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:FM:MODFreq?')
		return Conversions.str_to_float(response)
