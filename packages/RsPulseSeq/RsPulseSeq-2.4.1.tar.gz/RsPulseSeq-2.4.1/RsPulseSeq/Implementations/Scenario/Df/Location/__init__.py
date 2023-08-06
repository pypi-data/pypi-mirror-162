from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Location:
	"""Location commands group definition. 15 total commands, 3 Subgroups, 9 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("location", core, parent)

	@property
	def pstep(self):
		"""pstep commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_pstep'):
			from .Pstep import Pstep
			self._pstep = Pstep(self._core, self._cmd_group)
		return self._pstep

	@property
	def rec(self):
		"""rec commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rec'):
			from .Rec import Rec
			self._rec = Rec(self._core, self._cmd_group)
		return self._rec

	@property
	def waypoint(self):
		"""waypoint commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_waypoint'):
			from .Waypoint import Waypoint
			self._waypoint = Waypoint(self._core, self._cmd_group)
		return self._waypoint

	def get_altitude(self) -> float:
		"""SCPI: SCENario:DF:LOCation:ALTitude \n
		Snippet: value: float = driver.scenario.df.location.get_altitude() \n
		Use for defining the altitude of a fixed emitter (no movement) on a georeferenced map. \n
			:return: altitude: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:ALTitude?')
		return Conversions.str_to_float(response)

	def set_altitude(self, altitude: float) -> None:
		"""SCPI: SCENario:DF:LOCation:ALTitude \n
		Snippet: driver.scenario.df.location.set_altitude(altitude = 1.0) \n
		Use for defining the altitude of a fixed emitter (no movement) on a georeferenced map. \n
			:param altitude: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(altitude)
		self._core.io.write(f'SCENario:DF:LOCation:ALTitude {param}')

	def get_azimuth(self) -> float:
		"""SCPI: SCENario:DF:LOCation:AZIMuth \n
		Snippet: value: float = driver.scenario.df.location.get_azimuth() \n
		Sets the azimuth. \n
			:return: azimuth: float Range: 0 to 360
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:AZIMuth?')
		return Conversions.str_to_float(response)

	def set_azimuth(self, azimuth: float) -> None:
		"""SCPI: SCENario:DF:LOCation:AZIMuth \n
		Snippet: driver.scenario.df.location.set_azimuth(azimuth = 1.0) \n
		Sets the azimuth. \n
			:param azimuth: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(azimuth)
		self._core.io.write(f'SCENario:DF:LOCation:AZIMuth {param}')

	def get_east(self) -> float:
		"""SCPI: SCENario:DF:LOCation:EAST \n
		Snippet: value: float = driver.scenario.df.location.get_east() \n
		Sets the emitter coordinates. \n
			:return: east: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:EAST?')
		return Conversions.str_to_float(response)

	def set_east(self, east: float) -> None:
		"""SCPI: SCENario:DF:LOCation:EAST \n
		Snippet: driver.scenario.df.location.set_east(east = 1.0) \n
		Sets the emitter coordinates. \n
			:param east: float Range: -1e+09 to 1e+09, Unit: m
		"""
		param = Conversions.decimal_value_to_str(east)
		self._core.io.write(f'SCENario:DF:LOCation:EAST {param}')

	def get_elevation(self) -> float:
		"""SCPI: SCENario:DF:LOCation:ELEVation \n
		Snippet: value: float = driver.scenario.df.location.get_elevation() \n
		Sets the elevation. \n
			:return: elevation: float Range: -90 to 90
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:ELEVation?')
		return Conversions.str_to_float(response)

	def set_elevation(self, elevation: float) -> None:
		"""SCPI: SCENario:DF:LOCation:ELEVation \n
		Snippet: driver.scenario.df.location.set_elevation(elevation = 1.0) \n
		Sets the elevation. \n
			:param elevation: float Range: -90 to 90
		"""
		param = Conversions.decimal_value_to_str(elevation)
		self._core.io.write(f'SCENario:DF:LOCation:ELEVation {param}')

	def get_height(self) -> float:
		"""SCPI: SCENario:DF:LOCation:HEIGht \n
		Snippet: value: float = driver.scenario.df.location.get_height() \n
		Sets the height of the antenna. \n
			:return: height: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:HEIGht?')
		return Conversions.str_to_float(response)

	def set_height(self, height: float) -> None:
		"""SCPI: SCENario:DF:LOCation:HEIGht \n
		Snippet: driver.scenario.df.location.set_height(height = 1.0) \n
		Sets the height of the antenna. \n
			:param height: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(height)
		self._core.io.write(f'SCENario:DF:LOCation:HEIGht {param}')

	def get_latitude(self) -> float:
		"""SCPI: SCENario:DF:LOCation:LATitude \n
		Snippet: value: float = driver.scenario.df.location.get_latitude() \n
		Use for defining the position of a fixed emitter (no movement) on a georeferenced map. Positive values represent °East.
		Negative values represent °West. \n
			:return: latitude: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:LATitude?')
		return Conversions.str_to_float(response)

	def set_latitude(self, latitude: float) -> None:
		"""SCPI: SCENario:DF:LOCation:LATitude \n
		Snippet: driver.scenario.df.location.set_latitude(latitude = 1.0) \n
		Use for defining the position of a fixed emitter (no movement) on a georeferenced map. Positive values represent °East.
		Negative values represent °West. \n
			:param latitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(latitude)
		self._core.io.write(f'SCENario:DF:LOCation:LATitude {param}')

	def get_longitude(self) -> float:
		"""SCPI: SCENario:DF:LOCation:LONGitude \n
		Snippet: value: float = driver.scenario.df.location.get_longitude() \n
		Use for defining the position of a fixed emitter (no movement) on a georeferenced map. Positive values represent °East.
		Negative values represent °West. \n
			:return: longitude: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:LONGitude?')
		return Conversions.str_to_float(response)

	def set_longitude(self, longitude: float) -> None:
		"""SCPI: SCENario:DF:LOCation:LONGitude \n
		Snippet: driver.scenario.df.location.set_longitude(longitude = 1.0) \n
		Use for defining the position of a fixed emitter (no movement) on a georeferenced map. Positive values represent °East.
		Negative values represent °West. \n
			:param longitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(longitude)
		self._core.io.write(f'SCENario:DF:LOCation:LONGitude {param}')

	def get_north(self) -> float:
		"""SCPI: SCENario:DF:LOCation:NORTh \n
		Snippet: value: float = driver.scenario.df.location.get_north() \n
		Sets the emitter coordinates. \n
			:return: north: float Range: -1e+09 to 1e+09, Unit: m
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:NORTh?')
		return Conversions.str_to_float(response)

	def set_north(self, north: float) -> None:
		"""SCPI: SCENario:DF:LOCation:NORTh \n
		Snippet: driver.scenario.df.location.set_north(north = 1.0) \n
		Sets the emitter coordinates. \n
			:param north: float Range: -1e+09 to 1e+09, Unit: m
		"""
		param = Conversions.decimal_value_to_str(north)
		self._core.io.write(f'SCENario:DF:LOCation:NORTh {param}')

	# noinspection PyTypeChecker
	def get_pmode(self) -> enums.PmodeLocation:
		"""SCPI: SCENario:DF:LOCation:PMODe \n
		Snippet: value: enums.PmodeLocation = driver.scenario.df.location.get_pmode() \n
		Sets if the emitter is static or moving. \n
			:return: pmode: STATic| STEPs| MOVing
		"""
		response = self._core.io.query_str('SCENario:DF:LOCation:PMODe?')
		return Conversions.str_to_scalar_enum(response, enums.PmodeLocation)

	def set_pmode(self, pmode: enums.PmodeLocation) -> None:
		"""SCPI: SCENario:DF:LOCation:PMODe \n
		Snippet: driver.scenario.df.location.set_pmode(pmode = enums.PmodeLocation.MOVing) \n
		Sets if the emitter is static or moving. \n
			:param pmode: STATic| STEPs| MOVing
		"""
		param = Conversions.enum_scalar_to_str(pmode, enums.PmodeLocation)
		self._core.io.write(f'SCENario:DF:LOCation:PMODe {param}')

	def clone(self) -> 'Location':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Location(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
