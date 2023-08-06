#   Regular Imports #

import qiskit as qk
from qiskit import *
from qiskit import BasicAer
import pennylane as qml
import numpy as np
from numpy.linalg import qr as qrdecomp

#### Qiskit's State Tomography ####
#Imports
from qiskit_experiments.framework import ParallelExperiment
from qiskit_experiments.library import StateTomography
#from qiskit import qiskit_experiments
import qiskit_experiments.framework.composite.parallel_experiment
# For simulation
from qiskit.providers.aer import AerSimulator


dev = qml.device('default.mixed', wires=1) # Use the mixed state simulator to save some steps in plotting later
backend = BasicAer.get_backend('statevector_simulator')

#   DEFAULT VALUES FOR THE LIBRARY
numpy_random_seed = 0
np.random.seed(numpy_random_seed)
num_samples = 1000
N = 1

def SeelmanQuantumLibrarySetup(num_qubits, num_random_samples, numpy_random_seed): 
    '''
    Sets up parameters for the library. The inputs are:
        num_qubits: User may specify how many qubits they want to use
        num_random_samples: User may specify how many unitaries they want to generate
        numpy_random_seed: User may specify a seed
    '''
    N = num_qubits #User may specify how many qubits they want to use
    num_samples = num_random_samples #User may specify how many unitaries they want to generate
    np.random.seed(numpy_random_seed) #User may specify a seed

X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])

def qr_haar(N):
    """Generate a Haar-random matrix using the QR decomposition."""
    # Step 1
    A, B = np.random.normal(size=(N, N)), np.random.normal(size=(N, N))
    Z = A + 1j * B

    # Step 2
    Q, R = qrdecomp(Z)

    # Step 3
    Lambda = np.diag([R[i, i] / np.abs(R[i, i]) for i in range(N)])

    # Step 4
    return np.dot(Q, Lambda)

@qml.qnode(dev)
def qr_haar_random_unitary():
    qml.QubitUnitary(qr_haar(N), wires=0)
    return qml.state()

def convert_to_bloch_vector(rho):
    """Convert a density matrix to a Bloch vector."""
    ax = np.trace(np.dot(rho, X)).real
    ay = np.trace(np.dot(rho, Y)).real
    az = np.trace(np.dot(rho, Z)).real
    return [ax, ay, az]

qr = qk.QuantumRegister(N)
cr = qk.ClassicalRegister(N)

thetas = []
phis = []

def cart2sph(x, y, z):
    '''Converts Cartesian to Spherical coordinates'''
    xy = np.sqrt(x**2 + y**2) # sqrt(x² + y²)
    x_2 = x**2
    y_2 = y**2
    z_2 = z**2
    r = np.sqrt(x_2 + y_2 + z_2) # r = sqrt(x² + y² + z²)
    theta = np.arctan2(y, x) 
    phi = np.arctan2(xy, z) 
    return r, theta, phi

def generateRandomValues():
    qr_haar_samples = [qr_haar_random_unitary() for _ in range(num_samples)] # Unitaries for every sample
    qr_haar_bloch_vectors = np.array([convert_to_bloch_vector(s) for s in qr_haar_samples])
    
    for i in range(len(qr_haar_samples)):
        x = qr_haar_bloch_vectors[i][0]
        y = qr_haar_bloch_vectors[i][1]
        z = qr_haar_bloch_vectors[i][2]
        theta = cart2sph(x,y,z)[1]
        phi = cart2sph(x,y,z)[2]
        thetas.append(theta)
        phis.append(phi)

randomizedUnitaryCircuits = []

def createRandomUnitaries(randomGateNum):
    generateRandomValues()
    θ = thetas[randomGateNum]
    ϕ = phis[randomGateNum]
    for i in range(num_samples):
        circ = qk.QuantumCircuit(qr,cr)
        circ.u(float(θ), float(ϕ), 0, qr)
    randomizedUnitaryCircuits.append(circ)

randomBlochVectorList = []

def StateTomography():
    createRandomUnitaries()
    for _ in range(len(randomizedUnitaryCircuits)):
        qstexp1 = StateTomography(randomizedUnitaryCircuits[_])
        qstdata1 = qstexp1.run(backend, seed_simulation=numpy_random_seed).block_for_results()
        state_result = qstdata1.analysis_results("state")
        tempVal = convert_to_bloch_vector(state_result.value)
        tempVal = tempVal / np.linalg.norm(tempVal)
        randomBlochVectorList.append(tempVal)
        return randomBlochVectorList
'''Verify the Haar randomness with histograms and
plot_bloch_sphere(randomBlochVectorList)

'''