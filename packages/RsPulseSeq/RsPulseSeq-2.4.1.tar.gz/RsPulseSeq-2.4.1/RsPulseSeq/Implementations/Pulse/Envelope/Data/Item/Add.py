from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Add:
	"""Add commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("add", core, parent)

	def set(self) -> None:
		"""SCPI: PULSe:ENVelope:DATA:ITEM:ADD \n
		Snippet: driver.pulse.envelope.data.item.add.set() \n
		Appends new item. \n
		"""
		self._core.io.write(f'PULSe:ENVelope:DATA:ITEM:ADD')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PULSe:ENVelope:DATA:ITEM:ADD \n
		Snippet: driver.pulse.envelope.data.item.add.set_with_opc() \n
		Appends new item. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PULSe:ENVelope:DATA:ITEM:ADD', opc_timeout_ms)
