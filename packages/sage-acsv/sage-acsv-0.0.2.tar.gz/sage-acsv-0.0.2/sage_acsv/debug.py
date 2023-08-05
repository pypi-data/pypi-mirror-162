from sage_acsv.constants import *
import time

class Timer(object):
    def __init__(self, show_time=True):
        self._time_created = time.monotonic()
        self._last_checkpoint = self._time_created
        self.show_time = show_time
    
    def checkpoint(self, name=None):
        if self.show_time and name:
            time_diff = time.monotonic() - self._last_checkpoint
            print(f"{bcolors.OKBLUE}Timer:{bcolors.ENDC} Executed " + name + " in " + str(time_diff) + " seconds.")
        
        self._last_checkpoint = time.monotonic()
    
    def total(self, name):
        if self.show_time and name:
            time_diff = time.monotonic() - self._time_created
            print(f"{bcolors.OKBLUE}Timer:{bcolors.ENDC}Total runtime of " + name + " is " + str(time_diff) + " seconds.")

class ACSVException(Exception):
    def __init__(self, message, *args):
        super().__init__(message)
        self.message = message
        self.info = args
    
    def __str__(self):
        return self.message

def DesmosifyPolynomial(F):
    return " + ".join(["{0}x**{{{1}}}".format(coeff, power) for (coeff, power) in zip(F.coefficients(), range(F.degree()+2))])

def SageifyPolynomial(F):
    return " + ".join(["{0}*x**{1}".format(coeff, power) for (coeff, power) in zip(F.coefficients(), range(F.degree()+2))])

def Prettify(x, trunc = 5):
    x = CIF(x)
    if (x.is_exact()):
        return float(x.real()) + float(x.imag()) * I
    if (x.real().contains_zero()):
        x = x.imag() * I
    if (x.imag().contains_zero()):
       x = x.real()
    return round(float(x.real()), trunc) + round(float(x.imag()), trunc) * I

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
