from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Waveform:
	"""Waveform commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("waveform", core, parent)

	def clear(self) -> None:
		"""SCPI: WAVeform:WAVeform:CLEar \n
		Snippet: driver.waveform.waveform.clear() \n
		Removes the imported waveform or file with I/Q data. \n
		"""
		self._core.io.write(f'WAVeform:WAVeform:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: WAVeform:WAVeform:CLEar \n
		Snippet: driver.waveform.waveform.clear_with_opc() \n
		Removes the imported waveform or file with I/Q data. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'WAVeform:WAVeform:CLEar', opc_timeout_ms)

	def load(self, load: str) -> None:
		"""SCPI: WAVeform:WAVeform:LOAD \n
		Snippet: driver.waveform.waveform.load(load = '1') \n
		Load the selected waveform file (*.wv) , see Table 'Supported file types'. \n
			:param load: string Complete file path with file name and extension
		"""
		param = Conversions.value_to_quoted_str(load)
		self._core.io.write(f'WAVeform:WAVeform:LOAD {param}')
