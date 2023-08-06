from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pstep:
	"""Pstep commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pstep", core, parent)

	def get_select(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:PSTep:SELect \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.pstep.get_select() \n
		Selects the specified point on a trace trajectory. \n
			:return: select: float
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:PSTep:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:PSTep:SELect \n
		Snippet: driver.scenario.localized.receiver.movement.pstep.set_select(select = 1.0) \n
		Selects the specified point on a trace trajectory. \n
			:param select: float
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:PSTep:SELect {param}')
