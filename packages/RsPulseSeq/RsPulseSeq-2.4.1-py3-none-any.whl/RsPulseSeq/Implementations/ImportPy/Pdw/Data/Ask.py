from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Ask:
	"""Ask commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ask", core, parent)

	def get_chip_count(self) -> float:
		"""SCPI: IMPort:PDW:DATA:ASK:CHIPcount \n
		Snippet: value: float = driver.importPy.pdw.data.ask.get_chip_count() \n
		Queries the pulse parameter. \n
			:return: chip_count: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:ASK:CHIPcount?')
		return Conversions.str_to_float(response)

	def get_pattern(self) -> str:
		"""SCPI: IMPort:PDW:DATA:ASK:PATTern \n
		Snippet: value: str = driver.importPy.pdw.data.ask.get_pattern() \n
		Queries the pulse parameter. \n
			:return: pattern: string
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:ASK:PATTern?')
		return trim_str_response(response)

	def get_rate(self) -> float:
		"""SCPI: IMPort:PDW:DATA:ASK:RATE \n
		Snippet: value: float = driver.importPy.pdw.data.ask.get_rate() \n
		Queries the pulse parameter. \n
			:return: rate: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:ASK:RATE?')
		return Conversions.str_to_float(response)

	def get_states(self) -> float:
		"""SCPI: IMPort:PDW:DATA:ASK:STATes \n
		Snippet: value: float = driver.importPy.pdw.data.ask.get_states() \n
		Queries the pulse parameter. \n
			:return: states: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:ASK:STATes?')
		return Conversions.str_to_float(response)

	def get_step(self) -> float:
		"""SCPI: IMPort:PDW:DATA:ASK:STEP \n
		Snippet: value: float = driver.importPy.pdw.data.ask.get_step() \n
		Queries the pulse parameter. \n
			:return: step: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:ASK:STEP?')
		return Conversions.str_to_float(response)
