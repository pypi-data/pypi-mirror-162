from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Sin:
	"""Sin commands group definition. 6 total commands, 0 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sin", core, parent)

	def get_height(self) -> float:
		"""SCPI: SCAN:SIN:HEIGht \n
		Snippet: value: float = driver.scan.sin.get_height() \n
		Sets the amplitude of the sine wave. \n
			:return: height: float Range: 1 to 90
		"""
		response = self._core.io.query_str('SCAN:SIN:HEIGht?')
		return Conversions.str_to_float(response)

	def set_height(self, height: float) -> None:
		"""SCPI: SCAN:SIN:HEIGht \n
		Snippet: driver.scan.sin.set_height(height = 1.0) \n
		Sets the amplitude of the sine wave. \n
			:param height: float Range: 1 to 90
		"""
		param = Conversions.decimal_value_to_str(height)
		self._core.io.write(f'SCAN:SIN:HEIGht {param}')

	def get_inversion(self) -> bool:
		"""SCPI: SCAN:SIN:INVersion \n
		Snippet: value: bool = driver.scan.sin.get_inversion() \n
		Sets whether the upper or the down (mirrored) sine wave is used first. \n
			:return: inversion: ON| OFF| 1| 0 OFF Upper sine first ON Down sine first
		"""
		response = self._core.io.query_str('SCAN:SIN:INVersion?')
		return Conversions.str_to_bool(response)

	def set_inversion(self, inversion: bool) -> None:
		"""SCPI: SCAN:SIN:INVersion \n
		Snippet: driver.scan.sin.set_inversion(inversion = False) \n
		Sets whether the upper or the down (mirrored) sine wave is used first. \n
			:param inversion: ON| OFF| 1| 0 OFF Upper sine first ON Down sine first
		"""
		param = Conversions.bool_to_str(inversion)
		self._core.io.write(f'SCAN:SIN:INVersion {param}')

	def get_rate(self) -> float:
		"""SCPI: SCAN:SIN:RATE \n
		Snippet: value: float = driver.scan.sin.get_rate() \n
		Sets the turning speed. \n
			:return: rate: float Range: 0.01 to 100000, Unit: degree/s
		"""
		response = self._core.io.query_str('SCAN:SIN:RATE?')
		return Conversions.str_to_float(response)

	def set_rate(self, rate: float) -> None:
		"""SCPI: SCAN:SIN:RATE \n
		Snippet: driver.scan.sin.set_rate(rate = 1.0) \n
		Sets the turning speed. \n
			:param rate: float Range: 0.01 to 100000, Unit: degree/s
		"""
		param = Conversions.decimal_value_to_str(rate)
		self._core.io.write(f'SCAN:SIN:RATE {param}')

	# noinspection PyTypeChecker
	def get_rotation(self) -> enums.Rotation:
		"""SCPI: SCAN:SIN:ROTation \n
		Snippet: value: enums.Rotation = driver.scan.sin.get_rotation() \n
		Sets the rotation direction of the antenna. \n
			:return: rotation: CW| CCW
		"""
		response = self._core.io.query_str('SCAN:SIN:ROTation?')
		return Conversions.str_to_scalar_enum(response, enums.Rotation)

	def set_rotation(self, rotation: enums.Rotation) -> None:
		"""SCPI: SCAN:SIN:ROTation \n
		Snippet: driver.scan.sin.set_rotation(rotation = enums.Rotation.CCW) \n
		Sets the rotation direction of the antenna. \n
			:param rotation: CW| CCW
		"""
		param = Conversions.enum_scalar_to_str(rotation, enums.Rotation)
		self._core.io.write(f'SCAN:SIN:ROTation {param}')

	def get_uni_direction(self) -> bool:
		"""SCPI: SCAN:SIN:UNIDirection \n
		Snippet: value: bool = driver.scan.sin.get_uni_direction() \n
		Enables a unidirectional scan mode. \n
			:return: uni_direction: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:SIN:UNIDirection?')
		return Conversions.str_to_bool(response)

	def set_uni_direction(self, uni_direction: bool) -> None:
		"""SCPI: SCAN:SIN:UNIDirection \n
		Snippet: driver.scan.sin.set_uni_direction(uni_direction = False) \n
		Enables a unidirectional scan mode. \n
			:param uni_direction: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(uni_direction)
		self._core.io.write(f'SCAN:SIN:UNIDirection {param}')

	def get_width(self) -> float:
		"""SCPI: SCAN:SIN:WIDTh \n
		Snippet: value: float = driver.scan.sin.get_width() \n
		Sets the angle on the XY plane between the origin and the end of the scan. \n
			:return: width: float Range: 1 to 180
		"""
		response = self._core.io.query_str('SCAN:SIN:WIDTh?')
		return Conversions.str_to_float(response)

	def set_width(self, width: float) -> None:
		"""SCPI: SCAN:SIN:WIDTh \n
		Snippet: driver.scan.sin.set_width(width = 1.0) \n
		Sets the angle on the XY plane between the origin and the end of the scan. \n
			:param width: float Range: 1 to 180
		"""
		param = Conversions.decimal_value_to_str(width)
		self._core.io.write(f'SCAN:SIN:WIDTh {param}')
