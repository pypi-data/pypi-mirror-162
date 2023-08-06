from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ImportPy:
	"""ImportPy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("importPy", core, parent)

	def set(self) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:IMPort \n
		Snippet: driver.scenario.localized.receiver.movement.importPy.set() \n
		Imports the selected waypoint and vehicle description files into the repository and applies them. \n
		"""
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:IMPort')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:IMPort \n
		Snippet: driver.scenario.localized.receiver.movement.importPy.set_with_opc() \n
		Imports the selected waypoint and vehicle description files into the repository and applies them. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:LOCalized:RECeiver:MOVement:IMPort', opc_timeout_ms)
