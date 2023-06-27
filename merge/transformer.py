from jinja2 import Environment, FileSystemLoader
import json
import re
import signatures


BINARY_OP = ["And", "Or"]
UNARY_OP = ["Pred"]
SIGNATURES = []
PATH = "./tests/or_2"


def merger(subformula_left:dict, subformula_right:dict) -> tuple[list, list, list]:
    args_left = [var for var in subformula_left['args'] if (var[0] == 'x') or (var == 'tp')]
    args_right = [var for var in subformula_right['args'] if (var[0] == 'x') or (var == 'tp')]

    union = sorted(list(set(args_right + args_left)), key=lambda x:  x[1:])
    union.remove("tp")
    union = ['tp'] + union


    sig_left = subformula_left['sig']
    add_sig_left = subformula_left['add_sig']
    sig_right = subformula_right['sig']
    add_sig_right= subformula_right['add_sig']
    sig = []
    add_sig = []
    for elem in union:
        if elem in args_left:
            index = args_left.index(elem)
            sig.append(sig_left[index])
            add_sig.append(add_sig_left[index])
        else:
            index = args_right.index(elem)
            sig.append(sig_right[index])
            add_sig.append(add_sig_right[index])
    
    return sig, add_sig, union

def pred_op(op:str, js_formula:list, id:int):
    formula = {}
    name = js_formula[1].capitalize()
    sig1, sig2 = signatures.search(SIGNATURES, name)


    js_args = js_formula[2]
    args = ['tp']
    for input in js_args:
        typ = input[0]
        val = input[1][1]
        if(typ == 'Var'):
            args.append('x' + str(val))
        elif(typ == 'Const'):
            args.append(str(val))
    

    formula['operator'] = op
    formula['name'] = name
    formula['identifier'] = id
    formula['sig'] = sig2
    formula['add_sig'] = sig1
    formula['args'] = args
    

    id += 1
    return formula, id


def and__or_op(op:str, js_formula:list, id:int):
    formula = {}
    formula['operator'] = op
    formula['identifier'] = id
    id += 1

    js_left_subformula = js_formula[1]
    js_right_subformula = js_formula[2]

    subformula_left,id  = general_formula(js_left_subformula,id)
    formula['subformula_left'] = subformula_left

    subformula_right,id  = general_formula(js_right_subformula,id)
    formula['subformula_right'] = subformula_right

    sig, add_sig, args = merger(subformula_left, subformula_right)
    
    formula['sig'] = sig
    formula['add_sig'] = add_sig
    formula['args'] = args


    return formula, id




def binary_formula(op:str, js_formula:list, id:int):
    if op == 'And':
        return and__or_op(op,js_formula,id)
    elif op == 'Or':
        return and__or_op(op,js_formula,id)
    return and__or_op(op,js_formula,id)

def unary_formula(op:str, js_formula:list, id:int):
    #if op == 'Pred':
    return pred_op(op,js_formula,id)
    


def general_formula(js_formula:list, id=0):
    op = js_formula[0]
    if op in BINARY_OP:
        return binary_formula(op,js_formula, id)
    elif op in UNARY_OP:
        return unary_formula(op,js_formula, id)

    else:
        raise RuntimeError("not defined args for signature")


def remove_entries_with_keyname(data, keyname):
    if isinstance(data, dict):
        if keyname in data:
            del data[keyname]
        for value in data.values():
            remove_entries_with_keyname(value, keyname)
    elif isinstance(data, list):
        for item in data:
            remove_entries_with_keyname(item, keyname)


def translate(filename_or_path:str): # -> dict later
    global SIGNATURES
    SIGNATURES = signatures.get_signatures(PATH+'/ex.sig')
    tree = json.load(open(filename_or_path))

    formula,id = general_formula(tree)
    remove_entries_with_keyname(formula, 'add_sig') 
    output = json.dumps(formula, indent=6)
    print(re.sub(r'",\s+', '", ', output))

    return general_formula(tree)

    """
    formula,id = general_formula(tree)
    remove_entries_with_keyname(formula, 'add_sig') 
    output = json.dumps(formula, indent=6)
    print(re.sub(r'",\s+', '", ', output))
    """


def main():
    
    formula,_= translate(PATH + '/ex.json')
    context = {'formula': formula}
    
    environment = Environment(loader=FileSystemLoader("templates/"), trim_blocks=True, lstrip_blocks=True)
    results_template = environment.get_template("base.dl")

    with open("program.dl", mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))



if __name__ == '__main__':
    main()
