from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Msk:
	"""Msk commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("msk", core, parent)

	def get_invert(self) -> bool:
		"""SCPI: PULSe:MOP:MSK:INVert \n
		Snippet: value: bool = driver.pulse.mop.msk.get_invert() \n
		Inverts the modulation. \n
			:return: invert: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PULSe:MOP:MSK:INVert?')
		return Conversions.str_to_bool(response)

	def set_invert(self, invert: bool) -> None:
		"""SCPI: PULSe:MOP:MSK:INVert \n
		Snippet: driver.pulse.mop.msk.set_invert(invert = False) \n
		Inverts the modulation. \n
			:param invert: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(invert)
		self._core.io.write(f'PULSe:MOP:MSK:INVert {param}')

	def get_symbol_rate(self) -> float:
		"""SCPI: PULSe:MOP:MSK:SRATe \n
		Snippet: value: float = driver.pulse.mop.msk.get_symbol_rate() \n
		Sets the symbol rate. \n
			:return: srate: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:MSK:SRATe?')
		return Conversions.str_to_float(response)

	def set_symbol_rate(self, srate: float) -> None:
		"""SCPI: PULSe:MOP:MSK:SRATe \n
		Snippet: driver.pulse.mop.msk.set_symbol_rate(srate = 1.0) \n
		Sets the symbol rate. \n
			:param srate: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(srate)
		self._core.io.write(f'PULSe:MOP:MSK:SRATe {param}')
