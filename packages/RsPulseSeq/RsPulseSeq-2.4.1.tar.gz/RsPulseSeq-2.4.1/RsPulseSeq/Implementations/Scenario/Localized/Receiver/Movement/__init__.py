from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Movement:
	"""Movement commands group definition. 23 total commands, 4 Subgroups, 17 group commands"""

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
	def pstep(self):
		"""pstep commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pstep'):
			from .Pstep import Pstep
			self._pstep = Pstep(self._core, self._cmd_group)
		return self._pstep

	@property
	def vfile(self):
		"""vfile commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_vfile'):
			from .Vfile import Vfile
			self._vfile = Vfile(self._core, self._cmd_group)
		return self._vfile

	@property
	def waypoint(self):
		"""waypoint commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_waypoint'):
			from .Waypoint import Waypoint
			self._waypoint = Waypoint(self._core, self._cmd_group)
		return self._waypoint

	def get_acceleration(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:ACCeleration \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_acceleration() \n
		Sets the acceleration of the moving emitter. \n
			:return: acceleration: float Range: -100 to 100
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:ACCeleration?')
		return Conversions.str_to_float(response)

	def set_acceleration(self, acceleration: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:ACCeleration \n
		Snippet: driver.scenario.localized.receiver.movement.set_acceleration(acceleration = 1.0) \n
		Sets the acceleration of the moving emitter. \n
			:param acceleration: float Range: -100 to 100
		"""
		param = Conversions.decimal_value_to_str(acceleration)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:ACCeleration {param}')

	def get_angle(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:ANGLe \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_angle() \n
		Sets the arc angle and thus defines the arc length. \n
			:return: angle: float Range: -360 to 360
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:ANGLe?')
		return Conversions.str_to_float(response)

	def set_angle(self, angle: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:ANGLe \n
		Snippet: driver.scenario.localized.receiver.movement.set_angle(angle = 1.0) \n
		Sets the arc angle and thus defines the arc length. \n
			:param angle: float Range: -360 to 360
		"""
		param = Conversions.decimal_value_to_str(angle)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:ANGLe {param}')

	# noinspection PyTypeChecker
	def get_attitude(self) -> enums.Attitude:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:ATTitude \n
		Snippet: value: enums.Attitude = driver.scenario.localized.receiver.movement.get_attitude() \n
		Defines how the attitude information is defined. \n
			:return: attitude: WAYPoint| MOTion| CONStant WAYPoint The attitude parameters are extracted from the selected waypoint file. MOTion Enables a constant rate of change of the roll. See method RsPulseSeq.Scenario.Localized.Movement.roll Constant The attitude is constant values.
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:ATTitude?')
		return Conversions.str_to_scalar_enum(response, enums.Attitude)

	def set_attitude(self, attitude: enums.Attitude) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:ATTitude \n
		Snippet: driver.scenario.localized.receiver.movement.set_attitude(attitude = enums.Attitude.CONStant) \n
		Defines how the attitude information is defined. \n
			:param attitude: WAYPoint| MOTion| CONStant WAYPoint The attitude parameters are extracted from the selected waypoint file. MOTion Enables a constant rate of change of the roll. See method RsPulseSeq.Scenario.Localized.Movement.roll Constant The attitude is constant values.
		"""
		param = Conversions.enum_scalar_to_str(attitude, enums.Attitude)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:ATTitude {param}')

	def clear(self) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:CLEar \n
		Snippet: driver.scenario.localized.receiver.movement.clear() \n
		Discards the waypoint and vehicle description file. \n
		"""
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:CLEar \n
		Snippet: driver.scenario.localized.receiver.movement.clear_with_opc() \n
		Discards the waypoint and vehicle description file. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:LOCalized:RECeiver:MOVement:CLEar', opc_timeout_ms)

	def get_east(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:EAST \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_east() \n
		Sets the East/North coordinates of the emitter at the end of the movement. \n
			:return: east: No help available
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:EAST?')
		return Conversions.str_to_float(response)

	def set_east(self, east: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:EAST \n
		Snippet: driver.scenario.localized.receiver.movement.set_east(east = 1.0) \n
		Sets the East/North coordinates of the emitter at the end of the movement. \n
			:param east: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(east)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:EAST {param}')

	def get_height(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:HEIGht \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_height() \n
		Sets the height of the emitter at the end of the movement. \n
			:return: height: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:HEIGht?')
		return Conversions.str_to_float(response)

	def set_height(self, height: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:HEIGht \n
		Snippet: driver.scenario.localized.receiver.movement.set_height(height = 1.0) \n
		Sets the height of the emitter at the end of the movement. \n
			:param height: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(height)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:HEIGht {param}')

	def get_north(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:NORTh \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_north() \n
		Sets the East/North coordinates of the emitter at the end of the movement. \n
			:return: north: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:NORTh?')
		return Conversions.str_to_float(response)

	def set_north(self, north: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:NORTh \n
		Snippet: driver.scenario.localized.receiver.movement.set_north(north = 1.0) \n
		Sets the East/North coordinates of the emitter at the end of the movement. \n
			:param north: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(north)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:NORTh {param}')

	def get_pitch(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:PITCh \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_pitch() \n
		Sets the angles of rotation in the corresponding direction. \n
			:return: pitch: No help available
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:PITCh?')
		return Conversions.str_to_float(response)

	def set_pitch(self, pitch: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:PITCh \n
		Snippet: driver.scenario.localized.receiver.movement.set_pitch(pitch = 1.0) \n
		Sets the angles of rotation in the corresponding direction. \n
			:param pitch: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(pitch)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:PITCh {param}')

	# noinspection PyTypeChecker
	def get_rframe(self) -> enums.MovementRframe:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:RFRame \n
		Snippet: value: enums.MovementRframe = driver.scenario.localized.receiver.movement.get_rframe() \n
		Select the reference frame used to define the emitters coordinates. \n
			:return: rframe: WGS| PZ
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:RFRame?')
		return Conversions.str_to_scalar_enum(response, enums.MovementRframe)

	def set_rframe(self, rframe: enums.MovementRframe) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:RFRame \n
		Snippet: driver.scenario.localized.receiver.movement.set_rframe(rframe = enums.MovementRframe.PZ) \n
		Select the reference frame used to define the emitters coordinates. \n
			:param rframe: WGS| PZ
		"""
		param = Conversions.enum_scalar_to_str(rframe, enums.MovementRframe)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:RFRame {param}')

	# noinspection PyTypeChecker
	def get_rmode(self) -> enums.MovementRmode:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:RMODe \n
		Snippet: value: enums.MovementRmode = driver.scenario.localized.receiver.movement.get_rmode() \n
		Defines the behavior of the moving object when the end of the trajectory is reached. \n
			:return: rmode: CYCLic| ROUNdtrip| ONEWay
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:RMODe?')
		return Conversions.str_to_scalar_enum(response, enums.MovementRmode)

	def set_rmode(self, rmode: enums.MovementRmode) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:RMODe \n
		Snippet: driver.scenario.localized.receiver.movement.set_rmode(rmode = enums.MovementRmode.CYCLic) \n
		Defines the behavior of the moving object when the end of the trajectory is reached. \n
			:param rmode: CYCLic| ROUNdtrip| ONEWay
		"""
		param = Conversions.enum_scalar_to_str(rmode, enums.MovementRmode)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:RMODe {param}')

	def get_roll(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:ROLL \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_roll() \n
		Sets the angles of rotation in the corresponding direction. \n
			:return: roll: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:ROLL?')
		return Conversions.str_to_float(response)

	def set_roll(self, roll: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:ROLL \n
		Snippet: driver.scenario.localized.receiver.movement.set_roll(roll = 1.0) \n
		Sets the angles of rotation in the corresponding direction. \n
			:param roll: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(roll)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:ROLL {param}')

	def get_smoothening(self) -> bool:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:SMOothening \n
		Snippet: value: bool = driver.scenario.localized.receiver.movement.get_smoothening() \n
		If a vehicle description file is loaded, activates smoothening. See method RsPulseSeq.Scenario.Localized.Movement.Vfile.
		value. \n
			:return: smoothening: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:SMOothening?')
		return Conversions.str_to_bool(response)

	def set_smoothening(self, smoothening: bool) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:SMOothening \n
		Snippet: driver.scenario.localized.receiver.movement.set_smoothening(smoothening = False) \n
		If a vehicle description file is loaded, activates smoothening. See method RsPulseSeq.Scenario.Localized.Movement.Vfile.
		value. \n
			:param smoothening: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(smoothening)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:SMOothening {param}')

	def get_speed(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:SPEed \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_speed() \n
		Sets the speed of the moving emitter. \n
			:return: speed: float Range: 0 to 5999
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:SPEed?')
		return Conversions.str_to_float(response)

	def set_speed(self, speed: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:SPEed \n
		Snippet: driver.scenario.localized.receiver.movement.set_speed(speed = 1.0) \n
		Sets the speed of the moving emitter. \n
			:param speed: float Range: 0 to 5999
		"""
		param = Conversions.decimal_value_to_str(speed)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:SPEed {param}')

	def get_spinning(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:SPINning \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_spinning() \n
		No command help available \n
			:return: spinning: No help available
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:SPINning?')
		return Conversions.str_to_float(response)

	def set_spinning(self, spinning: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:SPINning \n
		Snippet: driver.scenario.localized.receiver.movement.set_spinning(spinning = 1.0) \n
		No command help available \n
			:param spinning: No help available
		"""
		param = Conversions.decimal_value_to_str(spinning)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:SPINning {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.MovementType:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:TYPE \n
		Snippet: value: enums.MovementType = driver.scenario.localized.receiver.movement.get_type_py() \n
		Defines the trajectory shape. \n
			:return: type_py: LINE| ARC| WAYPoint| TRACe
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.MovementType)

	def set_type_py(self, type_py: enums.MovementType) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:TYPE \n
		Snippet: driver.scenario.localized.receiver.movement.set_type_py(type_py = enums.MovementType.ARC) \n
		Defines the trajectory shape. \n
			:param type_py: LINE| ARC| WAYPoint| TRACe
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.MovementType)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:TYPE {param}')

	# noinspection PyTypeChecker
	def get_vehicle(self) -> enums.Vehicle:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:VEHicle \n
		Snippet: value: enums.Vehicle = driver.scenario.localized.receiver.movement.get_vehicle() \n
		Assigns the selected icon. \n
			:return: vehicle: LVEHicle| SHIP| AIRPlane| STATionary| RECeiver
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:VEHicle?')
		return Conversions.str_to_scalar_enum(response, enums.Vehicle)

	def set_vehicle(self, vehicle: enums.Vehicle) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:VEHicle \n
		Snippet: driver.scenario.localized.receiver.movement.set_vehicle(vehicle = enums.Vehicle.AIRPlane) \n
		Assigns the selected icon. \n
			:param vehicle: LVEHicle| SHIP| AIRPlane| STATionary| RECeiver
		"""
		param = Conversions.enum_scalar_to_str(vehicle, enums.Vehicle)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:VEHicle {param}')

	def get_yaw(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:YAW \n
		Snippet: value: float = driver.scenario.localized.receiver.movement.get_yaw() \n
		Sets the angles of rotation in the corresponding direction. \n
			:return: yaw: No help available
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:MOVement:YAW?')
		return Conversions.str_to_float(response)

	def set_yaw(self, yaw: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:MOVement:YAW \n
		Snippet: driver.scenario.localized.receiver.movement.set_yaw(yaw = 1.0) \n
		Sets the angles of rotation in the corresponding direction. \n
			:param yaw: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(yaw)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:MOVement:YAW {param}')

	def clone(self) -> 'Movement':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Movement(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
