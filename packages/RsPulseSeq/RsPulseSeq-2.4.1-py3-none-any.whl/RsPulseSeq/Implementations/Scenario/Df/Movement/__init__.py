from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Movement:
	"""Movement commands group definition. 26 total commands, 2 Subgroups, 23 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("movement", core, parent)

	@property
	def importPy(self):
		"""importPy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_importPy'):
			from .ImportPy import ImportPy
			self._importPy = ImportPy(self._core, self._cmd_group)
		return self._importPy

	@property
	def vfile(self):
		"""vfile commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_vfile'):
			from .Vfile import Vfile
			self._vfile = Vfile(self._core, self._cmd_group)
		return self._vfile

	def get_acceleration(self) -> float:
		"""SCPI: SCENario:DF:MOVement:ACCeleration \n
		Snippet: value: float = driver.scenario.df.movement.get_acceleration() \n
		Sets the acceleration of the moving emitter. \n
			:return: acceleration: float Range: -100 to 100
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:ACCeleration?')
		return Conversions.str_to_float(response)

	def set_acceleration(self, acceleration: float) -> None:
		"""SCPI: SCENario:DF:MOVement:ACCeleration \n
		Snippet: driver.scenario.df.movement.set_acceleration(acceleration = 1.0) \n
		Sets the acceleration of the moving emitter. \n
			:param acceleration: float Range: -100 to 100
		"""
		param = Conversions.decimal_value_to_str(acceleration)
		self._core.io.write(f'SCENario:DF:MOVement:ACCeleration {param}')

	def get_altitude(self) -> float:
		"""SCPI: SCENario:DF:MOVement:ALTitude \n
		Snippet: value: float = driver.scenario.df.movement.get_altitude() \n
		Use for defining the altitude of a moving emitter (line trajectory) on a georeferenced map. Use to define the altitude of
		the end-points of the line. \n
			:return: altitude: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:ALTitude?')
		return Conversions.str_to_float(response)

	def set_altitude(self, altitude: float) -> None:
		"""SCPI: SCENario:DF:MOVement:ALTitude \n
		Snippet: driver.scenario.df.movement.set_altitude(altitude = 1.0) \n
		Use for defining the altitude of a moving emitter (line trajectory) on a georeferenced map. Use to define the altitude of
		the end-points of the line. \n
			:param altitude: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(altitude)
		self._core.io.write(f'SCENario:DF:MOVement:ALTitude {param}')

	def get_angle(self) -> float:
		"""SCPI: SCENario:DF:MOVement:ANGLe \n
		Snippet: value: float = driver.scenario.df.movement.get_angle() \n
		Sets the arc angle and thus defines the arc length. \n
			:return: angle: float Range: -360 to 360
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:ANGLe?')
		return Conversions.str_to_float(response)

	def set_angle(self, angle: float) -> None:
		"""SCPI: SCENario:DF:MOVement:ANGLe \n
		Snippet: driver.scenario.df.movement.set_angle(angle = 1.0) \n
		Sets the arc angle and thus defines the arc length. \n
			:param angle: float Range: -360 to 360
		"""
		param = Conversions.decimal_value_to_str(angle)
		self._core.io.write(f'SCENario:DF:MOVement:ANGLe {param}')

	# noinspection PyTypeChecker
	def get_attitude(self) -> enums.Attitude:
		"""SCPI: SCENario:DF:MOVement:ATTitude \n
		Snippet: value: enums.Attitude = driver.scenario.df.movement.get_attitude() \n
		Defines how the attitude information is defined. \n
			:return: attitude: WAYPoint| MOTion| CONStant WAYPoint The attitude parameters are extracted from the selected waypoint file. MOTion Enables a constant rate of change of the roll. See method RsPulseSeq.Scenario.Localized.Movement.roll Constant The attitude is constant values.
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:ATTitude?')
		return Conversions.str_to_scalar_enum(response, enums.Attitude)

	def set_attitude(self, attitude: enums.Attitude) -> None:
		"""SCPI: SCENario:DF:MOVement:ATTitude \n
		Snippet: driver.scenario.df.movement.set_attitude(attitude = enums.Attitude.CONStant) \n
		Defines how the attitude information is defined. \n
			:param attitude: WAYPoint| MOTion| CONStant WAYPoint The attitude parameters are extracted from the selected waypoint file. MOTion Enables a constant rate of change of the roll. See method RsPulseSeq.Scenario.Localized.Movement.roll Constant The attitude is constant values.
		"""
		param = Conversions.enum_scalar_to_str(attitude, enums.Attitude)
		self._core.io.write(f'SCENario:DF:MOVement:ATTitude {param}')

	def get_clatitude(self) -> float:
		"""SCPI: SCENario:DF:MOVement:CLATitude \n
		Snippet: value: float = driver.scenario.df.movement.get_clatitude() \n
		Use for defining the movement of an emitter (arc trajectory) on a georeferenced map. Use to define the center-point of
		the arc. Positive values represent °East. Negative values represent °West. \n
			:return: clatitude: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:CLATitude?')
		return Conversions.str_to_float(response)

	def set_clatitude(self, clatitude: float) -> None:
		"""SCPI: SCENario:DF:MOVement:CLATitude \n
		Snippet: driver.scenario.df.movement.set_clatitude(clatitude = 1.0) \n
		Use for defining the movement of an emitter (arc trajectory) on a georeferenced map. Use to define the center-point of
		the arc. Positive values represent °East. Negative values represent °West. \n
			:param clatitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(clatitude)
		self._core.io.write(f'SCENario:DF:MOVement:CLATitude {param}')

	def clear(self) -> None:
		"""SCPI: SCENario:DF:MOVement:CLEar \n
		Snippet: driver.scenario.df.movement.clear() \n
		Discards the waypoint and vehicle description file. \n
		"""
		self._core.io.write(f'SCENario:DF:MOVement:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:DF:MOVement:CLEar \n
		Snippet: driver.scenario.df.movement.clear_with_opc() \n
		Discards the waypoint and vehicle description file. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:DF:MOVement:CLEar', opc_timeout_ms)

	def get_clongitude(self) -> float:
		"""SCPI: SCENario:DF:MOVement:CLONgitude \n
		Snippet: value: float = driver.scenario.df.movement.get_clongitude() \n
		Use for defining the movement of an emitter (arc trajectory) on a georeferenced map. Use to define the center-point of
		the arc. Positive values represent °East. Negative values represent °West. \n
			:return: clongitude: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:CLONgitude?')
		return Conversions.str_to_float(response)

	def set_clongitude(self, clongitude: float) -> None:
		"""SCPI: SCENario:DF:MOVement:CLONgitude \n
		Snippet: driver.scenario.df.movement.set_clongitude(clongitude = 1.0) \n
		Use for defining the movement of an emitter (arc trajectory) on a georeferenced map. Use to define the center-point of
		the arc. Positive values represent °East. Negative values represent °West. \n
			:param clongitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(clongitude)
		self._core.io.write(f'SCENario:DF:MOVement:CLONgitude {param}')

	def get_east(self) -> float:
		"""SCPI: SCENario:DF:MOVement:EAST \n
		Snippet: value: float = driver.scenario.df.movement.get_east() \n
		Sets the East/North coordinates of the emitter at the end of the movement. \n
			:return: east: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:EAST?')
		return Conversions.str_to_float(response)

	def set_east(self, east: float) -> None:
		"""SCPI: SCENario:DF:MOVement:EAST \n
		Snippet: driver.scenario.df.movement.set_east(east = 1.0) \n
		Sets the East/North coordinates of the emitter at the end of the movement. \n
			:param east: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(east)
		self._core.io.write(f'SCENario:DF:MOVement:EAST {param}')

	def get_height(self) -> float:
		"""SCPI: SCENario:DF:MOVement:HEIGht \n
		Snippet: value: float = driver.scenario.df.movement.get_height() \n
		Sets the height of the emitter at the end of the movement. \n
			:return: height: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:HEIGht?')
		return Conversions.str_to_float(response)

	def set_height(self, height: float) -> None:
		"""SCPI: SCENario:DF:MOVement:HEIGht \n
		Snippet: driver.scenario.df.movement.set_height(height = 1.0) \n
		Sets the height of the emitter at the end of the movement. \n
			:param height: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(height)
		self._core.io.write(f'SCENario:DF:MOVement:HEIGht {param}')

	def get_latitude(self) -> float:
		"""SCPI: SCENario:DF:MOVement:LATitude \n
		Snippet: value: float = driver.scenario.df.movement.get_latitude() \n
		Use for defining the movement of an emitter (line trajectory) on a georeferenced map. Use to define the end-points of the
		line. Positive values represent °East. Negative values represent °West. \n
			:return: latitude: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:LATitude?')
		return Conversions.str_to_float(response)

	def set_latitude(self, latitude: float) -> None:
		"""SCPI: SCENario:DF:MOVement:LATitude \n
		Snippet: driver.scenario.df.movement.set_latitude(latitude = 1.0) \n
		Use for defining the movement of an emitter (line trajectory) on a georeferenced map. Use to define the end-points of the
		line. Positive values represent °East. Negative values represent °West. \n
			:param latitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(latitude)
		self._core.io.write(f'SCENario:DF:MOVement:LATitude {param}')

	def get_longitude(self) -> float:
		"""SCPI: SCENario:DF:MOVement:LONGitude \n
		Snippet: value: float = driver.scenario.df.movement.get_longitude() \n
		Use for defining the movement of an emitter (line trajectory) on a georeferenced map. Use to define the end-points of the
		line. Positive values represent °East. Negative values represent °West. \n
			:return: longitude: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:LONGitude?')
		return Conversions.str_to_float(response)

	def set_longitude(self, longitude: float) -> None:
		"""SCPI: SCENario:DF:MOVement:LONGitude \n
		Snippet: driver.scenario.df.movement.set_longitude(longitude = 1.0) \n
		Use for defining the movement of an emitter (line trajectory) on a georeferenced map. Use to define the end-points of the
		line. Positive values represent °East. Negative values represent °West. \n
			:param longitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(longitude)
		self._core.io.write(f'SCENario:DF:MOVement:LONGitude {param}')

	def get_north(self) -> float:
		"""SCPI: SCENario:DF:MOVement:NORTh \n
		Snippet: value: float = driver.scenario.df.movement.get_north() \n
		Sets the East/North coordinates of the emitter at the end of the movement. \n
			:return: north: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:NORTh?')
		return Conversions.str_to_float(response)

	def set_north(self, north: float) -> None:
		"""SCPI: SCENario:DF:MOVement:NORTh \n
		Snippet: driver.scenario.df.movement.set_north(north = 1.0) \n
		Sets the East/North coordinates of the emitter at the end of the movement. \n
			:param north: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(north)
		self._core.io.write(f'SCENario:DF:MOVement:NORTh {param}')

	def get_pitch(self) -> float:
		"""SCPI: SCENario:DF:MOVement:PITCh \n
		Snippet: value: float = driver.scenario.df.movement.get_pitch() \n
		Sets the angles of rotation in the corresponding direction. \n
			:return: pitch: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:PITCh?')
		return Conversions.str_to_float(response)

	def set_pitch(self, pitch: float) -> None:
		"""SCPI: SCENario:DF:MOVement:PITCh \n
		Snippet: driver.scenario.df.movement.set_pitch(pitch = 1.0) \n
		Sets the angles of rotation in the corresponding direction. \n
			:param pitch: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(pitch)
		self._core.io.write(f'SCENario:DF:MOVement:PITCh {param}')

	# noinspection PyTypeChecker
	def get_rframe(self) -> enums.MovementRframe:
		"""SCPI: SCENario:DF:MOVement:RFRame \n
		Snippet: value: enums.MovementRframe = driver.scenario.df.movement.get_rframe() \n
		Select the reference frame used to define the emitters coordinates. \n
			:return: rframe: WGS| PZ
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:RFRame?')
		return Conversions.str_to_scalar_enum(response, enums.MovementRframe)

	def set_rframe(self, rframe: enums.MovementRframe) -> None:
		"""SCPI: SCENario:DF:MOVement:RFRame \n
		Snippet: driver.scenario.df.movement.set_rframe(rframe = enums.MovementRframe.PZ) \n
		Select the reference frame used to define the emitters coordinates. \n
			:param rframe: WGS| PZ
		"""
		param = Conversions.enum_scalar_to_str(rframe, enums.MovementRframe)
		self._core.io.write(f'SCENario:DF:MOVement:RFRame {param}')

	# noinspection PyTypeChecker
	def get_rmode(self) -> enums.MovementRmode:
		"""SCPI: SCENario:DF:MOVement:RMODe \n
		Snippet: value: enums.MovementRmode = driver.scenario.df.movement.get_rmode() \n
		Defines the behavior of the moving object when the end of the trajectory is reached. \n
			:return: rmode: CYCLic| ROUNdtrip| ONEWay
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:RMODe?')
		return Conversions.str_to_scalar_enum(response, enums.MovementRmode)

	def set_rmode(self, rmode: enums.MovementRmode) -> None:
		"""SCPI: SCENario:DF:MOVement:RMODe \n
		Snippet: driver.scenario.df.movement.set_rmode(rmode = enums.MovementRmode.CYCLic) \n
		Defines the behavior of the moving object when the end of the trajectory is reached. \n
			:param rmode: CYCLic| ROUNdtrip| ONEWay
		"""
		param = Conversions.enum_scalar_to_str(rmode, enums.MovementRmode)
		self._core.io.write(f'SCENario:DF:MOVement:RMODe {param}')

	def get_roll(self) -> float:
		"""SCPI: SCENario:DF:MOVement:ROLL \n
		Snippet: value: float = driver.scenario.df.movement.get_roll() \n
		Sets the angles of rotation in the corresponding direction. \n
			:return: roll: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:ROLL?')
		return Conversions.str_to_float(response)

	def set_roll(self, roll: float) -> None:
		"""SCPI: SCENario:DF:MOVement:ROLL \n
		Snippet: driver.scenario.df.movement.set_roll(roll = 1.0) \n
		Sets the angles of rotation in the corresponding direction. \n
			:param roll: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(roll)
		self._core.io.write(f'SCENario:DF:MOVement:ROLL {param}')

	def get_smoothening(self) -> bool:
		"""SCPI: SCENario:DF:MOVement:SMOothening \n
		Snippet: value: bool = driver.scenario.df.movement.get_smoothening() \n
		If a vehicle description file is loaded, activates smoothening. See method RsPulseSeq.Scenario.Localized.Movement.Vfile.
		value. \n
			:return: smoothening: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:SMOothening?')
		return Conversions.str_to_bool(response)

	def set_smoothening(self, smoothening: bool) -> None:
		"""SCPI: SCENario:DF:MOVement:SMOothening \n
		Snippet: driver.scenario.df.movement.set_smoothening(smoothening = False) \n
		If a vehicle description file is loaded, activates smoothening. See method RsPulseSeq.Scenario.Localized.Movement.Vfile.
		value. \n
			:param smoothening: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(smoothening)
		self._core.io.write(f'SCENario:DF:MOVement:SMOothening {param}')

	def get_speed(self) -> float:
		"""SCPI: SCENario:DF:MOVement:SPEed \n
		Snippet: value: float = driver.scenario.df.movement.get_speed() \n
		Sets the speed of the moving emitter. \n
			:return: speed: float Range: 0 to 5999
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:SPEed?')
		return Conversions.str_to_float(response)

	def set_speed(self, speed: float) -> None:
		"""SCPI: SCENario:DF:MOVement:SPEed \n
		Snippet: driver.scenario.df.movement.set_speed(speed = 1.0) \n
		Sets the speed of the moving emitter. \n
			:param speed: float Range: 0 to 5999
		"""
		param = Conversions.decimal_value_to_str(speed)
		self._core.io.write(f'SCENario:DF:MOVement:SPEed {param}')

	def get_spinning(self) -> float:
		"""SCPI: SCENario:DF:MOVement:SPINning \n
		Snippet: value: float = driver.scenario.df.movement.get_spinning() \n
		No command help available \n
			:return: spinning: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:SPINning?')
		return Conversions.str_to_float(response)

	def set_spinning(self, spinning: float) -> None:
		"""SCPI: SCENario:DF:MOVement:SPINning \n
		Snippet: driver.scenario.df.movement.set_spinning(spinning = 1.0) \n
		No command help available \n
			:param spinning: No help available
		"""
		param = Conversions.decimal_value_to_str(spinning)
		self._core.io.write(f'SCENario:DF:MOVement:SPINning {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.MovementType:
		"""SCPI: SCENario:DF:MOVement:TYPE \n
		Snippet: value: enums.MovementType = driver.scenario.df.movement.get_type_py() \n
		Defines the trajectory shape. \n
			:return: type_py: LINE| ARC| WAYPoint| TRACe
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.MovementType)

	def set_type_py(self, type_py: enums.MovementType) -> None:
		"""SCPI: SCENario:DF:MOVement:TYPE \n
		Snippet: driver.scenario.df.movement.set_type_py(type_py = enums.MovementType.ARC) \n
		Defines the trajectory shape. \n
			:param type_py: LINE| ARC| WAYPoint| TRACe
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.MovementType)
		self._core.io.write(f'SCENario:DF:MOVement:TYPE {param}')

	# noinspection PyTypeChecker
	def get_vehicle(self) -> enums.VehicleMovement:
		"""SCPI: SCENario:DF:MOVement:VEHicle \n
		Snippet: value: enums.VehicleMovement = driver.scenario.df.movement.get_vehicle() \n
		Assigns the selected icon. \n
			:return: vehicle: LVEHicle| SHIP| AIRPlane| STATionary| DEFault| CAR
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:VEHicle?')
		return Conversions.str_to_scalar_enum(response, enums.VehicleMovement)

	def set_vehicle(self, vehicle: enums.VehicleMovement) -> None:
		"""SCPI: SCENario:DF:MOVement:VEHicle \n
		Snippet: driver.scenario.df.movement.set_vehicle(vehicle = enums.VehicleMovement.AIRPlane) \n
		Assigns the selected icon. \n
			:param vehicle: LVEHicle| SHIP| AIRPlane| STATionary| DEFault| CAR
		"""
		param = Conversions.enum_scalar_to_str(vehicle, enums.VehicleMovement)
		self._core.io.write(f'SCENario:DF:MOVement:VEHicle {param}')

	def get_waypoint(self) -> str:
		"""SCPI: SCENario:DF:MOVement:WAYPoint \n
		Snippet: value: str = driver.scenario.df.movement.get_waypoint() \n
		Loads the selected waypoint file. To import and apply the files, send the command method RsPulseSeq.Scenario.Localized.
		Movement.ImportPy.set. \n
			:return: waypoint: string Filename or complete file path, incl. file extension. Waypoint files must have the extension *.txt, *.kml or *.xtd. Example files are provided with the software. For description, see 'Movement files'.
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:WAYPoint?')
		return trim_str_response(response)

	def set_waypoint(self, waypoint: str) -> None:
		"""SCPI: SCENario:DF:MOVement:WAYPoint \n
		Snippet: driver.scenario.df.movement.set_waypoint(waypoint = '1') \n
		Loads the selected waypoint file. To import and apply the files, send the command method RsPulseSeq.Scenario.Localized.
		Movement.ImportPy.set. \n
			:param waypoint: string Filename or complete file path, incl. file extension. Waypoint files must have the extension *.txt, *.kml or *.xtd. Example files are provided with the software. For description, see 'Movement files'.
		"""
		param = Conversions.value_to_quoted_str(waypoint)
		self._core.io.write(f'SCENario:DF:MOVement:WAYPoint {param}')

	def get_yaw(self) -> float:
		"""SCPI: SCENario:DF:MOVement:YAW \n
		Snippet: value: float = driver.scenario.df.movement.get_yaw() \n
		Sets the angles of rotation in the corresponding direction. \n
			:return: yaw: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:MOVement:YAW?')
		return Conversions.str_to_float(response)

	def set_yaw(self, yaw: float) -> None:
		"""SCPI: SCENario:DF:MOVement:YAW \n
		Snippet: driver.scenario.df.movement.set_yaw(yaw = 1.0) \n
		Sets the angles of rotation in the corresponding direction. \n
			:param yaw: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(yaw)
		self._core.io.write(f'SCENario:DF:MOVement:YAW {param}')

	def clone(self) -> 'Movement':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Movement(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
