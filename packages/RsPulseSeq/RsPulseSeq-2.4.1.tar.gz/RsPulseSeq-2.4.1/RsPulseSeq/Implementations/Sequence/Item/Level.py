from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Level:
	"""Level commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("level", core, parent)

	def get_offset(self) -> float:
		"""SCPI: SEQuence:ITEM:LEVel:OFFSet \n
		Snippet: value: float = driver.sequence.item.level.get_offset() \n
		Sets a level offset. \n
			:return: offset: float Range: -100 to 0, Unit: dB
		"""
		response = self._core.io.query_str('SEQuence:ITEM:LEVel:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, offset: float) -> None:
		"""SCPI: SEQuence:ITEM:LEVel:OFFSet \n
		Snippet: driver.sequence.item.level.set_offset(offset = 1.0) \n
		Sets a level offset. \n
			:param offset: float Range: -100 to 0, Unit: dB
		"""
		param = Conversions.decimal_value_to_str(offset)
		self._core.io.write(f'SEQuence:ITEM:LEVel:OFFSet {param}')
