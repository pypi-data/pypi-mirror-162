from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Item:
	"""Item commands group definition. 56 total commands, 10 Subgroups, 11 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("item", core, parent)

	@property
	def add(self):
		"""add commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_add'):
			from .Add import Add
			self._add = Add(self._core, self._cmd_group)
		return self._add

	@property
	def filler(self):
		"""filler commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_filler'):
			from .Filler import Filler
			self._filler = Filler(self._core, self._cmd_group)
		return self._filler

	@property
	def frequency(self):
		"""frequency commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import Frequency
			self._frequency = Frequency(self._core, self._cmd_group)
		return self._frequency

	@property
	def ipm(self):
		"""ipm commands group. 4 Sub-classes, 6 commands."""
		if not hasattr(self, '_ipm'):
			from .Ipm import Ipm
			self._ipm = Ipm(self._core, self._cmd_group)
		return self._ipm

	@property
	def level(self):
		"""level commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_level'):
			from .Level import Level
			self._level = Level(self._core, self._cmd_group)
		return self._level

	@property
	def loop(self):
		"""loop commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_loop'):
			from .Loop import Loop
			self._loop = Loop(self._core, self._cmd_group)
		return self._loop

	@property
	def marker(self):
		"""marker commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_marker'):
			from .Marker import Marker
			self._marker = Marker(self._core, self._cmd_group)
		return self._marker

	@property
	def ovl(self):
		"""ovl commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_ovl'):
			from .Ovl import Ovl
			self._ovl = Ovl(self._core, self._cmd_group)
		return self._ovl

	@property
	def phase(self):
		"""phase commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_phase'):
			from .Phase import Phase
			self._phase = Phase(self._core, self._cmd_group)
		return self._phase

	@property
	def rep(self):
		"""rep commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_rep'):
			from .Rep import Rep
			self._rep = Rep(self._core, self._cmd_group)
		return self._rep

	def clear(self) -> None:
		"""SCPI: SEQuence:ITEM:CLEar \n
		Snippet: driver.sequence.item.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SEQuence:ITEM:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SEQuence:ITEM:CLEar \n
		Snippet: driver.sequence.item.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SEQuence:ITEM:CLEar', opc_timeout_ms)

	def get_count(self) -> float:
		"""SCPI: SEQuence:ITEM:COUNt \n
		Snippet: value: float = driver.sequence.item.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('SEQuence:ITEM:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: SEQuence:ITEM:DELete \n
		Snippet: driver.sequence.item.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'SEQuence:ITEM:DELete {param}')

	def get_indent(self) -> float:
		"""SCPI: SEQuence:ITEM:INDent \n
		Snippet: value: float = driver.sequence.item.get_indent() \n
		Indents the selected item rows to include it, for example, in a loop. \n
			:return: indent: float Range: 0 to 5
		"""
		response = self._core.io.query_str('SEQuence:ITEM:INDent?')
		return Conversions.str_to_float(response)

	def set_indent(self, indent: float) -> None:
		"""SCPI: SEQuence:ITEM:INDent \n
		Snippet: driver.sequence.item.set_indent(indent = 1.0) \n
		Indents the selected item rows to include it, for example, in a loop. \n
			:param indent: float Range: 0 to 5
		"""
		param = Conversions.decimal_value_to_str(indent)
		self._core.io.write(f'SEQuence:ITEM:INDent {param}')

	def get_pdelay(self) -> float:
		"""SCPI: SEQuence:ITEM:PDELay \n
		Snippet: value: float = driver.sequence.item.get_pdelay() \n
		Enables a start delay. \n
			:return: pdelay: float Range: 0 to 1e+09, Unit: sec
		"""
		response = self._core.io.query_str('SEQuence:ITEM:PDELay?')
		return Conversions.str_to_float(response)

	def set_pdelay(self, pdelay: float) -> None:
		"""SCPI: SEQuence:ITEM:PDELay \n
		Snippet: driver.sequence.item.set_pdelay(pdelay = 1.0) \n
		Enables a start delay. \n
			:param pdelay: float Range: 0 to 1e+09, Unit: sec
		"""
		param = Conversions.decimal_value_to_str(pdelay)
		self._core.io.write(f'SEQuence:ITEM:PDELay {param}')

	def get_prf(self) -> float:
		"""SCPI: SEQuence:ITEM:PRF \n
		Snippet: value: float = driver.sequence.item.get_prf() \n
		Sets the pulse repetition interval (PRI) or the pulse repetition frequency (PRF) . \n
			:return: prf: No help available
		"""
		response = self._core.io.query_str('SEQuence:ITEM:PRF?')
		return Conversions.str_to_float(response)

	def set_prf(self, prf: float) -> None:
		"""SCPI: SEQuence:ITEM:PRF \n
		Snippet: driver.sequence.item.set_prf(prf = 1.0) \n
		Sets the pulse repetition interval (PRI) or the pulse repetition frequency (PRF) . \n
			:param prf: float Range: 0 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(prf)
		self._core.io.write(f'SEQuence:ITEM:PRF {param}')

	def get_pri(self) -> float:
		"""SCPI: SEQuence:ITEM:PRI \n
		Snippet: value: float = driver.sequence.item.get_pri() \n
		Sets the pulse repetition interval (PRI) or the pulse repetition frequency (PRF) . \n
			:return: pri: float Range: 0 to 1e+09
		"""
		response = self._core.io.query_str('SEQuence:ITEM:PRI?')
		return Conversions.str_to_float(response)

	def set_pri(self, pri: float) -> None:
		"""SCPI: SEQuence:ITEM:PRI \n
		Snippet: driver.sequence.item.set_pri(pri = 1.0) \n
		Sets the pulse repetition interval (PRI) or the pulse repetition frequency (PRF) . \n
			:param pri: float Range: 0 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(pri)
		self._core.io.write(f'SEQuence:ITEM:PRI {param}')

	def get_pulse(self) -> str:
		"""SCPI: SEQuence:ITEM:PULSe \n
		Snippet: value: str = driver.sequence.item.get_pulse() \n
		Assigns a pulse or a waveform to the selected item. Use the commands method RsPulseSeq.Pulse.
		catalog and method RsPulseSeq.Waveform.catalog to querry the available pulses and waveforms. \n
			:return: pulse: string Pulse name
		"""
		response = self._core.io.query_str('SEQuence:ITEM:PULSe?')
		return trim_str_response(response)

	def set_pulse(self, pulse: str) -> None:
		"""SCPI: SEQuence:ITEM:PULSe \n
		Snippet: driver.sequence.item.set_pulse(pulse = '1') \n
		Assigns a pulse or a waveform to the selected item. Use the commands method RsPulseSeq.Pulse.
		catalog and method RsPulseSeq.Waveform.catalog to querry the available pulses and waveforms. \n
			:param pulse: string Pulse name
		"""
		param = Conversions.value_to_quoted_str(pulse)
		self._core.io.write(f'SEQuence:ITEM:PULSe {param}')

	def get_select(self) -> float:
		"""SCPI: SEQuence:ITEM:SELect \n
		Snippet: value: float = driver.sequence.item.get_select() \n
		Selects the item to which the subsequent commands apply. \n
			:return: select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		response = self._core.io.query_str('SEQuence:ITEM:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SEQuence:ITEM:SELect \n
		Snippet: driver.sequence.item.set_select(select = 1.0) \n
		Selects the item to which the subsequent commands apply. \n
			:param select: float Item number within the range 1 to ...:COUNt. For example, method RsPulseSeq.Sequence.Item.count. Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SEQuence:ITEM:SELect {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.ItemType:
		"""SCPI: SEQuence:ITEM:TYPE \n
		Snippet: value: enums.ItemType = driver.sequence.item.get_type_py() \n
		Sets the content type of the selected item. \n
			:return: type_py: PULSe| FILLer| LOOP | | OVL| SUBSequence| WAVeform
		"""
		response = self._core.io.query_str('SEQuence:ITEM:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ItemType)

	def set_type_py(self, type_py: enums.ItemType) -> None:
		"""SCPI: SEQuence:ITEM:TYPE \n
		Snippet: driver.sequence.item.set_type_py(type_py = enums.ItemType.FILLer) \n
		Sets the content type of the selected item. \n
			:param type_py: PULSe| FILLer| LOOP | | OVL| SUBSequence| WAVeform
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.ItemType)
		self._core.io.write(f'SEQuence:ITEM:TYPE {param}')

	def get_waveform(self) -> str:
		"""SCPI: SEQuence:ITEM:WAVeform \n
		Snippet: value: str = driver.sequence.item.get_waveform() \n
		Assigns a pulse or a waveform to the selected item. Use the commands method RsPulseSeq.Pulse.
		catalog and method RsPulseSeq.Waveform.catalog to querry the available pulses and waveforms. \n
			:return: waveform: No help available
		"""
		response = self._core.io.query_str('SEQuence:ITEM:WAVeform?')
		return trim_str_response(response)

	def set_waveform(self, waveform: str) -> None:
		"""SCPI: SEQuence:ITEM:WAVeform \n
		Snippet: driver.sequence.item.set_waveform(waveform = '1') \n
		Assigns a pulse or a waveform to the selected item. Use the commands method RsPulseSeq.Pulse.
		catalog and method RsPulseSeq.Waveform.catalog to querry the available pulses and waveforms. \n
			:param waveform: string Pulse name
		"""
		param = Conversions.value_to_quoted_str(waveform)
		self._core.io.write(f'SEQuence:ITEM:WAVeform {param}')

	def clone(self) -> 'Item':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Item(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
