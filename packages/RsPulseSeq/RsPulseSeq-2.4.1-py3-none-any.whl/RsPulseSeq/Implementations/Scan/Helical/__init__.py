from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Helical:
	"""Helical commands group definition. 5 total commands, 1 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("helical", core, parent)

	@property
	def elevation(self):
		"""elevation commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_elevation'):
			from .Elevation import Elevation
			self._elevation = Elevation(self._core, self._cmd_group)
		return self._elevation

	def get_retrace(self) -> float:
		"""SCPI: SCAN:HELical:RETRace \n
		Snippet: value: float = driver.scan.helical.get_retrace() \n
		Sets the speed for the antenna to return to the initial orientation. \n
			:return: retrace: float Range: 0 to 1
		"""
		response = self._core.io.query_str('SCAN:HELical:RETRace?')
		return Conversions.str_to_float(response)

	def set_retrace(self, retrace: float) -> None:
		"""SCPI: SCAN:HELical:RETRace \n
		Snippet: driver.scan.helical.set_retrace(retrace = 1.0) \n
		Sets the speed for the antenna to return to the initial orientation. \n
			:param retrace: float Range: 0 to 1
		"""
		param = Conversions.decimal_value_to_str(retrace)
		self._core.io.write(f'SCAN:HELical:RETRace {param}')

	# noinspection PyTypeChecker
	def get_rotation(self) -> enums.Rotation:
		"""SCPI: SCAN:HELical:ROTation \n
		Snippet: value: enums.Rotation = driver.scan.helical.get_rotation() \n
		Sets the rotation direction of the antenna. \n
			:return: rotation: CW| CCW
		"""
		response = self._core.io.query_str('SCAN:HELical:ROTation?')
		return Conversions.str_to_scalar_enum(response, enums.Rotation)

	def set_rotation(self, rotation: enums.Rotation) -> None:
		"""SCPI: SCAN:HELical:ROTation \n
		Snippet: driver.scan.helical.set_rotation(rotation = enums.Rotation.CCW) \n
		Sets the rotation direction of the antenna. \n
			:param rotation: CW| CCW
		"""
		param = Conversions.enum_scalar_to_str(rotation, enums.Rotation)
		self._core.io.write(f'SCAN:HELical:ROTation {param}')

	def get_rpm(self) -> float:
		"""SCPI: SCAN:HELical:RPM \n
		Snippet: value: float = driver.scan.helical.get_rpm() \n
		Sets the rotation speed of the antenna. \n
			:return: rpm: float Range: 0.01 to 1000, Unit: degree/s
		"""
		response = self._core.io.query_str('SCAN:HELical:RPM?')
		return Conversions.str_to_float(response)

	def set_rpm(self, rpm: float) -> None:
		"""SCPI: SCAN:HELical:RPM \n
		Snippet: driver.scan.helical.set_rpm(rpm = 1.0) \n
		Sets the rotation speed of the antenna. \n
			:param rpm: float Range: 0.01 to 1000, Unit: degree/s
		"""
		param = Conversions.decimal_value_to_str(rpm)
		self._core.io.write(f'SCAN:HELical:RPM {param}')

	def get_turns(self) -> float:
		"""SCPI: SCAN:HELical:TURNs \n
		Snippet: value: float = driver.scan.helical.get_turns() \n
		Sets the number of turns. \n
			:return: turns: float Range: 1 to 30
		"""
		response = self._core.io.query_str('SCAN:HELical:TURNs?')
		return Conversions.str_to_float(response)

	def set_turns(self, turns: float) -> None:
		"""SCPI: SCAN:HELical:TURNs \n
		Snippet: driver.scan.helical.set_turns(turns = 1.0) \n
		Sets the number of turns. \n
			:param turns: float Range: 1 to 30
		"""
		param = Conversions.decimal_value_to_str(turns)
		self._core.io.write(f'SCAN:HELical:TURNs {param}')

	def clone(self) -> 'Helical':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Helical(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
