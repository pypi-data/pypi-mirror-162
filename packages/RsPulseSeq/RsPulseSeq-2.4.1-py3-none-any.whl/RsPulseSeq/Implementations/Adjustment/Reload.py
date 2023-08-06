from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Reload:
	"""Reload commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("reload", core, parent)

	def set(self) -> None:
		"""SCPI: ADJustment:RELoad \n
		Snippet: driver.adjustment.reload.set() \n
		Reinitializes the adjustment database. You can create the level adjustment files not only automatically with the build-in
		Run Level Adjustment function but also externally (or manually) , by performing your own specific measurements. With this
		command, you can (re) load the level adjustment files, irrespectively of way they are created. \n
		"""
		self._core.io.write(f'ADJustment:RELoad')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: ADJustment:RELoad \n
		Snippet: driver.adjustment.reload.set_with_opc() \n
		Reinitializes the adjustment database. You can create the level adjustment files not only automatically with the build-in
		Run Level Adjustment function but also externally (or manually) , by performing your own specific measurements. With this
		command, you can (re) load the level adjustment files, irrespectively of way they are created. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'ADJustment:RELoad', opc_timeout_ms)
