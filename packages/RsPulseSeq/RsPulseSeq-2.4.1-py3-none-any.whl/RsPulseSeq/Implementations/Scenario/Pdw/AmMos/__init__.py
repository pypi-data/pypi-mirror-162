from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AmMos:
	"""AmMos commands group definition. 5 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("amMos", core, parent)

	@property
	def utime(self):
		"""utime commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_utime'):
			from .Utime import Utime
			self._utime = Utime(self._core, self._cmd_group)
		return self._utime

	# noinspection PyTypeChecker
	def get_azimuth(self) -> enums.Azimuth:
		"""SCPI: SCENario:PDW:AMMos:AZIMuth \n
		Snippet: value: enums.Azimuth = driver.scenario.pdw.amMos.get_azimuth() \n
		For method RsPulseSeq.Scenario.Pdw.typePyAMMos, defines whether the angle of the Rx antenna or the bearing is reported. \n
			:return: azimuth: RX| BEARing
		"""
		response = self._core.io.query_str('SCENario:PDW:AMMos:AZIMuth?')
		return Conversions.str_to_scalar_enum(response, enums.Azimuth)

	def set_azimuth(self, azimuth: enums.Azimuth) -> None:
		"""SCPI: SCENario:PDW:AMMos:AZIMuth \n
		Snippet: driver.scenario.pdw.amMos.set_azimuth(azimuth = enums.Azimuth.BEARing) \n
		For method RsPulseSeq.Scenario.Pdw.typePyAMMos, defines whether the angle of the Rx antenna or the bearing is reported. \n
			:param azimuth: RX| BEARing
		"""
		param = Conversions.enum_scalar_to_str(azimuth, enums.Azimuth)
		self._core.io.write(f'SCENario:PDW:AMMos:AZIMuth {param}')

	def get_frame(self) -> float:
		"""SCPI: SCENario:PDW:AMMos:FRAMe \n
		Snippet: value: float = driver.scenario.pdw.amMos.get_frame() \n
		Sets the frame length. \n
			:return: frame: float Range: 50 to 500
		"""
		response = self._core.io.query_str('SCENario:PDW:AMMos:FRAMe?')
		return Conversions.str_to_float(response)

	def set_frame(self, frame: float) -> None:
		"""SCPI: SCENario:PDW:AMMos:FRAMe \n
		Snippet: driver.scenario.pdw.amMos.set_frame(frame = 1.0) \n
		Sets the frame length. \n
			:param frame: float Range: 50 to 500
		"""
		param = Conversions.decimal_value_to_str(frame)
		self._core.io.write(f'SCENario:PDW:AMMos:FRAMe {param}')

	def get_ppdw(self) -> bool:
		"""SCPI: SCENario:PDW:AMMos:PPDW \n
		Snippet: value: bool = driver.scenario.pdw.amMos.get_ppdw() \n
		If enabled, the format of the AMMOS file is set to PPDW. Otherwise PDW is assumed. \n
			:return: ppdw: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:PDW:AMMos:PPDW?')
		return Conversions.str_to_bool(response)

	def set_ppdw(self, ppdw: bool) -> None:
		"""SCPI: SCENario:PDW:AMMos:PPDW \n
		Snippet: driver.scenario.pdw.amMos.set_ppdw(ppdw = False) \n
		If enabled, the format of the AMMOS file is set to PPDW. Otherwise PDW is assumed. \n
			:param ppdw: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(ppdw)
		self._core.io.write(f'SCENario:PDW:AMMos:PPDW {param}')

	def clone(self) -> 'AmMos':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AmMos(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
