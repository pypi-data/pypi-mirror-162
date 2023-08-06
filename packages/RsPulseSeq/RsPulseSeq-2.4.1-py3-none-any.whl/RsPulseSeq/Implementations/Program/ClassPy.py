from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ClassPy:
	"""ClassPy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("classPy", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:CLASs:ENABle \n
		Snippet: value: bool = driver.program.classPy.get_enable() \n
		Enables whether the workspace classification level appears in the lower window (restart required) . \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:CLASs:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:CLASs:ENABle \n
		Snippet: driver.program.classPy.set_enable(enable = False) \n
		Enables whether the workspace classification level appears in the lower window (restart required) . \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:CLASs:ENABle {param}')
