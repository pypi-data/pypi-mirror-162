from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Level:
	"""Level commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("level", core, parent)

	def get_droop(self) -> float:
		"""SCPI: PULSe:LEVel:DROop \n
		Snippet: value: float = driver.pulse.level.get_droop() \n
		Sets the amplitude droop. \n
			:return: droop: float Range: 0 to 50
		"""
		response = self._core.io.query_str('PULSe:LEVel:DROop?')
		return Conversions.str_to_float(response)

	def set_droop(self, droop: float) -> None:
		"""SCPI: PULSe:LEVel:DROop \n
		Snippet: driver.pulse.level.set_droop(droop = 1.0) \n
		Sets the amplitude droop. \n
			:param droop: float Range: 0 to 50
		"""
		param = Conversions.decimal_value_to_str(droop)
		self._core.io.write(f'PULSe:LEVel:DROop {param}')

	def get_off(self) -> float:
		"""SCPI: PULSe:LEVel:OFF \n
		Snippet: value: float = driver.pulse.level.get_off() \n
		Sets the power during the pulse on time or the pulse off time. \n
			:return: off: No help available
		"""
		response = self._core.io.query_str('PULSe:LEVel:OFF?')
		return Conversions.str_to_float(response)

	def set_off(self, off: float) -> None:
		"""SCPI: PULSe:LEVel:OFF \n
		Snippet: driver.pulse.level.set_off(off = 1.0) \n
		Sets the power during the pulse on time or the pulse off time. \n
			:param off: float Range: 0 to 100
		"""
		param = Conversions.decimal_value_to_str(off)
		self._core.io.write(f'PULSe:LEVel:OFF {param}')

	def get_on(self) -> float:
		"""SCPI: PULSe:LEVel:ON \n
		Snippet: value: float = driver.pulse.level.get_on() \n
		Sets the power during the pulse on time or the pulse off time. \n
			:return: on: float Range: 0 to 100
		"""
		response = self._core.io.query_str('PULSe:LEVel:ON?')
		return Conversions.str_to_float(response)

	def set_on(self, on: float) -> None:
		"""SCPI: PULSe:LEVel:ON \n
		Snippet: driver.pulse.level.set_on(on = 1.0) \n
		Sets the power during the pulse on time or the pulse off time. \n
			:param on: float Range: 0 to 100
		"""
		param = Conversions.decimal_value_to_str(on)
		self._core.io.write(f'PULSe:LEVel:ON {param}')
