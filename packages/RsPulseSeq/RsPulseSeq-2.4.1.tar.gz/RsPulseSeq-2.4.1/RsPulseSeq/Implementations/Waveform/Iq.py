from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Iq:
	"""Iq commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("iq", core, parent)

	def clear(self) -> None:
		"""SCPI: WAVeform:IQ:CLEar \n
		Snippet: driver.waveform.iq.clear() \n
		Removes the imported waveform or file with I/Q data. \n
		"""
		self._core.io.write(f'WAVeform:IQ:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: WAVeform:IQ:CLEar \n
		Snippet: driver.waveform.iq.clear_with_opc() \n
		Removes the imported waveform or file with I/Q data. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'WAVeform:IQ:CLEar', opc_timeout_ms)
