from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Elevation:
	"""Elevation commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("elevation", core, parent)

	def get_step(self) -> float:
		"""SCPI: SCAN:HELical:ELEVation:STEP \n
		Snippet: value: float = driver.scan.helical.elevation.get_step() \n
		Sets the step width with that the antenna changes its elevation. \n
			:return: step: float Range: 0.01 to 11.25, Unit: degree
		"""
		response = self._core.io.query_str('SCAN:HELical:ELEVation:STEP?')
		return Conversions.str_to_float(response)

	def set_step(self, step: float) -> None:
		"""SCPI: SCAN:HELical:ELEVation:STEP \n
		Snippet: driver.scan.helical.elevation.set_step(step = 1.0) \n
		Sets the step width with that the antenna changes its elevation. \n
			:param step: float Range: 0.01 to 11.25, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(step)
		self._core.io.write(f'SCAN:HELical:ELEVation:STEP {param}')
