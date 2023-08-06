from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Emitter:
	"""Emitter commands group definition. 24 total commands, 3 Subgroups, 15 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("emitter", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	@property
	def blankRanges(self):
		"""blankRanges commands group. 1 Sub-classes, 6 commands."""
		if not hasattr(self, '_blankRanges'):
			from .BlankRanges import BlankRanges
			self._blankRanges = BlankRanges(self._core, self._cmd_group)
		return self._blankRanges

	@property
	def direction(self):
		"""direction commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_direction'):
			from .Direction import Direction
			self._direction = Direction(self._core, self._cmd_group)
		return self._direction

	def get_alias(self) -> str:
		"""SCPI: PLATform:EMITter:ALIas \n
		Snippet: value: str = driver.platform.emitter.get_alias() \n
		Sets an alias name for the selected platform emitter element. \n
			:return: alias: string
		"""
		response = self._core.io.query_str('PLATform:EMITter:ALIas?')
		return trim_str_response(response)

	def set_alias(self, alias: str) -> None:
		"""SCPI: PLATform:EMITter:ALIas \n
		Snippet: driver.platform.emitter.set_alias(alias = '1') \n
		Sets an alias name for the selected platform emitter element. \n
			:param alias: string
		"""
		param = Conversions.value_to_quoted_str(alias)
		self._core.io.write(f'PLATform:EMITter:ALIas {param}')

	def get_angle(self) -> float:
		"""SCPI: PLATform:EMITter:ANGLe \n
		Snippet: value: float = driver.platform.emitter.get_angle() \n
		You can set the position of the selected emitter relative to the platform's origin, using this command combined with
		method RsPulseSeq.Platform.Emitter.radius.
			- method RsPulseSeq.Platform.Emitter.angle sets the angle of the emitter element on the azimuth plane, relative to the platform's heading.
			- method RsPulseSeq.Platform.Emitter.radius sets the distance of the emitter element on the azimuth plane, relative to the platform's origin. \n
			:return: angle: float Range: 0 to 360
		"""
		response = self._core.io.query_str('PLATform:EMITter:ANGLe?')
		return Conversions.str_to_float(response)

	def set_angle(self, angle: float) -> None:
		"""SCPI: PLATform:EMITter:ANGLe \n
		Snippet: driver.platform.emitter.set_angle(angle = 1.0) \n
		You can set the position of the selected emitter relative to the platform's origin, using this command combined with
		method RsPulseSeq.Platform.Emitter.radius.
			- method RsPulseSeq.Platform.Emitter.angle sets the angle of the emitter element on the azimuth plane, relative to the platform's heading.
			- method RsPulseSeq.Platform.Emitter.radius sets the distance of the emitter element on the azimuth plane, relative to the platform's origin. \n
			:param angle: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(angle)
		self._core.io.write(f'PLATform:EMITter:ANGLe {param}')

	def get_azimuth(self) -> float:
		"""SCPI: PLATform:EMITter:AZIMuth \n
		Snippet: value: float = driver.platform.emitter.get_azimuth() \n
		Angle of the emitter element's pointing direction relative to the platform's heading. \n
			:return: azimuth: float Range: 0 to 360
		"""
		response = self._core.io.query_str('PLATform:EMITter:AZIMuth?')
		return Conversions.str_to_float(response)

	def set_azimuth(self, azimuth: float) -> None:
		"""SCPI: PLATform:EMITter:AZIMuth \n
		Snippet: driver.platform.emitter.set_azimuth(azimuth = 1.0) \n
		Angle of the emitter element's pointing direction relative to the platform's heading. \n
			:param azimuth: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(azimuth)
		self._core.io.write(f'PLATform:EMITter:AZIMuth {param}')

	def get_bm(self) -> str:
		"""SCPI: PLATform:EMITter:BM \n
		Snippet: value: str = driver.platform.emitter.get_bm() \n
		No command help available \n
			:return: bm: No help available
		"""
		response = self._core.io.query_str('PLATform:EMITter:BM?')
		return trim_str_response(response)

	def set_bm(self, bm: str) -> None:
		"""SCPI: PLATform:EMITter:BM \n
		Snippet: driver.platform.emitter.set_bm(bm = '1') \n
		No command help available \n
			:param bm: No help available
		"""
		param = Conversions.value_to_quoted_str(bm)
		self._core.io.write(f'PLATform:EMITter:BM {param}')

	def get_bmid(self) -> str:
		"""SCPI: PLATform:EMITter:BMID \n
		Snippet: value: str = driver.platform.emitter.get_bmid() \n
		No command help available \n
			:return: bmid: No help available
		"""
		response = self._core.io.query_str('PLATform:EMITter:BMID?')
		return trim_str_response(response)

	def set_bmid(self, bmid: str) -> None:
		"""SCPI: PLATform:EMITter:BMID \n
		Snippet: driver.platform.emitter.set_bmid(bmid = '1') \n
		No command help available \n
			:param bmid: No help available
		"""
		param = Conversions.value_to_quoted_str(bmid)
		self._core.io.write(f'PLATform:EMITter:BMID {param}')

	def clear(self) -> None:
		"""SCPI: PLATform:EMITter:CLEar \n
		Snippet: driver.platform.emitter.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'PLATform:EMITter:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: PLATform:EMITter:CLEar \n
		Snippet: driver.platform.emitter.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PLATform:EMITter:CLEar', opc_timeout_ms)

	def delete(self, delete: float) -> None:
		"""SCPI: PLATform:EMITter:DELete \n
		Snippet: driver.platform.emitter.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'PLATform:EMITter:DELete {param}')

	def get_elevation(self) -> float:
		"""SCPI: PLATform:EMITter:ELEVation \n
		Snippet: value: float = driver.platform.emitter.get_elevation() \n
		Elevation of the emitter item's pointing direction, relative to the azimuth plane. \n
			:return: elevation: float Range: -90 to 90
		"""
		response = self._core.io.query_str('PLATform:EMITter:ELEVation?')
		return Conversions.str_to_float(response)

	def set_elevation(self, elevation: float) -> None:
		"""SCPI: PLATform:EMITter:ELEVation \n
		Snippet: driver.platform.emitter.set_elevation(elevation = 1.0) \n
		Elevation of the emitter item's pointing direction, relative to the azimuth plane. \n
			:param elevation: float Range: -90 to 90
		"""
		param = Conversions.decimal_value_to_str(elevation)
		self._core.io.write(f'PLATform:EMITter:ELEVation {param}')

	def get_height(self) -> float:
		"""SCPI: PLATform:EMITter:HEIGht \n
		Snippet: value: float = driver.platform.emitter.get_height() \n
		Height of the selected emitter element relative to the platform's origin. Can be used, for example, to differentiate
		between:
			- Radars mounted on different parts of a ship or aircraft.
			- Various radars situated across a land-based radar installation. \n
			:return: height: float Range: -500 to 500
		"""
		response = self._core.io.query_str('PLATform:EMITter:HEIGht?')
		return Conversions.str_to_float(response)

	def set_height(self, height: float) -> None:
		"""SCPI: PLATform:EMITter:HEIGht \n
		Snippet: driver.platform.emitter.set_height(height = 1.0) \n
		Height of the selected emitter element relative to the platform's origin. Can be used, for example, to differentiate
		between:
			- Radars mounted on different parts of a ship or aircraft.
			- Various radars situated across a land-based radar installation. \n
			:param height: float Range: -500 to 500
		"""
		param = Conversions.decimal_value_to_str(height)
		self._core.io.write(f'PLATform:EMITter:HEIGht {param}')

	def get_radius(self) -> float:
		"""SCPI: PLATform:EMITter:RADius \n
		Snippet: value: float = driver.platform.emitter.get_radius() \n
		You can set the position of the selected emitter relative to the platform's origin, using this command combined with
		method RsPulseSeq.Platform.Emitter.angle.
			- method RsPulseSeq.Platform.Emitter.angle sets the angle of the emitter element on the azimuth plane, relative to the platform's heading.
			- method RsPulseSeq.Platform.Emitter.radius sets the distance of the emitter element on the azimuth plane, relative to the platform's origin. \n
			:return: radius: float Range: 0 to 2000
		"""
		response = self._core.io.query_str('PLATform:EMITter:RADius?')
		return Conversions.str_to_float(response)

	def set_radius(self, radius: float) -> None:
		"""SCPI: PLATform:EMITter:RADius \n
		Snippet: driver.platform.emitter.set_radius(radius = 1.0) \n
		You can set the position of the selected emitter relative to the platform's origin, using this command combined with
		method RsPulseSeq.Platform.Emitter.angle.
			- method RsPulseSeq.Platform.Emitter.angle sets the angle of the emitter element on the azimuth plane, relative to the platform's heading.
			- method RsPulseSeq.Platform.Emitter.radius sets the distance of the emitter element on the azimuth plane, relative to the platform's origin. \n
			:param radius: float Range: 0 to 2000
		"""
		param = Conversions.decimal_value_to_str(radius)
		self._core.io.write(f'PLATform:EMITter:RADius {param}')

	def get_roll(self) -> float:
		"""SCPI: PLATform:EMITter:ROLL \n
		Snippet: value: float = driver.platform.emitter.get_roll() \n
		Roll of the emitter item's pointing direction relative to the platform's up direction. Can be used, for example, to
		simulate the emissions from a mast-mounted radar on a marine platform affected by wind. \n
			:return: roll: float Range: -180 to 180
		"""
		response = self._core.io.query_str('PLATform:EMITter:ROLL?')
		return Conversions.str_to_float(response)

	def set_roll(self, roll: float) -> None:
		"""SCPI: PLATform:EMITter:ROLL \n
		Snippet: driver.platform.emitter.set_roll(roll = 1.0) \n
		Roll of the emitter item's pointing direction relative to the platform's up direction. Can be used, for example, to
		simulate the emissions from a mast-mounted radar on a marine platform affected by wind. \n
			:param roll: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(roll)
		self._core.io.write(f'PLATform:EMITter:ROLL {param}')

	def get_select(self) -> float:
		"""SCPI: PLATform:EMITter:SELect \n
		Snippet: value: float = driver.platform.emitter.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('PLATform:EMITter:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: PLATform:EMITter:SELect \n
		Snippet: driver.platform.emitter.set_select(select = 1.0) \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'PLATform:EMITter:SELect {param}')

	def get_x(self) -> float:
		"""SCPI: PLATform:EMITter:X \n
		Snippet: value: float = driver.platform.emitter.get_x() \n
		Set the position of the selected emitter relative to the platform's origin, using this command combined with method
		RsPulseSeq.Platform.Emitter.y.
			INTRO_CMD_HELP: X and Y represent the two principle axis of the platform. \n
			- The Y-axis represents the axis along the center-line of the platform. This axis:
			Table Header:  \n
			- Corresponds to its heading.
			- Passes through the origin.
			- The X-axis:
			Table Header:  \n
			- Is at right-angles to the Y-axis.
			- Passes through the origin.
			INTRO_CMD_HELP: X and Y represent the two principle axis of the platform. \n
			- method RsPulseSeq.Platform.Emitter.y sets the distance of the emitter element from the origin, along the Y-axis. Positive values are towards the heading.
			- method RsPulseSeq.Platform.Emitter.x sets the distance of the emitter element from the origin, along the X-axis. \n
			:return: x: float Range: -2000 to 2000
		"""
		response = self._core.io.query_str('PLATform:EMITter:X?')
		return Conversions.str_to_float(response)

	def set_x(self, x: float) -> None:
		"""SCPI: PLATform:EMITter:X \n
		Snippet: driver.platform.emitter.set_x(x = 1.0) \n
		Set the position of the selected emitter relative to the platform's origin, using this command combined with method
		RsPulseSeq.Platform.Emitter.y.
			INTRO_CMD_HELP: X and Y represent the two principle axis of the platform. \n
			- The Y-axis represents the axis along the center-line of the platform. This axis:
			Table Header:  \n
			- Corresponds to its heading.
			- Passes through the origin.
			- The X-axis:
			Table Header:  \n
			- Is at right-angles to the Y-axis.
			- Passes through the origin.
			INTRO_CMD_HELP: X and Y represent the two principle axis of the platform. \n
			- method RsPulseSeq.Platform.Emitter.y sets the distance of the emitter element from the origin, along the Y-axis. Positive values are towards the heading.
			- method RsPulseSeq.Platform.Emitter.x sets the distance of the emitter element from the origin, along the X-axis. \n
			:param x: float Range: -2000 to 2000
		"""
		param = Conversions.decimal_value_to_str(x)
		self._core.io.write(f'PLATform:EMITter:X {param}')

	def get_y(self) -> float:
		"""SCPI: PLATform:EMITter:Y \n
		Snippet: value: float = driver.platform.emitter.get_y() \n
		Set the position of the selected emitter relative to the platform's origin, using this command combined with method
		RsPulseSeq.Platform.Emitter.x.
			INTRO_CMD_HELP: X and Y represent the two principle axis of the platform. \n
			- The Y-axis represents the axis along the center-line of the platform. This axis:
			Table Header:  \n
			- Corresponds to its heading.
			- Passes through the origin.
			- The X-axis:
			Table Header:  \n
			- Is at right-angles to the Y-axis.
			- Passes through the origin.
			INTRO_CMD_HELP: X and Y represent the two principle axis of the platform. \n
			- method RsPulseSeq.Platform.Emitter.y sets the distance of the emitter element from the origin, along the Y-axis. Positive values are towards the heading. Step = 0.01 m
			- method RsPulseSeq.Platform.Emitter.x sets the distance of the emitter element from the origin, along the X-axis. Step = 0.01 m \n
			:return: y: float Range: -2000 to 2000
		"""
		response = self._core.io.query_str('PLATform:EMITter:Y?')
		return Conversions.str_to_float(response)

	def set_y(self, y: float) -> None:
		"""SCPI: PLATform:EMITter:Y \n
		Snippet: driver.platform.emitter.set_y(y = 1.0) \n
		Set the position of the selected emitter relative to the platform's origin, using this command combined with method
		RsPulseSeq.Platform.Emitter.x.
			INTRO_CMD_HELP: X and Y represent the two principle axis of the platform. \n
			- The Y-axis represents the axis along the center-line of the platform. This axis:
			Table Header:  \n
			- Corresponds to its heading.
			- Passes through the origin.
			- The X-axis:
			Table Header:  \n
			- Is at right-angles to the Y-axis.
			- Passes through the origin.
			INTRO_CMD_HELP: X and Y represent the two principle axis of the platform. \n
			- method RsPulseSeq.Platform.Emitter.y sets the distance of the emitter element from the origin, along the Y-axis. Positive values are towards the heading. Step = 0.01 m
			- method RsPulseSeq.Platform.Emitter.x sets the distance of the emitter element from the origin, along the X-axis. Step = 0.01 m \n
			:param y: float Range: -2000 to 2000
		"""
		param = Conversions.decimal_value_to_str(y)
		self._core.io.write(f'PLATform:EMITter:Y {param}')

	def get_value(self) -> str:
		"""SCPI: PLATform:EMITter \n
		Snippet: value: str = driver.platform.emitter.get_value() \n
		The string must be unique within the repository. Letters, numbers, spaces and some special characters can be used.
			INTRO_CMD_HELP: Examples of special characters: \n
			- Supported: !$% =?-+_.
			- Not supported: §&/:äöü \n
			:return: emitter: string
		"""
		response = self._core.io.query_str('PLATform:EMITter?')
		return trim_str_response(response)

	def set_value(self, emitter: str) -> None:
		"""SCPI: PLATform:EMITter \n
		Snippet: driver.platform.emitter.set_value(emitter = '1') \n
		The string must be unique within the repository. Letters, numbers, spaces and some special characters can be used.
			INTRO_CMD_HELP: Examples of special characters: \n
			- Supported: !$% =?-+_.
			- Not supported: §&/:äöü \n
			:param emitter: string
		"""
		param = Conversions.value_to_quoted_str(emitter)
		self._core.io.write(f'PLATform:EMITter {param}')

	def clone(self) -> 'Emitter':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Emitter(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
