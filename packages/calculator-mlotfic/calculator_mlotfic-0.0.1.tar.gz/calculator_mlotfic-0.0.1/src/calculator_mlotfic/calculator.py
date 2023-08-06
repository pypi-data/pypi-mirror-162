# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 22:00:25 2022 

@author: mahmoud lotfi
"""

# Program make a simple calculator

# class definition
class Calculator():
    '''
    Create a class and using a constructor to initialize values of that class.
    '''
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    # This method add two nubers
    def add(self):
        return self.x + self.y
    # This method subtracting two numbers
    def sub(self):
        return self.x - self.y

    # This method multiplying two numbers
    def mul(self):
        return self.x * self.y  

    # This method dividing two numbers
    def div(self):
        return self.x / self.y