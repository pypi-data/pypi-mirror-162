from sage_acsv.dependencies import *

# Number of times we should double newton precision before erroring 
NUM_NEWTON_ITERATIONS = 3

# Number of attempts at computing the minimal critical point before erroring
MAX_MIN_CRIT_RETRIES = 3

# Minimum number of attempts at doubling precision of roots for Smale's test
MIN_SMALE_RETRIES = 5

# Constant from Smale's Alpha Test
SMALE_CONSTANT = (13 - 3 * sqrt(7))/4
