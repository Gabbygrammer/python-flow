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

def flow_to_code(node_connections: list, nodes: list, language: str, add_final_block: bool, skip_print: bool = False):
    if initialize(node_connections):
        sort_connections(node_connections, nodes)
        if not skip_print:
            print_result()
        try:
            code = translate_to_code(language, add_final_block, skip_print)
            return code
        except TranslationException as e:
            raise e

def sort_connections(node_connections: list, nodes: list):
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

def get_value_type(value: str):
    if value.startswith("\"") and value.endswith("\""):
        return "String"
    elif value.startswith("'") and value.endswith("'"):
        return "String"
    
    try:
        int(value)
        return "int"
    except ValueError:
        try:
            float(value)
            return "double"
        except:
            return None

def get_list_type(list: str | list, is_list: bool = False):
    global list_contents, variable_types
    list_types = []
    return_type = ""
    if not is_list:
        for value in list_contents[list]:
            if not get_value_type(value) in list_types:
                list_types.append(get_value_type(value))
    else:
        for value in list:
            if not get_value_type(value) in list_types:
                list_types.append(get_value_type(value))
    if len(list_types) > 1:
        return_type = "ArrayList<Object>"
    else:
        return_type = "ArrayList<" + list_types[0] + ">"
    if not is_list:
        variable_types[list] = return_type
    return return_type

syntax = {
    "python": {
        "print": "print($0)",
        "variabledecl": "$0 = $1",
        "variableset": "$0 = $1",
        "if": "if $0 $1 $2:",
        "ifnotin": "if not $0 in $1:",
        "ifnotis": "if not $0 is $1:",
        "else": "else:",
        "def": "def $0($1):",
        "defcall": "$0($1)",
        "defcallvar": "$0 = $1($2)",
        "return": "return $0",
        "listdecl": "$0 = []",
        "listsetappend": "$0.append($1)",
        "listsetappendmultiple": "for item in [$0]:\n$1.append(item)",
        "listsetremove": "$0.remove($1)",
        "listsetremovemultiple": "for item in [$0]:\n$1.remove(item)",
        "match": "match $0:",
        "case": "case $0:",
        "forlist": "for $0 in $1:",
        "forrange": "for $0 in range($1, $2):",
        "while": "while $0 $1 $2:",
        "import": "import $0"
    },

    "java": {
        "print": "System.out.println($0);",
        "variabledecl": "type $0 = $1;",
        "variableset": "$0 = $1;",
        "if": "if ($0 $1 $2) {",
        "ifin": "if ($1.contains($0)) {",
        "ifnotin": "if (!$1.contains($0)) {",
        "ifis": "if ($0 instanceof $1) {",
        "ifnotis": "if (!($0 instanceof $1)) {",
        "else": "} else {",
        "def": "public static type $0($1) {",
        "defcall": "$0($1);",
        "defcallvar": "type $0 = $1($2);",
        "return": "return $0;",
        "listdecl": "ArrayList<type> $0 = new ArrayList<type>();",
        "listsetappend": "$0.add($1);",
        "listsetappendmultiple": "for (Object item : List.of($0)) {\n$1.add(item);\n}",
        "listsetremove": "$0.remove($1);",
        "listsetremovemultiple": "for (Object item : List.of($0)) {\n$1.remove(item);\n}",
        "match": "switch ($0) {",
        "case": "case $0:",
        "forlist": "for (type $0 : $1) {",
        "forrange": "for (int $0 = $1; i < $2; i++) {",
        "while": "while ($0 $1 $2) {",
        "import": "import $0"
    }
}

