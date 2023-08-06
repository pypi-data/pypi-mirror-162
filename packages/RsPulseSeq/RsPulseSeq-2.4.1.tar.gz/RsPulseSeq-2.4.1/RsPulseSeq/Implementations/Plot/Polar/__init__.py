from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Polar:
	"""Polar commands group definition. 3 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("polar", core, parent)

	@property
	def log(self):
		"""log commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_log'):
			from .Log import Log
			self._log = Log(self._core, self._cmd_group)
		return self._log

	def set_cut(self, cut: enums.PolarCut) -> None:
		"""SCPI: PLOT:POLar:CUT \n
		Snippet: driver.plot.polar.set_cut(cut = enums.PolarCut.XY) \n
		Sets the diagram cut. \n
			:param cut: XY| YZ
		"""
		param = Conversions.enum_scalar_to_str(cut, enums.PolarCut)
		self._core.io.write(f'PLOT:POLar:CUT {param}')

	def set_type_py(self, type_py: enums.PolarType) -> None:
		"""SCPI: PLOT:POLar:TYPE \n
		Snippet: driver.plot.polar.set_type_py(type_py = enums.PolarType.CARTesian) \n
		Sets the coordinates of the 2D antenna pattern diagram. \n
			:param type_py: POLar| CARTesian
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.PolarType)
		self._core.io.write(f'PLOT:POLar:TYPE {param}')

	def clone(self) -> 'Polar':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Polar(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
