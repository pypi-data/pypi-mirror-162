from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Noise:
	"""Noise commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("noise", core, parent)

	def get_bandwidth(self) -> float:
		"""SCPI: PULSe:MOP:NOISe:BWIDth \n
		Snippet: value: float = driver.pulse.mop.noise.get_bandwidth() \n
		Sets the bandwidth. \n
			:return: bwidth: float Range: 1 to 1e+09, Unit: Hz
		"""
		response = self._core.io.query_str('PULSe:MOP:NOISe:BWIDth?')
		return Conversions.str_to_float(response)

	def set_bandwidth(self, bwidth: float) -> None:
		"""SCPI: PULSe:MOP:NOISe:BWIDth \n
		Snippet: driver.pulse.mop.noise.set_bandwidth(bwidth = 1.0) \n
		Sets the bandwidth. \n
			:param bwidth: float Range: 1 to 1e+09, Unit: Hz
		"""
		param = Conversions.decimal_value_to_str(bwidth)
		self._core.io.write(f'PULSe:MOP:NOISe:BWIDth {param}')
