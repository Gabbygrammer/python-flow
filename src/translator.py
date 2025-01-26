import os

from translation import TranslationException

ordered_node_connections = []
connections_number = 0

def initialize(node_connections: list):
    global connections_number, ordered_node_connections
    ordered_node_connections = []
    connections_number = len(node_connections) - 1
    for connection in node_connections:
        if connection[0].type == "start":
            ordered_node_connections.append(connection[0])
            ordered_node_connections.append(connection[1])
            node_connections.remove(connection)
            return True
        elif connection[1].type == "start":
            ordered_node_connections.append(connection[1])
            ordered_node_connections.append(connection[0])
            node_connections.remove(connection)
            return True
    return False

def flow_to_code(node_connections: list, nodes: list):
    if initialize(node_connections):
        sort_connections(node_connections, nodes)
        print_result()
        try:
            code = translate_to_code()
            return code
        except TranslationException as e:
            raise e

def sort_connections(node_connections: list, nodes: list): # TODO: finish this once and for all
    is_first_path_connected = {} # contains whether the first path of the node was sorted or not (if the node has more than 1 output)
    opened_nodes = []
    for node in nodes:
        if node.output_circles_number > 1:
            is_first_path_connected[node] = False
    for _ in range(connections_number):
        other_node = ordered_node_connections[len(ordered_node_connections) - 1]
        if other_node.type in ["if", "def", "match", "forrange", "forlist"]:
            opened_nodes.append(other_node)
        for connection in node_connections:
            second_node = connection[1] if other_node == connection[0] else None
            if other_node.type in ["endif", "enddef", "endmatch", "endforrange", "endforlist", "return"]:
                opened_node = opened_nodes[len(opened_nodes) - 1]
                second_node = connection[1] if opened_node == connection[0] else None
                if second_node is None:
                    continue
                found = False
                for circle in opened_node.circles:
                    if is_first_path_connected[opened_node]:
                        if opened_node.circle_io_types[circle] == "output" and opened_node.circle_types[circle] == "2":
                            if opened_node.circle_connections[circle] in second_node.circles:
                                ordered_node_connections.append(second_node)
                                found = True
                                break
                if found:
                    opened_nodes.remove(opened_node)
                    break
                else:
                    continue

            if second_node is None:
                continue
            if other_node.output_circles_number <= 1:
                ordered_node_connections.append(second_node)
                node_connections.remove(connection)
                break
            else:
                found = False
                for circle in other_node.circles:
                    if not is_first_path_connected[other_node]:
                        if other_node.circle_io_types[circle] == "output" and other_node.circle_types[circle] == "1":
                            if other_node.circle_connections[circle] in second_node.circles:
                                ordered_node_connections.append(second_node)
                                is_first_path_connected[other_node] = True
                                found = True
                                break
                if found:
                    break

def print_result():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("------CONNECTION FLOW------")
    for node in ordered_node_connections:
        print(node.type)
        if not ordered_node_connections[len(ordered_node_connections) - 1] == node:
            print("|")
            print("V")

condition_dict = {"==": "==",
                  "!=": "!=",
                  ">": ">",
                  "<": "<",
                  ">=": ">=",
                  "<=": "<=",
                  "è": "is",
                  "non è": "not is",
                  "è in": "in",
                  "non è in": "not in"}

list_action_dict = {"Aggiungi": "append",
                    "Rimuovi": "remove"}

def validate_string(string: str):
    double_quote_count = 0
    single_quote_count = 0
    for char in string:
        if char == "\"":
            double_quote_count += 1
        elif char == "'":
            single_quote_count += 1
    if double_quote_count % 2 == 0 and single_quote_count % 2 == 0:
        return True
    else:
        return False

def validate_name(name: str):
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    for char in name:
        if char not in valid_chars:
            return False
    return True

