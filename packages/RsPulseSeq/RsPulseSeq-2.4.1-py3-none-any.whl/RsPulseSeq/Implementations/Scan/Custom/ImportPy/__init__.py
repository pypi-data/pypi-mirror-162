from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ImportPy:
	"""ImportPy commands group definition. 2 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("importPy", core, parent)

	@property
	def exec(self):
		"""exec commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_exec'):
			from .Exec import Exec
			self._exec = Exec(self._core, self._cmd_group)
		return self._exec

	def get_file(self) -> str:
		"""SCPI: SCAN:CUSTom:IMPort:FILE \n
		Snippet: value: str = driver.scan.custom.importPy.get_file() \n
		Sets the file to import. \n
			:return: file: string
		"""
		response = self._core.io.query_str('SCAN:CUSTom:IMPort:FILE?')
		return trim_str_response(response)

	def set_file(self, file: str) -> None:
		"""SCPI: SCAN:CUSTom:IMPort:FILE \n
		Snippet: driver.scan.custom.importPy.set_file(file = '1') \n
		Sets the file to import. \n
			:param file: string
		"""
		param = Conversions.value_to_quoted_str(file)
		self._core.io.write(f'SCAN:CUSTom:IMPort:FILE {param}')

	def clone(self) -> 'ImportPy':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ImportPy(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
