from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Gpu:
	"""Gpu commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gpu", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:GPU:ENABle \n
		Snippet: value: bool = driver.program.gpu.get_enable() \n
		Enables the GPU (Graphics Processing Unit) to be used for antenna pattern calculations. Using the GPU accelerates the
		calculation. Requires a restart. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:GPU:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:GPU:ENABle \n
		Snippet: driver.program.gpu.set_enable(enable = False) \n
		Enables the GPU (Graphics Processing Unit) to be used for antenna pattern calculations. Using the GPU accelerates the
		calculation. Requires a restart. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:GPU:ENABle {param}')
