from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Init:
	"""Init commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("init", core, parent)

	def get_float_value(self) -> float:
		"""SCPI: DSRC:ITEM:PRBS:INIT:VALue \n
		Snippet: value: float = driver.dsrc.item.prbs.init.get_float_value() \n
		Set a new initialization value. \n
			:return: value: float Range: 1 to 511
		"""
		response = self._core.io.query_str('DSRC:ITEM:PRBS:INIT:VALue?')
		return Conversions.str_to_float(response)

	def set_float_value(self, value: float) -> None:
		"""SCPI: DSRC:ITEM:PRBS:INIT:VALue \n
		Snippet: driver.dsrc.item.prbs.init.set_float_value(value = 1.0) \n
		Set a new initialization value. \n
			:param value: float Range: 1 to 511
		"""
		param = Conversions.decimal_value_to_str(value)
		self._core.io.write(f'DSRC:ITEM:PRBS:INIT:VALue {param}')

	def get_value(self) -> bool:
		"""SCPI: DSRC:ITEM:PRBS:INIT \n
		Snippet: value: bool = driver.dsrc.item.prbs.init.get_value() \n
		Enables/disables initialization of the shift register with a user-defined value. \n
			:return: init: ON| OFF
		"""
		response = self._core.io.query_str('DSRC:ITEM:PRBS:INIT?')
		return Conversions.str_to_bool(response)

	def set_value(self, init: bool) -> None:
		"""SCPI: DSRC:ITEM:PRBS:INIT \n
		Snippet: driver.dsrc.item.prbs.init.set_value(init = False) \n
		Enables/disables initialization of the shift register with a user-defined value. \n
			:param init: ON| OFF
		"""
		param = Conversions.bool_to_str(init)
		self._core.io.write(f'DSRC:ITEM:PRBS:INIT {param}')
