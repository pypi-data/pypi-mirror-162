from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Xpol:
	"""Xpol commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("xpol", core, parent)

	def get_attenuation(self) -> float:
		"""SCPI: REPository:XPOL:ATTenuation \n
		Snippet: value: float = driver.repository.xpol.get_attenuation() \n
		Sets the attenuation used to calculate the cross-polarized antenna patterns. \n
			:return: attenuation: float
		"""
		response = self._core.io.query_str('REPository:XPOL:ATTenuation?')
		return Conversions.str_to_float(response)

	def set_attenuation(self, attenuation: float) -> None:
		"""SCPI: REPository:XPOL:ATTenuation \n
		Snippet: driver.repository.xpol.set_attenuation(attenuation = 1.0) \n
		Sets the attenuation used to calculate the cross-polarized antenna patterns. \n
			:param attenuation: float
		"""
		param = Conversions.decimal_value_to_str(attenuation)
		self._core.io.write(f'REPository:XPOL:ATTenuation {param}')
