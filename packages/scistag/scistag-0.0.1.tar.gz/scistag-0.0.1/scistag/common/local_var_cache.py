from typing import Callable, Optional, Union, List


class LocalVariableCache:
    """
    A class which temporarily caches values, e.g. a loaded DataFrame or a rendered text
    """

    def __init__(self):
        """
        Initializer
        """
        self.dict_cache = {}

    def cache(self, identifier: str, builder: Callable[[object], object],
              parameters: Optional[object] = None) -> object:
        """
        Tries to retrieve given element from cache. If the element is not stored in the cache it will be created
        using the builder callback which should await a single parameter and return a single value.
        If parameters (optional) is passed it will be verified if the parameters were modified.
        :param identifier: The identifier. Either a string or a dictionary with a configuration.
        :param builder: The function to call if the value does not exist
        :param parameters: If the data may dynamically change using the same identifier, pass it too
        :return: The data
        """
        if isinstance(identifier, str):
            if identifier in self.dict_cache:
                element = self.dict_cache[identifier]
                if element['parameters'] is None:
                    return element['data']
                if element['parameters'] is not None and parameters is not None:
                    if element['parameters'] == parameters:
                        return element['data']
            new_data = builder(parameters) if parameters is not None else builder()
            self.dict_cache[identifier] = {'data': new_data, 'parameters': parameters}
            return new_data
        else:
            raise ValueError("Invalid identifier type")

    def remove(self, names: Union[str, List[str]]) -> None:
        """
        Removes one or multiple elements from the cache
        :param names: The list of names
        """
        if isinstance(names, str):
            if names in self.dict_cache:
                del self.dict_cache[names]
        else:
            for cur_name in names:
                if cur_name in self.dict_cache:
                    del self.dict_cache[cur_name]

    def clear(self):
        """
        Clears the whole cache
        """
        self.dict_cache = {}
