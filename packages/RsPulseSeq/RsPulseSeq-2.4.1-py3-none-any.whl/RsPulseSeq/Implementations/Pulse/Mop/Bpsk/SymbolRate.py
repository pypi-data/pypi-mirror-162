from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SymbolRate:
	"""SymbolRate commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("symbolRate", core, parent)

	def get_auto(self) -> bool:
		"""SCPI: PULSe:MOP:BPSK:SRATe:AUTO \n
		Snippet: value: bool = driver.pulse.mop.bpsk.symbolRate.get_auto() \n
		Enables automatic adjusting of the bits in the pulse width. \n
			:return: auto: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PULSe:MOP:BPSK:SRATe:AUTO?')
		return Conversions.str_to_bool(response)

	def set_auto(self, auto: bool) -> None:
		"""SCPI: PULSe:MOP:BPSK:SRATe:AUTO \n
		Snippet: driver.pulse.mop.bpsk.symbolRate.set_auto(auto = False) \n
		Enables automatic adjusting of the bits in the pulse width. \n
			:param auto: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(auto)
		self._core.io.write(f'PULSe:MOP:BPSK:SRATe:AUTO {param}')

	def get_value(self) -> float:
		"""SCPI: PULSe:MOP:BPSK:SRATe \n
		Snippet: value: float = driver.pulse.mop.bpsk.symbolRate.get_value() \n
		Sets the symbol rate. \n
			:return: srate: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:BPSK:SRATe?')
		return Conversions.str_to_float(response)

	def set_value(self, srate: float) -> None:
		"""SCPI: PULSe:MOP:BPSK:SRATe \n
		Snippet: driver.pulse.mop.bpsk.symbolRate.set_value(srate = 1.0) \n
		Sets the symbol rate. \n
			:param srate: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(srate)
		self._core.io.write(f'PULSe:MOP:BPSK:SRATe {param}')
