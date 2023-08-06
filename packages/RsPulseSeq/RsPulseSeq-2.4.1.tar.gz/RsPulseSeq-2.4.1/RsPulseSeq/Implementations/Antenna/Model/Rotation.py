from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Rotation:
	"""Rotation commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rotation", core, parent)

	def get_x(self) -> float:
		"""SCPI: ANTenna:MODel:ROTation:X \n
		Snippet: value: float = driver.antenna.model.rotation.get_x() \n
		Sets the X and Z antenna rotation. \n
			:return: x: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:ROTation:X?')
		return Conversions.str_to_float(response)

	def set_x(self, x: float) -> None:
		"""SCPI: ANTenna:MODel:ROTation:X \n
		Snippet: driver.antenna.model.rotation.set_x(x = 1.0) \n
		Sets the X and Z antenna rotation. \n
			:param x: float Range: -180 to 180, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(x)
		self._core.io.write(f'ANTenna:MODel:ROTation:X {param}')

	def get_z(self) -> float:
		"""SCPI: ANTenna:MODel:ROTation:Z \n
		Snippet: value: float = driver.antenna.model.rotation.get_z() \n
		Sets the X and Z antenna rotation. \n
			:return: z: float Range: -180 to 180, Unit: degree
		"""
		response = self._core.io.query_str('ANTenna:MODel:ROTation:Z?')
		return Conversions.str_to_float(response)

	def set_z(self, z: float) -> None:
		"""SCPI: ANTenna:MODel:ROTation:Z \n
		Snippet: driver.antenna.model.rotation.set_z(z = 1.0) \n
		Sets the X and Z antenna rotation. \n
			:param z: float Range: -180 to 180, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(z)
		self._core.io.write(f'ANTenna:MODel:ROTation:Z {param}')
