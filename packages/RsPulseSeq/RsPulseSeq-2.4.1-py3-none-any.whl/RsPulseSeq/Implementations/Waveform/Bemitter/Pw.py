from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pw:
	"""Pw commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pw", core, parent)

	def get_maximum(self) -> float:
		"""SCPI: WAVeform:BEMitter:PW:MAXimum \n
		Snippet: value: float = driver.waveform.bemitter.pw.get_maximum() \n
		Sets the value range for the pulse width values. \n
			:return: maximum: float Range: 5e-05 to 1
		"""
		response = self._core.io.query_str('WAVeform:BEMitter:PW:MAXimum?')
		return Conversions.str_to_float(response)

	def set_maximum(self, maximum: float) -> None:
		"""SCPI: WAVeform:BEMitter:PW:MAXimum \n
		Snippet: driver.waveform.bemitter.pw.set_maximum(maximum = 1.0) \n
		Sets the value range for the pulse width values. \n
			:param maximum: float Range: 5e-05 to 1
		"""
		param = Conversions.decimal_value_to_str(maximum)
		self._core.io.write(f'WAVeform:BEMitter:PW:MAXimum {param}')

	def get_minimum(self) -> float:
		"""SCPI: WAVeform:BEMitter:PW:MINimum \n
		Snippet: value: float = driver.waveform.bemitter.pw.get_minimum() \n
		Sets the value range for the pulse width values. \n
			:return: minimum: No help available
		"""
		response = self._core.io.query_str('WAVeform:BEMitter:PW:MINimum?')
		return Conversions.str_to_float(response)

	def set_minimum(self, minimum: float) -> None:
		"""SCPI: WAVeform:BEMitter:PW:MINimum \n
		Snippet: driver.waveform.bemitter.pw.set_minimum(minimum = 1.0) \n
		Sets the value range for the pulse width values. \n
			:param minimum: float Range: 5e-05 to 1
		"""
		param = Conversions.decimal_value_to_str(minimum)
		self._core.io.write(f'WAVeform:BEMitter:PW:MINimum {param}')
