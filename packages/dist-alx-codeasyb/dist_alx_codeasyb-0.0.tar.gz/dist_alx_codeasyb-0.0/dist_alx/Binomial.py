import math
from .Distribution import Distribution

class Binomial(Distribution):
    """Binomial distribution class for calculating and 
    visualizing a binomial distribution
    
    Attributes:
        mean (float) representing the mean of the distribution
        stdev (flaot) representing the standard deviation of the distribution
        data_list (list of floats) a list of floats to be extracted from the data file
        p (float) representing the probility of an evern occuring 
        n (int) number of trials
    """
    def __init__(self, prob=5, size=20):
        
        self.n = size
        self.p = prob
        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev())
        
    def calculate_mean(self):
        """Function to calculate the mean form p and n
        
        Args:
            None
        Returns:
            float: mean of the data set
        """
        self.mean = self.p * self.n
        return self.mean
        
    def calculate_stdev(self):
        """Function to calculate the standard deviation from p and n.
        
        Args:
            None
        Returns:
            flaots: standard deviation of the data set
        """
        self.stdev = math.sqrt(self.n * self.p * (1 - self.p))
        return stdev