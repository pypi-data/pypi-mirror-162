from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Path:
	"""Path commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("path", core, parent)

	def get_list_py(self) -> str:
		"""SCPI: CPANel:UNUSed:PATH:LIST \n
		Snippet: value: str = driver.cpanel.unused.path.get_list_py() \n
		Queries the available RF paths of the selected signal generators. \n
			:return: list_py: 'Path#1','Paht#2',...
		"""
		response = self._core.io.query_str('CPANel:UNUSed:PATH:LIST?')
		return trim_str_response(response)

	def set_list_py(self, list_py: str) -> None:
		"""SCPI: CPANel:UNUSed:PATH:LIST \n
		Snippet: driver.cpanel.unused.path.set_list_py(list_py = '1') \n
		Queries the available RF paths of the selected signal generators. \n
			:param list_py: 'Path#1','Paht#2',...
		"""
		param = Conversions.value_to_quoted_str(list_py)
		self._core.io.write(f'CPANel:UNUSed:PATH:LIST {param}')

	def get_select(self) -> str:
		"""SCPI: CPANel:UNUSed:PATH:SELect \n
		Snippet: value: str = driver.cpanel.unused.path.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('CPANel:UNUSed:PATH:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: CPANel:UNUSed:PATH:SELect \n
		Snippet: driver.cpanel.unused.path.set_select(select = '1') \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'CPANel:UNUSed:PATH:SELect {param}')
