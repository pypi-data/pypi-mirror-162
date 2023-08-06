from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Maps:
	"""Maps commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("maps", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: SCENario:LOCalized:MAPS:ENABle \n
		Snippet: value: bool = driver.scenario.localized.maps.get_enable() \n
		Enable maps for the selected scenario. This operation cannot be undone. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MAPS:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:LOCalized:MAPS:ENABle \n
		Snippet: driver.scenario.localized.maps.set_enable(enable = False) \n
		Enable maps for the selected scenario. This operation cannot be undone. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:LOCalized:MAPS:ENABle {param}')

	def load(self, load: List[int]) -> None:
		"""SCPI: SCENario:LOCalized:MAPS:LOAD \n
		Snippet: driver.scenario.localized.maps.load(load = [1, 2, 3]) \n
		This command loads a georeferenced map for the selected scenario. Supported formats:
			INTRO_CMD_HELP: Examples of special characters: \n
			- .tif
			- .tiff \n
			:param load: No help available
		"""
		param = Conversions.list_to_csv_str(load)
		self._core.io.write(f'SCENario:LOCalized:MAPS:LOAD {param}')
