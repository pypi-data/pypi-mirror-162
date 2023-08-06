from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class View:
	"""View commands group definition. 5 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("view", core, parent)

	@property
	def zoom(self):
		"""zoom commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_zoom'):
			from .Zoom import Zoom
			self._zoom = Zoom(self._core, self._cmd_group)
		return self._zoom

	def set(self) -> None:
		"""SCPI: SCENario:VOLatile:VIEW \n
		Snippet: driver.scenario.volatile.view.set() \n
		If a waveform exists in the volatile memory, opens the 'Waveform Viewer' and displays this waveform. \n
		"""
		self._core.io.write(f'SCENario:VOLatile:VIEW')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:VOLatile:VIEW \n
		Snippet: driver.scenario.volatile.view.set_with_opc() \n
		If a waveform exists in the volatile memory, opens the 'Waveform Viewer' and displays this waveform. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:VOLatile:VIEW', opc_timeout_ms)

	def set_xmode(self, xmode: enums.ViewXode) -> None:
		"""SCPI: SCENario:VOLatile:VIEW:XMODe \n
		Snippet: driver.scenario.volatile.view.set_xmode(xmode = enums.ViewXode.SAMPles) \n
		Sets the units (time or samples) used on the x axis. \n
			:param xmode: SAMPles| TIME
		"""
		param = Conversions.enum_scalar_to_str(xmode, enums.ViewXode)
		self._core.io.write(f'SCENario:VOLatile:VIEW:XMODe {param}')

	def set_ymode(self, ymode: enums.Ymode) -> None:
		"""SCPI: SCENario:VOLatile:VIEW:YMODe \n
		Snippet: driver.scenario.volatile.view.set_ymode(ymode = enums.Ymode.FREQuency) \n
		Sets the view mode. \n
			:param ymode: IQ| MAGDb| MAGW| MAGV| PHASe| FREQuency| PAV
		"""
		param = Conversions.enum_scalar_to_str(ymode, enums.Ymode)
		self._core.io.write(f'SCENario:VOLatile:VIEW:YMODe {param}')

	def clone(self) -> 'View':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = View(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
