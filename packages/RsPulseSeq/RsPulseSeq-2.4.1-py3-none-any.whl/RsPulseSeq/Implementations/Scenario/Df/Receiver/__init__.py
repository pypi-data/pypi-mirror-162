from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Receiver:
	"""Receiver commands group definition. 30 total commands, 2 Subgroups, 4 group commands"""

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

	def get_height(self) -> float:
		"""SCPI: SCENario:DF:RECeiver:HEIGht \n
		Snippet: value: float = driver.scenario.df.receiver.get_height() \n
		Sets the height of the antenna. \n
			:return: height: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('SCENario:DF:RECeiver:HEIGht?')
		return Conversions.str_to_float(response)

	def set_height(self, height: float) -> None:
		"""SCPI: SCENario:DF:RECeiver:HEIGht \n
		Snippet: driver.scenario.df.receiver.set_height(height = 1.0) \n
		Sets the height of the antenna. \n
			:param height: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(height)
		self._core.io.write(f'SCENario:DF:RECeiver:HEIGht {param}')

	def get_latitude(self) -> float:
		"""SCPI: SCENario:DF:RECeiver:LATitude \n
		Snippet: value: float = driver.scenario.df.receiver.get_latitude() \n
		Sets the latitude/longitude coordinates of the static receiver. \n
			:return: latitude: No help available
		"""
		response = self._core.io.query_str('SCENario:DF:RECeiver:LATitude?')
		return Conversions.str_to_float(response)

	def set_latitude(self, latitude: float) -> None:
		"""SCPI: SCENario:DF:RECeiver:LATitude \n
		Snippet: driver.scenario.df.receiver.set_latitude(latitude = 1.0) \n
		Sets the latitude/longitude coordinates of the static receiver. \n
			:param latitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(latitude)
		self._core.io.write(f'SCENario:DF:RECeiver:LATitude {param}')

	def get_longitude(self) -> float:
		"""SCPI: SCENario:DF:RECeiver:LONGitude \n
		Snippet: value: float = driver.scenario.df.receiver.get_longitude() \n
		Sets the latitude/longitude coordinates of the static receiver. \n
			:return: longitude: float Range: -180 to 180
		"""
		response = self._core.io.query_str('SCENario:DF:RECeiver:LONGitude?')
		return Conversions.str_to_float(response)

	def set_longitude(self, longitude: float) -> None:
		"""SCPI: SCENario:DF:RECeiver:LONGitude \n
		Snippet: driver.scenario.df.receiver.set_longitude(longitude = 1.0) \n
		Sets the latitude/longitude coordinates of the static receiver. \n
			:param longitude: float Range: -180 to 180
		"""
		param = Conversions.decimal_value_to_str(longitude)
		self._core.io.write(f'SCENario:DF:RECeiver:LONGitude {param}')

	def get_value(self) -> str:
		"""SCPI: SCENario:DF:RECeiver \n
		Snippet: value: str = driver.scenario.df.receiver.get_value() \n
		Selects an existing receiver, see method RsPulseSeq.Receiver.catalog. \n
			:return: receiver: string
		"""
		response = self._core.io.query_str('SCENario:DF:RECeiver?')
		return trim_str_response(response)

	def set_value(self, receiver: str) -> None:
		"""SCPI: SCENario:DF:RECeiver \n
		Snippet: driver.scenario.df.receiver.set_value(receiver = '1') \n
		Selects an existing receiver, see method RsPulseSeq.Receiver.catalog. \n
			:param receiver: string
		"""
		param = Conversions.value_to_quoted_str(receiver)
		self._core.io.write(f'SCENario:DF:RECeiver {param}')

	def clone(self) -> 'Receiver':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Receiver(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
