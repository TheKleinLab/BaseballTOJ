from klibs.KLIndependentVariable import IndependentVariableSet

# Initialize object containing the project's independent variables

BaseballTOJ_ind_vars = IndependentVariableSet()


# Define project variables and variable types

## Factors ##
# 'trial_type': the type of trial ("probe" = colour probe, "TOJ" = TOJ)
# 'first_arrival': whether the runner arrives at base or ball arrives at the glove first
# 'soa_frames': the interval in frames between the onsets of the first and second targets

# SOAs are defined in terms of frames here, so 1 = 16.67ms, 3 = 50ms, 6 = 100ms, etc.
# This assumes the experiment is run on a monitor with a refresh rate of 60Hz.
soa_list = [(1, 3), (3, 2), (6, 2), (9, 2), (16, 1)]

BaseballTOJ_ind_vars.add_variable("trial_type", str, ["probe", ("TOJ", 2)])
BaseballTOJ_ind_vars.add_variable("first_arrival", str, ["runner", "ball"])
BaseballTOJ_ind_vars.add_variable("soa_frames", int, soa_list)
