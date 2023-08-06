from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pdw:
	"""Pdw commands group definition. 44 total commands, 4 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pdw", core, parent)

	@property
	def data(self):
		"""data commands group. 9 Sub-classes, 8 commands."""
		if not hasattr(self, '_data'):
			from .Data import Data
			self._data = Data(self._core, self._cmd_group)
		return self._data

	@property
	def execute(self):
		"""execute commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_execute'):
			from .Execute import Execute
			self._execute = Execute(self._core, self._cmd_group)
		return self._execute

	@property
	def file(self):
		"""file commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_file'):
			from .File import File
			self._file = File(self._core, self._cmd_group)
		return self._file

	@property
	def store(self):
		"""store commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_store'):
			from .Store import Store
			self._store = Store(self._core, self._cmd_group)
		return self._store

	def get_norm(self) -> bool:
		"""SCPI: IMPort:PDW:NORM \n
		Snippet: value: bool = driver.importPy.pdw.get_norm() \n
		Normalizes the TOA (time of arrival) of the first pulse to 0. Subsequent TOAs are relative. \n
			:return: norm: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('IMPort:PDW:NORM?')
		return Conversions.str_to_bool(response)

	def set_norm(self, norm: bool) -> None:
		"""SCPI: IMPort:PDW:NORM \n
		Snippet: driver.importPy.pdw.set_norm(norm = False) \n
		Normalizes the TOA (time of arrival) of the first pulse to 0. Subsequent TOAs are relative. \n
			:param norm: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(norm)
		self._core.io.write(f'IMPort:PDW:NORM {param}')

	def get_status(self) -> bool:
		"""SCPI: IMPort:PDW:STATus \n
		Snippet: value: bool = driver.importPy.pdw.get_status() \n
		Queries the parsing status. \n
			:return: status: ON| OFF| 1| 0 1 Import completed
		"""
		response = self._core.io.query_str('IMPort:PDW:STATus?')
		return Conversions.str_to_bool(response)

	def clone(self) -> 'Pdw':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Pdw(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
