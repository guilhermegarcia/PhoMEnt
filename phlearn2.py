import argparse
import megatableau
import geneval
import optimizer
import time

'''phlearn2.py is just like phlearn, but prints out how long various steps take.
'''

    ### TIME
mark = time.time()

#####################################################################
## Parse command line arguments
#####################################################################
parser = argparse.ArgumentParser(description = 'Maximum entropy harmonic grammar')
parser.add_argument('attested_file_name', help='Name of input file')
parser.add_argument('constraint_file_name', help='Name of constraints file')
parser.add_argument('-a', '--alphabet_file_name', default=None, help='List of segments in alphabet; one per line')
parser.add_argument('-m', '--maxstrlen', type=int, default=5, help='Maximum string length in contrast set')
parser.add_argument('-o', '--outfile', help='Name of output file')

## weight-setting parameters
parser.add_argument('-l', '--L1', type=float, default=0.0, help='Multiplier for L1 regularizer')
parser.add_argument('-L', '--L2', type=float, default=0.0, help='Multiplier for L1 regularizer')
parser.add_argument('-p', '--precision', type=float, default=10000000, help='Precision for gradient search (see docs)')

args = parser.parse_args()

### TIMER - keep track of how long each step takes
mark = time.time()

def timer(task):
    print task, "\t", round(time.time() - mark, 4), "sec"
    return time.time()


#####################################################################
## Main code
#####################################################################

# Create and fill MegaTableau
mt = megatableau.MegaTableau()

# read in attested forms and add to MegaTableau
geneval.read_data_only(mt, args.attested_file_name)

mark = timer("Parsed arguments:")

# get alphabet
if args.alphabet_file_name:
    alphabet = geneval.read_sigma(mt, args.alphabet_file_name)
else:
    alphabet = geneval.read_sigma(mt)

mark = timer("Inferred alphabet:")

## read in constraints
constraints = geneval.read_constraints(mt, args.constraint_file_name)

mark = timer("Read constraints:")

## add non-attested forms to tableau
geneval.augment_sigma_k(mt, alphabet, args.maxstrlen)

mark = timer("Gen augmentation:")

## apply constraints (this is the costliest step...)
geneval.apply_mark_list(mt, constraints)

mark = timer("Computed violations:")

# Optimize mt.weights
optimizer.learn_weights(mt, args.L1, args.L2, args.precision)

mark = timer("Optimized weights:")

# Write the final MegaTableau to file
if args.outfile:
    mt.write_output(args.outfile)


