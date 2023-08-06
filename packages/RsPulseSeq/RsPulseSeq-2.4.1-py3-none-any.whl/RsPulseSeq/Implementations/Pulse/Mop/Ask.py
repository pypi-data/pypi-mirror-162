from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Ask:
	"""Ask commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ask", core, parent)

	def get_invert(self) -> bool:
		"""SCPI: PULSe:MOP:ASK:INVert \n
		Snippet: value: bool = driver.pulse.mop.ask.get_invert() \n
		Inverts the modulation. \n
			:return: invert: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PULSe:MOP:ASK:INVert?')
		return Conversions.str_to_bool(response)

	def set_invert(self, invert: bool) -> None:
		"""SCPI: PULSe:MOP:ASK:INVert \n
		Snippet: driver.pulse.mop.ask.set_invert(invert = False) \n
		Inverts the modulation. \n
			:param invert: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(invert)
		self._core.io.write(f'PULSe:MOP:ASK:INVert {param}')

	def get_mdepth(self) -> float:
		"""SCPI: PULSe:MOP:ASK:MDEPth \n
		Snippet: value: float = driver.pulse.mop.ask.get_mdepth() \n
		Sets the modulation depth. \n
			:return: mdepth: float Range: 0 to 100, Unit: percent
		"""
		response = self._core.io.query_str('PULSe:MOP:ASK:MDEPth?')
		return Conversions.str_to_float(response)

	def set_mdepth(self, mdepth: float) -> None:
		"""SCPI: PULSe:MOP:ASK:MDEPth \n
		Snippet: driver.pulse.mop.ask.set_mdepth(mdepth = 1.0) \n
		Sets the modulation depth. \n
			:param mdepth: float Range: 0 to 100, Unit: percent
		"""
		param = Conversions.decimal_value_to_str(mdepth)
		self._core.io.write(f'PULSe:MOP:ASK:MDEPth {param}')

	def get_symbol_rate(self) -> float:
		"""SCPI: PULSe:MOP:ASK:SRATe \n
		Snippet: value: float = driver.pulse.mop.ask.get_symbol_rate() \n
		Sets the symbol rate. \n
			:return: srate: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:ASK:SRATe?')
		return Conversions.str_to_float(response)

	def set_symbol_rate(self, srate: float) -> None:
		"""SCPI: PULSe:MOP:ASK:SRATe \n
		Snippet: driver.pulse.mop.ask.set_symbol_rate(srate = 1.0) \n
		Sets the symbol rate. \n
			:param srate: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(srate)
		self._core.io.write(f'PULSe:MOP:ASK:SRATe {param}')
