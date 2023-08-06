from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Volatile:
	"""Volatile commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("volatile", core, parent)

	def get_path(self) -> str:
		"""SCPI: REPository:VOLatile:PATH \n
		Snippet: value: str = driver.repository.volatile.get_path() \n
		Queries the directory in that the volatile data is saved. \n
			:return: path: string
		"""
		response = self._core.io.query_str('REPository:VOLatile:PATH?')
		return trim_str_response(response)
