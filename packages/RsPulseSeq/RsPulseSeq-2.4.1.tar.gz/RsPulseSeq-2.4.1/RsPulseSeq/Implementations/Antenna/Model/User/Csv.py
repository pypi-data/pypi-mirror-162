from typing import List

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Csv:
	"""Csv commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("csv", core, parent)

	def set_format_py(self, format_py: List[int]) -> None:
		"""SCPI: ANTenna:MODel:USER:CSV:FORMat \n
		Snippet: driver.antenna.model.user.csv.set_format_py(format_py = [1, 2, 3]) \n
		Defines how the data in the selected *.csv file is interpreted. The settings in this command are not permanent.
		The command affects only the currently selected antenna. For description of the *.csv file format, see 'Antenna pattern
		file formats'. \n
			:param format_py: No help available
		"""
		param = Conversions.list_to_csv_str(format_py)
		self._core.io.write(f'ANTenna:MODel:USER:CSV:FORMat {param}')
