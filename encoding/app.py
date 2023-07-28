from jinja2 import Environment, FileSystemLoader
import json

"""
Needed, since we cannot have lowercase relations in DDlog!
"""
def capitalize_first_letters(strings:list) -> list:
    capitalized_strings = [string.capitalize() for string in strings]
    return capitalized_strings

"""
Gets the signatures from a file and transforms it . Please use capitalized signatures and
write one signature per line and do not use "," to seperate predicates!
Do not use names as Timestamp, Output or result.
Only allows strings and int as inputs.

Remark: Does only consider "strings" or "int" yet as argss, can be easily extended
"""
def get_signatures(file_or_path:str) -> list:
    strings = []
    with open(file_or_path, 'r') as file:
        content = file.read()
        #Yes it's ugly- but now we don't have to worry about how sig is formatted..
        content = content.replace('\n', '').replace(' ', '').replace('\t', '')
        strings = capitalize_first_letters([s + ')' for s in content.split(")") if s!= ""])
    
    signatures = []
    for s in strings:
        index = s.index("(")
        symbol = s[:index]
        argss = s[index:]

        arguments = argss.replace("(", "").replace(")", "").split(",")
        transformed = []

        counter_int = 0
        counter_string = 0
        for argument in arguments:
            args_type = argument.split(":")[1]
            if(args_type == "string"):
                transformed.append(("y"+str(counter_string), "string"))
                counter_string += 1
            elif(args_type == "int"):
                transformed.append(("x"+str(counter_int), "s32"))
                counter_int += 1
            else:
                raise RuntimeError("not defined args for signature")
            
        signatures.append((symbol,transformed))
    
    return signatures
          
"""
Gets the nested list representing the formula from a Json file
"""
def get_Formula(filename_or_path:str) -> list:
    return json.load(open(filename_or_path))

def handle_none(value):
    return value if value is not None else ''

def main():
    #formula = get_Formula('ex.json')
    signatures = get_signatures("ex.sig")
    

    #Formula : P(x) UNTIL[2,4] (NEXT Q(x,y))
    formula = {
                'operator': 'Until',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32","id1:s32"],
                'args': ["tp","x0", "x1"],
                'intervall_lw': 2,
                'intervall_up': 4,

                'subformula_left': {
                    'operator': 'Pred',
                    'name': "P",
                    'sig': ["tp:u32", "id0:s32"],
                    'args': ["tp","x0"], 
                    'identifier': 1
                },
                'subformula_right': {
                    'operator': 'Next',
                    'sig': ["tp:u32", "id0:s32","id1:s32"],
                    'args': ["tp","x0", "x1"], 
                    'intervall_lw': 0,
                    'intervall_up': -1,
                    'identifier': 2,
                    'subformula': {
                        'operator': 'Pred',
                        'name': "Q",
                        'sig': ["tp:u32", "id0:s32","id1:s32"],
                        'args': ["tp","x0", "x1"], 
                        'identifier': 3  
                    }
                },

    }


    context = {
         'signatures': signatures,
         'formula': formula
     }


    environment = Environment(loader=FileSystemLoader("templates/"),trim_blocks=True, lstrip_blocks=True)
    results_template = environment.get_template("base.dl")

    with open("program.dl", mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))





