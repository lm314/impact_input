# Python Class For managing IMPACT-Z/T input files

import copy
import re
from collections.abc import Iterable

class IMPACT_IN:
    
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
        
    def replace(self,varnames=[],varvals=[]):
        # Replace all variables with the associated values in string
        # return new instance of IMPACT_IN
        
        # cannot loop over scaler
        if isinstance(varvals, Iterable):
            rep = dict((re.escape(k), str(v)) for k, v in zip(varnames,varvals)) 
        else:
            rep = {re.escape(varnames):str(varvals)}
            
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m : rep[re.escape(m.group(0))], self.contents)
        return IMPACT_IN(contents=text)
        
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