from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Program:
	"""Program commands group definition. 24 total commands, 15 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("program", core, parent)

	@property
	def adjustments(self):
		"""adjustments commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_adjustments'):
			from .Adjustments import Adjustments
			self._adjustments = Adjustments(self._core, self._cmd_group)
		return self._adjustments

	@property
	def classPy(self):
		"""classPy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_classPy'):
			from .ClassPy import ClassPy
			self._classPy = ClassPy(self._core, self._cmd_group)
		return self._classPy

	@property
	def comment(self):
		"""comment commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_comment'):
			from .Comment import Comment
			self._comment = Comment(self._core, self._cmd_group)
		return self._comment

	@property
	def gpu(self):
		"""gpu commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_gpu'):
			from .Gpu import Gpu
			self._gpu = Gpu(self._core, self._cmd_group)
		return self._gpu

	@property
	def hide(self):
		"""hide commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_hide'):
			from .Hide import Hide
			self._hide = Hide(self._core, self._cmd_group)
		return self._hide

	@property
	def path(self):
		"""path commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_path'):
			from .Path import Path
			self._path = Path(self._core, self._cmd_group)
		return self._path

	@property
	def ramBuff(self):
		"""ramBuff commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ramBuff'):
			from .RamBuff import RamBuff
			self._ramBuff = RamBuff(self._core, self._cmd_group)
		return self._ramBuff

	@property
	def scenario(self):
		"""scenario commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_scenario'):
			from .Scenario import Scenario
			self._scenario = Scenario(self._core, self._cmd_group)
		return self._scenario

	@property
	def settings(self):
		"""settings commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_settings'):
			from .Settings import Settings
			self._settings = Settings(self._core, self._cmd_group)
		return self._settings

	@property
	def show(self):
		"""show commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_show'):
			from .Show import Show
			self._show = Show(self._core, self._cmd_group)
		return self._show

	@property
	def startup(self):
		"""startup commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_startup'):
			from .Startup import Startup
			self._startup = Startup(self._core, self._cmd_group)
		return self._startup

	@property
	def storageLoc(self):
		"""storageLoc commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_storageLoc'):
			from .StorageLoc import StorageLoc
			self._storageLoc = StorageLoc(self._core, self._cmd_group)
		return self._storageLoc

	@property
	def toolbar(self):
		"""toolbar commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_toolbar'):
			from .Toolbar import Toolbar
			self._toolbar = Toolbar(self._core, self._cmd_group)
		return self._toolbar

	@property
	def transfer(self):
		"""transfer commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_transfer'):
			from .Transfer import Transfer
			self._transfer = Transfer(self._core, self._cmd_group)
		return self._transfer

	@property
	def tutorials(self):
		"""tutorials commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_tutorials'):
			from .Tutorials import Tutorials
			self._tutorials = Tutorials(self._core, self._cmd_group)
		return self._tutorials

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.ProgramMode:
		"""SCPI: PROGram:MODE \n
		Snippet: value: enums.ProgramMode = driver.program.get_mode() \n
		Selects the operation mode on start-up. \n
			:return: mode: DEMO| STANdard| EXPert
		"""
		response = self._core.io.query_str('PROGram:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.ProgramMode)

	def set_mode(self, mode: enums.ProgramMode) -> None:
		"""SCPI: PROGram:MODE \n
		Snippet: driver.program.set_mode(mode = enums.ProgramMode.DEMO) \n
		Selects the operation mode on start-up. \n
			:param mode: DEMO| STANdard| EXPert
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.ProgramMode)
		self._core.io.write(f'PROGram:MODE {param}')

	def clone(self) -> 'Program':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Program(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
