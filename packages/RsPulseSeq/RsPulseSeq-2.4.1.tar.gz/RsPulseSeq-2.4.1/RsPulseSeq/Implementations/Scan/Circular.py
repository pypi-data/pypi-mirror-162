from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Circular:
	"""Circular commands group definition. 10 total commands, 0 Subgroups, 10 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("circular", core, parent)

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.CircularMode:
		"""SCPI: SCAN:CIRCular:MODE \n
		Snippet: value: enums.CircularMode = driver.scan.circular.get_mode() \n
		Sets if the scan turning speed is set as a scans rate or as a period. \n
			:return: mode: RPM| SEC RPM Scan rate, set with the command method RsPulseSeq.Scan.Circular.rpm. SEC Scan period, set with the command method RsPulseSeq.Scan.Circular.period.
		"""
		response = self._core.io.query_str('SCAN:CIRCular:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.CircularMode)

	def set_mode(self, mode: enums.CircularMode) -> None:
		"""SCPI: SCAN:CIRCular:MODE \n
		Snippet: driver.scan.circular.set_mode(mode = enums.CircularMode.RPM) \n
		Sets if the scan turning speed is set as a scans rate or as a period. \n
			:param mode: RPM| SEC RPM Scan rate, set with the command method RsPulseSeq.Scan.Circular.rpm. SEC Scan period, set with the command method RsPulseSeq.Scan.Circular.period.
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.CircularMode)
		self._core.io.write(f'SCAN:CIRCular:MODE {param}')

	def get_nelevation(self) -> float:
		"""SCPI: SCAN:CIRCular:NELevation \n
		Snippet: value: float = driver.scan.circular.get_nelevation() \n
		Sets the elevation angle. \n
			:return: nelevation: float Range: 0.01 to 90
		"""
		response = self._core.io.query_str('SCAN:CIRCular:NELevation?')
		return Conversions.str_to_float(response)

	def set_nelevation(self, nelevation: float) -> None:
		"""SCPI: SCAN:CIRCular:NELevation \n
		Snippet: driver.scan.circular.set_nelevation(nelevation = 1.0) \n
		Sets the elevation angle. \n
			:param nelevation: float Range: 0.01 to 90
		"""
		param = Conversions.decimal_value_to_str(nelevation)
		self._core.io.write(f'SCAN:CIRCular:NELevation {param}')

	def get_nodding(self) -> bool:
		"""SCPI: SCAN:CIRCular:NODDing \n
		Snippet: value: bool = driver.scan.circular.get_nodding() \n
		Enables superimposing a horizontal nodding on the scan. \n
			:return: nodding: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:CIRCular:NODDing?')
		return Conversions.str_to_bool(response)

	def set_nodding(self, nodding: bool) -> None:
		"""SCPI: SCAN:CIRCular:NODDing \n
		Snippet: driver.scan.circular.set_nodding(nodding = False) \n
		Enables superimposing a horizontal nodding on the scan. \n
			:param nodding: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(nodding)
		self._core.io.write(f'SCAN:CIRCular:NODDing {param}')

	def get_nrate(self) -> float:
		"""SCPI: SCAN:CIRCular:NRATe \n
		Snippet: value: float = driver.scan.circular.get_nrate() \n
		Sets the elevation rate. \n
			:return: nrate: float Range: 0.01 to 2000
		"""
		response = self._core.io.query_str('SCAN:CIRCular:NRATe?')
		return Conversions.str_to_float(response)

	def set_nrate(self, nrate: float) -> None:
		"""SCPI: SCAN:CIRCular:NRATe \n
		Snippet: driver.scan.circular.set_nrate(nrate = 1.0) \n
		Sets the elevation rate. \n
			:param nrate: float Range: 0.01 to 2000
		"""
		param = Conversions.decimal_value_to_str(nrate)
		self._core.io.write(f'SCAN:CIRCular:NRATe {param}')

	def get_palmer(self) -> bool:
		"""SCPI: SCAN:CIRCular:PALMer \n
		Snippet: value: bool = driver.scan.circular.get_palmer() \n
		Enables superimposing a conical scan on the current scan. \n
			:return: palmer: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:CIRCular:PALMer?')
		return Conversions.str_to_bool(response)

	def set_palmer(self, palmer: bool) -> None:
		"""SCPI: SCAN:CIRCular:PALMer \n
		Snippet: driver.scan.circular.set_palmer(palmer = False) \n
		Enables superimposing a conical scan on the current scan. \n
			:param palmer: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(palmer)
		self._core.io.write(f'SCAN:CIRCular:PALMer {param}')

	def get_period(self) -> float:
		"""SCPI: SCAN:CIRCular:PERiod \n
		Snippet: value: float = driver.scan.circular.get_period() \n
		Sets the time it takes for the antenna to turn once. \n
			:return: period: float Range: 0.006 to 6000
		"""
		response = self._core.io.query_str('SCAN:CIRCular:PERiod?')
		return Conversions.str_to_float(response)

	def set_period(self, period: float) -> None:
		"""SCPI: SCAN:CIRCular:PERiod \n
		Snippet: driver.scan.circular.set_period(period = 1.0) \n
		Sets the time it takes for the antenna to turn once. \n
			:param period: float Range: 0.006 to 6000
		"""
		param = Conversions.decimal_value_to_str(period)
		self._core.io.write(f'SCAN:CIRCular:PERiod {param}')

	def get_prate(self) -> float:
		"""SCPI: SCAN:CIRCular:PRATe \n
		Snippet: value: float = driver.scan.circular.get_prate() \n
		Sets the scan rate. \n
			:return: prate: float Range: 0.1 to 1000
		"""
		response = self._core.io.query_str('SCAN:CIRCular:PRATe?')
		return Conversions.str_to_float(response)

	def set_prate(self, prate: float) -> None:
		"""SCPI: SCAN:CIRCular:PRATe \n
		Snippet: driver.scan.circular.set_prate(prate = 1.0) \n
		Sets the scan rate. \n
			:param prate: float Range: 0.1 to 1000
		"""
		param = Conversions.decimal_value_to_str(prate)
		self._core.io.write(f'SCAN:CIRCular:PRATe {param}')

	def get_psquint(self) -> float:
		"""SCPI: SCAN:CIRCular:PSQuint \n
		Snippet: value: float = driver.scan.circular.get_psquint() \n
		Sets the squint angle. \n
			:return: psquint: float Range: 0.05 to 45
		"""
		response = self._core.io.query_str('SCAN:CIRCular:PSQuint?')
		return Conversions.str_to_float(response)

	def set_psquint(self, psquint: float) -> None:
		"""SCPI: SCAN:CIRCular:PSQuint \n
		Snippet: driver.scan.circular.set_psquint(psquint = 1.0) \n
		Sets the squint angle. \n
			:param psquint: float Range: 0.05 to 45
		"""
		param = Conversions.decimal_value_to_str(psquint)
		self._core.io.write(f'SCAN:CIRCular:PSQuint {param}')

	# noinspection PyTypeChecker
	def get_rotation(self) -> enums.Rotation:
		"""SCPI: SCAN:CIRCular:ROTation \n
		Snippet: value: enums.Rotation = driver.scan.circular.get_rotation() \n
		Sets the rotation direction of the antenna. \n
			:return: rotation: CW| CCW
		"""
		response = self._core.io.query_str('SCAN:CIRCular:ROTation?')
		return Conversions.str_to_scalar_enum(response, enums.Rotation)

	def set_rotation(self, rotation: enums.Rotation) -> None:
		"""SCPI: SCAN:CIRCular:ROTation \n
		Snippet: driver.scan.circular.set_rotation(rotation = enums.Rotation.CCW) \n
		Sets the rotation direction of the antenna. \n
			:param rotation: CW| CCW
		"""
		param = Conversions.enum_scalar_to_str(rotation, enums.Rotation)
		self._core.io.write(f'SCAN:CIRCular:ROTation {param}')

	def get_rpm(self) -> float:
		"""SCPI: SCAN:CIRCular:RPM \n
		Snippet: value: float = driver.scan.circular.get_rpm() \n
		Sets the rotation speed of the antenna. \n
			:return: rpm: float Range: 0.01 to 1000, Unit: degree/s
		"""
		response = self._core.io.query_str('SCAN:CIRCular:RPM?')
		return Conversions.str_to_float(response)

	def set_rpm(self, rpm: float) -> None:
		"""SCPI: SCAN:CIRCular:RPM \n
		Snippet: driver.scan.circular.set_rpm(rpm = 1.0) \n
		Sets the rotation speed of the antenna. \n
			:param rpm: float Range: 0.01 to 1000, Unit: degree/s
		"""
		param = Conversions.decimal_value_to_str(rpm)
		self._core.io.write(f'SCAN:CIRCular:RPM {param}')
