from typing import List

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Repmanager:
	"""Repmanager commands group definition. 7 total commands, 1 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("repmanager", core, parent)

	@property
	def path(self):
		"""path commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_path'):
			from .Path import Path
			self._path = Path(self._core, self._cmd_group)
		return self._path

	def get_catalog(self) -> List[int]:
		"""SCPI: REPManager:CATalog \n
		Snippet: value: List[int] = driver.repmanager.get_catalog() \n
		Queries available repository elements in the database. \n
			:return: catalog: 'RepositryName','path' RepositryName is the name of the repository as defined with the command method RsPulseSeq.Repository.create Path is the compete file path
		"""
		response = self._core.io.query_bin_or_ascii_int_list('REPManager:CATalog?')
		return response

	def delete(self, delete: List[int]) -> None:
		"""SCPI: REPManager:DELete \n
		Snippet: driver.repmanager.delete(delete = [1, 2, 3]) \n
		Deletes the entire repository from the permanent mass storage. \n
			:param delete: No help available
		"""
		param = Conversions.list_to_csv_str(delete)
		self._core.io.write(f'REPManager:DELete {param}')

	def export(self, export: List[int]) -> None:
		"""SCPI: REPManager:EXPort \n
		Snippet: driver.repmanager.export(export = [1, 2, 3]) \n
		Exports the selected repository file to an archive file. \n
			:param export: No help available
		"""
		param = Conversions.list_to_csv_str(export)
		self._core.io.write(f'REPManager:EXPort {param}')

	def load(self, load: List[int]) -> None:
		"""SCPI: REPManager:LOAD \n
		Snippet: driver.repmanager.load(load = [1, 2, 3]) \n
		Loads the selected repository to the workspace. If more than one repository with the same name exist, loaded is the first
		repository with a name match. To query the available repository elements in the database, use the command method
		RsPulseSeq.Repository.catalog. \n
			:param load: No help available
		"""
		param = Conversions.list_to_csv_str(load)
		self._core.io.write(f'REPManager:LOAD {param}')

	def clone(self) -> 'Repmanager':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Repmanager(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
