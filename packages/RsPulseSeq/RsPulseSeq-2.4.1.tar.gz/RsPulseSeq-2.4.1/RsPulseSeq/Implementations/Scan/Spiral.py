from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Spiral:
	"""Spiral commands group definition. 9 total commands, 0 Subgroups, 9 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("spiral", core, parent)

	def get_palmer(self) -> bool:
		"""SCPI: SCAN:SPIRal:PALMer \n
		Snippet: value: bool = driver.scan.spiral.get_palmer() \n
		Enables superimposing a conical scan on the current scan. \n
			:return: palmer: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:SPIRal:PALMer?')
		return Conversions.str_to_bool(response)

	def set_palmer(self, palmer: bool) -> None:
		"""SCPI: SCAN:SPIRal:PALMer \n
		Snippet: driver.scan.spiral.set_palmer(palmer = False) \n
		Enables superimposing a conical scan on the current scan. \n
			:param palmer: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(palmer)
		self._core.io.write(f'SCAN:SPIRal:PALMer {param}')

	def get_prate(self) -> float:
		"""SCPI: SCAN:SPIRal:PRATe \n
		Snippet: value: float = driver.scan.spiral.get_prate() \n
		Sets the scan rate. \n
			:return: prate: float Range: 0.1 to 1000
		"""
		response = self._core.io.query_str('SCAN:SPIRal:PRATe?')
		return Conversions.str_to_float(response)

	def set_prate(self, prate: float) -> None:
		"""SCPI: SCAN:SPIRal:PRATe \n
		Snippet: driver.scan.spiral.set_prate(prate = 1.0) \n
		Sets the scan rate. \n
			:param prate: float Range: 0.1 to 1000
		"""
		param = Conversions.decimal_value_to_str(prate)
		self._core.io.write(f'SCAN:SPIRal:PRATe {param}')

	def get_psquint(self) -> float:
		"""SCPI: SCAN:SPIRal:PSQuint \n
		Snippet: value: float = driver.scan.spiral.get_psquint() \n
		Sets the squint angle. \n
			:return: psquint: float Range: 0.05 to 45
		"""
		response = self._core.io.query_str('SCAN:SPIRal:PSQuint?')
		return Conversions.str_to_float(response)

	def set_psquint(self, psquint: float) -> None:
		"""SCPI: SCAN:SPIRal:PSQuint \n
		Snippet: driver.scan.spiral.set_psquint(psquint = 1.0) \n
		Sets the squint angle. \n
			:param psquint: float Range: 0.05 to 45
		"""
		param = Conversions.decimal_value_to_str(psquint)
		self._core.io.write(f'SCAN:SPIRal:PSQuint {param}')

	def get_retrace(self) -> float:
		"""SCPI: SCAN:SPIRal:RETRace \n
		Snippet: value: float = driver.scan.spiral.get_retrace() \n
		Sets the speed for the antenna to return to the initial orientation. \n
			:return: retrace: float Range: 0 to 1
		"""
		response = self._core.io.query_str('SCAN:SPIRal:RETRace?')
		return Conversions.str_to_float(response)

	def set_retrace(self, retrace: float) -> None:
		"""SCPI: SCAN:SPIRal:RETRace \n
		Snippet: driver.scan.spiral.set_retrace(retrace = 1.0) \n
		Sets the speed for the antenna to return to the initial orientation. \n
			:param retrace: float Range: 0 to 1
		"""
		param = Conversions.decimal_value_to_str(retrace)
		self._core.io.write(f'SCAN:SPIRal:RETRace {param}')

	# noinspection PyTypeChecker
	def get_rotation(self) -> enums.Rotation:
		"""SCPI: SCAN:SPIRal:ROTation \n
		Snippet: value: enums.Rotation = driver.scan.spiral.get_rotation() \n
		Sets the rotation direction of the antenna. \n
			:return: rotation: CW| CCW
		"""
		response = self._core.io.query_str('SCAN:SPIRal:ROTation?')
		return Conversions.str_to_scalar_enum(response, enums.Rotation)

	def set_rotation(self, rotation: enums.Rotation) -> None:
		"""SCPI: SCAN:SPIRal:ROTation \n
		Snippet: driver.scan.spiral.set_rotation(rotation = enums.Rotation.CCW) \n
		Sets the rotation direction of the antenna. \n
			:param rotation: CW| CCW
		"""
		param = Conversions.enum_scalar_to_str(rotation, enums.Rotation)
		self._core.io.write(f'SCAN:SPIRal:ROTation {param}')

	def get_rounds(self) -> float:
		"""SCPI: SCAN:SPIRal:ROUNds \n
		Snippet: value: float = driver.scan.spiral.get_rounds() \n
		Sets the number of rounds the antenna performs. \n
			:return: rounds: float Range: 0.1 to 15
		"""
		response = self._core.io.query_str('SCAN:SPIRal:ROUNds?')
		return Conversions.str_to_float(response)

	def set_rounds(self, rounds: float) -> None:
		"""SCPI: SCAN:SPIRal:ROUNds \n
		Snippet: driver.scan.spiral.set_rounds(rounds = 1.0) \n
		Sets the number of rounds the antenna performs. \n
			:param rounds: float Range: 0.1 to 15
		"""
		param = Conversions.decimal_value_to_str(rounds)
		self._core.io.write(f'SCAN:SPIRal:ROUNds {param}')

	def get_rtime(self) -> float:
		"""SCPI: SCAN:SPIRal:RTIMe \n
		Snippet: value: float = driver.scan.spiral.get_rtime() \n
		Sets the turning speed of the antenna. \n
			:return: rtime: float Range: 0.01 to 10, Unit: degree/s
		"""
		response = self._core.io.query_str('SCAN:SPIRal:RTIMe?')
		return Conversions.str_to_float(response)

	def set_rtime(self, rtime: float) -> None:
		"""SCPI: SCAN:SPIRal:RTIMe \n
		Snippet: driver.scan.spiral.set_rtime(rtime = 1.0) \n
		Sets the turning speed of the antenna. \n
			:param rtime: float Range: 0.01 to 10, Unit: degree/s
		"""
		param = Conversions.decimal_value_to_str(rtime)
		self._core.io.write(f'SCAN:SPIRal:RTIMe {param}')

	def get_step(self) -> float:
		"""SCPI: SCAN:SPIRal:STEP \n
		Snippet: value: float = driver.scan.spiral.get_step() \n
		Determines the step size to increase the scan radius. \n
			:return: step: float Range: 1 to 11.25, Unit: degree
		"""
		response = self._core.io.query_str('SCAN:SPIRal:STEP?')
		return Conversions.str_to_float(response)

	def set_step(self, step: float) -> None:
		"""SCPI: SCAN:SPIRal:STEP \n
		Snippet: driver.scan.spiral.set_step(step = 1.0) \n
		Determines the step size to increase the scan radius. \n
			:param step: float Range: 1 to 11.25, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(step)
		self._core.io.write(f'SCAN:SPIRal:STEP {param}')

	def get_uni_direction(self) -> bool:
		"""SCPI: SCAN:SPIRal:UNIDirection \n
		Snippet: value: bool = driver.scan.spiral.get_uni_direction() \n
		Enables a unidirectional scan mode. \n
			:return: uni_direction: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:SPIRal:UNIDirection?')
		return Conversions.str_to_bool(response)

	def set_uni_direction(self, uni_direction: bool) -> None:
		"""SCPI: SCAN:SPIRal:UNIDirection \n
		Snippet: driver.scan.spiral.set_uni_direction(uni_direction = False) \n
		Enables a unidirectional scan mode. \n
			:param uni_direction: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(uni_direction)
		self._core.io.write(f'SCAN:SPIRal:UNIDirection {param}')
