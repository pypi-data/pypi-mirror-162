from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Group:
	"""Group commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("group", core, parent)

	def get_list_py(self) -> str:
		"""SCPI: ASSignment:GROup:LIST \n
		Snippet: value: str = driver.assignment.group.get_list_py() \n
		If interleaving groups are defined, queries the alias names of the unassigned interleaving groups. \n
			:return: list_py: string
		"""
		response = self._core.io.query_str('ASSignment:GROup:LIST?')
		return trim_str_response(response)

	def get_select(self) -> str:
		"""SCPI: ASSignment:GROup:SELect \n
		Snippet: value: str = driver.assignment.group.get_select() \n
		Assigns the selected group to the plugin and path selected with the commands method RsPulseSeq.Assignment.Destination.
		select and method RsPulseSeq.Assignment.Destination.Path.select. \n
			:return: select: string
		"""
		response = self._core.io.query_str('ASSignment:GROup:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: ASSignment:GROup:SELect \n
		Snippet: driver.assignment.group.set_select(select = '1') \n
		Assigns the selected group to the plugin and path selected with the commands method RsPulseSeq.Assignment.Destination.
		select and method RsPulseSeq.Assignment.Destination.Path.select. \n
			:param select: string
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'ASSignment:GROup:SELect {param}')
