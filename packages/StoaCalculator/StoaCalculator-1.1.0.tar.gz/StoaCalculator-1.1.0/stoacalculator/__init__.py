import math
import statistics
import matplotlib.pyplot as plt
import numpy as np
from sympy import *

# simple operations, basic aritmethic


def add_numbers(num1, num2):
    print(num1 + num2)


def substract_numbers(num1, num2):
    print(num1 - num2)


def multiply_numbers(num1, num2):
    print(num1 * num2)


def divide_numbers(num1, num2):
    print(num1 / num2)


def pow_numbers(num1, num2):
    print(num1 ** num2)


def sqr_root(num1):
    print(math.sqrt(num1))


# trigonometry
def sin(num1):
    print(math.sin(num1))


def cos(num1):
    print(math.cos(num1))


def tan(num1):
    print(math.tan(num1))


def acos(num1):
    print(math.acos(num1))


def asin(num1):
    print(math.asin(num1))


def atan(num1):
    print(math.atan(num1))

# Geometry circle (add radius)


def areacircle(num1):
    area = math.pi * num1 * num1
    print(area)

# Geometry rectangle (add height and width)


def arearectangle(num1, num2):
    area = num1 * num2
    print(area)

# Geometry square (add sides)


def areasquare(num1):
    area = num1 * num1
    print(area)

# Geometry triangle (add all sides)


def areatriangle(num1, num2, num3):
    semiperimeter = (num1 + num2 + num3) / 2
    area = (semiperimeter*(semiperimeter-num1) *
            (semiperimeter-num2)*(semiperimeter-num3)) ** 0.5
    print(area)

# Statistics


def mean(list):
    print(statistics.mean(list))


def median(list):
    print(statistics.median(list))


def mode(list):
    print(statistics.mode(list))

# Plotting


def linearplot(x, linearformula):

    plt.style.use('dark_background')

    # setting the axes at the centre
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title('Stoas Calculator Graph')
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_color('#00FFFF')
    ax.spines['bottom'].set_color('#00FFFF')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # plot the function
    plt.plot(x, linearformula, 'w', label='Equation')

    plt.legend(loc='upper left')

    # show the plot
    plt.show()


def quadraticplot(x, quadraticformula):

    plt.style.use('dark_background')

    # setting the axes at the centre
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title('Stoas Calculator Graph')
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_color('#00FFFF')
    ax.spines['bottom'].set_color('#00FFFF')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # plot the function
    plt.plot(x, quadraticformula, 'w', label='Equation')

    plt.legend(loc='upper left')

    # show the plot
    plt.show()


def cubicplot(x, cubicformula):

    plt.style.use('dark_background')

    # setting the axes at the centre
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title('Stoas Calculator Graph')
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_color('#00FFFF')
    ax.spines['bottom'].set_color('#00FFFF')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # plot the function
    plt.plot(x, cubicformula, 'w', label='Equation')

    plt.legend(loc='upper left')

    # show the plot
    plt.show()


def trigonometricplot(x, trigonometricformula):

    plt.style.use('dark_background')

    # setting the axes at the centre
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title('Stoas Calculator Graph')
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_color('#00FFFF')
    ax.spines['bottom'].set_color('#00FFFF')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # plot the function
    plt.plot(x, trigonometricformula, 'w')

    # show the plot
    plt.show()


def exponentialplot(x, exponentialformula):

    plt.style.use('dark_background')

    # setting the axes at the centre
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title('Stoas Calculator Graph')
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_color('#00FFFF')
    ax.spines['bottom'].set_color('#00FFFF')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # plot the function
    plt.plot(x, exponentialformula, 'w')

    # show the plot
    plt.show()


def biplot(x, formula1, formula2):

    plt.style.use('dark_background')

    # setting the axes at the centre
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title('Stoas Calculator Graph')
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_color('#00FFFF')
    ax.spines['bottom'].set_color('#00FFFF')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # plot the function
    plt.plot(x, formula1, 'w', label='1st Equation')
    plt.plot(x, formula2, 'm', label='2nd Equation')

    plt.legend(loc='upper left')

    # show the plot
    plt.show()


def derivatives(function):
    print(diff(function))


def integrals(function):
    print(integrate(function))


def GCM(num1, num2):
    print(math.gcd(num1, num2))


def LCM(num1, num2):
    print(math.lcm(num1, num2))


def D2F(num1):
    print((num1).as_integer_ratio())


def roots(list):
    print(np.roots(list))


def factorial(num1):
    print(math.factorial(num1))


def absolute(num1):
    print(math.fabs(num1))


def euclidean(num1, num2):
    print(math.hypot(num1, num2))


def acosh(num1):
    print(math.acosh(num1))


def asinh(num1):
    print(math.asinh(num1))


def atanh(num1):
    print(math.atanh(num1))


def cosh(num1):
    print(math.cosh(num1))


def sinh(num1):
    print(math.sinh(num1))


def tanh(num1):
    print(math.tanh(num1))


def partfrac(function):
    print(apart(function))


def less(num1):
    print(math.floor(num1))


def more(num1):
    print(math.ceil(num1))


def limits(function, x, y):
    print(limit(function, x, y))


def modf(num1):
    print(math.modf(num1))


def truncated(num1):
    print(math.trunc(num1))


