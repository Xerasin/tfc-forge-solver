import numpy as np 
import itertools
from tabulate import tabulate
from collections import deque
from libs.xoro import solve_tool_target

WORLD_SEED = -8490670550227183441

enders = {
    "axe"    : [['U', 'H', 'P']],
    "lamp"   : [['D', 'B', 'B']],
    "chain"  : [['H', 'H', 'D']],
    "shovel" : [['H', 'P']     ],
    "pickaxe": [['D', 'B', 'P'], ['B', 'D', 'P']],
    "javelin": [['D', 'H', 'H']],
    "knife"  : [['D', 'D', 'H']],
    "hoe"    : [['B', 'H', 'P']],
    "chisel" : [['D', 'H', 'H']],
    "saw"    : [['H', 'H']     ],
    "hammer" : [['S', 'P']     ],
    "rod"    : [['D', 'D', 'B']],
    "sheet"  : [['H', 'H', 'H']],
    "tongs"  : [['B', 'D', 'H']],
    "tuyere"   : [['B', 'B']],
}

metals = {
    "copper": "Copper",
    "bronze": "Bronze",
    "brass": "Brass",
    "cast_iron": "Cast Iron",
    "wrought_iron": "Wrought Iron",
    "bismuth_bronze": "Bismuth Bronze",
    "steel": "Steel",
    "black_steel": "Black Steel",
    "blue_steel": "Blue Steel",
    "red_steel": "Red Steel",
}

tool_metals = {
    "copper",
    "bronze",
    "wrought_iron",
    "bismuth_bronze",
    "steel",
    "black_steel",
    "blue_steel",
    "red_steel"
}

tools = {
    "axe"     : ( "tfc:anvil/{}_axe_head", enders["axe"    ]),
    "shovel"  : ( "tfc:anvil/{}_shovel_head", enders["shovel" ]),
    "pickaxe" : ( "tfc:anvil/{}_pickaxe_head", enders["pickaxe"]),
    "javelin" : ( "tfc:anvil/{}_javelin_head", enders["javelin"]),
    "knife"   : ( "tfc:anvil/{}_knife_blade", enders["knife"  ]),
    "hoe"     : ( "tfc:anvil/{}_hoe_head", enders["hoe"    ]),
    "chisel"  : ( "tfc:anvil/{}_chisel_head", enders["chisel" ]),
    "saw"     : ( "tfc:anvil/{}_saw_blade", enders["saw"    ]),
    "hammer"  : ( "tfc:anvil/{}_hammer_head", enders["hammer" ]),
    "lamp"    : ( "tfc:anvil/{}_lamp", enders["lamp"   ]),
    "chain"   : ( "tfc:anvil/{}_chain", enders["chain"  ]),
    "tuyere"   : ( "tfc:anvil/{}_tuyere", enders["tuyere"  ]),
    "tongs"   : ( "tfchotornot:anvil/tong_part/{}", enders["tongs"  ]),
}

others = {
    "rod"     : ( "tfc:anvil/{}_rod", enders["rod"    ]),
    "sheet"   : ( "tfc:anvil/{}_sheet", enders["sheet"    ]),
}

special = {
    "copper": {
        "fluid_pipe"    : ( "create:crafting/kinetics/fluid_pipe", [['B', 'H', 'P'], ['H', 'B', 'P']]),

    },
    "brass": {
        "mechanisms"    : ( "tfc:anvil/brass_mechanisms", [['P', 'H', 'P']]),
        "blowpipe"    : ( "tfc:anvil/blowpipe", [['H', 'D', 'D']]),
        "hand"          : ( "create:crafting/kinetics/brass_hand", [['S', 'B', 'B']]),
    },
    "wrought_iron": {
        "refined_bloom" : ( "tfc:anvil/refined_iron_bloom", 
                            [['H', 'H', 'H']]),
        "ingot"         : ( "tfc:anvil/wrought_iron_from_bloom", 
                            [['H', 'H', 'H']]),
        "propeller"     : ( "create:crafting/kinetics/propeller", 
                            [['D', 'D', 'B']]),
        "sawblade"      : ( "immersiveengineering:crafting/sawblade", 
                            [['D', 'D', 'B']]),
        #"Press"        : ( 82, 
        #                   [['S', 'B', 'B']]),
        "whisk"         : ( "create:crafting/kinetics/whisk", 
                            [['D', 'D', 'B']]),
        "flask"         : ( "waterflasks:anvil/unfinished_iron_flask", 
                            [['B', 'B', 'P']]),
    },
    "steel": {
        "high_carbon_ingot": ("tfc:anvil/high_carbon_steel_ingot", 
                            [['H', 'H', 'H']]),
        "ingot": ("tfc:anvil/steel_ingot", 
                            [['H', 'H', 'H']]),
    },
    "black_steel": {
        "ingot": ("tfc:anvil/steel_ingot", 
                            [['H', 'H', 'H']]),
    },
    "blue_steel": {
        "ingot": ("tfc:anvil/steel_ingot", 
                            [['H', 'H', 'H']]),
    },
    "red_steel": {
        "ingot": ("tfc:anvil/steel_ingot", 
                            [['H', 'H', 'H']]),
    }
}   

def solve_target(tool_pattern, metalstr=None):
    if metalstr is not None:
        return (solve_tool_target(WORLD_SEED, (tool_pattern[0].format(metalstr))), tool_pattern[1])
    elif type(tool_pattern[0]) == int:
        return tool_pattern
    else:
        return (solve_tool_target(WORLD_SEED, tool_pattern[0]), tool_pattern[1])


solving  = {
    metalstr: {
        tool: solve_target(tool_pattern, metalstr) for tool, tool_pattern in others.items()
    } for metalstr in metals
}

