from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Sector:
	"""Sector commands group definition. 10 total commands, 0 Subgroups, 10 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sector", core, parent)

	def get_flyback(self) -> float:
		"""SCPI: SCAN:SECTor:FLYBack \n
		Snippet: value: float = driver.scan.sector.get_flyback() \n
		Sets the Flyback time for the antenna working in unidirectional mode. \n
			:return: flyback: float Range: 0 to 1, Unit: s
		"""
		response = self._core.io.query_str('SCAN:SECTor:FLYBack?')
		return Conversions.str_to_float(response)

	def set_flyback(self, flyback: float) -> None:
		"""SCPI: SCAN:SECTor:FLYBack \n
		Snippet: driver.scan.sector.set_flyback(flyback = 1.0) \n
		Sets the Flyback time for the antenna working in unidirectional mode. \n
			:param flyback: float Range: 0 to 1, Unit: s
		"""
		param = Conversions.decimal_value_to_str(flyback)
		self._core.io.write(f'SCAN:SECTor:FLYBack {param}')

	def get_nelevation(self) -> float:
		"""SCPI: SCAN:SECTor:NELevation \n
		Snippet: value: float = driver.scan.sector.get_nelevation() \n
		Sets the elevation angle. \n
			:return: nelevation: float Range: 0.01 to 90
		"""
		response = self._core.io.query_str('SCAN:SECTor:NELevation?')
		return Conversions.str_to_float(response)

	def set_nelevation(self, nelevation: float) -> None:
		"""SCPI: SCAN:SECTor:NELevation \n
		Snippet: driver.scan.sector.set_nelevation(nelevation = 1.0) \n
		Sets the elevation angle. \n
			:param nelevation: float Range: 0.01 to 90
		"""
		param = Conversions.decimal_value_to_str(nelevation)
		self._core.io.write(f'SCAN:SECTor:NELevation {param}')

	def get_nodding(self) -> bool:
		"""SCPI: SCAN:SECTor:NODDing \n
		Snippet: value: bool = driver.scan.sector.get_nodding() \n
		Enables superimposing a horizontal nodding on the scan. \n
			:return: nodding: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:SECTor:NODDing?')
		return Conversions.str_to_bool(response)

	def set_nodding(self, nodding: bool) -> None:
		"""SCPI: SCAN:SECTor:NODDing \n
		Snippet: driver.scan.sector.set_nodding(nodding = False) \n
		Enables superimposing a horizontal nodding on the scan. \n
			:param nodding: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(nodding)
		self._core.io.write(f'SCAN:SECTor:NODDing {param}')

	def get_nrate(self) -> float:
		"""SCPI: SCAN:SECTor:NRATe \n
		Snippet: value: float = driver.scan.sector.get_nrate() \n
		Sets the elevation rate. \n
			:return: nrate: float Range: 0.01 to 2000
		"""
		response = self._core.io.query_str('SCAN:SECTor:NRATe?')
		return Conversions.str_to_float(response)

	def set_nrate(self, nrate: float) -> None:
		"""SCPI: SCAN:SECTor:NRATe \n
		Snippet: driver.scan.sector.set_nrate(nrate = 1.0) \n
		Sets the elevation rate. \n
			:param nrate: float Range: 0.01 to 2000
		"""
		param = Conversions.decimal_value_to_str(nrate)
		self._core.io.write(f'SCAN:SECTor:NRATe {param}')

	def get_palmer(self) -> bool:
		"""SCPI: SCAN:SECTor:PALMer \n
		Snippet: value: bool = driver.scan.sector.get_palmer() \n
		Enables superimposing a conical scan on the current scan. \n
			:return: palmer: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:SECTor:PALMer?')
		return Conversions.str_to_bool(response)

	def set_palmer(self, palmer: bool) -> None:
		"""SCPI: SCAN:SECTor:PALMer \n
		Snippet: driver.scan.sector.set_palmer(palmer = False) \n
		Enables superimposing a conical scan on the current scan. \n
			:param palmer: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(palmer)
		self._core.io.write(f'SCAN:SECTor:PALMer {param}')

	def get_prate(self) -> float:
		"""SCPI: SCAN:SECTor:PRATe \n
		Snippet: value: float = driver.scan.sector.get_prate() \n
		Sets the scan rate. \n
			:return: prate: float Range: 0.1 to 1000
		"""
		response = self._core.io.query_str('SCAN:SECTor:PRATe?')
		return Conversions.str_to_float(response)

	def set_prate(self, prate: float) -> None:
		"""SCPI: SCAN:SECTor:PRATe \n
		Snippet: driver.scan.sector.set_prate(prate = 1.0) \n
		Sets the scan rate. \n
			:param prate: float Range: 0.1 to 1000
		"""
		param = Conversions.decimal_value_to_str(prate)
		self._core.io.write(f'SCAN:SECTor:PRATe {param}')

	def get_psquint(self) -> float:
		"""SCPI: SCAN:SECTor:PSQuint \n
		Snippet: value: float = driver.scan.sector.get_psquint() \n
		Sets the squint angle. \n
			:return: psquint: float Range: 0.05 to 45
		"""
		response = self._core.io.query_str('SCAN:SECTor:PSQuint?')
		return Conversions.str_to_float(response)

	def set_psquint(self, psquint: float) -> None:
		"""SCPI: SCAN:SECTor:PSQuint \n
		Snippet: driver.scan.sector.set_psquint(psquint = 1.0) \n
		Sets the squint angle. \n
			:param psquint: float Range: 0.05 to 45
		"""
		param = Conversions.decimal_value_to_str(psquint)
		self._core.io.write(f'SCAN:SECTor:PSQuint {param}')

	def get_rate(self) -> float:
		"""SCPI: SCAN:SECTor:RATE \n
		Snippet: value: float = driver.scan.sector.get_rate() \n
		Sets the turning speed. \n
			:return: rate: float Range: 0.01 to 100000, Unit: degree/s
		"""
		response = self._core.io.query_str('SCAN:SECTor:RATE?')
		return Conversions.str_to_float(response)

	def set_rate(self, rate: float) -> None:
		"""SCPI: SCAN:SECTor:RATE \n
		Snippet: driver.scan.sector.set_rate(rate = 1.0) \n
		Sets the turning speed. \n
			:param rate: float Range: 0.01 to 100000, Unit: degree/s
		"""
		param = Conversions.decimal_value_to_str(rate)
		self._core.io.write(f'SCAN:SECTor:RATE {param}')

	def get_uni_direction(self) -> bool:
		"""SCPI: SCAN:SECTor:UNIDirection \n
		Snippet: value: bool = driver.scan.sector.get_uni_direction() \n
		Enables a unidirectional scan mode. \n
			:return: uni_direction: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:SECTor:UNIDirection?')
		return Conversions.str_to_bool(response)

	def set_uni_direction(self, uni_direction: bool) -> None:
		"""SCPI: SCAN:SECTor:UNIDirection \n
		Snippet: driver.scan.sector.set_uni_direction(uni_direction = False) \n
		Enables a unidirectional scan mode. \n
			:param uni_direction: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(uni_direction)
		self._core.io.write(f'SCAN:SECTor:UNIDirection {param}')

	def get_width(self) -> float:
		"""SCPI: SCAN:SECTor:WIDTh \n
		Snippet: value: float = driver.scan.sector.get_width() \n
		Sets the width of the sector to be scanned. \n
			:return: width: float Range: 0.1 to 360, Unit: degree
		"""
		response = self._core.io.query_str('SCAN:SECTor:WIDTh?')
		return Conversions.str_to_float(response)

	def set_width(self, width: float) -> None:
		"""SCPI: SCAN:SECTor:WIDTh \n
		Snippet: driver.scan.sector.set_width(width = 1.0) \n
		Sets the width of the sector to be scanned. \n
			:param width: float Range: 0.1 to 360, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(width)
		self._core.io.write(f'SCAN:SECTor:WIDTh {param}')
