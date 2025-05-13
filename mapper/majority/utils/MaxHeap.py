import heapq

class MaxHeap:
    """
    A max-heap implementation using Python's `heapq` module.

    This class assumes the elements pushed into the heap override the
    comparison operators (like `__lt__`) to reverse the order, such as
    using a wrapper like `MaxHeapObj`.

    Attributes:
        h (list): Internal list representing the heap.
    """

    def __init__(self): 
        """
        Initializes an empty max-heap.
        """
        self.h = []

    def heappush(self, obj): 
        """
        Pushes an object onto the heap.

        Args:
            obj: An object implementing reversed comparison (e.g., MaxHeapObj).
        """
        heapq.heappush(self.h, obj)

    def heappop(self): 
        """
        Pops and returns the maximum-priority element from the heap.

        Returns:
            The element with the highest priority.
        """
        return heapq.heappop(self.h)
    
    def __getitem__(self, i): 
        """
        Allows indexing into the heap.

        Args:
            i (int): The index to retrieve.

        Returns:
            The element at index i in the internal heap list.
        """
        return self.h[i]
    
    def __len__(self): 
        """
        Returns the number of elements currently in the heap.

        Returns:
            int: Heap size.
        """
        return len(self.h)
