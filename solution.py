assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'

# This is bunch of preprocessed data to speed up sudoku processing and reduce memory footprint by reusing this data.
# All these elements will be used in one or another method of this code.
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[''.join(x) for x in zip(rows, cols)], [''.join(x) for x in zip(rows, cols[::-1])]]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def eliminate_value_from_string(input_string, eliminate_value):
    """Eliminate single number from string and return processed string. 
    This is just helper to make call to string replace a bit more readable.
    Args:
        input_string(string): String from which nu ber will be eliminated.
        eliminate_value(string): Single number to eliminate from string.
    
    Returns:
        string 'input_string' without number from 'eliminate_value'.
    """
    return input_string.replace(eliminate_value, '')

def naked_twins_eliminate(values, unit, naked_twin_index_1, naked_twin_index_2):
    """Eliminate naked twins from all unit values, except naked twin values.
    Args:
        values(dict): All values
        naked_twin_index_1(string): Index of first naked twin in values.
        naked_twin_index_12(string): Index of second naked twin in values.
    """
    # Iterate over all items in unit.
    for unit_item in unit:
        # Skip unit item if it is naked twin. We should not eliminate values in them.
        if unit_item == naked_twin_index_1 or unit_item == naked_twin_index_2:
            continue
            
        # Iterate over all numbers in first naked twin value.
        for number in values[naked_twin_index_1]:
            # Eliminate naked twin numbers in the current unit item and write result back to the values dict.
            assign_value(values, unit_item, eliminate_value_from_string(values[unit_item], number))

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """        
    # Iterate over all units lists.
    for unit in unitlist:
        # First loop over all items in units list.
        for unit_item_1 in unit:
            # Get value of unit item.
            unit_item_1_val = values[unit_item_1]
            
            # If unit item value length is not 2 then this item could not be naked twin.
            if len(unit_item_1_val) != 2:
                continue

            # Second loop over all items in units list.                
            for unit_item_2 in unit:
                # Get value of unit item.                
                unit_item_2_val = values[unit_item_2]
                
                # If unit item value length is not 2 then this item could not be naked twin.                            
                if len(unit_item_2_val) != 2:
                    continue      
                
                # If first unit item and second unit item points to the same cell then skip this value.    
                if unit_item_1 == unit_item_2:
                    continue
                    
                # If first unit item is not equal to the second unit item value then these items could not be naked twins.    
                if unit_item_1_val != unit_item_2_val:
                    continue
                    
                # Eliminate numbers from naked twins in another unit items.
                naked_twins_eliminate(values, unit, unit_item_1, unit_item_2)

    return values
    
def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    # Prepare data for the dictionary values.
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    # Zip value indices with actual cell values.
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        The resulting sudoku in dictionary form.
    """    
    # First of all lets find already solved values. They always have length 1.
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        # Get solved value.
        digit = values[box]
        # Iterate over all peers of solved value.
        for peer in peers[box]:
            # Replace peer number that is equal to solved value with nothing (erasing it).
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Args: 
        values(dict): The sudoku in dictionary form
    Returns:
        The resulting sudoku in dictionary form.
    """
    # Iterate over all units.
    for unit in unitlist:
        # Iterate over all digits.
        for digit in '123456789':
            # Find places that may accept digit.
            dplaces = [box for box in unit if digit in values[box]]
            # Use places list with only one item.
            if len(dplaces) == 1:
                # Replace this place with digit because this digit may not be in any other places.
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Args:
        values(dict): The sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        # Get amount of solved values to check for stall later.
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Apply eliminate strategy.
        values = eliminate(values)
        # Apply only choice strategy.
        values = only_choice(values)
        # Apply naked twins strategy.
        values = naked_twins(values) 
        # Get amount of solved values to check for stall.
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # Check for stall. If we have not solve any other new values then we are stalled.
        stalled = solved_values_before == solved_values_after
        # This is bad if we have not any number in values cell.
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    values = reduce_puzzle(values)
    if values is False:
        return False
    # Check if we solve all values.
    if all(len(values[s]) == 1 for s in boxes): 
        return values
    # Select cell with minimum value length        
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Iterate on number of this cell, substitute number as cell value and try to make iterative search.
    for value in values[s]:
        new_sudoku = values.copy()
        assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))
    
if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
