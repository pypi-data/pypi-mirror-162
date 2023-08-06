from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Bpsk:
	"""Bpsk commands group definition. 6 total commands, 1 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bpsk", core, parent)

	@property
	def symbolRate(self):
		"""symbolRate commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_symbolRate'):
			from .SymbolRate import SymbolRate
			self._symbolRate = SymbolRate(self._core, self._cmd_group)
		return self._symbolRate

	def get_phase(self) -> float:
		"""SCPI: PULSe:MOP:BPSK:PHASe \n
		Snippet: value: float = driver.pulse.mop.bpsk.get_phase() \n
		Sets the phase. \n
			:return: phase: float Range: 0.1 to 180, Unit: degree
		"""
		response = self._core.io.query_str('PULSe:MOP:BPSK:PHASe?')
		return Conversions.str_to_float(response)

	def set_phase(self, phase: float) -> None:
		"""SCPI: PULSe:MOP:BPSK:PHASe \n
		Snippet: driver.pulse.mop.bpsk.set_phase(phase = 1.0) \n
		Sets the phase. \n
			:param phase: float Range: 0.1 to 180, Unit: degree
		"""
		param = Conversions.decimal_value_to_str(phase)
		self._core.io.write(f'PULSe:MOP:BPSK:PHASe {param}')

	def get_ttime(self) -> float:
		"""SCPI: PULSe:MOP:BPSK:TTIMe \n
		Snippet: value: float = driver.pulse.mop.bpsk.get_ttime() \n
		Sets the transition time. \n
			:return: ttime: float Range: 0 to 50, Unit: percent
		"""
		response = self._core.io.query_str('PULSe:MOP:BPSK:TTIMe?')
		return Conversions.str_to_float(response)

	def set_ttime(self, ttime: float) -> None:
		"""SCPI: PULSe:MOP:BPSK:TTIMe \n
		Snippet: driver.pulse.mop.bpsk.set_ttime(ttime = 1.0) \n
		Sets the transition time. \n
			:param ttime: float Range: 0 to 50, Unit: percent
		"""
		param = Conversions.decimal_value_to_str(ttime)
		self._core.io.write(f'PULSe:MOP:BPSK:TTIMe {param}')

	# noinspection PyTypeChecker
	def get_ttype(self) -> enums.BpskTtype:
		"""SCPI: PULSe:MOP:BPSK:TTYPe \n
		Snippet: value: enums.BpskTtype = driver.pulse.mop.bpsk.get_ttype() \n
		Selects the transition type. \n
			:return: ttype: LINear| COSine
		"""
		response = self._core.io.query_str('PULSe:MOP:BPSK:TTYPe?')
		return Conversions.str_to_scalar_enum(response, enums.BpskTtype)

	def set_ttype(self, ttype: enums.BpskTtype) -> None:
		"""SCPI: PULSe:MOP:BPSK:TTYPe \n
		Snippet: driver.pulse.mop.bpsk.set_ttype(ttype = enums.BpskTtype.COSine) \n
		Selects the transition type. \n
			:param ttype: LINear| COSine
		"""
		param = Conversions.enum_scalar_to_str(ttype, enums.BpskTtype)
		self._core.io.write(f'PULSe:MOP:BPSK:TTYPe {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.BpskType:
		"""SCPI: PULSe:MOP:BPSK:TYPE \n
		Snippet: value: enums.BpskType = driver.pulse.mop.bpsk.get_type_py() \n
		Sets the modulation type. \n
			:return: type_py: STANdard| CONStant
		"""
		response = self._core.io.query_str('PULSe:MOP:BPSK:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.BpskType)

	def set_type_py(self, type_py: enums.BpskType) -> None:
		"""SCPI: PULSe:MOP:BPSK:TYPE \n
		Snippet: driver.pulse.mop.bpsk.set_type_py(type_py = enums.BpskType.CONStant) \n
		Sets the modulation type. \n
			:param type_py: STANdard| CONStant
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.BpskType)
		self._core.io.write(f'PULSe:MOP:BPSK:TYPE {param}')

	def clone(self) -> 'Bpsk':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Bpsk(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
