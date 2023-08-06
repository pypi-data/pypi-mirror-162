from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Deployed:
	"""Deployed commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("deployed", core, parent)

	def get_name(self) -> str:
		"""SCPI: CPANel:SCENario:DEPLoyed:NAME \n
		Snippet: value: str = driver.cpanel.scenario.deployed.get_name() \n
		Queries the name of the current/last deployed scenario. \n
			:return: name: string
		"""
		response = self._core.io.query_str('CPANel:SCENario:DEPLoyed:NAME?')
		return trim_str_response(response)

	def get_time(self) -> str:
		"""SCPI: CPANel:SCENario:DEPLoyed:TIME \n
		Snippet: value: str = driver.cpanel.scenario.deployed.get_time() \n
		Queries the date and time the scenario has been deployed. \n
			:return: time: DD MMM YYY hh:mm:ss
		"""
		response = self._core.io.query_str('CPANel:SCENario:DEPLoyed:TIME?')
		return trim_str_response(response)
