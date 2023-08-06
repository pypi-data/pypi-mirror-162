from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pedestal:
	"""Pedestal commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pedestal", core, parent)

	def get_x(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:PEDestal:X \n
		Snippet: value: float = driver.antenna.model.carray.pedestal.get_x() \n
		No command help available \n
			:return: x: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:PEDestal:X?')
		return Conversions.str_to_float(response)

	def set_x(self, x: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:PEDestal:X \n
		Snippet: driver.antenna.model.carray.pedestal.set_x(x = 1.0) \n
		No command help available \n
			:param x: No help available
		"""
		param = Conversions.decimal_value_to_str(x)
		self._core.io.write(f'ANTenna:MODel:CARRay:PEDestal:X {param}')

	def get_z(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:PEDestal:Z \n
		Snippet: value: float = driver.antenna.model.carray.pedestal.get_z() \n
		No command help available \n
			:return: z: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:PEDestal:Z?')
		return Conversions.str_to_float(response)

	def set_z(self, z: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:PEDestal:Z \n
		Snippet: driver.antenna.model.carray.pedestal.set_z(z = 1.0) \n
		No command help available \n
			:param z: No help available
		"""
		param = Conversions.decimal_value_to_str(z)
		self._core.io.write(f'ANTenna:MODel:CARRay:PEDestal:Z {param}')

	def get_value(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:PEDestal \n
		Snippet: value: float = driver.antenna.model.carray.pedestal.get_value() \n
		Sets the Pedestal of the Planar Phased Array antenna. \n
			:return: pedestal: float Range: 0 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:PEDestal?')
		return Conversions.str_to_float(response)

	def set_value(self, pedestal: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:PEDestal \n
		Snippet: driver.antenna.model.carray.pedestal.set_value(pedestal = 1.0) \n
		Sets the Pedestal of the Planar Phased Array antenna. \n
			:param pedestal: float Range: 0 to 1
		"""
		param = Conversions.decimal_value_to_str(pedestal)
		self._core.io.write(f'ANTenna:MODel:CARRay:PEDestal {param}')
