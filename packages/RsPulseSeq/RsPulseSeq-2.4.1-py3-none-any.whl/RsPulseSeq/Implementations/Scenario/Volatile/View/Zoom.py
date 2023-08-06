from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Zoom:
	"""Zoom commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("zoom", core, parent)

	def set_point(self, point: float) -> None:
		"""SCPI: SCENario:VOLatile:VIEW:ZOOM:POINt \n
		Snippet: driver.scenario.volatile.view.zoom.set_point(point = 1.0) \n
		Sets center point of the displayed area. \n
			:param point: float Always related to time Unit: s
		"""
		param = Conversions.decimal_value_to_str(point)
		self._core.io.write(f'SCENario:VOLatile:VIEW:ZOOM:POINt {param}')

	def set_range(self, range_py: float) -> None:
		"""SCPI: SCENario:VOLatile:VIEW:ZOOM:RANGe \n
		Snippet: driver.scenario.volatile.view.zoom.set_range(range_py = 1.0) \n
		Sets the displayed waveform part as a range around the selected center point, set with the command method RsPulseSeq.
		Scenario.Volatile.View.Zoom.point. \n
			:param range_py: float Expressed as a time span (units can be omitted) or as number of samples
		"""
		param = Conversions.decimal_value_to_str(range_py)
		self._core.io.write(f'SCENario:VOLatile:VIEW:ZOOM:RANGe {param}')