if __name__ == '__main__':
    main()


    """
    #Formula : P(x,y) AND Q(y,x)
    formula = {
                'operator': 'And',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32", "id1:s32"],
                'args':   ["tp","x0","x1"], 
                'subformula_left': {
                        'operator': 'Pred',
                        'name': "P",
                        'sig': ["tp:u32", "id0:s32", "id1:s32"],
                        'args' : ["tp","x0","x1"],
                        'identifier': 1
                },
                'subformula_right': {
                        'operator': 'Pred',
                        'name': "Q",
                        'sig': ["tp:u32", "id0:s32", "id1:s32"],
                        'args': ["tp","x1","x0"], 
                        'identifier': 2
                }
    }
    """

    """
    #Formula : P(x,y) AND Q(y,x) AND R(5)
    
    formula = {
                'operator': 'And',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32", "id1:s32", "id2:s32"],
                'args':   ["tp","x0","x1", "5"], 
                'args_left': ["tp","x0","x1"],
                'args_right': ["tp","5"], 

                'subformula_left': {
                    'operator': 'And',
                    'identifier': 1,
                    'sig': ["tp:u32", "id0:s32", "id1:s32"],
                    'args':   ["tp","x0","x1"],
                    'args_left':["tp","x0","x1"],
                    'args_right':["tp","x1","x0"], 
                    'subformula_left': {
                            'operator': 'Pred',
                            'name': "P",
                            'sig': ["tp:u32", "id0:s32", "id1:s32"],
                            'args' : ["tp","x0","x1"],
                            'identifier': 2
                    },
                    'subformula_right': {
                            'operator': 'Pred',
                            'name': "Q",
                            'sig': ["tp:u32", "id0:s32", "id1:s32"],
                            'args' : ["tp","x1","x0"], 
                            'identifier': 3
                    }
                },

                'subformula_right': {
                    'operator': 'Pred',
                    'name': "R",
                    'sig': ["tp:u32", "id0:s32"],
                    'args': ["tp","5"], 
                    'identifier': 4
                }
          
    }
     
    """

    """
    #Formula : NOT R(5)

    formula = {
                'operator': 'Neg',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32"],
                'args': ["tp","5"],
                'subformula': {
                        'operator': 'Pred',
                        'name': "R",
                        'sig': ["tp:u32", "id0:s32"],
                        'args': ["tp","5"], 
                        'identifier': 1
                }
    }
    """

    """
    #Formula : P(x) OR Q(x)
    formula = {
                'operator': 'Or',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32"],
                'args': ["tp","x0"],
                'subformula_left': {
                        'operator': 'Pred',
                        'name': "P",
                        'sig': ["tp:u32", "id0:s32"],
                        'args': ["tp","x0"], 
                        'identifier': 1
                },
                'subformula_right': {
                        'operator': 'Pred',
                        'name': "Q",
                        'sig': ["tp:u32", "id0:s32"],
                        'args': ["tp","x0"], 
                        'identifier': 2
                }
    }
    """

    """
    #Formula : Exists x. P(x,y)

    formula = {
                'operator': 'Exists',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32", "id1:s32"],
                'args': ["tp","x0", "x1"],
                'subformula': {
                        'operator': 'Pred',
                        'name': "P",
                        'sig': ["tp:u32", "id0:s32", "id2:s32"],
                        'args': ["tp","x0", "x1"], 
                        'identifier': 1
                }
    }
    """

"""
    #Formula : PREV[0,4] (P(x) AND Q(x))
    formula = {
                'operator': 'Prev',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32"],
                'args': ["tp","x0"],
                'intervall_lw': 0,
                'intervall_up': 4,
                'subformula': {
                        'operator': 'And',
                        'sig': ["tp:u32", "id0:s32"],
                        'args': ["tp","x0"], 
                        'identifier': 1,
                        'subformula_left': {
                            'operator': 'Pred',
                            'name': "P",
                            'sig': ["tp:u32", "id0:s32"],
                            'args': ["tp","x0"], 
                            'identifier': 2
                        },
                        'subformula_right': {
                            'operator': 'Pred',
                            'name': "Q",
                            'sig': ["tp:u32", "id0:s32"],
                            'args': ["tp","x0"], 
                            'identifier': 3
                        },
                }
    }
"""

"""

    #Formula : PREV (P(x) AND Q(x))
    formula = {
                'operator': 'Prev',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32"],
                'args': ["tp","x0"],
                'intervall_lw': 0,
                'intervall_up': -1,
                'subformula': {
                        'operator': 'And',
                        'sig': ["tp:u32", "id0:s32"],
                        'args': ["tp","x0"], 
                        'identifier': 1,
                        'subformula_left': {
                            'operator': 'Pred',
                            'name': "P",
                            'sig': ["tp:u32", "id0:s32"],
                            'args': ["tp","x0"], 
                            'identifier': 2
                        },
                        'subformula_right': {
                            'operator': 'Pred',
                            'name': "Q",
                            'sig': ["tp:u32", "id0:s32"],
                            'args': ["tp","x0"], 
                            'identifier': 3
                        },
                }
    }
"""

"""
    #Formula : P(x) SINCE[2,4] Q(x,y)
    formula = {
                'operator': 'Since',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32","id1:s32"],
                'args': ["tp","x0", "x1"],
                'intervall_lw': 2,
                'intervall_up': 4,

                'subformula_left': {
                    'operator': 'Pred',
                    'name': "P",
                    'sig': ["tp:u32", "id0:s32"],
                    'args': ["tp","x0"], 
                    'identifier': 1
                },
                'subformula_right': {
                    'operator': 'Pred',
                    'name': "Q",
                    'sig': ["tp:u32", "id0:s32","id1:s32"],
                    'args': ["tp","x0", "x1"], 
                    'identifier': 2
                },

    }
"""

"""
    #Formula : P(x) UNTIL[2,4] Q(x,y)
    formula = {
                'operator': 'Until',
                'identifier': 0,
                'sig': ["tp:u32", "id0:s32","id1:s32"],
                'args': ["tp","x0", "x1"],
                'intervall_lw': 2,
                'intervall_up': 4,

                'subformula_left': {
                    'operator': 'Pred',
                    'name': "P",
                    'sig': ["tp:u32", "id0:s32"],
                    'args': ["tp","x0"], 
                    'identifier': 1
                },
                'subformula_right': {
                    'operator': 'Pred',
                    'name': "Q",
                    'sig': ["tp:u32", "id0:s32","id1:s32"],
                    'args': ["tp","x0", "x1"], 
                    'identifier': 2
                },

    }
"""