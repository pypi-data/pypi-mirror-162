from typing import List

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Instrument:
	"""Instrument commands group definition. 19 total commands, 1 Subgroups, 18 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("instrument", core, parent)

	@property
	def adb(self):
		"""adb commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_adb'):
			from .Adb import Adb
			self._adb = Adb(self._core, self._cmd_group)
		return self._adb

	def set_add(self, add: str) -> None:
		"""SCPI: INSTrument:ADD \n
		Snippet: driver.instrument.set_add(add = '1') \n
		Adds an instrument with the specified IP address, computer name, or the VISA resource string. \n
			:param add: string 'IP_Address' or 'Computer_Name' or 'GPIB_Address'
		"""
		param = Conversions.value_to_quoted_str(add)
		self._core.io.write(f'INSTrument:ADD {param}')

	def get_capabilities(self) -> str:
		"""SCPI: INSTrument:CAPabilities \n
		Snippet: value: str = driver.instrument.get_capabilities() \n
		Queries the generator capabilities regarding supported scenario types and processing of waveforms and multi-segment files. \n
			:return: capabilities: string
		"""
		response = self._core.io.query_str('INSTrument:CAPabilities?')
		return trim_str_response(response)

	def set_capabilities(self, capabilities: str) -> None:
		"""SCPI: INSTrument:CAPabilities \n
		Snippet: driver.instrument.set_capabilities(capabilities = '1') \n
		Queries the generator capabilities regarding supported scenario types and processing of waveforms and multi-segment files. \n
			:param capabilities: string
		"""
		param = Conversions.value_to_quoted_str(capabilities)
		self._core.io.write(f'INSTrument:CAPabilities {param}')

	def clear(self) -> None:
		"""SCPI: INSTrument:CLEar \n
		Snippet: driver.instrument.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'INSTrument:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: INSTrument:CLEar \n
		Snippet: driver.instrument.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'INSTrument:CLEar', opc_timeout_ms)

	def get_comment(self) -> str:
		"""SCPI: INSTrument:COMMent \n
		Snippet: value: str = driver.instrument.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('INSTrument:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: INSTrument:COMMent \n
		Snippet: driver.instrument.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'INSTrument:COMMent {param}')

	def set_connect(self, connect: str) -> None:
		"""SCPI: INSTrument:CONNect \n
		Snippet: driver.instrument.set_connect(connect = '1') \n
		Connects to the instrument defined by method RsPulseSeq.Instrument.select \n
			:param connect: string
		"""
		param = Conversions.value_to_quoted_str(connect)
		self._core.io.write(f'INSTrument:CONNect {param}')

	def get_count(self) -> float:
		"""SCPI: INSTrument:COUNt \n
		Snippet: value: float = driver.instrument.get_count() \n
		Queries the number of existing items. \n
			:return: count: integer
		"""
		response = self._core.io.query_str('INSTrument:COUNt?')
		return Conversions.str_to_float(response)

	def delete(self, delete: float) -> None:
		"""SCPI: INSTrument:DELete \n
		Snippet: driver.instrument.delete(delete = 1.0) \n
		Deletes the particular item. \n
			:param delete: float
		"""
		param = Conversions.decimal_value_to_str(delete)
		self._core.io.write(f'INSTrument:DELete {param}')

	def get_firmware(self) -> str:
		"""SCPI: INSTrument:FIRMware \n
		Snippet: value: str = driver.instrument.get_firmware() \n
		Queries the firmware version of the selected instrument. \n
			:return: firmware: string
		"""
		response = self._core.io.query_str('INSTrument:FIRMware?')
		return trim_str_response(response)

	def get_list_py(self) -> List[int]:
		"""SCPI: INSTrument:LIST \n
		Snippet: value: List[int] = driver.instrument.get_list_py() \n
		Queries the names of the signal generators that are connected to the R&S Pulse Sequencer in the current setup. See method
		RsPulseSeq.Setup.listPy. \n
			:return: list_py: 'Instr#1','Instr#2',...
		"""
		response = self._core.io.query_bin_or_ascii_int_list('INSTrument:LIST?')
		return response

	def get_name(self) -> str:
		"""SCPI: INSTrument:NAME \n
		Snippet: value: str = driver.instrument.get_name() \n
		Queries the name of the selected instrument. \n
			:return: name: string
		"""
		response = self._core.io.query_str('INSTrument:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: INSTrument:NAME \n
		Snippet: driver.instrument.set_name(name = '1') \n
		Queries the name of the selected instrument. \n
			:param name: string
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'INSTrument:NAME {param}')

	def get_online(self) -> float:
		"""SCPI: INSTrument:ONLine \n
		Snippet: value: float = driver.instrument.get_online() \n
		Queries the connection status of a physical signal generator. \n
			:return: online: float 0 Offline 1 Online
		"""
		response = self._core.io.query_str('INSTrument:ONLine?')
		return Conversions.str_to_float(response)

	def set_online(self, online: float) -> None:
		"""SCPI: INSTrument:ONLine \n
		Snippet: driver.instrument.set_online(online = 1.0) \n
		Queries the connection status of a physical signal generator. \n
			:param online: float 0 Offline 1 Online
		"""
		param = Conversions.decimal_value_to_str(online)
		self._core.io.write(f'INSTrument:ONLine {param}')

	# noinspection PyTypeChecker
	def get_pmod(self) -> enums.PmodSource:
		"""SCPI: INSTrument:PMOD \n
		Snippet: value: enums.PmodSource = driver.instrument.get_pmod() \n
		Select the marker source if pulse modulator is used, see method RsPulseSeq.Setup.Pmod.enable. \n
			:return: pmod: OFF| INTernal| EXTernal OFF Disables the function for the selected instrument. INTernal No additional cabling or configuration of marker signals is required. EXTernal Requires that: 1) the instruments are cabled according to the wiring diagram 2) high the clock rate is selected 3) pulse marker M2 is set to pulse width 4) sequence marker M2 is enabled 5) the generation of the dedicated marker signal is enabled
		"""
		response = self._core.io.query_str('INSTrument:PMOD?')
		return Conversions.str_to_scalar_enum(response, enums.PmodSource)

	def set_pmod(self, pmod: enums.PmodSource) -> None:
		"""SCPI: INSTrument:PMOD \n
		Snippet: driver.instrument.set_pmod(pmod = enums.PmodSource.EXTernal) \n
		Select the marker source if pulse modulator is used, see method RsPulseSeq.Setup.Pmod.enable. \n
			:param pmod: OFF| INTernal| EXTernal OFF Disables the function for the selected instrument. INTernal No additional cabling or configuration of marker signals is required. EXTernal Requires that: 1) the instruments are cabled according to the wiring diagram 2) high the clock rate is selected 3) pulse marker M2 is set to pulse width 4) sequence marker M2 is enabled 5) the generation of the dedicated marker signal is enabled
		"""
		param = Conversions.enum_scalar_to_str(pmod, enums.PmodSource)
		self._core.io.write(f'INSTrument:PMOD {param}')

	# noinspection PyTypeChecker
	def get_psec(self) -> enums.Psec:
		"""SCPI: INSTrument:PSEC \n
		Snippet: value: enums.Psec = driver.instrument.get_psec() \n
		Sets the Primary/Secondary order in synchronized setups. \n
			:return: psec: NONE| PRIMary| SEC1| SEC2| SEC3| SEC4| SEC5| SEC6| SEC7| SEC8| SEC9| SEC10| SEC11| SEC12| SEC13| SEC14| SEC15| SEC16 NONE Unsynchronized instrument. PRIMary The primary instrument. SEC1 Denotes the secondary instruments.
		"""
		response = self._core.io.query_str('INSTrument:PSEC?')
		return Conversions.str_to_scalar_enum(response, enums.Psec)

	def set_psec(self, psec: enums.Psec) -> None:
		"""SCPI: INSTrument:PSEC \n
		Snippet: driver.instrument.set_psec(psec = enums.Psec.NONE) \n
		Sets the Primary/Secondary order in synchronized setups. \n
			:param psec: NONE| PRIMary| SEC1| SEC2| SEC3| SEC4| SEC5| SEC6| SEC7| SEC8| SEC9| SEC10| SEC11| SEC12| SEC13| SEC14| SEC15| SEC16 NONE Unsynchronized instrument. PRIMary The primary instrument. SEC1 Denotes the secondary instruments.
		"""
		param = Conversions.enum_scalar_to_str(psec, enums.Psec)
		self._core.io.write(f'INSTrument:PSEC {param}')

	def get_resource(self) -> str:
		"""SCPI: INSTrument:RESource \n
		Snippet: value: str = driver.instrument.get_resource() \n
		Queries the resource string of the instrument selected with the command method RsPulseSeq.Instrument.select. \n
			:return: resource: string
		"""
		response = self._core.io.query_str('INSTrument:RESource?')
		return trim_str_response(response)

	def get_select(self) -> float:
		"""SCPI: INSTrument:SELect \n
		Snippet: value: float = driver.instrument.get_select() \n
		Selects the element to which the subsequent commands apply. \n
			:return: select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		response = self._core.io.query_str('INSTrument:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: INSTrument:SELect \n
		Snippet: driver.instrument.set_select(select = 1.0) \n
		Selects the element to which the subsequent commands apply. \n
			:param select: string Available element as queried with the corresponding ...:LIST command. For example, method RsPulseSeq.Assignment.Generator.Path.Antenna.listPy
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'INSTrument:SELect {param}')

	def get_supported(self) -> float:
		"""SCPI: INSTrument:SUPPorted \n
		Snippet: value: float = driver.instrument.get_supported() \n
		Queries the supported status. \n
			:return: supported: 0| 1 1 Supported 0 Not supported
		"""
		response = self._core.io.query_str('INSTrument:SUPPorted?')
		return Conversions.str_to_float(response)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.GeneratorType:
		"""SCPI: INSTrument:TYPE \n
		Snippet: value: enums.GeneratorType = driver.instrument.get_type_py() \n
		No command help available \n
			:return: type_py: SMU| SMM| SMBB| SW| SGT| SMBV| SMJ| SMW
		"""
		response = self._core.io.query_str('INSTrument:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.GeneratorType)

	def set_type_py(self, type_py: enums.GeneratorType) -> None:
		"""SCPI: INSTrument:TYPE \n
		Snippet: driver.instrument.set_type_py(type_py = enums.GeneratorType.SGT) \n
		No command help available \n
			:param type_py: SMU| SMM| SMBB| SW| SGT| SMBV| SMJ| SMW
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.GeneratorType)
		self._core.io.write(f'INSTrument:TYPE {param}')

	def get_virtual(self) -> bool:
		"""SCPI: INSTrument:VIRTual \n
		Snippet: value: bool = driver.instrument.get_virtual() \n
		No command help available \n
			:return: virtual: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('INSTrument:VIRTual?')
		return Conversions.str_to_bool(response)

	def clone(self) -> 'Instrument':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Instrument(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
