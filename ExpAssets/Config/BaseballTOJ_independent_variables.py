__author__ = 'jono'
from klibs.KLIndependentVariable import IndependentVariableSet, IndependentVariable

# Initialize object containing project's independent variables

BaseballTOJ_ind_vars = IndependentVariableSet()


# Define project variables and variable types

soa_list = [(15, 3), (45, 2), (90, 2), (135, 2), (240, 1)]

BaseballTOJ_ind_vars.add_variable("probe_targets", str, ["BASE", "GLOVE", ("TOJ", 4)])
BaseballTOJ_ind_vars.add_variable("condition", str, ["RUNNER", "BALL"])
BaseballTOJ_ind_vars.add_variable("probe_location", str, [("glove", 8), ("base", 2)])
BaseballTOJ_ind_vars.add_variable("soa", int, soa_list)
