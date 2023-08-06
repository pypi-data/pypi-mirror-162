from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Emitters:
	"""Emitters commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("emitters", core, parent)

	def get_list_py(self) -> str:
		"""SCPI: ASSignment:EMITters:LIST \n
		Snippet: value: str = driver.assignment.emitters.get_list_py() \n
		Queries the alias names of the unassigned emitters/interferers. \n
			:return: list_py: 'Emitter/Inter#1','Emitter/Inter#2',...
		"""
		response = self._core.io.query_str('ASSignment:EMITters:LIST?')
		return trim_str_response(response)

	def get_select(self) -> str:
		"""SCPI: ASSignment:EMITters:SELect \n
		Snippet: value: str = driver.assignment.emitters.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('ASSignment:EMITters:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: ASSignment:EMITters:SELect \n
		Snippet: driver.assignment.emitters.set_select(select = '1') \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'ASSignment:EMITters:SELect {param}')
