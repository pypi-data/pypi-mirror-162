from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Enable:
	"""Enable commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def get_interleave(self) -> bool:
		"""SCPI: SCENario:CACHe:REPository:ENABle:INTerleave \n
		Snippet: value: bool = driver.scenario.cache.repository.enable.get_interleave() \n
		Enables file storage in the repository when interleaving is active. \n
			:return: interleave: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CACHe:REPository:ENABle:INTerleave?')
		return Conversions.str_to_bool(response)

	def set_interleave(self, interleave: bool) -> None:
		"""SCPI: SCENario:CACHe:REPository:ENABle:INTerleave \n
		Snippet: driver.scenario.cache.repository.enable.set_interleave(interleave = False) \n
		Enables file storage in the repository when interleaving is active. \n
			:param interleave: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(interleave)
		self._core.io.write(f'SCENario:CACHe:REPository:ENABle:INTerleave {param}')

	def get_value(self) -> bool:
		"""SCPI: SCENario:CACHe:REPository:ENABle \n
		Snippet: value: bool = driver.scenario.cache.repository.enable.get_value() \n
		Enables file storage in the repository. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CACHe:REPository:ENABle?')
		return Conversions.str_to_bool(response)

	def set_value(self, enable: bool) -> None:
		"""SCPI: SCENario:CACHe:REPository:ENABle \n
		Snippet: driver.scenario.cache.repository.enable.set_value(enable = False) \n
		Enables file storage in the repository. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:CACHe:REPository:ENABle {param}')
