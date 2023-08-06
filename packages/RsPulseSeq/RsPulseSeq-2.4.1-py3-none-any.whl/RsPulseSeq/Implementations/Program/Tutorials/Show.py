from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Show:
	"""Show commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("show", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:TUTorials:SHOW:ENABle \n
		Snippet: value: bool = driver.program.tutorials.show.get_enable() \n
		This setting re-enables all tutorials. Tutorials are shown upon opening certain dialogs for the first time (e.g. 2D Map) .
		When the tutorial has been viewed, it is then disabled. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:TUTorials:SHOW:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:TUTorials:SHOW:ENABle \n
		Snippet: driver.program.tutorials.show.set_enable(enable = False) \n
		This setting re-enables all tutorials. Tutorials are shown upon opening certain dialogs for the first time (e.g. 2D Map) .
		When the tutorial has been viewed, it is then disabled. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:TUTorials:SHOW:ENABle {param}')
