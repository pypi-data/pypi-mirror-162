from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Fm:
	"""Fm commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fm", core, parent)

	def get_deviation(self) -> float:
		"""SCPI: PULSe:MOP:FM:DEViation \n
		Snippet: value: float = driver.pulse.mop.fm.get_deviation() \n
		Sets the modulation deviation. \n
			:return: deviation: float Range: 0.1 to 1e+09, Unit: Hz
		"""
		response = self._core.io.query_str('PULSe:MOP:FM:DEViation?')
		return Conversions.str_to_float(response)

	def set_deviation(self, deviation: float) -> None:
		"""SCPI: PULSe:MOP:FM:DEViation \n
		Snippet: driver.pulse.mop.fm.set_deviation(deviation = 1.0) \n
		Sets the modulation deviation. \n
			:param deviation: float Range: 0.1 to 1e+09, Unit: Hz
		"""
		param = Conversions.decimal_value_to_str(deviation)
		self._core.io.write(f'PULSe:MOP:FM:DEViation {param}')

	def get_frequency(self) -> float:
		"""SCPI: PULSe:MOP:FM:FREQuency \n
		Snippet: value: float = driver.pulse.mop.fm.get_frequency() \n
		Sets the modulation frequency. \n
			:return: frequency: float Range: 0.002 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:FM:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: PULSe:MOP:FM:FREQuency \n
		Snippet: driver.pulse.mop.fm.set_frequency(frequency = 1.0) \n
		Sets the modulation frequency. \n
			:param frequency: float Range: 0.002 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'PULSe:MOP:FM:FREQuency {param}')
