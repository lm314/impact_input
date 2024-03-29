# Python Class For managing IMPACT-Z/T input files

import copy
import re
from collections.abc import Iterable

class ImpactIN:
    
    def __init__(self,filename: str="", contents: str = "",exclude_comments: bool = True):
        #Read in uncommented lines of impact input file and contents as single string
        if not contents:
            with open(filename) as f:
                if exclude_comments == True:
                    textline = []
                    for line in f:
                        if (not line.lstrip().startswith('!')):
                            textline.append(line)
                    contents = contents.join(textline)
                else:
                    contents = f.read()
        self.contents = contents
        
    def replace(self,**kwargs):
        # Replace all variables with the associated values in string
        # return new instance of IMPACT_IN
        # To replace variables using two strings using the keyword arguments
        # varnames and varvals.
        # To replace using a dictionary, use the keyword variables.
        
        if all([key in ['varnames','varvals'] for key in kwargs.keys()]):
            varnames = kwargs['varnames']
            varvals = kwargs['varvals']
        elif 'variables' in kwargs.keys():
            varnames = kwargs['variables'].keys()
            varvals = kwargs['variables'].values()
        else:
            raise TypeError(f'The following keyword arguments were provided but did not match match the expected values: {kwargs.keys()}',)
            
        # cannot loop over scaler
        if isinstance(varvals, Iterable):
            rep = dict((rf'\b{re.escape(k)}\b', str(v)) for k, v in zip(varnames,varvals)) 
        else:
            rep = {rf'\b{re.escape(varnames)}\b':str(varvals)}
            
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m : rep[rf'\b{re.escape(m.group(0))}\b'], self.contents)
        return ImpactIN(contents=text)
        
    def write(self,filename: str):
        with open(filename, 'w') as f:
            f.write(self.contents)
  
    def variables(self):
        # returns the variables the need to be set in the contents of the file
        variable = []
        for line in self.contents.splitlines():
            if (not line.lstrip().startswith('!')):
                line_cleaned = line.split("/", 1)[0]
                for chunk in line_cleaned.split():
                    try:
                        float(chunk)
                    except ValueError:
                        variable.append(chunk)

        # remove numbers in fortran d notation
        regex = re.compile(r"[+-]?((\d+\.\d*)|(\.\d+)|(\d+))([dD][+-]?\d+)?")
        variable = [i for i in variable if not regex.match(i)]
        
        return variable
        
    def __str__(self):
        return self.contents
