from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Filler:
	"""Filler commands group definition. 5 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("filler", core, parent)

	@property
	def time(self):
		"""time commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_time'):
			from .Time import Time
			self._time = Time(self._core, self._cmd_group)
		return self._time

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.FillerMode:
		"""SCPI: SEQuence:ITEM:FILLer:MODE \n
		Snippet: value: enums.FillerMode = driver.sequence.item.filler.get_mode() \n
		Sets how the filler duration is determined. \n
			:return: mode: DURation| TSYNc
		"""
		response = self._core.io.query_str('SEQuence:ITEM:FILLer:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.FillerMode)

	def set_mode(self, mode: enums.FillerMode) -> None:
		"""SCPI: SEQuence:ITEM:FILLer:MODE \n
		Snippet: driver.sequence.item.filler.set_mode(mode = enums.FillerMode.DURation) \n
		Sets how the filler duration is determined. \n
			:param mode: DURation| TSYNc
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.FillerMode)
		self._core.io.write(f'SEQuence:ITEM:FILLer:MODE {param}')

	# noinspection PyTypeChecker
	def get_signal(self) -> enums.FillerSignal:
		"""SCPI: SEQuence:ITEM:FILLer:SIGNal \n
		Snippet: value: enums.FillerSignal = driver.sequence.item.filler.get_signal() \n
		Sets the signal type. \n
			:return: signal: BLANk | | CW| HOLD
		"""
		response = self._core.io.query_str('SEQuence:ITEM:FILLer:SIGNal?')
		return Conversions.str_to_scalar_enum(response, enums.FillerSignal)

	def set_signal(self, signal: enums.FillerSignal) -> None:
		"""SCPI: SEQuence:ITEM:FILLer:SIGNal \n
		Snippet: driver.sequence.item.filler.set_signal(signal = enums.FillerSignal.BLANk) \n
		Sets the signal type. \n
			:param signal: BLANk | | CW| HOLD
		"""
		param = Conversions.enum_scalar_to_str(signal, enums.FillerSignal)
		self._core.io.write(f'SEQuence:ITEM:FILLer:SIGNal {param}')

	def clone(self) -> 'Filler':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Filler(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
