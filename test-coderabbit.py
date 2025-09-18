"""
Test file to validate Code Rabbit integration.
This file will be used to trigger a Code Rabbit review and then deleted.
"""

def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number using recursion."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    """Main function to demonstrate the fibonacci calculation."""
    result = calculate_fibonacci(10)
    print(f"The 10th Fibonacci number is: {result}")

if __name__ == "__main__":
    main()
