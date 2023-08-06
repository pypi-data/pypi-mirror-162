from IPython.display import display, Javascript, clear_output
from .src.resources.static_files_manager import StaticFilesManager
import time
try:
    display(Javascript(StaticFilesManager.js('kaggle-specs')))
    clear_output()
    time.sleep(1)
except:
    pass
from .main import cf
from .src.attribute import Attribute
from .src.filter import Filter
from .src.field import Field
from .src.metric import Metric
from .src.compare_metric import CompareMetric
from .src.row import Row
from .src.column import Column
from .src.legend import Legend
from .src.grid import Grid
from .src.markline import MarkLine
from .src.color import Color
