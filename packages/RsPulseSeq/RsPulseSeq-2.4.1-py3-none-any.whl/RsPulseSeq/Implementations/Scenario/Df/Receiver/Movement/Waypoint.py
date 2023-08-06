from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Waypoint:
	"""Waypoint commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("waypoint", core, parent)

	def clear(self) -> None:
		"""SCPI: SCENario:DF:RECeiver:MOVement:WAYPoint:CLEar \n
		Snippet: driver.scenario.df.receiver.movement.waypoint.clear() \n
		Discards the selected file. \n
		"""
		self._core.io.write(f'SCENario:DF:RECeiver:MOVement:WAYPoint:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:DF:RECeiver:MOVement:WAYPoint:CLEar \n
		Snippet: driver.scenario.df.receiver.movement.waypoint.clear_with_opc() \n
		Discards the selected file. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:DF:RECeiver:MOVement:WAYPoint:CLEar', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: SCENario:DF:RECeiver:MOVement:WAYPoint \n
		Snippet: value: str = driver.scenario.df.receiver.movement.waypoint.get_value() \n
		Loads the selected waypoint file. To import and apply the files, send the command method RsPulseSeq.Scenario.Localized.
		Movement.ImportPy.set. \n
			:return: waypoint: string Filename or complete file path, incl. file extension. Waypoint files must have the extension *.txt, *.kml or *.xtd. Example files are provided with the software. For description, see 'Movement files'.
		"""
		response = self._core.io.query_str('SCENario:DF:RECeiver:MOVement:WAYPoint?')
		return trim_str_response(response)

	def set_value(self, waypoint: str) -> None:
		"""SCPI: SCENario:DF:RECeiver:MOVement:WAYPoint \n
		Snippet: driver.scenario.df.receiver.movement.waypoint.set_value(waypoint = '1') \n
		Loads the selected waypoint file. To import and apply the files, send the command method RsPulseSeq.Scenario.Localized.
		Movement.ImportPy.set. \n
			:param waypoint: string Filename or complete file path, incl. file extension. Waypoint files must have the extension *.txt, *.kml or *.xtd. Example files are provided with the software. For description, see 'Movement files'.
		"""
		param = Conversions.value_to_quoted_str(waypoint)
		self._core.io.write(f'SCENario:DF:RECeiver:MOVement:WAYPoint {param}')
