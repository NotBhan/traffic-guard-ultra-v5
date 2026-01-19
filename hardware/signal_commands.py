# hardware/signal_commands.py

"""
Defines and validates traffic signal commands
sent from Python to Arduino.
"""

# -------------------------------
# VALID COMMANDS
# -------------------------------
VALID_DIRECTIONS = {"north", "south", "east", "west"}
VALID_COLORS = {"red", "yellow", "green"}


# -------------------------------
# VALIDATE INPUT
# -------------------------------
def validate_signal(direction, color):
    if direction not in VALID_DIRECTIONS:
        raise ValueError(f"Invalid direction: {direction}")

    if color not in VALID_COLORS:
        raise ValueError(f"Invalid color: {color}")


# -------------------------------
# BUILD COMMAND
# -------------------------------
def build_command(direction, color):
    """
    Returns standardized command string
    Example: NORTH_GREEN
    """
    validate_signal(direction, color)
    return f"{direction.upper()}_{color.upper()}"