def translate_to_code():
    code = ""
    indentation_level = 0
    declared_vars = []
    defined_funcs = []
    declared_lists = []
    is_first_case_of_last_match = False
    global last_node
    last_node = None
    for node in ordered_node_connections:
        match node.type:
            case "print":
                try:
                    line = f"{"    " * indentation_level}print({node.translate_items[0].get()})\n"
                    if validate_string(line):
                        if not "\"" and not "'" in node.translate_items[0].get():
                            if not node.translate_items[0].get() in declared_vars:
                                raise TranslationException(f"Variabile \"{node.translate_items[0].get()}\" non dichiarata", node)
                        code += line
                    else:
                        raise TranslationException("Stringa non chiusa correttamente", node)
                except AttributeError:
                    pass
            case "variabledecl":
                variable_name = ""
                variable_value = ""
                for item in node.translate_items:
                    try:
                        type = item.type
                        if type == "name":
                            name = item.get()
                            if validate_name(name):
                                variable_name = name
                                declared_vars.append(name)
                            else:
                                raise TranslationException(f"Nome variabile \"{name}\" non valido. Il nome deve contenere solo caratteri alfanumerici e/o trattini bassi", node)
                        elif type == "value":
                            value = item.get()
                            if validate_string(value):
                                variable_value = value
                            else:
                                raise TranslationException("Stringa non chiusa correttamente", node)
                    except AttributeError:
                        pass
                code += f"{"    " * indentation_level}{variable_name} = {variable_value}\n"
            
            case "variableset":
                variable_name = ""
                variable_value = ""
                for item in node.translate_items:
                    try:
                        type = item.type
                        if type == "name":
                            name = item.get()
                            if name in declared_vars:
                                variable_name = name
                            else:
                                raise TranslationException(f"Variabile \"{name}\" non dichiarata", node)
                        elif type == "value":
                            value = item.get()
                            if validate_string(value):
                                variable_value = value
                            else:
                                raise TranslationException("Stringa non chiusa correttamente", node)
                    except AttributeError:
                        pass
                code += f"{"    " * indentation_level}{variable_name} = {variable_value}\n"

            case "if":
                try:
                    if condition_dict[node.if_condition_operator.get()] == "not is":
                        line = f"{"    " * indentation_level}if not {node.translate_items[0].get()} is {node.translate_items[1].get()}:\n"
                        if validate_string(line):
                            code += line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    elif condition_dict[node.if_condition_operator.get()] == "not in":
                        line = f"{"    " * indentation_level}if not {node.translate_items[0].get()} in {node.translate_items[1].get()}:\n"
                        if validate_string(line):
                            code += line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    else:
                        line = f"{"    " * indentation_level}if {node.translate_items[0].get()} {condition_dict[node.if_condition_operator.get()]} {node.translate_items[1].get()}:\n"
                        if validate_string(line):
                            if not "\"" and not "'" in node.translate_items[0].get():
                                if not node.translate_items[0].get() in declared_vars:
                                    raise TranslationException(f"Variabile \"{node.translate_items[0].get()}\" non dichiarata", node)
                            if not "\"" and not "'" in node.translate_items[1].get():
                                if not node.translate_items[1].get() in declared_vars:
                                    raise TranslationException(f"Variabile \"{node.translate_items[1].get()}\" non dichiarata", node)
                            code += line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    indentation_level += 1
                except AttributeError:
                    pass

            case "else":
                try:
                    indentation_level -= 1
                    code += f"{"    " * indentation_level}else:\n"
                    indentation_level += 1
                except AttributeError:
                    pass

            case "endif":
                if last_node.type == "if":
                    raise TranslationException("Nodo di tipo \"se\" senza contenuto", last_node)
                indentation_level -= 1

            case "def":
                function_name = ""
                function_args = ""
                for item in node.translate_items:
                    try:
                        if item.type == "name":
                            name = item.get()
                            if validate_name(name):
                                function_name = name
                                defined_funcs.append(name)
                            else:
                                raise TranslationException(f"Nome funzione \"{name}\" non valido. Il nome deve contenere solo caratteri alfanumerici e/o trattini bassi", node)
                        elif item.type == "args":
                            function_args = item.get()
                            for arg in function_args:
                                if validate_name(arg):
                                    declared_vars.append(arg)
                                else:
                                    raise TranslationException(f"Nome argomento \"{arg}\" non valido. Il nome deve contenere solo caratteri alfanumerici e/o trattini bassi", node)
                    except:
                        pass
                code += f"{"    " * indentation_level}def {function_name}({function_args}):\n"
                indentation_level += 1

            case "defcall":
                function_name = ""
                function_args = ""
                for item in node.translate_items:
                    try:
                        if item.type == "name":
                            name = item.get()
                            if name in defined_funcs:
                                function_name = name
                            else:
                                raise TranslationException(f"Funzione non definita: \"{name}\"", node)
                        elif item.type == "args":
                            args = item.get()
                            if validate_string(args):
                                for arg in args.split(",").replace(" ", ""):
                                    if not "\"" and not "'" in arg:
                                        if not arg in declared_vars:
                                            raise TranslationException(f"Variabile \"{arg}\" non dichiarata", node)
                                function_args = args
                            else:
                                raise TranslationException("Stringa non chiusa correttamente", node)
                    except:
                        pass
                code += f"{"    " * indentation_level}{function_name}({function_args})\n"

            case "defcallvar":
                function_name = ""
                function_args = ""
                variable_name = ""
                for item in node.translate_items:
                    try:
                        if item.type == "name":
                            name = item.get()
                            if name in defined_funcs:
                                function_name = name
                            else:
                                raise TranslationException(f"Funzione non definita: \"{name}\"", node)
                        elif item.type == "args":
                            args = item.get()
                            if validate_string(args):
                                for arg in args.split(","):
                                    arg = arg.strip()
                                    if not "\"" and not "'" in arg:
                                        if not arg in declared_vars:
                                            raise TranslationException(f"Variabile \"{arg}\" non dichiarata", node)
                                function_args = args
                            else:
                                raise TranslationException("Stringa non chiusa correttamente", node)
                        elif item.type == "variable":
                            name = item.get()
                            if validate_name(name):
                                variable_name = name
                                declared_vars.append(name)
                            else:
                                raise TranslationException(f"Nome variabile \"{name}\" non valido. Il nome deve contenere solo caratteri alfanumerici e/o trattini bassi", node)
                    except:
                        pass
                code += f"{"    " * indentation_level}{variable_name} = {function_name}({function_args})\n"

            case "enddef":
                if last_node.type == "def":
                    raise TranslationException("Nodo di tipo \"def\" senza contenuto", last_node)
                indentation_level -= 1

            case "return":
                try:
                    line = f"{"    " * indentation_level}return {node.translate_items[0].get()}\n"
                    if validate_string(line):
                        code += line
                    else:
                        raise TranslationException("Stringa non chiusa correttamente", node)
                    indentation_level -= 1
                except:
                    pass

            case "listdecl":
                try:
                    if validate_name(node.translate_items[0].get()):
                        code += f"{"    " * indentation_level}{node.translate_items[0].get()} = []\n"
                        declared_lists.append(node.translate_items[0].get())
                    else:
                        raise TranslationException(f"Nome lista \"{node.translate_items[0].get()}\" non valido. Il nome deve contenere solo caratteri alfanumerici e/o trattini bassi", node)
                except:
                    pass

            case "listset":
                try:
                    action = list_action_dict[node.list_action.get()]
                    item_name = ""
                    list_name = ""
                    for item in node.translate_items:
                        if item.type == "item":
                            item = item.get()
                            if validate_string(item):
                                item_name = item
                            else:
                                raise TranslationException("Stringa non chiusa correttamente", node)
                        elif item.type == "list":
                            list = item.get()
                            if list in declared_lists:
                                list_name = list
                            else:
                                raise TranslationException(f"Lista non dichiarata: \"{list}\"", node)
                    items = item_name.split(";")
                    if len(items) > 1:
                        code += f"{"    " * indentation_level}for item in {"[" + ''.join(items) + "]"}:\n{"    " * indentation_level}    {list_name}.{action}(item)\n"
                    else:
                        code += f"{"    " * indentation_level}{list_name}.{action}({item_name})\n"
                except:
                    pass

            case "match":
                try:
                    variable_name = node.translate_items[0].get()
                    if variable_name in declared_vars:
                        code += f"{"    " * indentation_level}match {variable_name}:\n"
                        indentation_level += 1
                        is_first_case_of_last_match = True
                    else:
                        raise TranslationException(f"Variabile non dichiarata: \"{variable_name}\"", node)
                except:
                    pass

            case "case":
                try:
                    if not is_first_case_of_last_match:
                        indentation_level -= 1
                    else:
                        is_first_case_of_last_match = False
                    case_value = node.translate_items[0].get()
                    is_valid = False
                    try:
                        float(case_value)
                        is_valid = True
                    except:
                        if case_value in declared_vars or case_value == "default":
                            if case_value == "default":
                                case_value = "_"
                            is_valid = True
                        else:
                            if "\"" in case_value and "'" in case_value or "\"" in case_value or "'" in case_value:
                                if validate_string(case_value):
                                    is_valid = True
                                else:
                                    raise TranslationException("Stringa non chiusa correttamente", node)
                            else:
                                raise TranslationException(f"Variabile non dichiarata: \"{case_value}\"", node)
                    if is_valid:
                        code += f"{"    " * indentation_level}case {case_value}:\n"
                        indentation_level += 1
                except:
                    pass

            case "endmatch":
                if last_node.type == "match":
                    raise TranslationException("Nodo di tipo \"match\" senza contenuto", last_node)
                indentation_level -= 1

            case "forlist":
                try:
                    item_name = ""
                    list_name = ""
                    
                    for item in node.translate_items:
                        if item.type == "objectname":
                            item_name = item.get()
                        elif item.type == "list":
                            list_name = item.get()
                            if list_name in declared_lists:
                                code += f"{"    " * indentation_level}for {item_name} in {list_name}:\n"
                                indentation_level += 1
                            else:
                                raise TranslationException(f"Lista non dichiarata: \"{list_name}\"", node)
                except:
                    pass

            case "forrange":
                try:
                    item_name = ""
                    start = 0
                    end = 0
                    
                    for item in node.translate_items:
                        if item.type == "objectname":
                            item_name = item.get()
                        elif item.type == "rangestart":
                            start = item.get()
                            try:
                                int(start)
                            except:
                                raise TranslationException("Valore di inizio non valido", node)
                        elif item.type == "rangeend":
                            end = item.get()
                            try:
                                int(end)
                            except:
                                raise TranslationException("Valore di fine non valido", node)
                    code += f"{"    " * indentation_level}for {item_name} in range({start}, {end}):\n"
                    indentation_level += 1
                except:
                    pass

            case "endforlist":
                if last_node.type == "forlist":
                    raise TranslationException("Nodo di tipo \"forlist\" senza contenuto", last_node)
                indentation_level -= 1

            case "endforrange":
                if last_node.type == "forrange":
                    raise TranslationException("Nodo di tipo \"forrange\" senza contenuto", last_node)
                indentation_level -= 1

        last_node = node

    print(f"\n\n------TRANSLATED CODE------\n{code}")
    return code