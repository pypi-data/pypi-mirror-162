from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IpmPlot:
	"""IpmPlot commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ipmPlot", core, parent)

	def set_samples(self, samples: float) -> None:
		"""SCPI: DIALog:IPMPlot:SAMPles \n
		Snippet: driver.dialog.ipmPlot.set_samples(samples = 1.0) \n
		Sets the number of values to be displayed in the preview diagram of the IPM profile. \n
			:param samples: float
		"""
		param = Conversions.decimal_value_to_str(samples)
		self._core.io.write(f'DIALog:IPMPlot:SAMPles {param}')

	def set_view(self, view: enums.IpmPlotView) -> None:
		"""SCPI: DIALog:IPMPlot:VIEW \n
		Snippet: driver.dialog.ipmPlot.set_view(view = enums.IpmPlotView.HISTogram) \n
		Defines what kind of information is represented in the IPM profile diagram. \n
			:param view: TIMeseries| HISTogram TIMeseries Visualization of the profile variation over time HISTogram Statistical representation of the relative frequency density
		"""
		param = Conversions.enum_scalar_to_str(view, enums.IpmPlotView)
		self._core.io.write(f'DIALog:IPMPlot:VIEW {param}')