declared_vars = []
defined_funcs = []
declared_lists = []
list_contents = {}
variable_types = {}
def translate_to_code(language, add_final_block: bool, skip_print: bool):
    global last_node, declared_vars, defined_funcs, declared_lists
    code = ""
    indentation_level = 0
    is_first_case_of_last_match = False
    last_node = None
    lang_syntax = syntax[language]
    encountered_defs = []
    function_return_type = {}
    function_codes = {}

    if language == "java":
        code += f"{'import java.util.Scanner;' if add_final_block else ''}\n\npublic class Main {{\n    public static void main(String[] args) {{\n"
        indentation_level = 2

    for node in ordered_node_connections:
        line_to_add = ""
        match node.type:
            case "print":
                try:
                    value = node.translate_items[0].get()
                    if validate_string(value):
                        if not "\"" and not "'" in value:
                            if not value in declared_vars:
                                raise TranslationException(f"Variabile \"{value}\" non dichiarata", node)
                        line_to_add = f"{"    "*indentation_level}{lang_syntax["print"].replace("$0", value)}\n"
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
                line_to_add = f"{"    " * indentation_level}{lang_syntax["variabledecl"].replace("$0", variable_name).replace("$1", variable_value).replace("type", get_value_type(variable_value))}\n"
                variable_types[variable_name] = get_value_type(variable_value)
            
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
                line_to_add = f"{"    " * indentation_level}{lang_syntax["variableset"].replace("$0", variable_name).replace("$1", variable_value)}\n"
                operation_symbols = {"python": ["+", "-", "*", "/"], "java": ["+", "-", "*", "/"]}
                def check_for_operations():
                    for symbol in operation_symbols[language]:
                        if symbol in variable_value:
                            return True
                    return False
                if not check_for_operations():
                    variable_types[variable_name] = get_value_type(variable_value)

            case "if":
                try:
                    if condition_dict[node.if_condition_operator.get()] == "is" and language == "java":
                        line = f"{"    " * indentation_level}{lang_syntax["ifis"].replace("$0", node.translate_items[0].get()).replace("$1", node.translate_items[1].get())}\n"
                        if validate_string(line):
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    elif condition_dict[node.if_condition_operator.get()] == "in" and language == "java":
                        line = f"{"    " * indentation_level}{lang_syntax["ifin"].replace("$0", node.translate_items[0].get()).replace("$1", node.translate_items[1].get())}\n"
                        if validate_string(line):
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    elif condition_dict[node.if_condition_operator.get()] == "not is":
                        line = f"{"    " * indentation_level}{lang_syntax["ifnotis"].replace("$0", node.translate_items[0].get()).replace("$1", node.translate_items[1].get())}\n"
                        if validate_string(line):
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    elif condition_dict[node.if_condition_operator.get()] == "not in":
                        line = f"{"    " * indentation_level}{lang_syntax["ifnotin"].replace("$0", node.translate_items[0].get()).replace("$1", node.translate_items[1].get())}\n"
                        if validate_string(line):
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    else:
                        line = f"{"    " * indentation_level}{lang_syntax["if"].replace("$0", node.translate_items[0].get()).replace("$1", condition_dict[node.if_condition_operator.get()]).replace("$2", node.translate_items[1].get())}\n"
                        if validate_string(line):
                            if not "\"" and not "'" in node.translate_items[0].get():
                                if not node.translate_items[0].get() in declared_vars:
                                    raise TranslationException(f"Variabile \"{node.translate_items[0].get()}\" non dichiarata", node)
                            if not "\"" and not "'" in node.translate_items[1].get():
                                if not node.translate_items[1].get() in declared_vars:
                                    raise TranslationException(f"Variabile \"{node.translate_items[1].get()}\" non dichiarata", node)
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    indentation_level += 1
                except AttributeError:
                    pass

            case "else":
                try:
                    indentation_level -= 1
                    line_to_add = f"{"    " * indentation_level}{lang_syntax["else"]}\n"
                    indentation_level += 1
                except AttributeError:
                    pass

            case "endif":
                if last_node.type == "if":
                    raise TranslationException("Nodo di tipo \"se\" senza contenuto", last_node)
                indentation_level -= 1
                if language == "java":
                    line_to_add = f"{"    "*indentation_level}}}"

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
                line_to_add = f"{"    " * indentation_level}{lang_syntax["def"].replace("$0", function_name).replace("$1", function_args).replace("type", "<FUNCTION_RETURN_TYPE>")}\n"
                indentation_level += 1
                encountered_defs.append(function_name)
                function_codes[function_name] = ""

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
                line_to_add = f"{"    " * indentation_level}{lang_syntax["defcall"].replace("$0", function_name).replace("$1", function_args)}\n"

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
                line_to_add = f"{"    " * indentation_level}{lang_syntax["defcallvar"].replace("$0", variable_name).replace("$1", function_name).replace("$2", function_args).replace("type", function_return_type[function_name])}\n"

            case "enddef":
                if last_node.type == "def":
                    raise TranslationException("Nodo di tipo \"def\" senza contenuto", last_node)
                indentation_level -= 1
                if language == "java":
                    line_to_add = f"{"    "*indentation_level}}}\n"
                    function_codes[function_name] = function_codes[function_name] + line_to_add
                if len(encountered_defs) > 0:
                    code = code.replace(f"public static <FUNCTION_RETURN_TYPE> {encountered_defs[-1]}", f"public static void {encountered_defs[-1]}")
                    function_codes[encountered_defs[-1]] = function_codes[encountered_defs[-1]].replace(f"public static <FUNCTION_RETURN_TYPE> {encountered_defs[-1]}", f"public static void {encountered_defs[-1]}")
                    function_return_type[encountered_defs[-1]] = "void"
                    encountered_defs.pop(-1)

            case "return":
                line = f"{"    " * indentation_level}{lang_syntax["return"].replace("$0", node.translate_items[0].get())}\n"
                if not "\"" in line and not "'" in line:
                    if not node.translate_items[0].get() in declared_vars and not node.translate_items[0].get() in declared_lists:
                        try:
                            float(node.translate_items[0].get())
                        except:
                            raise TranslationException(f"Variabile \"{node.translate_items[0].get()}\" non dichiarata", node)
                if validate_string(line):
                    line_to_add = line
                    if language == "java":
                        line_to_add += f"{"    "*(indentation_level - 1)}}}\n"
                    function_codes[function_name] = function_codes[function_name] + line_to_add
                else:
                    raise TranslationException("Stringa non chiusa correttamente", node)
                indentation_level -= 1
                if len(encountered_defs) > 0:
                    return_type = ""
                    try:
                        return_type = variable_types[node.translate_items[0].get()]
                    except:
                        return_type = get_value_type(node.translate_items[0].get())
                    if "ArrayList" in return_type:
                        return_type = get_list_type(node.translate_items[0].get())
                    code = code.replace(f"public static <FUNCTION_RETURN_TYPE> {encountered_defs[-1]}", f"public static {return_type} {encountered_defs[-1]}")
                    function_codes[encountered_defs[-1]] = function_codes[encountered_defs[-1]].replace(f"public static <FUNCTION_RETURN_TYPE> {encountered_defs[-1]}", f"public static {return_type} {encountered_defs[-1]}")
                    function_return_type[encountered_defs[-1]] = return_type
                    encountered_defs.pop(-1)

            case "listdecl":
                if language == "java" and not "import java.util.ArrayList;" in code:
                    code = "import java.util.ArrayList;\n" + code
                if validate_name(node.translate_items[0].get()):
                    line_to_add = f"{"    " * indentation_level}{lang_syntax["listdecl"].replace("$0", node.translate_items[0].get()).replace("type", "Object")}\n"
                    declared_lists.append(node.translate_items[0].get())
                    variable_types[node.translate_items[0].get()] = "ArrayList<Object>"
                    list_contents[node.translate_items[0].get()] = []
                else:
                    raise TranslationException(f"Nome lista \"{node.translate_items[0].get()}\" non valido. Il nome deve contenere solo caratteri alfanumerici e/o trattini bassi", node)

            case "listset":
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
                    if language == "java" and not "import java.util.List;" in code:
                        code = "import java.util.List;\n" + code
                    temp_list_type = get_list_type(items, is_list=True).removeprefix("ArrayList<").removesuffix(">")
                    if action == "append":
                        lines = lang_syntax["listsetappendmultiple"].split("\n")
                        line_to_add = f"{"    " * indentation_level}{lines[0].replace("$0", ''.join(f"{item}, " for item in items).removesuffix(", ")).replace("Object", temp_list_type)}\n{"    " * (indentation_level + 1)}{lines[1].replace("$1", list_name)}\n{f"{'    ' * indentation_level}{lines[2]}\n" if language == "java" else ''}"
                        for item in items:
                            list_contents[list_name].append(item)
                    else:
                        lines = lang_syntax["listsetremovemultiple"].split("\n")
                        line_to_add = f"{"    " * indentation_level}{lines[0].replace("$0", ''.join(f"{item}, " for item in items).removesuffix(", ")).replace("Object", temp_list_type)}\n{"    " * (indentation_level + 1)}{lines[1].replace("$1", list_name)}\n{f"{'    ' * indentation_level}{lines[2]}\n" if language == "java" else ''}"
                        mod_line = ""
                        for line in line_to_add.split("\n"):
                            line = line.strip()
                            line = "    " * indentation_level + line
                            if "remove" in line:
                                line = "    " + line
                            mod_line += line + "\n"
                        line_to_add = mod_line
                        for item in items:
                            list_contents[list_name].remove(item)
                else:
                    if action == "append":
                        lines = lang_syntax["listsetappend"].split("\n")
                        line_to_add = f"{"    " * indentation_level}{lines[0].replace("$0", list_name)}\n{"    " * (indentation_level + 1)}{lines[1].replace("$1", item_name)}\n{f"{'    ' * indentation_level}{lines[2]}\n" if language == "java" else ''}"
                        list_contents[list_name].append(item_name)
                    else:
                        lines = lang_syntax["listsetremove"].split("\n")
                        line_to_add = f"{"    " * indentation_level}{lines[0].replace("$0", list_name)}\n{"    " * (indentation_level + 1)}{lines[1].replace("$1", item_name)}\n{f"{'    ' * indentation_level}{lines[2]}\n" if language == "java" else ''}"
                        list_contents[list_name].remove(item_name)

            case "match":
                try:
                    variable_name = node.translate_items[0].get()
                    if variable_name in declared_vars:
                        line_to_add = f"{"    " * indentation_level}{lang_syntax["match"].replace("$0", variable_name)}\n"
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
                        line_to_add = f"{"    " * indentation_level}{lang_syntax["case"].replace("$0", case_value)}\n"
                        indentation_level += 1
                except:
                    pass

            case "endmatch":
                if last_node.type == "match":
                    raise TranslationException("Nodo di tipo \"match\" senza contenuto", last_node)
                indentation_level -= 1
                if language == "java":
                    line_to_add = f"{"    " * indentation_level}}}\n"

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
                                line_to_add = f"{"    " * indentation_level}{lang_syntax["forlist"].replace("$0", item_name).replace("$1", list_name)}\n"
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
                    line_to_add = f"{"    " * indentation_level}{lang_syntax["forrange"].replace("$0", item_name).replace("$1", start).replace("$2", end)}\n"
                    indentation_level += 1
                except:
                    pass

            case "endforlist":
                if last_node.type == "forlist":
                    raise TranslationException("Nodo di tipo \"forlist\" senza contenuto", last_node)
                indentation_level -= 1
                if language == "java":
                    line_to_add = f"{"    " * indentation_level}}}\n"

            case "endforrange":
                if last_node.type == "forrange":
                    raise TranslationException("Nodo di tipo \"forrange\" senza contenuto", last_node)
                indentation_level -= 1
                if language == "java":
                    line_to_add = f"{"    " * indentation_level}}}\n"

            case "while":
                try:
                    first_part = ""
                    second_part = ""
                    for item in node.translate_items:
                        if item.type == "first":
                            first_part = item.get()
                        elif item.type == "second":
                            second_part = item.get()
                    if condition_dict[node.if_condition_operator.get()] == "is" and language == "java":
                        line = f"{"    " * indentation_level}{lang_syntax["ifis"].replace("$0", node.translate_items[0].get()).replace("$1", node.translate_items[1].get()).replace("if", "while")}\n"
                        if validate_string(line):
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    elif condition_dict[node.if_condition_operator.get()] == "in" and language == "java":
                        line = f"{"    " * indentation_level}{lang_syntax["ifin"].replace("$0", node.translate_items[0].get()).replace("$1", node.translate_items[1].get()).replace("if", "while")}\n"
                        if validate_string(line):
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    elif condition_dict[node.if_condition_operator.get()] == "not is":
                        line = f"{"    " * indentation_level}{lang_syntax["ifnotis"].replace("$0", node.translate_items[0].get()).replace("$1", node.translate_items[1].get()).replace("if", "while")}\n"
                        if validate_string(line):
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    elif condition_dict[node.if_condition_operator.get()] == "not in":
                        line = f"{"    " * indentation_level}{lang_syntax["ifnotin"].replace("$0", node.translate_items[0].get()).replace("$1", node.translate_items[1].get()).replace("if", "while")}\n"
                        if validate_string(line):
                            line_to_add = line
                        else:
                            raise TranslationException("Stringa non chiusa correttamente", node)
                    else:
                        line_to_add = f"{"    " * indentation_level}{lang_syntax["while"].replace("$0", first_part).replace("$1", condition_dict[node.if_condition_operator.get()]).replace("$2", second_part)}\n"
                    indentation_level += 1
                except:
                    pass

            case "endwhile":
                if last_node.type == "while":
                    raise TranslationException("Nodo di tipo \"while\" senza contenuto", last_node)
                indentation_level -= 1
                if language == "java":
                    line_to_add = f"{"    " * indentation_level}}}\n"

            case "import":
                line_to_add = f"{"    " * indentation_level}{lang_syntax["import"].replace("$0", node.translate_items[0].get())}\n"

        last_node = node

        code += line_to_add
        for key in function_codes:
            if key in encountered_defs:
                function_codes[key] = function_codes[key] + line_to_add

    if language == "python" and add_final_block:
        code += "\ninput(\"Premi invio per uscire...\")\nquit()"
    elif language == "java":
        if not add_final_block:
            code += "\n    }"
        else:
            space = " "*8
            code += f"\n{space}Scanner scanner = new Scanner(System.in);\n{space}System.out.println(\"Premi invio per uscire...\");\n{space}scanner.nextLine();\n{space}scanner.close();\n{space}System.exit(0);\n    }}\n"
        for key in function_codes:
            code = code.replace(function_codes[key], "")
            code += "\n"
            for line in function_codes[key].split("\n"):
                line = line.removeprefix("        ")
                code += f"\n    {line}"
        for key in variable_types:
            if "ArrayList" in variable_types[key]:
                code = code.replace(f"ArrayList<Object> {key} = new ArrayList<Object>()", f"{variable_types[key]} {key} = new {variable_types[key]}()")
        code += "\n}"

    if not skip_print:
        print(f"\n\n------TRANSLATED CODE------\n{code}")
    return code