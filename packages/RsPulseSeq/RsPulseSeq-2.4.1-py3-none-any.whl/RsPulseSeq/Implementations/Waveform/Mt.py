from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Mt:
	"""Mt commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mt", core, parent)

	def get_count(self) -> float:
		"""SCPI: WAVeform:MT:COUNt \n
		Snippet: value: float = driver.waveform.mt.get_count() \n
		Sets the number of tones. \n
			:return: count: integer Range: 2 to 1024
		"""
		response = self._core.io.query_str('WAVeform:MT:COUNt?')
		return Conversions.str_to_float(response)

	def set_count(self, count: float) -> None:
		"""SCPI: WAVeform:MT:COUNt \n
		Snippet: driver.waveform.mt.set_count(count = 1.0) \n
		Sets the number of tones. \n
			:param count: integer Range: 2 to 1024
		"""
		param = Conversions.decimal_value_to_str(count)
		self._core.io.write(f'WAVeform:MT:COUNt {param}')

	def get_spacing(self) -> float:
		"""SCPI: WAVeform:MT:SPACing \n
		Snippet: value: float = driver.waveform.mt.get_spacing() \n
		Sets the tone spacing. \n
			:return: spacing: float Range: 100 to 1e+07
		"""
		response = self._core.io.query_str('WAVeform:MT:SPACing?')
		return Conversions.str_to_float(response)

	def set_spacing(self, spacing: float) -> None:
		"""SCPI: WAVeform:MT:SPACing \n
		Snippet: driver.waveform.mt.set_spacing(spacing = 1.0) \n
		Sets the tone spacing. \n
			:param spacing: float Range: 100 to 1e+07
		"""
		param = Conversions.decimal_value_to_str(spacing)
		self._core.io.write(f'WAVeform:MT:SPACing {param}')