def laplace(num1, num2):
    gfg = np.random.laplace(num1, num2, 1000)
    count, bins, ignored = plt.hist(gfg, 30, density=True)
    plt.style.use('dark_background')
    plt.title('Stoas Calculator Graph')
    plt.show()


def natlog(num1):
    print(math.log(num1))


def baselog(num1, num2):
    print(math.log(num1, num2))


def dfourier(list):
    print(np.fft.fft(list))


def idfourier(list):
    print(np.fft.ifft(list))


def natlog1p(num1):
    print(math.log1p(num1))


def taylor(num1, num2):
    sine = 0
    for i in range(num2):
        sign = math.pow(-1, i)
        pi = math.pi
        a = num1*(pi/180)
        sine = sine+(sign*(a**(2.0*i+1))/math.factorial(2*i+1))
    print(sine)
    return sine


def base2log(num1):
    print(math.log2(num1))


def base10log(num1):
    print(math.log10(num1))


def atan2(num1, num2):
    print(math.atan2(num1, num2))


def addmatrices(list1, list2):
    matrix1 = np.array(list1)
    matrix2 = np.array(list2)
    print(matrix1 + matrix2)


def multiplymatrices(list1, list2):
    matrix1 = np.array(list1)
    matrix2 = np.array(list2)
    print(matrix1.dot(matrix2))


def transposematrix(list1):
    matrix1 = np.array(list1)
    print(matrix1.transpose())


def radtodeg(num1):
    print(np.rad2deg(num1))


def degtorad(num1):
    print(np.deg2rad(num1))


def minlist(list):
    list.sort()
    print(*list[:1])


def maxlist(list):
    list.sort()
    print(list[-1])


def rangelist(list):
    print(max(list)-min(list))


def orderlist(list):
    print(sorted(list))


def variance(list):
    print(statistics.variance(list))


def deviation(list):
    var = statistics.variance(list)
    dev = math.sqrt(var)
    print(dev)


def firstquartilelist(list):
    print(np.quantile(list, .25, interpolation='midpoint'))


def thirdquartilelist(list):
    print(np.quantile(list, .75, interpolation='midpoint'))


def interquartilelist(list):
    print(np.quantile(list, .50, interpolation='midpoint'))


def innermatrices(list1, list2):
    matrix1 = np.array(list1)
    matrix2 = np.array(list2)
    print(np.inner(matrix1, matrix2))


def dotmatrices(list1, list2):
    matrix1 = np.array(list1)
    matrix2 = np.array(list2)
    print(np.dot(matrix1, matrix2))


def tracematrix(list1):
    matrix1 = np.array(list1)
    print(matrix1.trace())


def rankmatrix(list1):
    matrix1 = np.array(list1)
    print((np.linalg.matrix_rank)(matrix1))


def detmatrix(list1):
    matrix1 = np.array(list1)
    print(np.round((np.linalg.det)(matrix1)))


def trueinvmatrix(list1):
    matrix1 = np.array(list1)
    print((np.linalg.inv)(matrix1))


def pseudoinvmatrix(list1):
    matrix1 = np.array(list1)
    print((np.linalg.pinv)(matrix1))


def flatmatrix(list1):
    matrix1 = np.array(list1)
    print(matrix1.flatten())


def eigmatrix(list1):
    matrix1 = np.array(list1)
    w, v = np.linalg.eig(matrix1)
    print("\nEigenvalues:")
    print(w)
    print("\nEigenvectors:")
    print(v)


def floatmean(list1):
    print(statistics.fmean(list1))


def geometricmean(list1):
    print(statistics.geometric_mean(list1))


def harmonicmean(list1):
    print(statistics.harmonic_mean(list1))


def medianlow(list1):
    print(statistics.median_low(list1))


def medianhigh(list1):
    print(statistics.median_high(list1))


def mediangrouped(list1):
    print(statistics.median_grouped(list1))


def multimode(list1):
    print(statistics.multimode(list1))


def popvariance(list1):
    print(statistics.pvariance(list1))


def popdeviation(list1):
    print(statistics.pstdev(list1))


def areatrapezoid(num1, num2, num3):
    print(((num1 + num2)/2)*num3)


def areaelipse(num1, num2):
    print(3.141592 * num1 * num2)


def areaparallelogram(num1, num2):
    print(num1 * num2)


def areasector(num1, num2):
    print((3.141592) * num1 * num1 * (num2/360))


def perimetertriangle(num1, num2, num3):
    print(num1+ num2 + num3)


def perimetersquare(num1):
    print(4 * num1)


def perimeterrectangle(num1, num2):
    print(2 * (num1+num2))


def perimetertrapezoid(num1, num2, num3, num4):
    print(num1 + num2 + num3 + num4)


def perimeterparallelogram(num1, num2):
    print(2 * (num1+num2))


def volumesphere(num1):
    print((4/3) * 3.141592 * num1 * num1 * num1)


def volumecone(num1, num2):
    print((1/3) * 3.141592 * num1 * num1 * num2)


def volumecube(num1):
    print(num1 * num1 * num1)


def volumerectprism(num1, num2, num3):
    print(num1 * num2 * num3)


def volumecylinder(num1, num2):
    print(3.141592 * num1 * num1 * num2)


def circumferencecircle(num1):
    print(2 * 3.141592 * num1)


def diametercircle(num1):
    print(3.141592 * num1)


def radiuscircle(num1):
    print((num1)/(2*3.141592))
