import math
from .Distribution import Distribution

class Gaussian(Distribution):
    """Gaussian distribution class for calculating and 
    visualizing a Gaussian distribution.

    Attributes:
        mean (flaot) representing the mea value of the distribution
        stdev (flaot) representing the standard deviationg of the distribution
        data_list (list of floats) a list of floats extracted from the data file
    """
    def __init__(self, mu=0, sigma=1):
        Distribution.__init__(self, mu, sigma)
        
    def calculate_mean(self):
        
        """Function to calculate the mean of the data set.
        
        Args: 
            None
        Returns:
            float: mean of the data set
        """
        avg = 1.0 * sum(self.data) / len(self.data)
        
        self.mean = avg
        return self.mean
    
    def calculate_stdev(self, sample=True):
        """Function to calculate the standard deviation of the data set.

        Args:
            sample (bool, optional): whether the data represents a sample or population
        
        Returns:
            float: standard deviation of the data set
        """
        if sample:
            n = len(self.data) - 1
        else:
            n = len(self.data)
        
        mean = self.calculate_mean()
        sigma = 0
        
        for d in self.data:
            sigma += (d - mean) ** 2
        
        sigma = math.sqrt(sigma / n)
        self.stdev = sigma
        return self.stdev
        

    def __repr__(self):
        """Function to output the characteristics of the Gaussain instance
        
        Args:
            None
        Returns:
            string: characteristics of the Gaussian
        """
        return "mean {}, standard deviation {}".format(self.mean, self.stdev)