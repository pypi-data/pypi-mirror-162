import os, os.path
THIS_SCRIPT = os.path.dirname(os.path.realpath(__file__))

from enum import Enum
from distutils.log import error, warn
from logging import warning
from pickletools import optimize
import sys
from typing import List, Dict
import warnings
import re
import tempfile
import subprocess
import json

import pyqubo as pq

from pulp import PulpSolverError
from quantagonia.enums import HybridSolverConnectionType, HybridSolverServers

from quantagonia.runner import Runner
from quantagonia.runner_factory import RunnerFactory
from quantagonia.cloud.spec_builder import QUBOSpecBuilder, QuboSolverType

class QuboVariable(object):

    def __init__(self, name : str, pos : int, initial=None):
        self.name = name
        self._pos = pos
        self.assignment = initial

    def id(self):
        return self._pos

    def eval(self):
        if(self.assignment is None):
            error("Variable " + self.name + " is still unassigned.")
        return self.assignment

    def __str__(self):
        return self.name

    def __mul__(self, other):
        return QuboTerm(1, [self, other])

    def __rmul__(self, other : float):
        return QuboTerm(other, [self])

class QuboTerm(object):

    def __init__(self, coefficient : float, vars : list[QuboVariable]):
        super().__init__()
        self.coefficient = coefficient
        self.order = len(vars)
        self.vars = vars

        if(self.order < 1 or self.order > 2):
            raise Exception("Only QuboTerms of order 1 or 2 are supported!")

        # by convention, we only store the upper triangular part of the QUBO ->
        # need to sort the variables ascendingly by their IDs
        sorted(self.vars, key = lambda v : v.id())

    def eval(self):
        E = self.coefficient * self.vars[0].eval()

        for var in self.vars[1:]:
            E *= var.eval()

        # assume symmetric QUBO
        if(self.order > 1):
            E *= 2

        return E

    def __str__(self):
        s = ""
        if(self.coefficient >= 0):
            s += "+ "
        else:
            s += "- "

        s += str(abs(self.coefficient))
        s += " * " + str(self.vars[0])
        for var in self.vars[1:]:
            s += " * " + str(var)

        return s

    def __hash__(self):
        return "_".join([hash(v) for v in self.vars])

    # Python 3.10: other: float | QuboVariable
    def __mul__(self, other):
        if isinstance(other, float):
            self.coefficient *= other
            return self

        if(self.order <= 1):
            return QuboTerm(self.coefficient, [*self.vars, other])

        raise Exception("Only QuboTerms of order 1 or 2 are supported!")

    # Python 3.10: other: float | QuboVariable
    def __rmul__(self, other):
        return QuboTerm(self.coefficient * other, self.vars)

class QuboExpression(object):

    def __init__(self):
        super().__init__()

        # hash -> (term with coefficient)
        self.terms = {}

    # Python 3.10: other: QuboTerm | QuboVariable
    def __iadd__(self, other):

        oother = other
        if isinstance(oother, QuboVariable):
            oother = QuboTerm(1, [oother])

        key = str(oother)
        if(key in self.terms):
            self.terms[key].coefficent += oother.coefficient

            if(self.terms[key].coefficent == 0):
                del self.terms[key]
        else:
            self.terms[key] = oother

        return self

    # Python 3.10: other: QuboTerm | QuboVariable
    def __isub__(self, other):

        oother = other
        if isinstance(oother, QuboVariable):
            oother = QuboTerm(1, [oother])

        key = str(oother)
        if(key in self.terms):
            self.terms[key].coefficent -= oother.coefficient

            if(self.terms[key].coefficent == 0):
                del self.terms[key]
        else:
            self.terms[key] = oother
            self.terms[key].coefficient *= -1

        return self

    def eval(self, shift = 0):
        E = shift

        for term in self.terms:
            E += self.terms[term].eval()

        return E

    def __str__(self):
        return " ".join([str(self.terms[t]) for t in self.terms])

class QuboModel(object):

    def __init__(self):

        self.vars = {}
        self.objective = QuboExpression()

        # for future use
        self.sos1 = []
        self.sos2 = []

        self._pos_ctr = 0

    def addSOS1(self, vars : list[QuboVariable]):
        warnings.warn("SOS1 constraints are currently not supported in QUBOs")
        self.sos1.append(vars)

    def addSOS2(self, vars : list[QuboVariable]):
        warnings.warn("SOS2 constraints are currently not supported in QUBOs")
        self.sos2.append(vars)

    def addVariable(self, name : str, initial=None, disable_warnings=False):
        if(name in self.vars):
            if(not disable_warnings):
                warnings.warn("Variable " + name + " already in QUBO...")

            return self.vars[name]

        self.vars[name] = QuboVariable(name, self._pos_ctr, initial)
        self._pos_ctr += 1

        return self.vars[name]

    def variable(self, name : str):
        return self.vars[name]

    def eval(self):
        return self.objective.eval()

    def writeQUBO(self, path : str):

        with open(path, 'w') as f:

            f.write("1\n")
            f.write("1.0\n")
            f.write("0.0\n")

            # create sparse matrix from terms in objective
            f.write(f"{len(self.vars)} {len(self.objective.terms)}\n")
            for key in self.objective.terms:
                term = self.objective.terms[key]

                if(term.order == 1):
                    f.write(f"{term.vars[0].id()} {term.vars[0].id()} {term.coefficient}\n")
                if(term.order == 2):
                    f.write(f"{term.vars[0].id()} {term.vars[1].id()} {term.coefficient}\n")

    def __str__(self):
        return str(self.objective)

    def solve(self, solver_type : QuboSolverType, runner : Runner):

        # temporary folder for the QUBO problem
        tmp_path = tempfile.mkdtemp()
        tmp_problem = os.path.join(tmp_path, "pulp.qubo")

        # convert problem into QUBO format (i.e. a matrix)
        self.writeQUBO(tmp_problem)

        # Convert solver type enum to one used by specs client. Interfaces (values of enums) have to match
        spec = QUBOSpecBuilder(type=solver_type).getd()

        # Actually solve the QUBO
        res = runner.solve(tmp_problem, spec, True)
        
        # parse solution, store assignments in variables
        sol_string_splitted = res['solution_file'].split("\n")

        for var in self.vars:
            self.vars[var].assignment = int(sol_string_splitted[self.vars[var].id()])

        # return (optimal) objective
        return self.eval()

    #######
    # PYQUBO Compatibility Layer
    #######
    def fromPyQuboModel(self, model : pq.Model):
        self.vars = {}
        self.objective = QuboExpression()
        self._pos_ctr = 0

        # guarantees that we only have terms of oders {1, 2}
        qmodel, shift = model.to_qubo()

        # create objective from QUBO model
        for term in qmodel:
            if(term[0] == term[1]):
                # unary term
                v = self.addVariable(term[0], disable_warnings=True)
                self.objective += QuboTerm(qmodel[term], [v])
            else:
                # pairwise term
                v0 = self.addVariable(term[0], disable_warnings=True)
                v1 = self.addVariable(term[1], disable_warnings=True)
                self.objective += QuboTerm(qmodel[term], [v0, v1])
