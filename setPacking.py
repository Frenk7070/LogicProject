import argparse
import subprocess
import sys

class Cnf:
    def __init__(self):
        self.clauses = []
        self.nextVar = 1

    def newVar(self):
        v = self.nextVar
        self.nextVar += 1
        return v

    def addClause(self, lits):
        self.clauses.append(list(lits))

    def numVars(self):
        return self.nextVar - 1

    def numClauses(self):
        return len(self.clauses)


def loadInstance(path):
    with open(path, "r") as f:
        first = f.readline().split()
        n = int(first[0])
        m = int(first[1])
        k = int(first[2])
        sets = []
        for _ in range(m):
            line = f.readline().strip().split()
            sets.append([int(x) for x in line])
    return n, m, k, sets


def encodeAtMostSequential(cnf, lits, r):
    n = len(lits)
    if r >= n or n == 0:
        return

    s = [[0]*(r+1) for _ in range(n)]
    for i in range(n):
        for j in range(1, r+1):
            s[i][j] = cnf.newVar()

    for i in range(n):
        cnf.addClause([-lits[i], s[i][1]])

    for i in range(1, n):
        for j in range(1, r+1):
            cnf.addClause([-s[i-1][j], s[i][j]])

    for i in range(1, n):
        for j in range(2, r+1):
            cnf.addClause([-lits[i], -s[i-1][j-1], s[i][j]])

    if r > 0:
        for i in range(1, n):
            cnf.addClause([-lits[i], -s[i-1][r]])


def encodeSetPacking(n, m, k, sets):
    cnf = Cnf()
    xVar = {}

    for i in range(1, m+1):
        xVar[i] = cnf.newVar()

    elemToSets = {}
    for i, s in enumerate(sets, start=1):
        for e in s:
            elemToSets.setdefault(e, []).append(i)

    for e, idx in elemToSets.items():
        for a in range(len(idx)):
            for b in range(a+1, len(idx)):
                cnf.addClause([-xVar[idx[a]], -xVar[idx[b]]])

    if k > 0:
        atMost = m - k
        if atMost < m:
            negs = [-xVar[i] for i in range(1, m+1)]
            encodeAtMostSequential(cnf, negs, atMost)

    return cnf, xVar


def writeDimacs(cnf, path):
    with open(path, "w") as f:
        f.write("p cnf {} {}\n".format(cnf.numVars(), cnf.numClauses()))
        for clause in cnf.clauses:
            f.write(" ".join(str(x) for x in clause) + " 0\n")


def runGlucose(solverPath, cnfPath, verbose):
    args = [solverPath, "-model"]
    if not verbose:
        args.append("-verb=0")
    args.append(cnfPath)

    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        print("Solver not found.")
        sys.exit(1)

    out = result.stdout.splitlines()
    sat = False
    lits = []

    for line in out:
        if line.startswith("s ") and "SATISFIABLE" in line and "UNSAT" not in line:
            sat = True
        if line.startswith("v "):
            parts = line.split()[1:]
            for p in parts:
                v = int(p)
                if v != 0:
                    lits.append(v)

    if not sat:
        return False, []

    if not lits:
        return True, []

    maxVar = max(abs(v) for v in lits)
    model = [False]*(maxVar+1)
    for lit in lits:
        if lit > 0:
            model[lit] = True
        else:
            model[-lit] = False

    return True, model


def decodeSolution(model, xVar, sets):
    chosen = []
    for i in xVar:
        v = xVar[i]
        if v < len(model) and model[v]:
            chosen.append(i)

    print("Chosen sets:", chosen)
    print("Packing size:", len(chosen))
    for i in chosen:
        print("S{}: {}".format(i, sets[i-1]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="formula.cnf")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-s", "--solver", required=True)
    args = parser.parse_args()

    n, m, k, sets = loadInstance(args.input)
    cnf, xVar = encodeSetPacking(n, m, k, sets)
    writeDimacs(cnf, args.output)

    sat, model = runGlucose(args.solver, args.output, args.verbose)

    if not sat:
        print("UNSAT")
        return
    decodeSolution(model, xVar, sets)


if __name__ == "__main__":
    main()
