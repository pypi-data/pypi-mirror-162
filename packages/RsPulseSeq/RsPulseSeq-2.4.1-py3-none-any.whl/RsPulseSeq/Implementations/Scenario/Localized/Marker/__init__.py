from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Marker:
	"""Marker commands group definition. 10 total commands, 1 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("marker", core, parent)

	@property
	def time(self):
		"""time commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_time'):
			from .Time import Time
			self._time = Time(self._core, self._cmd_group)
		return self._time

	def get_auto(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:AUTO \n
		Snippet: value: float = driver.scenario.localized.marker.get_auto() \n
		Enables the marker for restart. \n
			:return: auto: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:AUTO?')
		return Conversions.str_to_float(response)

	def set_auto(self, auto: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:AUTO \n
		Snippet: driver.scenario.localized.marker.set_auto(auto = 1.0) \n
		Enables the marker for restart. \n
			:param auto: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(auto)
		self._core.io.write(f'SCENario:LOCalized:MARKer:AUTO {param}')

	def get_fall(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:FALL \n
		Snippet: value: float = driver.scenario.localized.marker.get_fall() \n
		Enables the marker for fall time. \n
			:return: fall: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:FALL?')
		return Conversions.str_to_float(response)

	def set_fall(self, fall: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:FALL \n
		Snippet: driver.scenario.localized.marker.set_fall(fall = 1.0) \n
		Enables the marker for fall time. \n
			:param fall: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(fall)
		self._core.io.write(f'SCENario:LOCalized:MARKer:FALL {param}')

	def get_force(self) -> bool:
		"""SCPI: SCENario:LOCalized:MARKer:FORCe \n
		Snippet: value: bool = driver.scenario.localized.marker.get_force() \n
		Determines how the marker is handled. \n
			:return: force: ON| OFF| 1| 0 ON | 1 Forces the selected marker type for every pulse of the selected emitter OFF | 0 Leaves the marker unchanged, as defined in the pulses and sequences of this emitter.
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:FORCe?')
		return Conversions.str_to_bool(response)

	def set_force(self, force: bool) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:FORCe \n
		Snippet: driver.scenario.localized.marker.set_force(force = False) \n
		Determines how the marker is handled. \n
			:param force: ON| OFF| 1| 0 ON | 1 Forces the selected marker type for every pulse of the selected emitter OFF | 0 Leaves the marker unchanged, as defined in the pulses and sequences of this emitter.
		"""
		param = Conversions.bool_to_str(force)
		self._core.io.write(f'SCENario:LOCalized:MARKer:FORCe {param}')

	def get_gate(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:GATE \n
		Snippet: value: float = driver.scenario.localized.marker.get_gate() \n
		Enables marker for gate. \n
			:return: gate: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:GATE?')
		return Conversions.str_to_float(response)

	def set_gate(self, gate: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:GATE \n
		Snippet: driver.scenario.localized.marker.set_gate(gate = 1.0) \n
		Enables marker for gate. \n
			:param gate: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(gate)
		self._core.io.write(f'SCENario:LOCalized:MARKer:GATE {param}')

	def get_post(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:POST \n
		Snippet: value: float = driver.scenario.localized.marker.get_post() \n
		Enables marker for post time. \n
			:return: post: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:POST?')
		return Conversions.str_to_float(response)

	def set_post(self, post: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:POST \n
		Snippet: driver.scenario.localized.marker.set_post(post = 1.0) \n
		Enables marker for post time. \n
			:param post: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(post)
		self._core.io.write(f'SCENario:LOCalized:MARKer:POST {param}')

	def get_pre(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:PRE \n
		Snippet: value: float = driver.scenario.localized.marker.get_pre() \n
		Enables marker for pre time. \n
			:return: pre: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:PRE?')
		return Conversions.str_to_float(response)

	def set_pre(self, pre: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:PRE \n
		Snippet: driver.scenario.localized.marker.set_pre(pre = 1.0) \n
		Enables marker for pre time. \n
			:param pre: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(pre)
		self._core.io.write(f'SCENario:LOCalized:MARKer:PRE {param}')

	def get_rise(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:RISE \n
		Snippet: value: float = driver.scenario.localized.marker.get_rise() \n
		Enables marker for rise time. \n
			:return: rise: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:RISE?')
		return Conversions.str_to_float(response)

	def set_rise(self, rise: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:RISE \n
		Snippet: driver.scenario.localized.marker.set_rise(rise = 1.0) \n
		Enables marker for rise time. \n
			:param rise: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(rise)
		self._core.io.write(f'SCENario:LOCalized:MARKer:RISE {param}')

	def get_width(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:WIDTh \n
		Snippet: value: float = driver.scenario.localized.marker.get_width() \n
		Sets marker for the pulse width. \n
			:return: width: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:WIDTh?')
		return Conversions.str_to_float(response)

	def set_width(self, width: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:WIDTh \n
		Snippet: driver.scenario.localized.marker.set_width(width = 1.0) \n
		Sets marker for the pulse width. \n
			:param width: float Binary value, where: M1 = 1 M1 = 2 M1 = 4 M1 = 8 Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(width)
		self._core.io.write(f'SCENario:LOCalized:MARKer:WIDTh {param}')

	def clone(self) -> 'Marker':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Marker(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
