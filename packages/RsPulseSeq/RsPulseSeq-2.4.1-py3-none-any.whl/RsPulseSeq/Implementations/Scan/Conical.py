from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Conical:
	"""Conical commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("conical", core, parent)

	def get_rate(self) -> float:
		"""SCPI: SCAN:CONical:RATE \n
		Snippet: value: float = driver.scan.conical.get_rate() \n
		Sets the turning speed. \n
			:return: rate: float Range: 0.01 to 100000, Unit: degree/s
		"""
		response = self._core.io.query_str('SCAN:CONical:RATE?')
		return Conversions.str_to_float(response)

	def set_rate(self, rate: float) -> None:
		"""SCPI: SCAN:CONical:RATE \n
		Snippet: driver.scan.conical.set_rate(rate = 1.0) \n
		Sets the turning speed. \n
			:param rate: float Range: 0.01 to 100000, Unit: degree/s
		"""
		param = Conversions.decimal_value_to_str(rate)
		self._core.io.write(f'SCAN:CONical:RATE {param}')

	# noinspection PyTypeChecker
	def get_rotation(self) -> enums.Rotation:
		"""SCPI: SCAN:CONical:ROTation \n
		Snippet: value: enums.Rotation = driver.scan.conical.get_rotation() \n
		Sets the rotation direction of the antenna. \n
			:return: rotation: CW| CCW
		"""
		response = self._core.io.query_str('SCAN:CONical:ROTation?')
		return Conversions.str_to_scalar_enum(response, enums.Rotation)

	def set_rotation(self, rotation: enums.Rotation) -> None:
		"""SCPI: SCAN:CONical:ROTation \n
		Snippet: driver.scan.conical.set_rotation(rotation = enums.Rotation.CCW) \n
		Sets the rotation direction of the antenna. \n
			:param rotation: CW| CCW
		"""
		param = Conversions.enum_scalar_to_str(rotation, enums.Rotation)
		self._core.io.write(f'SCAN:CONical:ROTation {param}')

	def get_squint(self) -> float:
		"""SCPI: SCAN:CONical:SQUint \n
		Snippet: value: float = driver.scan.conical.get_squint() \n
		Sets the offset angle of the antenna beam, that means for the conical antenna the parameter sets the radius of the
		scanned circle. \n
			:return: squint: float Range: 0.05 to 15, Unit: degree
		"""
		response = self._core.io.query_str('SCAN:CONical:SQUint?')
		return Conversions.str_to_float(response)

	def set_squint(self, squint: float) -> None:
		"""SCPI: SCAN:CONical:SQUint \n
		Snippet: driver.scan.conical.set_squint(squint = 1.0) \n
		Sets the offset angle of the antenna beam, that means for the conical antenna the parameter sets the radius of the
		scanned circle. \n
			:param squint: float Range: 0.05 to 15, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(squint)
		self._core.io.write(f'SCAN:CONical:SQUint {param}')
