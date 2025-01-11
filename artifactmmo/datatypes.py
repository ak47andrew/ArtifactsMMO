from typing import Optional, Self
from dataclasses import dataclass
from .networking import JSON_TYPE


@dataclass
class Scale:
    """
    Represents a scale with a current value and a maximum value.

    Attributes:
        current_value (int): The current value of the scale.
        max_value (int): The maximum value of the scale.
    """

    current_value: int
    max_value: int

    @property
    def percentage(self) -> float:
        """
        Gets the current value as a percentage of the maximum value.

        Returns:
            float: The current value as a percentage.
        """
        return round(self.ratio * 100, 2)

    @property
    def ratio(self) -> float:
        """
        Gets the current value as a ratio of the maximum value.

        Returns:
            float: The current value as a ratio.
        """
        return self.current_value / self.max_value

    def __str__(self) -> str:
        return f"{self.current_value}/{self.max_value} ({self.percentage}%)"

    def __repr__(self) -> str:
        return f"Scale(current_value={self.current_value}, max_value={self.max_value})"

    def is_full(self) -> bool:
        """
        Checks if the scale is full (i.e., current value equals maximum value).

        Returns:
            bool: True if the scale is full, False otherwise.
        """
        return self.current_value == self.max_value

    def is_empty(self) -> bool:
        """
        Checks if the scale is empty (i.e., current value is zero).

        Returns:
            bool: True if the scale is empty, False otherwise.
        """
        return self.current_value == 0


@dataclass
class Point2D:
    """
    Represents a 2-dimensional point with x and y coordinates.

    Attributes:
        x (int): The x-coordinate of the point.
        y (int): The y-coordinate of the point.
    """

    x: int
    y: int

    @property
    def distance_to_origin(self) -> float:
        """
        Gets the distance from the point to the origin (0, 0).

        Returns:
            float: The distance from the point to the origin.
        """
        return (self.x**2 + self.y**2) ** 0.5

    def __add__(self, other: "Point2D") -> "Point2D":
        """
        Adds two points together, effectively translating one point by the other.

        Args:
            other (Point2D): The point to add.

        Returns:
            Point2D: The resulting point.
        """
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point2D") -> "Point2D":
        """
        Subtracts one point from another, effectively finding the vector between them.

        Args:
            other (Point2D): The point to subtract.

        Returns:
            Point2D: The resulting point.
        """
        return Point2D(self.x - other.x, self.y - other.y)

    def translate(self, dx: int, dy: int) -> "Point2D":
        """
        Translates the point by a specified amount.

        Args:
            dx (int): The amount to translate in the x-direction.
            dy (int): The amount to translate in the y-direction.

        Returns:
            Point2D: The translated point.
        """
        return Point2D(self.x + dx, self.y + dy)

    def manhattan_distance_to(self, other: "Point2D") -> int:
        """
        Gets the Manhattan distance (L1 distance) between two points.

        Args:
            other (Point2D): The other point.

        Returns:
            int: The Manhattan distance between the two points.
        """
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euclidean_distance_to(self, other: "Point2D") -> float:
        """
        Gets the Euclidean distance (L2 distance) between two points.

        Args:
            other (Point2D): The other point.

        Returns:
            float: The Euclidean distance between the two points.
        """
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class InGameTask:
    task_type: str
    progress: Scale

    @classmethod
    def from_json(cls, json_data: JSON_TYPE) -> Self:
        self = cls.__new__(cls)

        self.task_type = json_data["task_type"]
        self.progress = Scale(json_data["task_progress"], json_data["task_total"])

        return self


@dataclass
class Elemental:
    fire: int
    earth: int
    water: int
    air: int

    @classmethod
    def from_json(cls, json_data: JSON_TYPE, prefix: str) -> Self:
        self = cls.__new__(cls)

        self.fire = json_data[f"{prefix}fire"]
        self.earth = json_data[f"{prefix}earth"]
        self.water = json_data[f"{prefix}water"]
        self.air = json_data[f"{prefix}air"]

        return self


