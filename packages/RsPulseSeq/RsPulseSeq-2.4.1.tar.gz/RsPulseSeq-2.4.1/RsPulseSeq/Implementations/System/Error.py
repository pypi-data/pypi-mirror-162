from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Error:
	"""Error commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("error", core, parent)

	def get_all(self) -> str:
		"""SCPI: SYSTem:ERRor:ALL \n
		Snippet: value: str = driver.system.error.get_all() \n
		Queries the error/event queue for all unread items and removes them from the queue. The response is a comma-separated
		list of error number and a short description of the error in FIFO order. Positive error numbers are instrument-dependent.
		Negative error numbers are reserved by the SCPI standard. \n
			:return: all_py: string List of: Error/event_number,'Error/event_description[;Device-dependent info]' If the queue is empty, the response is 0,'No error'
		"""
		response = self._core.io.query_str('SYSTem:ERRor:ALL?')
		return trim_str_response(response)

	def get_count(self) -> str:
		"""SCPI: SYSTem:ERRor:COUNt \n
		Snippet: value: str = driver.system.error.get_count() \n
		Queries the number of entries in the error queue. If the error queue is empty, '0' is returned. \n
			:return: count: string
		"""
		response = self._core.io.query_str('SYSTem:ERRor:COUNt?')
		return trim_str_response(response)
