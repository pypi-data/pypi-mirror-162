from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Current:
	"""Current commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("current", core, parent)

	def get_name(self) -> str:
		"""SCPI: CPANel:SCENario:CURRent:NAME \n
		Snippet: value: str = driver.cpanel.scenario.current.get_name() \n
		Queries the name of the current/last deployed scenario. \n
			:return: name: string
		"""
		response = self._core.io.query_str('CPANel:SCENario:CURRent:NAME?')
		return trim_str_response(response)

	def get_status(self) -> str:
		"""SCPI: CPANel:SCENario:CURRent:STATus \n
		Snippet: value: str = driver.cpanel.scenario.current.get_status() \n
		Queries the scenario status. \n
			:return: status: string
		"""
		response = self._core.io.query_str('CPANel:SCENario:CURRent:STATus?')
		return trim_str_response(response)
