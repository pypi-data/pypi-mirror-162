from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Ripple:
	"""Ripple commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ripple", core, parent)

	def get_frequency(self) -> float:
		"""SCPI: PULSe:RIPPle:FREQuency \n
		Snippet: value: float = driver.pulse.ripple.get_frequency() \n
		Sets the ripple frequency. \n
			:return: frequency: float Range: 0 to 3e+08, Unit: Hz
		"""
		response = self._core.io.query_str('PULSe:RIPPle:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: PULSe:RIPPle:FREQuency \n
		Snippet: driver.pulse.ripple.set_frequency(frequency = 1.0) \n
		Sets the ripple frequency. \n
			:param frequency: float Range: 0 to 3e+08, Unit: Hz
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'PULSe:RIPPle:FREQuency {param}')

	def get_value(self) -> float:
		"""SCPI: PULSe:RIPPle \n
		Snippet: value: float = driver.pulse.ripple.get_value() \n
		Sets the ripple level. \n
			:return: ripple: float Range: 0 to 50
		"""
		response = self._core.io.query_str('PULSe:RIPPle?')
		return Conversions.str_to_float(response)

	def set_value(self, ripple: float) -> None:
		"""SCPI: PULSe:RIPPle \n
		Snippet: driver.pulse.ripple.set_value(ripple = 1.0) \n
		Sets the ripple level. \n
			:param ripple: float Range: 0 to 50
		"""
		param = Conversions.decimal_value_to_str(ripple)
		self._core.io.write(f'PULSe:RIPPle {param}')
