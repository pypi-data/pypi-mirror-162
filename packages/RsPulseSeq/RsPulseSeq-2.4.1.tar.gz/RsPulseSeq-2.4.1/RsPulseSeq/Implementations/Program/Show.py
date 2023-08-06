from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Show:
	"""Show commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("show", core, parent)

	def set(self) -> None:
		"""SCPI: PROGram:SHOW \n
		Snippet: driver.program.show.set() \n
		Minimizes/maximizes the R&S Pulse Sequencer Digital workspace. \n
		"""
		self._core.io.write(f'PROGram:SHOW')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PROGram:SHOW \n
		Snippet: driver.program.show.set_with_opc() \n
		Minimizes/maximizes the R&S Pulse Sequencer Digital workspace. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PROGram:SHOW', opc_timeout_ms)
