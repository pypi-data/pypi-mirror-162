from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Destination:
	"""Destination commands group definition. 14 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("destination", core, parent)

	@property
	def path(self):
		"""path commands group. 2 Sub-classes, 2 commands."""
		if not hasattr(self, '_path'):
			from .Path import Path
			self._path = Path(self._core, self._cmd_group)
		return self._path

	def get_list_py(self) -> str:
		"""SCPI: ASSignment:DESTination:LIST \n
		Snippet: value: str = driver.assignment.destination.get_list_py() \n
		Queries a list of the available destinations. \n
			:return: list_py: 'GenName#1','GenName2',...
		"""
		response = self._core.io.query_str('ASSignment:DESTination:LIST?')
		return trim_str_response(response)

	def get_select(self) -> str:
		"""SCPI: ASSignment:DESTination:SELect \n
		Snippet: value: str = driver.assignment.destination.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Destination.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('ASSignment:DESTination:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: ASSignment:DESTination:SELect \n
		Snippet: driver.assignment.destination.set_select(select = '1') \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Destination.Path.Antenna.listPy
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'ASSignment:DESTination:SELect {param}')

	def clone(self) -> 'Destination':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Destination(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
