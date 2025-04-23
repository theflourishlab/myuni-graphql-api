import re
from typing import Optional, Dict, Tuple

def parse_db_range_string(range_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    if not range_str:
        return None, None
    range_str = str(range_str).lower().replace(',', '').replace('naira', '').strip()
    numbers = [int(s) for s in re.findall(r'\d+', range_str)]

    if "greater than" in range_str or "greater" in range_str:
        return (numbers[0], None ) if numbers else (None, None)
    elif "less than" in range_str or "less" in range_str:
        return (None, numbers[0]) if numbers else (None, None)
    elif '-' in range_str and len(numbers) == 2:
        return tuple(sorted(numbers))
    elif len(numbers) == 1:
        return (numbers[0], numbers[0])
    else: 
        print(f"Warning: could not parse string, '{range_str}'")
        return None, None

def ranges_overlap(student_min: Optional[int], student_max: Optional[int],uni_min: Optional[int], uni_max: Optional[int]) -> bool:
    """
    Checks if two nullable ranges [min, max] overlap. 
    None represents infinity
    """
    if student_max is None:
        return (uni_max is None or (student_min is not None and uni_max >= student_min)) and \
            (student_min is None or uni_min is None or True)

    if student_min is None:
        return (uni_min is None or (student_max is not None and uni_min <= student_max)) and \
            (student_max is None or uni_max is None or True)

    if uni_max is None: 
        return (uni_min is not None and student_max >= uni_min) and \
            (uni_min is None or student_min is None or True)

    if uni_min is None:
        return (uni_max is not None and student_min <=  uni_max ) and \
            (uni_max is None or student_max is None or True)

    # Handle cases where one range is fully None (shouldn't happen with parse_db_range_string)
    # Or other edge cases if parsing fails. Consider default behavior (overlap or not?)

    return False

def calculate_tuition_difference(student_min: Optional[int], student_max: Optional[int],
uni_min: Optional[int], uni_max: Optional[int]
) -> float:
    """Calculates a difference metric for sorting when ranges don't overlap.
    Focuses on how far the university's range is *above* the student's max.
    Returns infinity if student max is None. Lower difference is better.
"""
    if student_max is None: 
        return 0
    
    if uni_min is not None and uni_min > student_max:
        return float(uni_min - student_max)
    
    # If uni range ends below student min (less likely scenario for fallback)
    if uni_max is not None and student_min is not None and uni_max < student_min:
        return float(student_min - uni_max) # How far below

    # If they overlap or uni is within/below student range
    return 0 # Treat overlap or being cheaper as zero difference for this fallback metric