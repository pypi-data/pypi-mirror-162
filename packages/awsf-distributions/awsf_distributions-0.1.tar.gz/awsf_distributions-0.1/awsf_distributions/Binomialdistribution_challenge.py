from .Generaldistribution import Distribution
import math
import matplotlib.pyplot as plt

class Binomial(Distribution):
    """ Binomial distribution class for calculating and 
    visualizing a Binomial distribution.
    
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data_list (list of floats) a list of floats to be extracted from the data file
        p (float) representing the probability of an event occurring
                
    """
       

    def __init__(self, p=0.5, n=5):
        self.p = p
        self.n = n
        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev()) 
            
    def calculate_mean(self): 
        """Function to calculate the mean from p and n
        
        Args: 
            None
        
        Returns: 
            float: mean of the data set"""
        return self.p * self.n  

    def calculate_stdev(self):
        """Function to calculate the standard deviation from p and n.
        
        Args: 
            None
        
        Returns: 
            float: standard deviation of the data set
    
        """
        return math.sqrt(self.n * self.p * (1 - self.p)) 



        """Function to calculate p and n from the data set. The function updates the p and n variables of the object.
        
        Args: 
            None
        
        Returns: 
            float: the p value
            float: the n value
    
        """
    def replace_stats_with_data(self):
        n = len(self.data)
        p = sum(self.data) / n
        self.n = n
        self.p = p
        self.calculate_mean()
        self.calculate_stdev()

        return p, n
       

    
        """Function to output a histogram of the instance variable data using 
        matplotlib pyplot library.
        
        Args:
            None
            
        Returns:
            None
        """
    #    plt.hist(self.data)
    
        """Probability density function calculator for the binomial distribution.
        
        Args:
            k (float): point for calculating the probability density function
            
        
        Returns:
            float: probability density function output
        """
    def pdf(self, k):
        """Probability density function calculator for the binomial distribution.
        
        Args:
            x (float): point for calculating the probability density function
            
        
        Returns:
            float: probability density function output
        """
        
        a = math.factorial(self.n) / (math.factorial(k) * (math.factorial(self.n - k)))
        b = (self.p ** k) * (1 - self.p) ** (self.n - k)
        
        return a * b
		




        """Function to plot the pdf of the binomial distribution
        
        Args:
            None
        
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
            
        """
    
    def __add__(self, other): 
        """Function to add together two Binomial distributions with equal p

        Args:
            other (Binomial): Binomial instance
            
        Returns:
            Binomial: Binomial distribution
            
        """
        try:
            assert self.p == other.p, 'p values are not equal'
        except AssertionError as error:
            raise
        result = Binomial()
        result.p = self.p
        result.n = self.n + other.n
        result.calculate_mean()
        result.calculate_stdev()
            
        return result 
        
    def __repr__(self):
        """Function to output the characteristics of the Binomial instance
        
        Args:
            None
        
        Returns:
            string: characteristics of the Binomial object
        
        """
        return f'mean {self.mean}, standard deviation {self.stdev}, p {self.p}, n {self.n}'
