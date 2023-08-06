from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Receiver:
	"""Receiver commands group definition. 33 total commands, 2 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("receiver", core, parent)

	@property
	def direction(self):
		"""direction commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_direction'):
			from .Direction import Direction
			self._direction = Direction(self._core, self._cmd_group)
		return self._direction

	@property
	def movement(self):
		"""movement commands group. 4 Sub-classes, 17 commands."""
		if not hasattr(self, '_movement'):
			from .Movement import Movement
			self._movement = Movement(self._core, self._cmd_group)
		return self._movement

	def get_antenna(self) -> str:
		"""SCPI: SCENario:LOCalized:RECeiver:ANTenna \n
		Snippet: value: str = driver.scenario.localized.receiver.get_antenna() \n
		Assigns an existing antenna pattern, see method RsPulseSeq.Antenna.catalog. \n
			:return: antenna: string
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:ANTenna?')
		return trim_str_response(response)

	def set_antenna(self, antenna: str) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:ANTenna \n
		Snippet: driver.scenario.localized.receiver.set_antenna(antenna = '1') \n
		Assigns an existing antenna pattern, see method RsPulseSeq.Antenna.catalog. \n
			:param antenna: string
		"""
		param = Conversions.value_to_quoted_str(antenna)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:ANTenna {param}')

	def get_bm(self) -> str:
		"""SCPI: SCENario:LOCalized:RECeiver:BM \n
		Snippet: value: str = driver.scenario.localized.receiver.get_bm() \n
		No command help available \n
			:return: bm: No help available
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:BM?')
		return trim_str_response(response)

	def set_bm(self, bm: str) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:BM \n
		Snippet: driver.scenario.localized.receiver.set_bm(bm = '1') \n
		No command help available \n
			:param bm: No help available
		"""
		param = Conversions.value_to_quoted_str(bm)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:BM {param}')

	def get_gain(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:GAIN \n
		Snippet: value: float = driver.scenario.localized.receiver.get_gain() \n
		Sets the antenna . \n
			:return: gain: float Range: -120 to 120
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:GAIN?')
		return Conversions.str_to_float(response)

	def set_gain(self, gain: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:GAIN \n
		Snippet: driver.scenario.localized.receiver.set_gain(gain = 1.0) \n
		Sets the antenna . \n
			:param gain: float Range: -120 to 120
		"""
		param = Conversions.decimal_value_to_str(gain)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:GAIN {param}')

	def get_height(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:HEIGht \n
		Snippet: value: float = driver.scenario.localized.receiver.get_height() \n
		Sets the height of the antenna. \n
			:return: height: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:HEIGht?')
		return Conversions.str_to_float(response)

	def set_height(self, height: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:HEIGht \n
		Snippet: driver.scenario.localized.receiver.set_height(height = 1.0) \n
		Sets the height of the antenna. \n
			:param height: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(height)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:HEIGht {param}')

	def get_latitude(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:LATitude \n
		Snippet: value: float = driver.scenario.localized.receiver.get_latitude() \n
		Sets the latitude/longitude coordinates of the static receiver. \n
			:return: latitude: No help available
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:LATitude?')
		return Conversions.str_to_float(response)

	def set_latitude(self, latitude: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:LATitude \n
		Snippet: driver.scenario.localized.receiver.set_latitude(latitude = 1.0) \n
		Sets the latitude/longitude coordinates of the static receiver. \n
			:param latitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(latitude)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:LATitude {param}')

	def get_longitude(self) -> float:
		"""SCPI: SCENario:LOCalized:RECeiver:LONGitude \n
		Snippet: value: float = driver.scenario.localized.receiver.get_longitude() \n
		Sets the latitude/longitude coordinates of the static receiver. \n
			:return: longitude: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:LONGitude?')
		return Conversions.str_to_float(response)

	def set_longitude(self, longitude: float) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:LONGitude \n
		Snippet: driver.scenario.localized.receiver.set_longitude(longitude = 1.0) \n
		Sets the latitude/longitude coordinates of the static receiver. \n
			:param longitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(longitude)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:LONGitude {param}')

	def get_scan(self) -> str:
		"""SCPI: SCENario:LOCalized:RECeiver:SCAN \n
		Snippet: value: str = driver.scenario.localized.receiver.get_scan() \n
		Assigns an existing antenna scan, see method RsPulseSeq.Scan.catalog. \n
			:return: scan: string
		"""
		response = self._core.io.query_str('SCENario:LOCalized:RECeiver:SCAN?')
		return trim_str_response(response)

	def set_scan(self, scan: str) -> None:
		"""SCPI: SCENario:LOCalized:RECeiver:SCAN \n
		Snippet: driver.scenario.localized.receiver.set_scan(scan = '1') \n
		Assigns an existing antenna scan, see method RsPulseSeq.Scan.catalog. \n
			:param scan: string
		"""
		param = Conversions.value_to_quoted_str(scan)
		self._core.io.write(f'SCENario:LOCalized:RECeiver:SCAN {param}')

	def clone(self) -> 'Receiver':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Receiver(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
