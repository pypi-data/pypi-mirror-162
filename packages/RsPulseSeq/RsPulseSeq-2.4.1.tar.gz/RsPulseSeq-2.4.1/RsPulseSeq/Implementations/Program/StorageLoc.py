from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StorageLoc:
	"""StorageLoc commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("storageLoc", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:STORageloc:ENABle \n
		Snippet: value: bool = driver.program.storageLoc.get_enable() \n
		If enabled, you can select the directory in that new repository is saved. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:STORageloc:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:STORageloc:ENABle \n
		Snippet: driver.program.storageLoc.set_enable(enable = False) \n
		If enabled, you can select the directory in that new repository is saved. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:STORageloc:ENABle {param}')
