from jinja2 import Environment, FileSystemLoader
import json
import re
import signatures
import warnings


BINARY_OP = ["And", "Or", "Since", "Until", "Eq"]
UNARY_OP = ["Pred", "Prev", "Next", "Exists", "Neg"]
SIGNATURES = []
PATH = "./tests/and_2"


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
    id_cnter = 0
    for elem in union:
        if elem in args_left:
            index = args_left.index(elem)
            if elem == "tp":
                sig.append(sig_left[index])
                add_sig.append(add_sig_left[index])
            else:
                val = re.sub('\d+',str(id_cnter),sig_left[index], count=1)
                splitted = val.split(":")
                sig.append(val)
                add_sig.append(splitted)
                id_cnter+=1
        else:
            index = args_right.index(elem)
            if elem == "tp":
                sig.append(sig_right[index])
                add_sig.append(add_sig_right[index])
            else:
                val = re.sub('\d+',str(id_cnter),sig_right[index], count=1)
                splitted = val.split(":")
                sig.append(val)
                add_sig.append(splitted)
                id_cnter+=1
    
    return sig, add_sig, union

def intervall(int:list) -> tuple[int,int]:
    lw = int[0][1]
    up = -1
    pre_up = int[1]
    if(pre_up[0] != "Infinity_enat"):
        up = pre_up[1][1]

    return lw, up


def pred_op(op:str, js_formula:list, id:int) -> tuple[dict, int]:
    name = js_formula[1].capitalize()

    formula = {}
    sig1, sig2 = signatures.search(SIGNATURES, name)

    js_args = js_formula[2]
    args = ['tp']
    cnt = 0
    index = 1
    sig = [sig2[0]]
    sub_args  = ['tp']
    add_sig = [sig1[0]]
    formula['constraints'] = []
    for input in js_args:
        typ = input[0]
        val = input[1][1]
        if(typ == 'Var'):

            if(('x' + str(val)) in sub_args):
                sub_args.append('x' + str(val) + "_" + str(cnt))
                formula['constraints'].append('x' + str(val) + "==" + 'x' + str(val) + "_" + str(cnt))
                cnt += 1
            else:
                sub_args.append('x' + str(val))
                args.append('x' + str(val))
                sig.append(sig2[index])
                add_sig.append(sig1[index])
        elif(typ == 'Const'):
            args.append(str(val))

        index += 1
        
    formula['sub_args'] = sub_args
    formula['operator'] = op
    formula['name'] = name
    formula['identifier'] = id
    formula['sig'] = sig
    formula['add_sig'] = add_sig
    formula['args'] = args
        
    id += 1
    return formula, id

def has_variables(lst:list) -> bool:
    for element in lst:
        if element.startswith('x'):
            return True
    return False

def not_op(op:str, js_formula:list, id:int)-> tuple[dict, int]:
    
    formula = {}
    formula['operator'] = op
    formula['identifier'] = id
    id += 1

    subformula, id = general_formula(js_formula[1],id)

    if(has_variables(subformula['args'])):
        warnings.warn("Might be incorrect, be careful")
        formula['subformula'] = subformula
        formula['sig'] = subformula['sig']
        formula['add_sig'] = subformula['add_sig']
        formula['args'] = subformula['args']
    else:
        formula['subformula'] = subformula
        formula['sig'] = ["tp:s32"]
        formula['add_sig'] = [["tp","s32"]]
        formula['args'] = ["tp"]

    return formula,id

def true_op(op:str, js_formula:list, id:int)-> tuple[dict, int]:
    
    if(js_formula[1] != js_formula[2]):
        raise RuntimeError("Eq not supported, only used as TRUE")

    formula = {}
    formula['operator'] = "true"
    formula['identifier'] = id
    formula['sig'] = ["tp:s32"]
    formula['args'] = ["tp"]
    formula['add_sig'] = [["tp","s32"]]
    id += 1
    return formula,id

def exists_op(op:str, js_formula:list, id:int) -> tuple[dict, int]:
    formula = {}
    formula['operator'] = op
    formula['identifier'] = id
    id += 1

    not_outputted_ids = ['x0']
    js_formula = js_formula[1]
    next = 1
    while (js_formula[0] == 'Exists'):
        not_outputted_ids.append('x'+str(next))
        next += 1
        js_formula = js_formula[1]

    subformula, id = general_formula(js_formula,id)

    formula['subformula'] = subformula
    formula['sig'] = []
    formula['add_sig'] = []
    formula['args'] = []


    for index in range(len(subformula['args'])):
        if subformula['args'][index] in not_outputted_ids:
            continue
        else:
            formula['sig'].append(subformula['sig'][index])
            formula['add_sig'].append(subformula['add_sig'][index])
            formula['args'].append(subformula['args'][index])



    return formula, id

