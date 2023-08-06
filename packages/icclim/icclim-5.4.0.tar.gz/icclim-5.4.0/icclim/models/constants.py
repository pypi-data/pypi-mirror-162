from __future__ import annotations

# fmt: off
# flake8: noqa

ICCLIM_VERSION = "5.4.0"

# placeholder for user_index
PERCENTILE_THRESHOLD_STAMP = "p"
WET_DAY_THRESHOLD = 1  # 1mm
PRECIPITATION = "p"
TEMPERATURE = "t"

# percentiles dimension from percentile_doy
PERCENTILES_COORD = "percentiles"
# attribut holding the in_base time bounds
IN_BASE_IDENTIFIER = "reference_epoch"

# Aliases of input variables names.
# Source: clix-meta (modified)
PR = ["pr", "pradjust","prAdjust", "prec", "rr", "precip", "PREC", "Prec", "RR", "PRECIP", "Precip"]
TAS = ["tas", "tavg", "ta", "tasadjust","tasAdjust", "tmean", "tm", "tg", "meant", "TMEAN", "Tmean", "TM", "TG", "MEANT", "meanT", "tasmidpoint"]
TAS_MAX = ["tasmax", "tasmaxadjust","tasmaxAdjust", "tmax", "tx", "maxt", "TMAX", "Tmax", "TX", "MAXT", "maxT"]
TAS_MIN = ["tasmin", "tasminadjust","tasminAdjust", "tmin", "tn", "mint", "TMIN", "Tmin", "TN", "MINT", "minT"]

# Aliases of input percentiles variables names
# Source icclim dev
VALID_PERCENTILE_DIMENSION = ["quantile", "percentile", "per", "centile"]

# Source of ECA&D indices definition
ECAD_ATBD = "ECA&D, Algorithm Theoretical Basis Document (ATBD) v11"

# Index qualifiers (needed to generate the API)
QUANTILE_BASED = "QUANTILE_BASED"  # fields: QUANTILE_INDEX_FIELDS
MODIFIABLE_UNIT = "MODIFIABLE_UNIT"  # fields: out_unit
MODIFIABLE_THRESHOLD = "MODIFIABLE_THRESHOLD"  # fields: threshold
MODIFIABLE_QUANTILE_WINDOW = "MODIFIABLE_QUANTILE_WINDOW"  # fields: window_width

# Map of months index to their short name, used to get a pandas frequency anchor
MONTHS_MAP = {1:"JAN",  2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC" }

# Season defined by their month numbers
AMJJAS_MONTHS = [*range(4, 9)]
ONDJFM_MONTHS = [10, 11, 12, 1, 2, 3]
DJF_MONTHS = [12, 1, 2]
MAM_MONTHS = [*range(3, 6)]
JJA_MONTHS = [*range(6, 9)]
SON_MONTHS = [*range(9, 12)]
