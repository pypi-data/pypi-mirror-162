from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Raster:
	"""Raster commands group definition. 13 total commands, 0 Subgroups, 13 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("raster", core, parent)

	def get_bars(self) -> float:
		"""SCPI: SCAN:RASTer:BARS \n
		Snippet: value: float = driver.scan.raster.get_bars() \n
		Sets the number of scanned bars (sectors) . \n
			:return: bars: float Range: 1 to 30
		"""
		response = self._core.io.query_str('SCAN:RASTer:BARS?')
		return Conversions.str_to_float(response)

	def set_bars(self, bars: float) -> None:
		"""SCPI: SCAN:RASTer:BARS \n
		Snippet: driver.scan.raster.set_bars(bars = 1.0) \n
		Sets the number of scanned bars (sectors) . \n
			:param bars: float Range: 1 to 30
		"""
		param = Conversions.decimal_value_to_str(bars)
		self._core.io.write(f'SCAN:RASTer:BARS {param}')

	def get_bar_trans_time(self) -> float:
		"""SCPI: SCAN:RASTer:BARTranstime \n
		Snippet: value: float = driver.scan.raster.get_bar_trans_time() \n
		Transition time between two bars in bidirectional scan mode. \n
			:return: bar_trans_time: float Range: 0 to 1, Unit: seconds
		"""
		response = self._core.io.query_str('SCAN:RASTer:BARTranstime?')
		return Conversions.str_to_float(response)

	def set_bar_trans_time(self, bar_trans_time: float) -> None:
		"""SCPI: SCAN:RASTer:BARTranstime \n
		Snippet: driver.scan.raster.set_bar_trans_time(bar_trans_time = 1.0) \n
		Transition time between two bars in bidirectional scan mode. \n
			:param bar_trans_time: float Range: 0 to 1, Unit: seconds
		"""
		param = Conversions.decimal_value_to_str(bar_trans_time)
		self._core.io.write(f'SCAN:RASTer:BARTranstime {param}')

	def get_bar_width(self) -> float:
		"""SCPI: SCAN:RASTer:BARWidth \n
		Snippet: value: float = driver.scan.raster.get_bar_width() \n
		Sets the distance between two consecutive scanned bars (sectors) . \n
			:return: bar_width: float Range: 0.1 to 9, Unit: m
		"""
		response = self._core.io.query_str('SCAN:RASTer:BARWidth?')
		return Conversions.str_to_float(response)

	def set_bar_width(self, bar_width: float) -> None:
		"""SCPI: SCAN:RASTer:BARWidth \n
		Snippet: driver.scan.raster.set_bar_width(bar_width = 1.0) \n
		Sets the distance between two consecutive scanned bars (sectors) . \n
			:param bar_width: float Range: 0.1 to 9, Unit: m
		"""
		param = Conversions.decimal_value_to_str(bar_width)
		self._core.io.write(f'SCAN:RASTer:BARWidth {param}')

	# noinspection PyTypeChecker
	def get_direction(self) -> enums.RasterDirection:
		"""SCPI: SCAN:RASTer:DIRection \n
		Snippet: value: enums.RasterDirection = driver.scan.raster.get_direction() \n
		Sets the scanning direction. \n
			:return: direction: HORizontal| VERTical
		"""
		response = self._core.io.query_str('SCAN:RASTer:DIRection?')
		return Conversions.str_to_scalar_enum(response, enums.RasterDirection)

	def set_direction(self, direction: enums.RasterDirection) -> None:
		"""SCPI: SCAN:RASTer:DIRection \n
		Snippet: driver.scan.raster.set_direction(direction = enums.RasterDirection.HORizontal) \n
		Sets the scanning direction. \n
			:param direction: HORizontal| VERTical
		"""
		param = Conversions.enum_scalar_to_str(direction, enums.RasterDirection)
		self._core.io.write(f'SCAN:RASTer:DIRection {param}')

	def get_flyback(self) -> float:
		"""SCPI: SCAN:RASTer:FLYBack \n
		Snippet: value: float = driver.scan.raster.get_flyback() \n
		Sets the Flyback time for the antenna working in unidirectional mode. \n
			:return: flyback: float Range: 0 to 1, Unit: s
		"""
		response = self._core.io.query_str('SCAN:RASTer:FLYBack?')
		return Conversions.str_to_float(response)

	def set_flyback(self, flyback: float) -> None:
		"""SCPI: SCAN:RASTer:FLYBack \n
		Snippet: driver.scan.raster.set_flyback(flyback = 1.0) \n
		Sets the Flyback time for the antenna working in unidirectional mode. \n
			:param flyback: float Range: 0 to 1, Unit: s
		"""
		param = Conversions.decimal_value_to_str(flyback)
		self._core.io.write(f'SCAN:RASTer:FLYBack {param}')

	def get_palmer(self) -> bool:
		"""SCPI: SCAN:RASTer:PALMer \n
		Snippet: value: bool = driver.scan.raster.get_palmer() \n
		Enables superimposing a conical scan on the current scan. \n
			:return: palmer: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:RASTer:PALMer?')
		return Conversions.str_to_bool(response)

	def set_palmer(self, palmer: bool) -> None:
		"""SCPI: SCAN:RASTer:PALMer \n
		Snippet: driver.scan.raster.set_palmer(palmer = False) \n
		Enables superimposing a conical scan on the current scan. \n
			:param palmer: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(palmer)
		self._core.io.write(f'SCAN:RASTer:PALMer {param}')

	def get_prate(self) -> float:
		"""SCPI: SCAN:RASTer:PRATe \n
		Snippet: value: float = driver.scan.raster.get_prate() \n
		Sets the scan rate. \n
			:return: prate: float Range: 0.1 to 1000
		"""
		response = self._core.io.query_str('SCAN:RASTer:PRATe?')
		return Conversions.str_to_float(response)

	def set_prate(self, prate: float) -> None:
		"""SCPI: SCAN:RASTer:PRATe \n
		Snippet: driver.scan.raster.set_prate(prate = 1.0) \n
		Sets the scan rate. \n
			:param prate: float Range: 0.1 to 1000
		"""
		param = Conversions.decimal_value_to_str(prate)
		self._core.io.write(f'SCAN:RASTer:PRATe {param}')

	def get_psquint(self) -> float:
		"""SCPI: SCAN:RASTer:PSQuint \n
		Snippet: value: float = driver.scan.raster.get_psquint() \n
		Sets the squint angle. \n
			:return: psquint: float Range: 0.05 to 45
		"""
		response = self._core.io.query_str('SCAN:RASTer:PSQuint?')
		return Conversions.str_to_float(response)

	def set_psquint(self, psquint: float) -> None:
		"""SCPI: SCAN:RASTer:PSQuint \n
		Snippet: driver.scan.raster.set_psquint(psquint = 1.0) \n
		Sets the squint angle. \n
			:param psquint: float Range: 0.05 to 45
		"""
		param = Conversions.decimal_value_to_str(psquint)
		self._core.io.write(f'SCAN:RASTer:PSQuint {param}')

	def get_rate(self) -> float:
		"""SCPI: SCAN:RASTer:RATE \n
		Snippet: value: float = driver.scan.raster.get_rate() \n
		Sets the turning speed. \n
			:return: rate: float Range: 0.01 to 100000, Unit: degree/s
		"""
		response = self._core.io.query_str('SCAN:RASTer:RATE?')
		return Conversions.str_to_float(response)

	def set_rate(self, rate: float) -> None:
		"""SCPI: SCAN:RASTer:RATE \n
		Snippet: driver.scan.raster.set_rate(rate = 1.0) \n
		Sets the turning speed. \n
			:param rate: float Range: 0.01 to 100000, Unit: degree/s
		"""
		param = Conversions.decimal_value_to_str(rate)
		self._core.io.write(f'SCAN:RASTer:RATE {param}')

	def get_retrace(self) -> float:
		"""SCPI: SCAN:RASTer:RETRace \n
		Snippet: value: float = driver.scan.raster.get_retrace() \n
		Sets the speed for the antenna to return to the initial orientation. \n
			:return: retrace: float Range: 0 to 1
		"""
		response = self._core.io.query_str('SCAN:RASTer:RETRace?')
		return Conversions.str_to_float(response)

	def set_retrace(self, retrace: float) -> None:
		"""SCPI: SCAN:RASTer:RETRace \n
		Snippet: driver.scan.raster.set_retrace(retrace = 1.0) \n
		Sets the speed for the antenna to return to the initial orientation. \n
			:param retrace: float Range: 0 to 1
		"""
		param = Conversions.decimal_value_to_str(retrace)
		self._core.io.write(f'SCAN:RASTer:RETRace {param}')

	def get_rewind(self) -> bool:
		"""SCPI: SCAN:RASTer:REWind \n
		Snippet: value: bool = driver.scan.raster.get_rewind() \n
		If enabled, the antenna scans forwards and backwards. \n
			:return: rewind: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:RASTer:REWind?')
		return Conversions.str_to_bool(response)

	def set_rewind(self, rewind: bool) -> None:
		"""SCPI: SCAN:RASTer:REWind \n
		Snippet: driver.scan.raster.set_rewind(rewind = False) \n
		If enabled, the antenna scans forwards and backwards. \n
			:param rewind: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(rewind)
		self._core.io.write(f'SCAN:RASTer:REWind {param}')

	def get_uni_direction(self) -> bool:
		"""SCPI: SCAN:RASTer:UNIDirection \n
		Snippet: value: bool = driver.scan.raster.get_uni_direction() \n
		Enables a unidirectional scan mode. \n
			:return: uni_direction: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:RASTer:UNIDirection?')
		return Conversions.str_to_bool(response)

	def set_uni_direction(self, uni_direction: bool) -> None:
		"""SCPI: SCAN:RASTer:UNIDirection \n
		Snippet: driver.scan.raster.set_uni_direction(uni_direction = False) \n
		Enables a unidirectional scan mode. \n
			:param uni_direction: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(uni_direction)
		self._core.io.write(f'SCAN:RASTer:UNIDirection {param}')

	def get_width(self) -> float:
		"""SCPI: SCAN:RASTer:WIDTh \n
		Snippet: value: float = driver.scan.raster.get_width() \n
		Sets the width of the sector to be scanned. \n
			:return: width: float Range: 0.1 to 360, Unit: degree
		"""
		response = self._core.io.query_str('SCAN:RASTer:WIDTh?')
		return Conversions.str_to_float(response)

	def set_width(self, width: float) -> None:
		"""SCPI: SCAN:RASTer:WIDTh \n
		Snippet: driver.scan.raster.set_width(width = 1.0) \n
		Sets the width of the sector to be scanned. \n
			:param width: float Range: 0.1 to 360, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(width)
		self._core.io.write(f'SCAN:RASTer:WIDTh {param}')
