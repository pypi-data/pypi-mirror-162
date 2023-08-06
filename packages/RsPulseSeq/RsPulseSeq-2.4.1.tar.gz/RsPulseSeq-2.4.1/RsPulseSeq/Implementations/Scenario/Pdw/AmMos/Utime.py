from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Utime:
	"""Utime commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("utime", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: SCENario:PDW:AMMos:UTIMe:ENABle \n
		Snippet: value: bool = driver.scenario.pdw.amMos.utime.get_enable() \n
		Defines how the report start time is set. \n
			:return: enable: ON| OFF| 1| 0 0 The reporting start time is time at that the scenario calculation starts. 1 The reporting starts at user-defined moment, set with the command method RsPulseSeq.Scenario.Pdw.AmMos.Utime.iso.
		"""
		response = self._core.io.query_str('SCENario:PDW:AMMos:UTIMe:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:PDW:AMMos:UTIMe:ENABle \n
		Snippet: driver.scenario.pdw.amMos.utime.set_enable(enable = False) \n
		Defines how the report start time is set. \n
			:param enable: ON| OFF| 1| 0 0 The reporting start time is time at that the scenario calculation starts. 1 The reporting starts at user-defined moment, set with the command method RsPulseSeq.Scenario.Pdw.AmMos.Utime.iso.
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:PDW:AMMos:UTIMe:ENABle {param}')

	def get_iso(self) -> str:
		"""SCPI: SCENario:PDW:AMMos:UTIMe:ISO \n
		Snippet: value: str = driver.scenario.pdw.amMos.utime.get_iso() \n
		Sets the reporting start time, if method RsPulseSeq.Scenario.Pdw.AmMos.Utime.enable1. \n
			:return: iso: 'YYYY-Month-DDTHH:MM:SS'
		"""
		response = self._core.io.query_str('SCENario:PDW:AMMos:UTIMe:ISO?')
		return trim_str_response(response)

	def set_iso(self, iso: str) -> None:
		"""SCPI: SCENario:PDW:AMMos:UTIMe:ISO \n
		Snippet: driver.scenario.pdw.amMos.utime.set_iso(iso = '1') \n
		Sets the reporting start time, if method RsPulseSeq.Scenario.Pdw.AmMos.Utime.enable1. \n
			:param iso: 'YYYY-Month-DDTHH:MM:SS'
		"""
		param = Conversions.value_to_quoted_str(iso)
		self._core.io.write(f'SCENario:PDW:AMMos:UTIMe:ISO {param}')
