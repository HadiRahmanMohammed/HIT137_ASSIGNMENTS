import turtle
import random

def draw_branch(t, branch_length, left_angle, right_angle, depth, reduction_factor):
    """
    Recursively draws branches of a tree.

    Parameters:
        t (turtle.Turtle): The turtle object used for drawing.
        branch_length (float): Length of the current branch.
        left_angle (float): Angle to turn left for left branches.
        right_angle (float): Angle to turn right for right branches.
        depth (int): Current depth of recursion.
        reduction_factor (float): Factor by which branch length is reduced at each level.
    """
    if depth == 0:
        return

    # Set a random color for the branch
    t.color(random.choice(["red", "green", "blue", "orange", "purple", "yellow", "pink"]))

    # Draw the current branch
    t.forward(branch_length)

    # Draw the left subtree
    t.left(left_angle)
    draw_branch(t, branch_length * reduction_factor, left_angle, right_angle, depth - 1, reduction_factor)

    # Return to the original position
    t.right(left_angle + right_angle)
    draw_branch(t, branch_length * reduction_factor, left_angle, right_angle, depth - 1, reduction_factor)

    # Return to the original orientation
    t.left(right_angle)
    t.backward(branch_length)

def main():
    try:
        # Take user inputs with validation
        left_angle = float(input("Enter the left branch angle (in degrees): "))
        right_angle = float(input("Enter the right branch angle (in degrees): "))
        branch_length = float(input("Enter the starting branch length (in pixels): "))
        
        if branch_length <= 0:
            raise ValueError("Branch length must be greater than 0.")

        depth = int(input("Enter the recursion depth: "))
        
        if depth < 0:
            raise ValueError("Recursion depth cannot be negative.")

        reduction_factor = float(input("Enter the branch length reduction factor (e.g., 0.7): "))
        
        if not (0 < reduction_factor < 1):
            raise ValueError("Reduction factor must be between 0 and 1 (exclusive).")

    except ValueError as e:
        print(f"Input error: {e}")
        return

    # Set up the turtle
    screen = turtle.Screen()
    screen.setup(width=800, height=600)
    screen.title("Recursive Colorful Tree Pattern")

    t = turtle.Turtle()
    t.speed(0)  # Set the turtle speed to the fastest
    t.left(90)  # Point the turtle upwards
    t.penup()
    t.goto(0, -250)  # Start near the bottom of the screen
    t.pendown()

    # Draw the tree
    try:
        draw_branch(t, branch_length, left_angle, right_angle, depth, reduction_factor)
    except Exception as e:
        print(f"An error occurred while drawing: {e}")

    # Keep the window open
    screen.mainloop()

if __name__ == "__main__":
    main()
