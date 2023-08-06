from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Vfile:
	"""Vfile commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("vfile", core, parent)

	def clear(self) -> None:
		"""SCPI: SCENario:LOCalized:MOVement:VFILe:CLEar \n
		Snippet: driver.scenario.localized.movement.vfile.clear() \n
		Discards the selected vehicle description file. \n
		"""
		self._core.io.write(f'SCENario:LOCalized:MOVement:VFILe:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:LOCalized:MOVement:VFILe:CLEar \n
		Snippet: driver.scenario.localized.movement.vfile.clear_with_opc() \n
		Discards the selected vehicle description file. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:LOCalized:MOVement:VFILe:CLEar', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: SCENario:LOCalized:MOVement:VFILe \n
		Snippet: value: str = driver.scenario.localized.movement.vfile.get_value() \n
		Loads the selected vehicle description file (*.xvd) . To import and apply the files, send the command method RsPulseSeq.
		Scenario.Localized.Movement.ImportPy.set. \n
			:return: vfile: string Filename or complete file path, incl. file extension. Example files are provided with the software. For description, see 'Vehicle description files (Used for smoothening) '.
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MOVement:VFILe?')
		return trim_str_response(response)

	def set_value(self, vfile: str) -> None:
		"""SCPI: SCENario:LOCalized:MOVement:VFILe \n
		Snippet: driver.scenario.localized.movement.vfile.set_value(vfile = '1') \n
		Loads the selected vehicle description file (*.xvd) . To import and apply the files, send the command method RsPulseSeq.
		Scenario.Localized.Movement.ImportPy.set. \n
			:param vfile: string Filename or complete file path, incl. file extension. Example files are provided with the software. For description, see 'Vehicle description files (Used for smoothening) '.
		"""
		param = Conversions.value_to_quoted_str(vfile)
		self._core.io.write(f'SCENario:LOCalized:MOVement:VFILe {param}')
