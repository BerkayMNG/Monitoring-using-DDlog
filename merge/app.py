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

def main():
    #formula = get_Formula('ex.json')
    signatures = get_signatures("ex.sig")
    """
    #Formula : P(x,y) AND Q(y,x)
    formula = {
                'operator': 'And',
                'identifier': 0,
                'args':   [("x0", "s32"), ("x1", "s32")], 
                'args_left': [("x0", "s32"), ("x1", "s32")],
                'args_right':[("x1", "s32"), ("x0", "s32")], 
                'subformula_left': {
                        'operator': 'Pred',
                        'name': "P",
                        'args' : [("x0", "s32"), ("x1", "s32")],
                        'identifier': 1
                },
                'subformula_right': {
                        'operator': 'Pred',
                        'name': "Q",
                        'args': [("x1", "s32"), ("x0", "s32")], 
                        'identifier': 2
                }
    }
    """

    #Formula : P(x,y) AND Q(y,x) AND R(y)
    formula = {
                'operator': 'And',
                'identifier': 0,
                'args':   [("x0", "s32"), ("x1", "s32")], 
                'args_left': [("x0", "s32"), ("x1", "s32")],
                'args_right':[("x1", "s32")], 

                'subformula_left': {
                    'operator': 'And',
                    'identifier': 1,
                    'args':   [("x0", "s32"), ("x1", "s32")], 
                    'args_left': [("x0", "s32"), ("x1", "s32")],
                    'args_right':[("x1", "s32"), ("x0", "s32")], 
                    'subformula_left': {
                            'operator': 'Pred',
                            'name': "P",
                            'args' : [("x0", "s32"), ("x1", "s32")],
                            'identifier': 2
                    },
                    'subformula_right': {
                            'operator': 'Pred',
                            'name': "Q",
                            'args': [("x1", "s32"), ("x0", "s32")], 
                            'identifier': 3
                    }
                },

                'subformula_right': {
                    'operator': 'Pred',
                    'name': "R",
                    'args': [("5", "s32")], 
                    'identifier': 4
                }

                
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