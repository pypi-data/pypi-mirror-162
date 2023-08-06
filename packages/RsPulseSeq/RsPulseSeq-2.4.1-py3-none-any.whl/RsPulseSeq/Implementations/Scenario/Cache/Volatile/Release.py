from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Release:
	"""Release commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("release", core, parent)

	def set(self) -> None:
		"""SCPI: SCENario:CACHe:VOLatile:RELease \n
		Snippet: driver.scenario.cache.volatile.release.set() \n
		Exports and stores the generated signal files in the repository. \n
		"""
		self._core.io.write(f'SCENario:CACHe:VOLatile:RELease')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:CACHe:VOLatile:RELease \n
		Snippet: driver.scenario.cache.volatile.release.set_with_opc() \n
		Exports and stores the generated signal files in the repository. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:CACHe:VOLatile:RELease', opc_timeout_ms)