@dataclass
class Skill:
    level: int
    xp: Scale

    @classmethod
    def from_json(cls, json_data: JSON_TYPE, prefix: str) -> Self:
        self = cls.__new__(cls)

        self.level = json_data[f"{prefix}level"]
        self.xp = Scale(json_data[f"{prefix}xp"], json_data[f"{prefix}max_xp"])

        return self


@dataclass
class GeneralItem:
    quantity: int
    slot: str = ""
    code: str = ""

    def to_json(self) -> JSON_TYPE:
        return {
            "slot": self.slot,
            "code": self.code,
            "quantity": self.quantity,
        }


@dataclass
class Equipment:
    weapon: str
    shield: str
    helmet: str
    body_armor: str
    leg_armor: str
    boots: str
    ring1: str
    ring2: str
    amulet: str
    artifact1: str
    artifact2: str
    artifact3: str
    utility1: GeneralItem
    utility2: GeneralItem

    @classmethod
    def from_json(cls, json_data: JSON_TYPE) -> Self:
        self = cls.__new__(cls)

        self.weapon = json_data["weapon_slot"]
        self.shield = json_data["shield_slot"]
        self.helmet = json_data["helmet_slot"]
        self.body_armor = json_data["body_armor_slot"]
        self.leg_armor = json_data["leg_armor_slot"]
        self.boots = json_data["boots_slot"]
        self.ring1 = json_data["ring1_slot"]
        self.ring2 = json_data["ring2_slot"]
        self.amulet = json_data["amulet_slot"]
        self.artifact1 = json_data["artifact1_slot"]
        self.artifact2 = json_data["artifact2_slot"]
        self.artifact3 = json_data["artifact3_slot"]
        self.utility1 = GeneralItem(
            slot=json_data["utility1_slot"],
            code="",  # TODO ??? Docs is kinda sucks
            quantity=json_data["utility1_slot_quantity"],
        )
        self.utility2 = GeneralItem(
            slot=json_data["utility2_slot"],
            code="",
            quantity=json_data["utility2_slot_quantity"],
        )

        return self


@dataclass
class CharacterData:
    name: str
    account: str
    skin: str
    gold: int
    hp: Scale
    position: Point2D

    combat: Skill
    mining: Skill
    woodcutting: Skill
    fishing: Skill
    weaponcrafting: Skill
    gearcrafting: Skill
    jewlercrafting: Skill
    cooking: Skill
    alchemy: Skill

    attack: Elemental
    dmg: Elemental
    res: Elemental

    task: Optional[InGameTask]

    equipment: Equipment
    inventory: list[GeneralItem]

    @classmethod
    def from_json(cls, data: JSON_TYPE) -> "CharacterData":
        self = cls.__new__(cls)

        self.name = data["name"]
        self.account = data["account"]
        self.skin = data["skin"]
        self.gold = data["gold"]
        self.hp = Scale(data["hp"], data["max_hp"])
        self.position = Point2D(data["x"], data["y"])

        self.combat = Skill.from_json(data, "")
        self.mining = Skill.from_json(data, "mining_")
        self.woodcutting = Skill.from_json(data, "woodcutting_")
        self.fishing = Skill.from_json(data, "fishing_")
        self.weaponcrafting = Skill.from_json(data, "weaponcrafting_")
        self.gearcrafting = Skill.from_json(data, "gearcrafting_")
        self.jewlercrafting = Skill.from_json(data, "jewelrycrafting_")
        self.cooking = Skill.from_json(data, "cooking_")
        self.alchemy = Skill.from_json(data, "alchemy_")

        self.attack = Elemental.from_json(data, "attack_")
        self.dmg = Elemental.from_json(data, "dmg_")
        self.res = Elemental.from_json(data, "res_")

        self.task = InGameTask.from_json(data)

        self.equipment = Equipment.from_json(data)
        self.inventory = [
            GeneralItem(slot=item["slot"], code=item["code"], quantity=item["quantity"])
            for item in data["inventory"]
        ]

        return self
