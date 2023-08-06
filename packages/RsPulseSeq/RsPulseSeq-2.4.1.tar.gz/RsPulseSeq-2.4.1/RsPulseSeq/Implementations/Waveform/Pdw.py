from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pdw:
	"""Pdw commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pdw", core, parent)

	def get_center(self) -> float:
		"""SCPI: WAVeform:PDW:CENTer \n
		Snippet: value: float = driver.waveform.pdw.get_center() \n
		During the import of PDW list files, the software evaluates the frequency information in the file and calculates the
		center frequency of all pulses. The center frequency is calculated as the middle frequency between the min and the max
		frequency values included in the PDW file. Chirp frequency deviations are also considered. The pulses are calculated
		relatively to this center frequency. If the actual frequency of the generator differs from the calculated one, use this
		command to set the center frequency of the generator. \n
			:return: center: float Range: 0 to 4e+10
		"""
		response = self._core.io.query_str('WAVeform:PDW:CENTer?')
		return Conversions.str_to_float(response)

	def set_center(self, center: float) -> None:
		"""SCPI: WAVeform:PDW:CENTer \n
		Snippet: driver.waveform.pdw.set_center(center = 1.0) \n
		During the import of PDW list files, the software evaluates the frequency information in the file and calculates the
		center frequency of all pulses. The center frequency is calculated as the middle frequency between the min and the max
		frequency values included in the PDW file. Chirp frequency deviations are also considered. The pulses are calculated
		relatively to this center frequency. If the actual frequency of the generator differs from the calculated one, use this
		command to set the center frequency of the generator. \n
			:param center: float Range: 0 to 4e+10
		"""
		param = Conversions.decimal_value_to_str(center)
		self._core.io.write(f'WAVeform:PDW:CENTer {param}')
