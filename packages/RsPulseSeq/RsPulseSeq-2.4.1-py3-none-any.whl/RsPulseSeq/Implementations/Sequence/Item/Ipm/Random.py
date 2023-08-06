from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Random:
	"""Random commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("random", core, parent)

	def get_reset(self) -> bool:
		"""SCPI: SEQuence:ITEM:IPM:RANDom:RESet \n
		Snippet: value: bool = driver.sequence.item.ipm.random.get_reset() \n
		Resets the start seed of random generator. \n
			:return: reset: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:RANDom:RESet?')
		return Conversions.str_to_bool(response)

	def set_reset(self, reset: bool) -> None:
		"""SCPI: SEQuence:ITEM:IPM:RANDom:RESet \n
		Snippet: driver.sequence.item.ipm.random.set_reset(reset = False) \n
		Resets the start seed of random generator. \n
			:param reset: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(reset)
		self._core.io.write(f'SEQuence:ITEM:IPM:RANDom:RESet {param}')
