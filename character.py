from asyncio import sleep
from typing import Optional
from networking import JSON_TYPE, make_request
from datatypes import CharacterData


class Task:
    """
    Represents a task that can be executed asynchronously, typically involving an API request.

    This class encapsulates the details needed to perform a task, such as the URL to hit,
    the HTTP method to use, and additional parameters. It also manages the task's cooldown
    and stores the response data.

    Attributes:
        cooldown (int): The remaining cooldown time in seconds.
        url (str): The URL for the API request.
        method (str): The HTTP method for the request (default: "POST").
        params (dict): Additional parameters for the request.
        character (Optional[CharacterData]): The character data parsed from the response.
        payload (JSON_TYPE): Additional data from the response, excluding cooldown and character.

    :raises ValueError: If the response data is malformed or missing expected keys.
    """

    cooldown: int

    def __init__(self, url: str, method: str = "POST", **params: JSON_TYPE):
        """
        Initialize a new Task instance.

        :param url: The URL for the API request.
        :param method: The HTTP method for the request (default: "POST").
        :param params: Additional parameters for the request.
        """
        self.url = url
        self.method = method
        self.params = params

        # Initialize cooldown to -1 (unset) before execution
        self.cooldown = -1
        self.character: Optional[CharacterData] = None  # Character data will be set after execution
        self.payload: JSON_TYPE = {}  # Additional response data

    async def execute(self):
        """
        Execute the task asynchronously by making an API request and processing the response.

        This method sends a request to the specified URL, parses the response, and updates
        the task's attributes accordingly. It sets the character data, cooldown, and stores
        any additional payload.

        :return: None
        :raises RequestError: If the API request fails.
        :raises JSONDecodeError: If the response cannot be parsed as JSON.
        """
        # Make the API request and get the response data
        data = await make_request(self.url, method=self.method, **self.params)

        # Parse character data from the response
        self.character = CharacterData.from_json(data["character"])

        # Set the cooldown based on the response
        self.cooldown = data["cooldown"]["remaining_seconds"]

        # Store additional payload data (excluding cooldown and character)
        for key in data:
            if key not in ("cooldown", "character"):  # Skip known keys
                self.payload[key] = data[key]  # Store the rest in payload


class Character:
    """
    Represents a character that can manage tasks and interact with a game or system API.

    This class handles the initialization of character data, task management, and task execution.
    It also manages cooldowns for tasks, if applicable.

    Attributes:
        on_cooldown (bool): Indicates if the character is currently on cooldown (default: False).
        tasks (list[Task]): A list of tasks queued for the character.
        character_data (CharacterData): The character's data, updated after task execution.
        name (str): The name of the character.

    :raises ValueError: If the character data cannot be found or is invalid.
    """

    on_cooldown: bool = False  # Flag to indicate if the character is on cooldown
    tasks: list[Task]  # List of tasks for the character
    character_data: CharacterData  # Character's data, updated after task execution

    def __init__(self, name: str):
        """
        Initialize a new Character instance.

        :param name: The name of the character.
        """
        self.name = name

    async def init(self):
        """
        Initialize the character by fetching and setting initial character data.

        This method fetches a list of characters from the API and finds the one matching
        the character's name. If found, it sets the character_data attribute.

        :return: None
        :raises ValueError: If the character data cannot be found or is invalid.
        """
        self.tasks = []  # Initialize tasks list

        # Fetch initial character data from the API
        data: list[JSON_TYPE] = await make_request(f"/my/characters")  # type: ignore
        self.character_data = \
            next(
                filter(
                    lambda char: char["name"] == self.name,
                    data
                )
            )  # Find the character data matching the name

    async def run_task(self):
        """
        Execute the next task in the queue and update character data accordingly.

        This method pops the first task from the queue, executes it, and updates the
        character_data if the task provides new character information. It also handles
        cooldowns if the task specifies one.

        :return: None
        :raises IndexError: If there are no tasks in the queue.
        """
        task = self.tasks.pop(0)  # Get the next task from the queue

        await task.execute()  # Execute the task asynchronously

        if task.character is not None:  # Update character data if provided by the task
            self.character_data = task.character

        # TODO: Implement callbacks or similar functionality for payload handling

        if task.cooldown > 0:  # Check if the task has a cooldown
            self.on_cooldown = True  # Set cooldown flag
            await sleep(task.cooldown)  # Wait for the cooldown period
            self.on_cooldown = False  # Clear cooldown flag

    async def add_task(self, task: Task):
        """
        Add a new task to the character's task queue.

        :param task: The Task instance to add to the queue.
        :return: None
        """
        self.tasks.append(task)  # Add the task to the end of the queue
