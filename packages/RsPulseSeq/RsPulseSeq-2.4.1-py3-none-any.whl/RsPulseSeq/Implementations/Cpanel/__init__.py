from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Cpanel:
	"""Cpanel commands group definition. 25 total commands, 6 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cpanel", core, parent)

	@property
	def mute(self):
		"""mute commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mute'):
			from .Mute import Mute
			self._mute = Mute(self._core, self._cmd_group)
		return self._mute

	@property
	def refresh(self):
		"""refresh commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_refresh'):
			from .Refresh import Refresh
			self._refresh = Refresh(self._core, self._cmd_group)
		return self._refresh

	@property
	def scenario(self):
		"""scenario commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_scenario'):
			from .Scenario import Scenario
			self._scenario = Scenario(self._core, self._cmd_group)
		return self._scenario

	@property
	def unmute(self):
		"""unmute commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_unmute'):
			from .Unmute import Unmute
			self._unmute = Unmute(self._core, self._cmd_group)
		return self._unmute

	@property
	def unused(self):
		"""unused commands group. 1 Sub-classes, 6 commands."""
		if not hasattr(self, '_unused'):
			from .Unused import Unused
			self._unused = Unused(self._core, self._cmd_group)
		return self._unused

	@property
	def used(self):
		"""used commands group. 1 Sub-classes, 5 commands."""
		if not hasattr(self, '_used'):
			from .Used import Used
			self._used = Used(self._core, self._cmd_group)
		return self._used

	def activate(self) -> None:
		"""SCPI: CPANel:ACTivate \n
		Snippet: driver.cpanel.activate() \n
		Activates and deactivates the remote control of the control panel. Further CPANel:... commands cannot be executed, if the
		remote control is not active. After configuration, always deactivate the remote control of the control panel. \n
		"""
		self._core.io.write(f'CPANel:ACTivate')

	def activate_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: CPANel:ACTivate \n
		Snippet: driver.cpanel.activate_with_opc() \n
		Activates and deactivates the remote control of the control panel. Further CPANel:... commands cannot be executed, if the
		remote control is not active. After configuration, always deactivate the remote control of the control panel. \n
		Same as activate, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'CPANel:ACTivate', opc_timeout_ms)

	def deactivate(self) -> None:
		"""SCPI: CPANel:DEACtivate \n
		Snippet: driver.cpanel.deactivate() \n
		Activates and deactivates the remote control of the control panel. Further CPANel:... commands cannot be executed, if the
		remote control is not active. After configuration, always deactivate the remote control of the control panel. \n
		"""
		self._core.io.write(f'CPANel:DEACtivate')

	def deactivate_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: CPANel:DEACtivate \n
		Snippet: driver.cpanel.deactivate_with_opc() \n
		Activates and deactivates the remote control of the control panel. Further CPANel:... commands cannot be executed, if the
		remote control is not active. After configuration, always deactivate the remote control of the control panel. \n
		Same as deactivate, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'CPANel:DEACtivate', opc_timeout_ms)

	def get_setup(self) -> str:
		"""SCPI: CPANel:SETup \n
		Snippet: value: str = driver.cpanel.get_setup() \n
		Queries the name of the setup selected in the 'Signal Generators' dialog. \n
			:return: setup: string
		"""
		response = self._core.io.query_str('CPANel:SETup?')
		return trim_str_response(response)

	def clone(self) -> 'Cpanel':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Cpanel(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
