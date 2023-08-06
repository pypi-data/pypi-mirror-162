from ..Internal.Core import Core
from ..Internal.CommandsGroup import CommandsGroup
from ..Internal import Conversions
from ..Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MsgLog:
	"""MsgLog commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("msgLog", core, parent)

	def get_error(self) -> str:
		"""SCPI: MSGLog:ERRor \n
		Snippet: value: str = driver.msgLog.get_error() \n
		Queries the last error listed in the 'Message Log' dialog. \n
			:return: error: string
		"""
		response = self._core.io.query_str('MSGLog:ERRor?')
		return trim_str_response(response)

	def get_popup(self) -> bool:
		"""SCPI: MSGLog:POPup \n
		Snippet: value: bool = driver.msgLog.get_popup() \n
		Opens/closes the 'Message Log' dialog. \n
			:return: popup: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('MSGLog:POPup?')
		return Conversions.str_to_bool(response)

	def set_popup(self, popup: bool) -> None:
		"""SCPI: MSGLog:POPup \n
		Snippet: driver.msgLog.set_popup(popup = False) \n
		Opens/closes the 'Message Log' dialog. \n
			:param popup: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(popup)
		self._core.io.write(f'MSGLog:POPup {param}')
