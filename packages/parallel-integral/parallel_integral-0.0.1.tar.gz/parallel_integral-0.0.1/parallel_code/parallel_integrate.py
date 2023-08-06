import numpy as np

class Integrator:
    def __init__(self,X,Y):
        self.X = X
        self.Y = Y
        
    def integrate(self):
        self.integral = np.sum(self.Y*(self.X[-1]-self.X[-2]))
        