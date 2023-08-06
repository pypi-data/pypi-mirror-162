from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Firing:
	"""Firing commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("firing", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: IPM:LIST:FIRing:ENABle \n
		Snippet: value: bool = driver.ipm.listPy.firing.get_enable() \n
		Enables using firing order for list-based IPM profiles. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('IPM:LIST:FIRing:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: IPM:LIST:FIRing:ENABle \n
		Snippet: driver.ipm.listPy.firing.set_enable(enable = False) \n
		Enables using firing order for list-based IPM profiles. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'IPM:LIST:FIRing:ENABle {param}')

	def get_sequence(self) -> str:
		"""SCPI: IPM:LIST:FIRing:SEQuence \n
		Snippet: value: str = driver.ipm.listPy.firing.get_sequence() \n
		Sets the firing order sequence. \n
			:return: sequence: string
		"""
		response = self._core.io.query_str('IPM:LIST:FIRing:SEQuence?')
		return trim_str_response(response)

	def set_sequence(self, sequence: str) -> None:
		"""SCPI: IPM:LIST:FIRing:SEQuence \n
		Snippet: driver.ipm.listPy.firing.set_sequence(sequence = '1') \n
		Sets the firing order sequence. \n
			:param sequence: string
		"""
		param = Conversions.value_to_quoted_str(sequence)
		self._core.io.write(f'IPM:LIST:FIRing:SEQuence {param}')
