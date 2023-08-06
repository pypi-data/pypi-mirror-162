from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Phase:
	"""Phase commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("phase", core, parent)

	def get_offset(self) -> float:
		"""SCPI: SEQuence:ITEM:PHASe:OFFSet \n
		Snippet: value: float = driver.sequence.item.phase.get_offset() \n
		Sets a phase offset. \n
			:return: offset: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SEQuence:ITEM:PHASe:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, offset: float) -> None:
		"""SCPI: SEQuence:ITEM:PHASe:OFFSet \n
		Snippet: driver.sequence.item.phase.set_offset(offset = 1.0) \n
		Sets a phase offset. \n
			:param offset: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(offset)
		self._core.io.write(f'SEQuence:ITEM:PHASe:OFFSet {param}')
