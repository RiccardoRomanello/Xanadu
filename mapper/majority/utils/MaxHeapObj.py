class MaxHeapObj:
    """
    A wrapper class to turn Python's built-in min-heap (used by `heapq`) into a max-heap.

    This is done by reversing the comparison logic so that larger values are treated as 'smaller'
    when inserted into the heap, effectively inverting the heap behavior.

    Attributes:
        val: The value stored in the heap element.
    """

    def __init__(self, val):
        """
        Initializes the MaxHeapObj with a value.

        Args:
            val: The value to store (any comparable type).
        """
        self.val = val

    def __lt__(self, other): 
        """
        Overrides less-than comparison to invert priority.

        Args:
            other (MaxHeapObj): Another heap object to compare with.

        Returns:
            bool: True if self has higher priority (greater value).
        """
        return self.val > other.val

    def __eq__(self, other): 
        """
        Checks equality based on the underlying value.

        Args:
            other (MaxHeapObj): Another heap object.

        Returns:
            bool: True if values are equal.
        """
        return self.val == other.val

    def __str__(self): 
        """
        Returns a string representation of the stored value.

        Returns:
            str: String form of the value.
        """
        return str(self.val)
