from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Path:
	"""Path commands group definition. 12 total commands, 2 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("path", core, parent)

	@property
	def antenna(self):
		"""antenna commands group. 1 Sub-classes, 4 commands."""
		if not hasattr(self, '_antenna'):
			from .Antenna import Antenna
			self._antenna = Antenna(self._core, self._cmd_group)
		return self._antenna

	@property
	def emitter(self):
		"""emitter commands group. 1 Sub-classes, 4 commands."""
		if not hasattr(self, '_emitter'):
			from .Emitter import Emitter
			self._emitter = Emitter(self._core, self._cmd_group)
		return self._emitter

	def get_list_py(self) -> str:
		"""SCPI: ASSignment:DESTination:PATH:LIST \n
		Snippet: value: str = driver.assignment.destination.path.get_list_py() \n
		Queries the available paths. \n
			:return: list_py: 'Path#1','Path#2',... List of available paths.
		"""
		response = self._core.io.query_str('ASSignment:DESTination:PATH:LIST?')
		return trim_str_response(response)

	def get_select(self) -> str:
		"""SCPI: ASSignment:DESTination:PATH:SELect \n
		Snippet: value: str = driver.assignment.destination.path.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Destination.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('ASSignment:DESTination:PATH:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: ASSignment:DESTination:PATH:SELect \n
		Snippet: driver.assignment.destination.path.set_select(select = '1') \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Destination.Path.Antenna.listPy
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'ASSignment:DESTination:PATH:SELect {param}')

	def clone(self) -> 'Path':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Path(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
