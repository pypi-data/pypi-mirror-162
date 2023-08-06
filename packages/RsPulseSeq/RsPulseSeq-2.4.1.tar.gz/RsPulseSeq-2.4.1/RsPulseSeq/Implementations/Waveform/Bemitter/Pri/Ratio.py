from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Ratio:
	"""Ratio commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ratio", core, parent)

	def get_maximum(self) -> float:
		"""SCPI: WAVeform:BEMitter:PRI:RATio:MAXimum \n
		Snippet: value: float = driver.waveform.bemitter.pri.ratio.get_maximum() \n
		Sets the value range for the PRI/PW ratio. \n
			:return: maximum: float Range: 10 to 1000
		"""
		response = self._core.io.query_str('WAVeform:BEMitter:PRI:RATio:MAXimum?')
		return Conversions.str_to_float(response)

	def set_maximum(self, maximum: float) -> None:
		"""SCPI: WAVeform:BEMitter:PRI:RATio:MAXimum \n
		Snippet: driver.waveform.bemitter.pri.ratio.set_maximum(maximum = 1.0) \n
		Sets the value range for the PRI/PW ratio. \n
			:param maximum: float Range: 10 to 1000
		"""
		param = Conversions.decimal_value_to_str(maximum)
		self._core.io.write(f'WAVeform:BEMitter:PRI:RATio:MAXimum {param}')

	def get_minimum(self) -> float:
		"""SCPI: WAVeform:BEMitter:PRI:RATio:MINimum \n
		Snippet: value: float = driver.waveform.bemitter.pri.ratio.get_minimum() \n
		Sets the value range for the PRI/PW ratio. \n
			:return: minimum: No help available
		"""
		response = self._core.io.query_str('WAVeform:BEMitter:PRI:RATio:MINimum?')
		return Conversions.str_to_float(response)

	def set_minimum(self, minimum: float) -> None:
		"""SCPI: WAVeform:BEMitter:PRI:RATio:MINimum \n
		Snippet: driver.waveform.bemitter.pri.ratio.set_minimum(minimum = 1.0) \n
		Sets the value range for the PRI/PW ratio. \n
			:param minimum: float Range: 10 to 1000
		"""
		param = Conversions.decimal_value_to_str(minimum)
		self._core.io.write(f'WAVeform:BEMitter:PRI:RATio:MINimum {param}')
