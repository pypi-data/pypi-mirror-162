from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Horn:
	"""Horn commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("horn", core, parent)

	def get_lx(self) -> float:
		"""SCPI: ANTenna:MODel:HORN:LX \n
		Snippet: value: float = driver.antenna.model.horn.get_lx() \n
		Sets the length of the rectangular sides of the Pyramidal Horn antenna. \n
			:return: lx: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:HORN:LX?')
		return Conversions.str_to_float(response)

	def set_lx(self, lx: float) -> None:
		"""SCPI: ANTenna:MODel:HORN:LX \n
		Snippet: driver.antenna.model.horn.set_lx(lx = 1.0) \n
		Sets the length of the rectangular sides of the Pyramidal Horn antenna. \n
			:param lx: float Range: 0.01 to 100, Unit: m
		"""
		param = Conversions.decimal_value_to_str(lx)
		self._core.io.write(f'ANTenna:MODel:HORN:LX {param}')

	def get_lz(self) -> float:
		"""SCPI: ANTenna:MODel:HORN:LZ \n
		Snippet: value: float = driver.antenna.model.horn.get_lz() \n
		Sets the length of the rectangular sides of the Pyramidal Horn antenna. \n
			:return: lz: float Range: 0.01 to 100, Unit: m
		"""
		response = self._core.io.query_str('ANTenna:MODel:HORN:LZ?')
		return Conversions.str_to_float(response)

	def set_lz(self, lz: float) -> None:
		"""SCPI: ANTenna:MODel:HORN:LZ \n
		Snippet: driver.antenna.model.horn.set_lz(lz = 1.0) \n
		Sets the length of the rectangular sides of the Pyramidal Horn antenna. \n
			:param lz: float Range: 0.01 to 100, Unit: m
		"""
		param = Conversions.decimal_value_to_str(lz)
		self._core.io.write(f'ANTenna:MODel:HORN:LZ {param}')

	def get_resolution(self) -> float:
		"""SCPI: ANTenna:MODel:HORN:RESolution \n
		Snippet: value: float = driver.antenna.model.horn.get_resolution() \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:return: resolution: float Range: 0.1 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:HORN:RESolution?')
		return Conversions.str_to_float(response)

	def set_resolution(self, resolution: float) -> None:
		"""SCPI: ANTenna:MODel:HORN:RESolution \n
		Snippet: driver.antenna.model.horn.set_resolution(resolution = 1.0) \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:param resolution: float Range: 0.1 to 1
		"""
		param = Conversions.decimal_value_to_str(resolution)
		self._core.io.write(f'ANTenna:MODel:HORN:RESolution {param}')
