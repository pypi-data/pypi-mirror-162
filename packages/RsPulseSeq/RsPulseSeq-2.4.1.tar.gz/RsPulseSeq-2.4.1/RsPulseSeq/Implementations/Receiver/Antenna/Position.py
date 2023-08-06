from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Position:
	"""Position commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("position", core, parent)

	def get_angle(self) -> float:
		"""SCPI: RECeiver:ANTenna:POSition:ANGLe \n
		Snippet: value: float = driver.receiver.antenna.position.get_angle() \n
		Sets the antenna element position as an angle offset from the X-axis. \n
			:return: angle: float Range: 0 to 360
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:POSition:ANGLe?')
		return Conversions.str_to_float(response)

	def set_angle(self, angle: float) -> None:
		"""SCPI: RECeiver:ANTenna:POSition:ANGLe \n
		Snippet: driver.receiver.antenna.position.set_angle(angle = 1.0) \n
		Sets the antenna element position as an angle offset from the X-axis. \n
			:param angle: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(angle)
		self._core.io.write(f'RECeiver:ANTenna:POSition:ANGLe {param}')

	def get_height(self) -> float:
		"""SCPI: RECeiver:ANTenna:POSition:HEIGht \n
		Snippet: value: float = driver.receiver.antenna.position.get_height() \n
		Sets the antenna element height, relative to the receiver origin. \n
			:return: height: float Range: -1e+06 to 1e+06
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:POSition:HEIGht?')
		return Conversions.str_to_float(response)

	def set_height(self, height: float) -> None:
		"""SCPI: RECeiver:ANTenna:POSition:HEIGht \n
		Snippet: driver.receiver.antenna.position.set_height(height = 1.0) \n
		Sets the antenna element height, relative to the receiver origin. \n
			:param height: float Range: -1e+06 to 1e+06
		"""
		param = Conversions.decimal_value_to_str(height)
		self._core.io.write(f'RECeiver:ANTenna:POSition:HEIGht {param}')

	def get_radius(self) -> float:
		"""SCPI: RECeiver:ANTenna:POSition:RADius \n
		Snippet: value: float = driver.receiver.antenna.position.get_radius() \n
		Sets the distance from the antenna element to the receiver origin. \n
			:return: radius: float Range: 0 to 1e+06
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:POSition:RADius?')
		return Conversions.str_to_float(response)

	def set_radius(self, radius: float) -> None:
		"""SCPI: RECeiver:ANTenna:POSition:RADius \n
		Snippet: driver.receiver.antenna.position.set_radius(radius = 1.0) \n
		Sets the distance from the antenna element to the receiver origin. \n
			:param radius: float Range: 0 to 1e+06
		"""
		param = Conversions.decimal_value_to_str(radius)
		self._core.io.write(f'RECeiver:ANTenna:POSition:RADius {param}')

	def get_x(self) -> float:
		"""SCPI: RECeiver:ANTenna:POSition:X \n
		Snippet: value: float = driver.receiver.antenna.position.get_x() \n
		Sets the antenna element position as X and Y values, relative to the receiver origin. \n
			:return: x: No help available
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:POSition:X?')
		return Conversions.str_to_float(response)

	def set_x(self, x: float) -> None:
		"""SCPI: RECeiver:ANTenna:POSition:X \n
		Snippet: driver.receiver.antenna.position.set_x(x = 1.0) \n
		Sets the antenna element position as X and Y values, relative to the receiver origin. \n
			:param x: float Range: -1e+06 to 1e+06
		"""
		param = Conversions.decimal_value_to_str(x)
		self._core.io.write(f'RECeiver:ANTenna:POSition:X {param}')

	def get_y(self) -> float:
		"""SCPI: RECeiver:ANTenna:POSition:Y \n
		Snippet: value: float = driver.receiver.antenna.position.get_y() \n
		Sets the antenna element position as X and Y values, relative to the receiver origin. \n
			:return: y: float Range: -1e+06 to 1e+06
		"""
		response = self._core.io.query_str('RECeiver:ANTenna:POSition:Y?')
		return Conversions.str_to_float(response)

	def set_y(self, y: float) -> None:
		"""SCPI: RECeiver:ANTenna:POSition:Y \n
		Snippet: driver.receiver.antenna.position.set_y(y = 1.0) \n
		Sets the antenna element position as X and Y values, relative to the receiver origin. \n
			:param y: float Range: -1e+06 to 1e+06
		"""
		param = Conversions.decimal_value_to_str(y)
		self._core.io.write(f'RECeiver:ANTenna:POSition:Y {param}')
