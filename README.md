This project solves the Set Packing problem by reducing it to SAT and 
solving the resulting CNF formula using the Glucose 4.2 SAT solver.

Input parameters:

n = number of elements

m = number of sets

k = required number of chosen sets (at least k)

Decision variables:
For each set S_i, the solver introduces a Boolean variable x_i.
x_i = True means the set is chosen.
x_i = False means the set is not chosen.
Constraints that must be considered:
Disjointness.
If two sets share any element, they cannot both be chosen.
This is encoded as: at least one of x_i or x_j must be False.

At least k sets must be selected.
We address this by making sure that at most m - k of the x_i variables 
may be False. To encode this, the program uses a standard 
counter that sequentially counts variables, thus 
encoding in a way that limits how many of the negated variables can be True.
This converts the whole Set Packing problem into a CNF formula.

Example instance:

5 3 2

1 2

3 4

1 3

This means:

n = 5

m = 3

k = 2

S1 = {1,2}

S2 = {3,4}

S3 = {1,3}

Example output:

Chosen sets: [1, 2]

Packing size: 2

S1: [1, 2]

S2: [3, 4]

unsatisfiable instance:

3 3 2

1 2

2 3

1 3

Output:

UNSAT

I tried the solver with bigger inputs i.e with a considerate number of
sets, but regardless, the solver produced an output virtually instantly 
slightly less than 1 second.

Running the script:
I am clarifying this as I was not too sure how you would run the script.
python3 setPacking.py -i test1.in -s /path/to/glucose
Adding -v to the end of the command will print the internal statistics.
