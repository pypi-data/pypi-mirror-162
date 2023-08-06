from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Lfm:
	"""Lfm commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lfm", core, parent)

	def get_rate(self) -> float:
		"""SCPI: IMPort:PDW:DATA:LFM:RATE \n
		Snippet: value: float = driver.importPy.pdw.data.lfm.get_rate() \n
		Queries the pulse parameter. \n
			:return: rate: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:LFM:RATE?')
		return Conversions.str_to_float(response)
