from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HpBw:
	"""HpBw commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hpBw", core, parent)

	def get_xy(self) -> float:
		"""SCPI: ANTenna:MODel:CUSTom:HPBW:XY \n
		Snippet: value: float = driver.antenna.model.custom.hpBw.get_xy() \n
		Sets the required HPBW of the custom antenna. \n
			:return: xy: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CUSTom:HPBW:XY?')
		return Conversions.str_to_float(response)

	def set_xy(self, xy: float) -> None:
		"""SCPI: ANTenna:MODel:CUSTom:HPBW:XY \n
		Snippet: driver.antenna.model.custom.hpBw.set_xy(xy = 1.0) \n
		Sets the required HPBW of the custom antenna. \n
			:param xy: float Range: 0.1 to 45
		"""
		param = Conversions.decimal_value_to_str(xy)
		self._core.io.write(f'ANTenna:MODel:CUSTom:HPBW:XY {param}')

	def get_yz(self) -> float:
		"""SCPI: ANTenna:MODel:CUSTom:HPBW:YZ \n
		Snippet: value: float = driver.antenna.model.custom.hpBw.get_yz() \n
		Sets the required HPBW of the custom antenna. \n
			:return: yz: float Range: 0.1 to 45
		"""
		response = self._core.io.query_str('ANTenna:MODel:CUSTom:HPBW:YZ?')
		return Conversions.str_to_float(response)

	def set_yz(self, yz: float) -> None:
		"""SCPI: ANTenna:MODel:CUSTom:HPBW:YZ \n
		Snippet: driver.antenna.model.custom.hpBw.set_yz(yz = 1.0) \n
		Sets the required HPBW of the custom antenna. \n
			:param yz: float Range: 0.1 to 45
		"""
		param = Conversions.decimal_value_to_str(yz)
		self._core.io.write(f'ANTenna:MODel:CUSTom:HPBW:YZ {param}')
