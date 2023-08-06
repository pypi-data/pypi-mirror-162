from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Antennas:
	"""Antennas commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("antennas", core, parent)

	def get_list_py(self) -> str:
		"""SCPI: ASSignment:ANTennas:LIST \n
		Snippet: value: str = driver.assignment.antennas.get_list_py() \n
		Queries the alias names of the unassigned receiver signals. \n
			:return: list_py: 'ReceiverSignal#1','ReceiverSignal#2',...
		"""
		response = self._core.io.query_str('ASSignment:ANTennas:LIST?')
		return trim_str_response(response)

	def get_select(self) -> str:
		"""SCPI: ASSignment:ANTennas:SELect \n
		Snippet: value: str = driver.assignment.antennas.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('ASSignment:ANTennas:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: ASSignment:ANTennas:SELect \n
		Snippet: driver.assignment.antennas.set_select(select = '1') \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'ASSignment:ANTennas:SELect {param}')
