from mapper.majority.utils.MaxHeapObj import MaxHeapObj

class KeyValMaxHeapObj(MaxHeapObj):
    """
    A class that extends MaxHeapObj to include a key-value pair.
    
    Attributes:
    key (any): The key associated with the object.
    val (any): The value associated with the object, inherited from MaxHeapObj.
    
    Methods:
    __init__(key, val): Initializes the object with a key and a value.
    """
    
    def __init__(self, key, val):
        """
        Initializes the KeyValMaxHeapObj with the given key and value.
        
        Args:
        key (any): The key to associate with the object.
        val (any): The value to associate with the object, passed to the parent class.
        """
        super().__init__(val)  # Initialize the parent class (MaxHeapObj) with the value
        self.key = key  # Store the key associated with the object
