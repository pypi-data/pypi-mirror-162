from sympy.matrices import Matrix
from sympy.physics.quantum import TensorProduct, qapply, Dagger, OrthogonalKet, OrthogonalBra
from sympy.interactive import printing
printing.init_printing(use_latex = True)
from sympy import *


class density_matrix:
    """
    -the density matrix as a sympy matrix

    -the dimensions of the subspaces in list
    for example if its a qubit times qubit which means 2x2
    hence 4 dimensional hilbert space the dimentions will be the list [2,2]

    """
    def __init__(self, matrix, dims):
        self.matrix = matrix
        self.dims = dims
        self.d = sum(dims)
    def __mul__(self,other):
        return density_matrix(self.matrix*other.matrix)
    def __add__(self,other):
        return density_matrix(self.matrix+other.matrix)
    def __sub__(self,other):
        return density_matrix(self.matrix-other.matrix)
    def __floordiv__(self,other):
        """
        I use the floordiv // operation for tensor product notation
        """
        return TensorProduct(self.matrix,other.matrix)
    def __mod__(self,quDits_to_be_dropped):
        """
        i use the mod % symbol for finding the partial trace by mentioning which qubits will be traced out
        for example let's say that we have a qubit times a qutrit times a qubit(a 2*3*2=A*B*C hilbert space) and
        we want to trace out the A and the C states, i.e. we want to get the substate B. We get that by writing
        density_matrix%[0,2] meaning trace out the first and the third qubit.
        """
        def tracors(dimensions_list, to_trace_out):
            trace_list = []
            d = eye(dimensions_list[to_trace_out])
            for i in range(dimensions_list[to_trace_out]):
                m = Matrix([[1]])
                for j in range(len(dimensions_list)):
                    if j==to_trace_out:
                        m = TensorProduct(m,d.col(i))
                    else:
                        m = TensorProduct(m,eye(dimensions_list[j]))
                trace_list.append(m)
            return trace_list
        def trace_out_one(operator,tracor_list):
            x,y= shape(tracor_list[0])
            n=int(self.d/int(x/y))
            s = zeros(n,n)
            for i in tracor_list:
                s+=Dagger(i)*operator*i
            return s
        m = self.matrix
        dims = (self.dims).copy()
        quDits_to_be_dropped.sort()
        q = quDits_to_be_dropped.copy()
        for i in range(len(quDits_to_be_dropped)):
            m = trace_out_one(m, tracors(dims,q[0]))
            dims.remove(dims[q[0]])
            q = q[1:]
            q[:] = [x - 1 for x in q]
        return density_matrix(m,dims)
    def shape(self):
        return shape(self.matrix_form)
    def get_matrix(self):
        return self.matrix
    def show(self):
        #display("Matrix form:")
        display(self.matrix)
    def dagger(self):
        return Dagger(self.matrix)
