from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Cosn:
	"""Cosn commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cosn", core, parent)

	def get_x(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:COSN:X \n
		Snippet: value: float = driver.antenna.model.array.cosn.get_x() \n
		No command help available \n
			:return: x: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:COSN:X?')
		return Conversions.str_to_float(response)

	def set_x(self, x: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:COSN:X \n
		Snippet: driver.antenna.model.array.cosn.set_x(x = 1.0) \n
		No command help available \n
			:param x: No help available
		"""
		param = Conversions.decimal_value_to_str(x)
		self._core.io.write(f'ANTenna:MODel:ARRay:COSN:X {param}')

	def get_z(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:COSN:Z \n
		Snippet: value: float = driver.antenna.model.array.cosn.get_z() \n
		No command help available \n
			:return: z: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:COSN:Z?')
		return Conversions.str_to_float(response)

	def set_z(self, z: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:COSN:Z \n
		Snippet: driver.antenna.model.array.cosn.set_z(z = 1.0) \n
		No command help available \n
			:param z: No help available
		"""
		param = Conversions.decimal_value_to_str(z)
		self._core.io.write(f'ANTenna:MODel:ARRay:COSN:Z {param}')

	def get_value(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:COSN \n
		Snippet: value: float = driver.antenna.model.array.cosn.get_value() \n
		Sets Cos^N of the Planar Phased Array antenna. \n
			:return: cosn: float Range: 2 to 10
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:COSN?')
		return Conversions.str_to_float(response)

	def set_value(self, cosn: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:COSN \n
		Snippet: driver.antenna.model.array.cosn.set_value(cosn = 1.0) \n
		Sets Cos^N of the Planar Phased Array antenna. \n
			:param cosn: float Range: 2 to 10
		"""
		param = Conversions.decimal_value_to_str(cosn)
		self._core.io.write(f'ANTenna:MODel:ARRay:COSN {param}')