def prev_next_op(op:str, js_formula:list, id:int) -> tuple[dict, int]:
    formula = {}
    formula['operator'] = op
    formula['identifier'] = id
    id += 1
    lw, up = intervall(js_formula[1])
    formula['intervall_lw'] = lw
    formula['intervall_up'] = up

    subformula, id = general_formula(js_formula[2],id)
    
    formula['subformula'] = subformula
    formula['sig'] = subformula['sig']
    formula['add_sig'] = subformula['add_sig']
    formula['args'] = subformula['args']

    return formula, id
    

def and_or_op(op:str, js_formula:list, id:int) -> tuple[dict, int]:

    formula = {}
    formula['identifier'] = id
    id += 1

    #special case
    if ((op == 'And') and (js_formula[1][0] == 'Neg')):
        warnings.warn("Should not be monitorable in MonPoly")
        formula['operator'] = 'And_Not'
        js_left_subformula = js_formula[2]
        js_right_subformula = js_formula[1][1]
    elif ((op == 'And') and (js_formula[2][0] == 'Neg')):
        formula['operator'] = 'And_Not'
        js_left_subformula = js_formula[1]
        js_right_subformula = js_formula[2][1]
    else:
        formula['operator'] = op
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

def since_until_op(op:str, js_formula:list, id:int) -> tuple[dict, int]:
    formula = {}
    formula['operator'] = op
    formula['identifier'] = id
    id += 1

    lw, up = intervall(js_formula[2])
    formula['intervall_lw'] = lw
    formula['intervall_up'] = up

    js_left_subformula = js_formula[1]
    js_right_subformula = js_formula[3]

    subformula_left,id  = general_formula(js_left_subformula,id)
    formula['subformula_left'] = subformula_left

    subformula_right,id  = general_formula(js_right_subformula,id)
    formula['subformula_right'] = subformula_right

    sig, add_sig, args = merger(subformula_left, subformula_right)
    
    formula['sig'] = sig
    formula['add_sig'] = add_sig
    formula['args'] = args


    return formula, id

def binary_formula(op:str, js_formula:list, id:int) -> tuple[dict, int]:
    if op == 'And':
        return and_or_op(op,js_formula,id)
    elif op == 'Or':
        return and_or_op(op,js_formula,id)
    elif op == 'Since':
        return since_until_op(op,js_formula,id)
    elif op == 'Eq':
        return true_op(op,js_formula,id)
    elif op == 'Until':
        warnings.warn("Using UNTIL might be unsound in more complex formulas")
        return since_until_op(op,js_formula,id)
    raise RuntimeError("Missing case")
    

def unary_formula(op:str, js_formula:list, id:int):
    if op == 'Pred':
        return pred_op(op,js_formula,id)
    elif op == 'Prev':
        return prev_next_op(op,js_formula,id)
    elif op == 'Next':
        return prev_next_op(op,js_formula,id)
    elif op == 'Exists':
        return exists_op(op,js_formula,id)
    elif op == 'Neg':
        warnings.warn("Negation is not fully supported in the translation.")
        return not_op(op,js_formula,id)
    else:
        raise RuntimeError("Missing case")
    

def general_formula(js_formula:list, id=0) -> tuple[dict, int]:
    op = js_formula[0]
    if op in BINARY_OP:
        return binary_formula(op,js_formula, id)
    elif op in UNARY_OP:
        return unary_formula(op,js_formula, id)

    else:
        raise RuntimeError("Missing case")


def remove_entries_with_keyname(data, keyname):
    if isinstance(data, dict):
        if keyname in data:
            del data[keyname]
        for value in data.values():
            remove_entries_with_keyname(value, keyname)
    elif isinstance(data, list):
        for item in data:
            remove_entries_with_keyname(item, keyname)


def translate(filename_or_path:str) -> tuple[dict, int]:
    global SIGNATURES
    SIGNATURES = signatures.get_signatures(PATH+'/ex.sig')
    tree = json.load(open(filename_or_path))


    formula,id = general_formula(tree)
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
    global signatures
    formula,_= translate(PATH + '/ex.json')
    signatures = signatures.get_signatures(PATH + '/ex.sig')
    context = {
         'signatures': signatures,
         'formula': formula
     }
    
    environment = Environment(loader=FileSystemLoader("templates/"), trim_blocks=True, lstrip_blocks=True)
    results_template = environment.get_template("base.dl")

    with open("program.dl", mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))



if __name__ == '__main__':
    main()
