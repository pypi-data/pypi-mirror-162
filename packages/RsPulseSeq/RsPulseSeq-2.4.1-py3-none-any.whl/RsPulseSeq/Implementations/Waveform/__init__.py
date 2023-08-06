from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Waveform:
	"""Waveform commands group definition. 28 total commands, 8 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("waveform", core, parent)

	@property
	def bemitter(self):
		"""bemitter commands group. 3 Sub-classes, 3 commands."""
		if not hasattr(self, '_bemitter'):
			from .Bemitter import Bemitter
			self._bemitter = Bemitter(self._core, self._cmd_group)
		return self._bemitter

	@property
	def iq(self):
		"""iq commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_iq'):
			from .Iq import Iq
			self._iq = Iq(self._core, self._cmd_group)
		return self._iq

	@property
	def level(self):
		"""level commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_level'):
			from .Level import Level
			self._level = Level(self._core, self._cmd_group)
		return self._level

	@property
	def mt(self):
		"""mt commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_mt'):
			from .Mt import Mt
			self._mt = Mt(self._core, self._cmd_group)
		return self._mt

	@property
	def noise(self):
		"""noise commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_noise'):
			from .Noise import Noise
			self._noise = Noise(self._core, self._cmd_group)
		return self._noise

	@property
	def pdw(self):
		"""pdw commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pdw'):
			from .Pdw import Pdw
			self._pdw = Pdw(self._core, self._cmd_group)
		return self._pdw

	@property
	def view(self):
		"""view commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_view'):
			from .View import View
			self._view = View(self._core, self._cmd_group)
		return self._view

	@property
	def waveform(self):
		"""waveform commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_waveform'):
			from .Waveform import Waveform
			self._waveform = Waveform(self._core, self._cmd_group)
		return self._waveform

	def get_catalog(self) -> str:
		"""SCPI: WAVeform:CATalog \n
		Snippet: value: str = driver.waveform.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('WAVeform:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: WAVeform:COMMent \n
		Snippet: value: str = driver.waveform.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('WAVeform:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: WAVeform:COMMent \n
		Snippet: driver.waveform.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'WAVeform:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: WAVeform:CREate \n
		Snippet: driver.waveform.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'WAVeform:CREate {param}')

	def get_name(self) -> str:
		"""SCPI: WAVeform:NAME \n
		Snippet: value: str = driver.waveform.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('WAVeform:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: WAVeform:NAME \n
		Snippet: driver.waveform.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'WAVeform:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: WAVeform:REMove \n
		Snippet: driver.waveform.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'WAVeform:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: WAVeform:SELect \n
		Snippet: value: str = driver.waveform.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('WAVeform:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: WAVeform:SELect \n
		Snippet: driver.waveform.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'WAVeform:SELect {param}')

	# noinspection PyTypeChecker
	def get_sig_cont(self) -> enums.SigCont:
		"""SCPI: WAVeform:SIGCont \n
		Snippet: value: enums.SigCont = driver.waveform.get_sig_cont() \n
		Defines the waveform signal type. \n
			:return: sig_cont: PULSe| COMM
		"""
		response = self._core.io.query_str('WAVeform:SIGCont?')
		return Conversions.str_to_scalar_enum(response, enums.SigCont)

	def set_sig_cont(self, sig_cont: enums.SigCont) -> None:
		"""SCPI: WAVeform:SIGCont \n
		Snippet: driver.waveform.set_sig_cont(sig_cont = enums.SigCont.COMM) \n
		Defines the waveform signal type. \n
			:param sig_cont: PULSe| COMM
		"""
		param = Conversions.enum_scalar_to_str(sig_cont, enums.SigCont)
		self._core.io.write(f'WAVeform:SIGCont {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.WaveformType:
		"""SCPI: WAVeform:TYPE \n
		Snippet: value: enums.WaveformType = driver.waveform.get_type_py() \n
		Sets the type of the waveform. \n
			:return: type_py: CW| NOISe| WAVeform| USER| BEMitter| MT| PDW| AIF| APDW| IQDW
		"""
		response = self._core.io.query_str('WAVeform:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.WaveformType)

	def set_type_py(self, type_py: enums.WaveformType) -> None:
		"""SCPI: WAVeform:TYPE \n
		Snippet: driver.waveform.set_type_py(type_py = enums.WaveformType.AIF) \n
		Sets the type of the waveform. \n
			:param type_py: CW| NOISe| WAVeform| USER| BEMitter| MT| PDW| AIF| APDW| IQDW
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.WaveformType)
		self._core.io.write(f'WAVeform:TYPE {param}')

	def clone(self) -> 'Waveform':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Waveform(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
