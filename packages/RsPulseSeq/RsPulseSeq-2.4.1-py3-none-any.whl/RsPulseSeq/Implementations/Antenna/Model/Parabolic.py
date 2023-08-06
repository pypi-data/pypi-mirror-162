from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Parabolic:
	"""Parabolic commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("parabolic", core, parent)

	def get_diameter(self) -> float:
		"""SCPI: ANTenna:MODel:PARabolic:DIAMeter \n
		Snippet: value: float = driver.antenna.model.parabolic.get_diameter() \n
		Sets the diameter of the parabolic dish antenna. \n
			:return: diameter: float Range: 0.05 to 100, Unit: m
		"""
		response = self._core.io.query_str('ANTenna:MODel:PARabolic:DIAMeter?')
		return Conversions.str_to_float(response)

	def set_diameter(self, diameter: float) -> None:
		"""SCPI: ANTenna:MODel:PARabolic:DIAMeter \n
		Snippet: driver.antenna.model.parabolic.set_diameter(diameter = 1.0) \n
		Sets the diameter of the parabolic dish antenna. \n
			:param diameter: float Range: 0.05 to 100, Unit: m
		"""
		param = Conversions.decimal_value_to_str(diameter)
		self._core.io.write(f'ANTenna:MODel:PARabolic:DIAMeter {param}')

	def get_resolution(self) -> float:
		"""SCPI: ANTenna:MODel:PARabolic:RESolution \n
		Snippet: value: float = driver.antenna.model.parabolic.get_resolution() \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:return: resolution: float Range: 0.1 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:PARabolic:RESolution?')
		return Conversions.str_to_float(response)

	def set_resolution(self, resolution: float) -> None:
		"""SCPI: ANTenna:MODel:PARabolic:RESolution \n
		Snippet: driver.antenna.model.parabolic.set_resolution(resolution = 1.0) \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:param resolution: float Range: 0.1 to 1
		"""
		param = Conversions.decimal_value_to_str(resolution)
		self._core.io.write(f'ANTenna:MODel:PARabolic:RESolution {param}')
