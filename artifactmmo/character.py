from asyncio import sleep
from typing import Optional, Callable
from networking import JSON_TYPE, make_request
from .datatypes import CharacterData, Point2D, GeneralItem


TASK_CALLBACK_TYPE = Optional[Callable[["Character", JSON_TYPE], None]]


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
    callback: TASK_CALLBACK_TYPE

    def __init__(
        self,
        url: str,
        method: str = "POST",
        callback: TASK_CALLBACK_TYPE = None,
        params: Optional[JSON_TYPE] = None,
    ):
        """
        Initialize a new Task instance.

        :param url: The URL for the API request.
        :param method: The HTTP method for the request (default: "POST").
        :param params: Additional parameters for the request.
        """
        self.url = url
        self.method = method
        self.params = params or {}  # Set default parameters if not provided
        self.callback = callback  # Set default callback if not provided

        # Initialize cooldown to -1 (unset) before execution
        self.cooldown = -1
        self.character: Optional[CharacterData] = (
            None  # Character data will be set after execution
        )
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
        self.character_data = next(
            filter(lambda char: char["name"] == self.name, data)
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

        if task.callback is not None:  # Check if the task has a callback function
            task.callback(
                self, task.payload
            )  # Call the callback function with character and payload data

        if task.cooldown > 0:  # Check if the task has a cooldown
            self.on_cooldown = True  # Set cooldown flag
            await sleep(task.cooldown)  # Wait for the cooldown period
            self.on_cooldown = False  # Clear cooldown flag

    def add_task(self, task: Task):
        """
        Add a new task to the character's task queue.

        :param task: The Task instance to add to the queue.
        :return: None
        """
        self.tasks.append(task)  # Add the task to the end of the queue

    # Actions
    def _make_action(
        self,
        action: str,
        params: Optional[JSON_TYPE] = None,
        callback: TASK_CALLBACK_TYPE = None,
    ) -> None:
        self.add_task(
            Task(
                f"/my/{self.name}/action/{action}",
                method="POST",
                callback=callback,
                params=params,
            )
        )

    def move(self, position: Point2D, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("move", {"x": position.x, "y": position.y}, callback=callback)

    def rest(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("rest", callback=callback)

    def equip_item(
        self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action("equip", item.to_json(), callback=callback)

    def unequip_item(
        self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "unequip",
            {
                "slot": item.slot,
                "quantity": item.quantity,
            },
            callback=callback,
        )

    def use_item(self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action(
            "use",
            {
                "code": item.code,
                "quantity": item.quantity,
            },
            callback=callback,
        )

    def fight(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("fight", callback=callback)

    def gathering(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("gathering", callback=callback)

    def crafting(self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action(
            "crafting",
            {
                "code": item.code,
                "quantity": item.quantity,
            },
            callback=callback,
        )

    def deposit_bank_gold(
        self, quantity: int, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "bank/deposit/gold", {"quantity": quantity}, callback=callback
        )

    def withdraw_bank_gold(
        self, quantity: int, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "bank/withdraw/gold", {"quantity": quantity}, callback=callback
        )

    def depost_bank_item(
        self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "bank/deposit",
            {
                "code": item.code,
                "quantity": item.quantity,
            },
            callback=callback,
        )

    def withdraw_bank(
        self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "bank/withdraw",
            {
                "code": item.code,
                "quantity": item.quantity,
            },
            callback=callback,
        )

    def buy_bank_extansion(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("bank/buy_expansion", callback=callback)

    def recycling(self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action(
            "recycling",
            {
                "code": item.code,
                "quantity": item.quantity,
            },
            callback=callback,
        )

    def ge_buy(
        self, order_id: str, quantity: int, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "grandexchange/buy",
            {"id": order_id, "quantity": quantity},
            callback=callback,
        )

    def ge_create_sell_order(
        self, item: GeneralItem, price: int, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "grandexchange/create_sell_order",
            {
                "code": item.code,
                "quantity": item.quantity,
                "price": price,
            },
            callback=callback,
        )

    def ge_cancel_sell_order(
        self, order_id: str, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "grandexchange/cancel_sell_order", {"id": order_id}, callback=callback
        )

    def complete_ingame_task(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("task/complete", callback=callback)

    def ingame_task_exchange(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("task/exchange", callback=callback)

    def ingame_task_accept_new(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("task/new", callback=callback)

    def ingame_task_trade(
        self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "task/trade",
            {
                "code": item.code,
                "quantity": item.quantity,
            },
            callback=callback,
        )

    def ingame_task_cancel(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("task/cancel", callback=callback)

    def christmas_exchange(self, callback: TASK_CALLBACK_TYPE = None) -> None:
        self._make_action("christmas/exchange", callback=callback)

    def delete_item(
        self, item: GeneralItem, callback: TASK_CALLBACK_TYPE = None
    ) -> None:
        self._make_action(
            "inventory/delete",
            {
                "code": item.code,
                "quantity": item.quantity,
            },
            callback=callback,
        )
