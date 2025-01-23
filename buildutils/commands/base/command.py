from abc import abstractmethod, ABC


class Command(ABC):

    """
    A high level abstract definition of a command.
    """

    def __init__(self, name: str):
        """
        Initializes the command.

        Args:
            name (str): The name of the command. The built-in commands typically use this for logging purposes.
        """
        self.name = name.lower().replace(' ', '_')

    @abstractmethod
    def execute(self) -> bool:
        pass
