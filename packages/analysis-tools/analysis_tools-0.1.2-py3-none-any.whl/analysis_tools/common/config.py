"""Configuration module

Commonly used constant parameters are defined in capital letters.
"""

# Author: Dongjin Yoon <djyoon0223@gmail.com>


# Common parameters
PARAMS = dict(
    RANDOM_STATE = 42,
    TEST_SIZE    = 0.2
)


# Plot parameters
PLOT_PARAMS = dict(
    SHOW_PLOT      = True,
    FIGSIZE        = (30, 10),
    BINS           = 50,
    N_CLASSES_PLOT = 5,
    N_COLS         = 5,
    LEARNING_CURVE_N_SUBSETS_STEP = 5
)
