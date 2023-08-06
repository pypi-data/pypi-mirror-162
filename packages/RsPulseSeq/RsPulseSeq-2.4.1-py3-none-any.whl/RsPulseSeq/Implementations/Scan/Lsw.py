from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Lsw:
	"""Lsw commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lsw", core, parent)

	# noinspection PyTypeChecker
	def get_direction(self) -> enums.LswDirection:
		"""SCPI: SCAN:LSW:DIRection \n
		Snippet: value: enums.LswDirection = driver.scan.lsw.get_direction() \n
		Sets the horizontal or vertical switching direction. \n
			:return: direction: H| V
		"""
		response = self._core.io.query_str('SCAN:LSW:DIRection?')
		return Conversions.str_to_scalar_enum(response, enums.LswDirection)

	def set_direction(self, direction: enums.LswDirection) -> None:
		"""SCPI: SCAN:LSW:DIRection \n
		Snippet: driver.scan.lsw.set_direction(direction = enums.LswDirection.H) \n
		Sets the horizontal or vertical switching direction. \n
			:param direction: H| V
		"""
		param = Conversions.enum_scalar_to_str(direction, enums.LswDirection)
		self._core.io.write(f'SCAN:LSW:DIRection {param}')

	def get_dwell(self) -> float:
		"""SCPI: SCAN:LSW:DWELl \n
		Snippet: value: float = driver.scan.lsw.get_dwell() \n
		Sets the speed with that the antenna switches between the lobes. \n
			:return: dwell: float Range: 1e-06 to 1
		"""
		response = self._core.io.query_str('SCAN:LSW:DWELl?')
		return Conversions.str_to_float(response)

	def set_dwell(self, dwell: float) -> None:
		"""SCPI: SCAN:LSW:DWELl \n
		Snippet: driver.scan.lsw.set_dwell(dwell = 1.0) \n
		Sets the speed with that the antenna switches between the lobes. \n
			:param dwell: float Range: 1e-06 to 1
		"""
		param = Conversions.decimal_value_to_str(dwell)
		self._core.io.write(f'SCAN:LSW:DWELl {param}')

	# noinspection PyTypeChecker
	def get_lobes(self) -> enums.LobesCount:
		"""SCPI: SCAN:LSW:LOBes \n
		Snippet: value: enums.LobesCount = driver.scan.lsw.get_lobes() \n
		Set the number of lobes. \n
			:return: lobes: 2| 4
		"""
		response = self._core.io.query_str('SCAN:LSW:LOBes?')
		return Conversions.str_to_scalar_enum(response, enums.LobesCount)

	def set_lobes(self, lobes: enums.LobesCount) -> None:
		"""SCPI: SCAN:LSW:LOBes \n
		Snippet: driver.scan.lsw.set_lobes(lobes = enums.LobesCount._2) \n
		Set the number of lobes. \n
			:param lobes: 2| 4
		"""
		param = Conversions.enum_scalar_to_str(lobes, enums.LobesCount)
		self._core.io.write(f'SCAN:LSW:LOBes {param}')

	# noinspection PyTypeChecker
	def get_rotation(self) -> enums.Rotation:
		"""SCPI: SCAN:LSW:ROTation \n
		Snippet: value: enums.Rotation = driver.scan.lsw.get_rotation() \n
		Sets the rotation direction of the antenna. \n
			:return: rotation: CW| CCW
		"""
		response = self._core.io.query_str('SCAN:LSW:ROTation?')
		return Conversions.str_to_scalar_enum(response, enums.Rotation)

	def set_rotation(self, rotation: enums.Rotation) -> None:
		"""SCPI: SCAN:LSW:ROTation \n
		Snippet: driver.scan.lsw.set_rotation(rotation = enums.Rotation.CCW) \n
		Sets the rotation direction of the antenna. \n
			:param rotation: CW| CCW
		"""
		param = Conversions.enum_scalar_to_str(rotation, enums.Rotation)
		self._core.io.write(f'SCAN:LSW:ROTation {param}')

	def get_squint(self) -> float:
		"""SCPI: SCAN:LSW:SQUint \n
		Snippet: value: float = driver.scan.lsw.get_squint() \n
		Sets the offset angle of the antenna beam, that means for the conical antenna the parameter sets the radius of the
		scanned circle. \n
			:return: squint: float Range: 0.05 to 15, Unit: degree
		"""
		response = self._core.io.query_str('SCAN:LSW:SQUint?')
		return Conversions.str_to_float(response)

	def set_squint(self, squint: float) -> None:
		"""SCPI: SCAN:LSW:SQUint \n
		Snippet: driver.scan.lsw.set_squint(squint = 1.0) \n
		Sets the offset angle of the antenna beam, that means for the conical antenna the parameter sets the radius of the
		scanned circle. \n
			:param squint: float Range: 0.05 to 15, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(squint)
		self._core.io.write(f'SCAN:LSW:SQUint {param}')
