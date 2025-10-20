'''
Define if given parameters match a set of mandatory parameters
The tuple's first value will be match on the set

@input totest -> a tuple containing all params
@input expected -> a set of the mandatory parameters

@requirements 
    all parameters must be tuples and have the form (str, ...) where .. can be an number o parameters of any type. 
'''
def same_values_unordered(totest, expected) -> bool:
    if len(totest) != len(expected) :
        raise AttributeError(f"Must have {len(expected)} parameters but only got {len(totest)}")
    
    # create a set with current parameter str component
    param_first = [id for id, _ in totest]
    seen = set(param_first)

    if seen != expected:
        # Test for any 
        missing = expected - seen
        extra = [v for v in param_first if param_first.count(v) > 1]
        illegal_parameters = all([param not in expected for param in param_first])
        
        msg = []
        if illegal_parameters:
            msg.append[f"Illegal parameter: {", ".join(illegal_parameters)}"]
        if missing:
            msg.append(f"Missing: {', '.join(missing)}")
        if extra:
            msg.append(f"Duplicates: {', '.join(set(extra))}")
        raise ValueError("Invalid parameters: " + "; ".join(msg))
    
    return True
    
'''
Return a list of string as a single string separated by \n, works recursivly

@input list -> a string or a list of strings or lists (lists must be lists of strings or lists recursivly)

@remark -> if a list ocntains everything but a str or a list, this will run indefinetly
'''
def flatten_str(list) -> str :
    return '\n'.join([s if type(s) == str else flatten_str(s) for s in list])

a = 'G1 X1.0 Y1.5 S7.0 Z4.0'
b = [a]
c = [b]
print(flatten_str(c))
print(type(a))