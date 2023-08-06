import PyQt5.QtCore

PyQt5.QtCore.QCoreApplication.setAttribute(PyQt5.QtCore.Qt.AA_ShareOpenGLContexts)

from .displayCollections import CollectionDisplayer
from .displaySensitivity import SensitivityDisplayer, analyse_sobol_plot_indices, analyse_sobol_plot_convergence, analyse_sobol_plot_2ndOrder_indices
from .displayOptimization import OptimizationDisplayer
from .viewOptimizationResults import ViewOptimizationResults
from .fastPlot import *
from .fastPlot3 import *

# Submodules import
from .graphs.widget_graphsVisual import *
from .widgets import *
from .onclick import *
from .selector import *


