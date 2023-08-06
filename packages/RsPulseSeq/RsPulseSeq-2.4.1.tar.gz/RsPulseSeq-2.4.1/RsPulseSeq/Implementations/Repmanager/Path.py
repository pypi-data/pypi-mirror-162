from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Path:
	"""Path commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("path", core, parent)

	def set_add(self, add: str) -> None:
		"""SCPI: REPManager:PATH:ADD \n
		Snippet: driver.repmanager.path.set_add(add = '1') \n
		Add the selected directory. \n
			:param add: string Complete file path
		"""
		param = Conversions.value_to_quoted_str(add)
		self._core.io.write(f'REPManager:PATH:ADD {param}')

	def delete(self, delete: str) -> None:
		"""SCPI: REPManager:PATH:DELete \n
		Snippet: driver.repmanager.path.delete(delete = '1') \n
		Removes the selected file path. \n
			:param delete: string File path
		"""
		param = Conversions.value_to_quoted_str(delete)
		self._core.io.write(f'REPManager:PATH:DELete {param}')

	def get_list_py(self) -> str:
		"""SCPI: REPManager:PATH:LIST \n
		Snippet: value: str = driver.repmanager.path.get_list_py() \n
		Queries the directory in that the repository files are stored. \n
			:return: list_py: string Compete file path
		"""
		response = self._core.io.query_str('REPManager:PATH:LIST?')
		return trim_str_response(response)
