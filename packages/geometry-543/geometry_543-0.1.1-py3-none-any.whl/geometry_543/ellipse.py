import numpy as np

class Ellipse:
    """
    Instantiate a representation of an ellipse.

    :param r0: length of first axis
    :type number: float

    :param r1: length of second axis
    :type number: float
    """

    
    def __init__(self, r0, r1):
        self.r0 = r0
        self.r1 = r1

        
    def calc_area(self):
        """
        Calculate the area of this ellipse
        """
        return self.r0*self.r1*np.pi
    