for metal in tool_metals:
    for tool, val in tools.items():
        if not metal in solving.keys():
            solving[metal] = {}
        solving[metal][tool] = solve_target(val, metal)

for metal, tools in special.items():
    for tool, val in tools.items():
        if not metal in solving.keys():
            solving[metal] = {}
        solving[metal][tool] = solve_target(val, metal)

operations = {
    'P':  + 2,
    'B':  + 7,
    'U':  +13,
    'S':  +16,
    'LH': - 3,
    'MH': - 6,
    'HH': - 9,
    'D':  -15,
}

operations_names = {
    'P' : "Punch",
    'B' : "Bend",
    'U' : "Upset",
    'S' : "Shrink",
    'LH': "Light Hit",
    'MH': "Medium Hit",
    'HH': "Hard Hit",
    'D' : "Draw"
}

operations_values = {
    'P':  "+2",
    'B':  "+7",
    'U':  "+13",
    'S':  "+16",
    'LH': "-3",
    'MH': "-6",
    'HH': "-9",
    'D':  "-15",
}

h_endings = ['LH', 'MH', 'HH']

sorted_operations = sorted(operations.items(), key=lambda x: x[1], reverse=True)
operations_rev = {value: key for key, value in operations.items()}
solving = dict(sorted(solving.items(), key=lambda item: (item[0])))

#Solvers
def bfs_shortest_path(target, start=0):
    queue = deque([(start, [])])
    visited = set()  

    while queue:
        current_value, sequence = queue.popleft()

        if current_value == target:
            return sequence
        
        for operation, effect in sorted_operations:
            next_value = current_value + effect

            if next_value not in visited:
                visited.add(next_value)
                queue.append((next_value, sequence + [operation]))

    return None

def find_minimum_sequence(final_value, end_sequences):
    sequence = []

    def get_end_costs(end_sequences):
        costs = []
        patterns = []
        for sequence in end_sequences:
            cost = []
            for k in sequence:
                if k == 'H':
                    cost.append([operations[e] for e in h_endings])
                else:
                    cost.append([operations[k]])

            formatted_combinations = [[combination[i] for combination in list(itertools.product(*cost))] for i in range(len(cost))]
            costs.append(np.sum(np.array(formatted_combinations), axis=0).tolist())
            patterns.append(formatted_combinations)

        return costs, patterns
    
    end_costs, pattern = get_end_costs(end_sequences)
    paths = []
    for seq in end_costs:
        path = []
        for end_cost in seq:
            new_final_value = final_value - end_cost
            possible_path = bfs_shortest_path(new_final_value)
            path.append(possible_path)

        paths.append(path)
    
    shortest_path, index = find_shortest_array(paths)
    
    if shortest_path:
        end_sequence = end_sequences[index[0]]
        sequence.extend(shortest_path)
        for k in range(len(end_sequence)):
            chosen_pattern = pattern[index[0]][k][index[1]]
            sequence.append(operations_rev[chosen_pattern])
    
    if sum(operations[v] for v in sequence) != final_value:
        raise ArithmeticError("Generated bad solve!")
    
    return sequence

def find_shortest_array(arrays):
    min_array = None
    min_length = float('inf')
    min_position = (None, None)

    for i, subarrays in enumerate(arrays):
        for j, array in enumerate(subarrays):
            if array is not None and len(array) < min_length:
                min_length = len(array)
                min_array = array
                min_position = (i, j)

    return min_array, min_position

#Translators
def do_nothing(operator):
    return operator

def full_name(operator):
    return operations_names[operator]

def by_value(operator):
    return operations_values[operator]
    
def sequence_string(sequence, translator=do_nothing):
    if not sequence:
        return 'No valid sequence'
    
    compressed = []
    count = 1
    previous = translator(sequence[0])

    for operation in sequence[1:]:
        translated_operator = translator(operation)

        if translated_operator  == previous:
            count += 1
        else:
            if count == 1:
                compressed.append(f"{previous}")
            else:
                compressed.append(f"{count} x {previous}")
            count = 1
            previous = translated_operator

    if count == 1:
        compressed.append(f"{previous}")  # append the last operation if count is 1
    else:
        compressed.append(f"{count} x {previous}")  # append the last set if count > 1
        
    return compressed


#Printing Crap
def compress_sequence(sequence):
    compressed = []
    count = 1
    previous = sequence[0]

    for operation in sequence[1:]:
        translated_operator = operation

        if translated_operator  == previous:
            count += 1
        else:
            if count == 1:
                compressed.append((previous, 1))
            else:
                compressed.append((previous, count))
            count = 1
            previous = translated_operator

    if count == 1:
        compressed.append((previous, 1))
    else:
        compressed.append((previous, count))

    return compressed

def getAllToolsSolved():
    solved = {
        metal: {
            k: find_minimum_sequence(final_value, end_sequence) for k, (final_value, end_sequence) in value.items()
        } for metal, value in solving.items()
    }
    return solved

def main():
    solved = getAllToolsSolved()

    types = sorted(list(set(metals.items())))
    while True:
        print("\nMenu")
        for i, type in enumerate(types):
            print(f"{i+1}. {type[1]}")
            
        try:
            select = int(input("Metal Option: "))
            if select is None or select < 1 or select > len(types):
                continue
        except:
            continue

        selectedType = types[select - 1][0]
        tabulated_data = tabulate(
            sorted(
                [[pattern, ', '.join(sequence_string(solution, lambda op: operations_names[op]))] for pattern, solution in solved[selectedType].items()],
                key=lambda x: x[0]
            ),
            headers=["Tool", "Sequence"], 
            tablefmt="grid")

        table_length = len(tabulated_data.split('\n')[1])
        print(f"{selectedType:^{table_length}}") 

        print(tabulated_data)

if __name__ == "__main__":
    main()