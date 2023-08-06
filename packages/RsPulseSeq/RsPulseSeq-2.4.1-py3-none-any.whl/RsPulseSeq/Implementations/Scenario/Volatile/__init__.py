from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Volatile:
	"""Volatile commands group definition. 6 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("volatile", core, parent)

	@property
	def view(self):
		"""view commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_view'):
			from .View import View
			self._view = View(self._core, self._cmd_group)
		return self._view

	def get_sel(self) -> float:
		"""SCPI: SCENario:VOLatile:SEL \n
		Snippet: value: float = driver.scenario.volatile.get_sel() \n
		If several files are created, select the one to be visualized. \n
			:return: sel: float Subsequent number, indicating the files in the volatile memory.
		"""
		response = self._core.io.query_str('SCENario:VOLatile:SEL?')
		return Conversions.str_to_float(response)

	def set_sel(self, sel: float) -> None:
		"""SCPI: SCENario:VOLatile:SEL \n
		Snippet: driver.scenario.volatile.set_sel(sel = 1.0) \n
		If several files are created, select the one to be visualized. \n
			:param sel: float Subsequent number, indicating the files in the volatile memory.
		"""
		param = Conversions.decimal_value_to_str(sel)
		self._core.io.write(f'SCENario:VOLatile:SEL {param}')

	def clone(self) -> 'Volatile':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Volatile(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
