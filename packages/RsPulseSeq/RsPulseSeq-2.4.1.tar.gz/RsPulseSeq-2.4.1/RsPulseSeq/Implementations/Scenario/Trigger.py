from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Trigger:
	"""Trigger commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("trigger", core, parent)

	def set(self) -> None:
		"""SCPI: SCENario:TRIGger \n
		Snippet: driver.scenario.trigger.set() \n
		Triggers the scenario, if separate trigger for scenario start is enabled. See method RsPulseSeq.Program.Scenario.Xtrg.
		enable. \n
		"""
		self._core.io.write(f'SCENario:TRIGger')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:TRIGger \n
		Snippet: driver.scenario.trigger.set_with_opc() \n
		Triggers the scenario, if separate trigger for scenario start is enabled. See method RsPulseSeq.Program.Scenario.Xtrg.
		enable. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:TRIGger', opc_timeout_ms)
