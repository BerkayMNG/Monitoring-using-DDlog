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

    #always new ideas, otherwise problems occur- doesnt matter anyways
    counter_int = 0
    counter_string = 0
    for s in strings:
        index = s.index("(")
        symbol = s[:index]
        argss = s[index:]

        arguments = argss.replace("(", "").replace(")", "").split(",")
        transformed_1 = [('tp', 'u32')]
        transformed_2 = ['tp:u32']

        for argument in arguments:
            args_type = argument.split(":")[1]
            if(args_type == "string"):
                transformed_1.append(("idy"+str(counter_string), "string"))
                transformed_2.append(("idy"+str(counter_string) + ":string"))
                counter_string += 1
            elif(args_type == "int"):
                transformed_1.append(("idx"+str(counter_int), "s32"))
                transformed_2.append(("idx"+str(counter_int) + ":s32"))
                counter_int += 1
            else:
                raise RuntimeError("not defined args for signature")
            
        signatures.append((symbol,transformed_1,transformed_2))
    
    return signatures

def search(signatures:list, name:str) -> list:
    name = name.capitalize()
    for p,sig1,sig2 in signatures:
        if p == name:
            return sig1, sig2
    raise RuntimeError("not defined args for signature")
    
    