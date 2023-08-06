from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ImportPy:
	"""ImportPy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("importPy", core, parent)

	def set(self) -> None:
		"""SCPI: SETup:RFALign:IMPort \n
		Snippet: driver.setup.rfAlign.importPy.set() \n
		Loads the selected *.rfsa file in the software. \n
		"""
		self._core.io.write(f'SETup:RFALign:IMPort')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SETup:RFALign:IMPort \n
		Snippet: driver.setup.rfAlign.importPy.set_with_opc() \n
		Loads the selected *.rfsa file in the software. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SETup:RFALign:IMPort', opc_timeout_ms)
