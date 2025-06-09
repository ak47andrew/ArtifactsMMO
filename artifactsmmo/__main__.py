from typing import Optional
import aiohttp
import aiohttp.client_exceptions
from artifactsmmo.character import Character
from artifactsmmo.datatypes import GeneralItem, Point2D
from artifactsmmo.networking import JSON_TYPE
import asyncio
from os import getenv

def get_amount_by_code(character: Character, code: str) -> int:
    for item in character.character_data.inventory:
        if item.code == code:
            return item.quantity
    return 0


def clear_invertory(character: Character, exceptions: Optional[list[str]] = None) -> None:
    if exceptions is None:
        exceptions = []
    exceptions.append("")
    for item in character.character_data.inventory:
        if item.code not in exceptions:
            if item.code not in exceptions:
                character.delete_item(item)
                print(f"Deleted item: {item}")


def is_inventory_full(character: Character) -> bool:
    total = 0
    for item in character.character_data.inventory:
        total += item.quantity
    return total >= 100


def safe_full_delete(character: Character, code: str):
    if (amount := get_amount_by_code(character, code)) > 0:
        character.delete_item(GeneralItem(code=code, quantity=amount))


async def fighter(name: str):
    char = Character(name)
    await char.init()

    if char.character_data.equipment.weapon == "wooden_stick":
        char.move(Point2D(-1, 0))
        def gathering_callback(character: Character, _: JSON_TYPE):
            if get_amount_by_code(character, "ash_wood") < 4:
                char.gathering(callback=gathering_callback)
        char.gathering(callback=gathering_callback)
        await char.run_all()
        char.unequip_item(GeneralItem(slot="weapon", quantity=1))
        char.move(Point2D(2, 1))
        char.crafting(GeneralItem(code="wooden_staff", quantity=1))
        char.equip_item(GeneralItem(slot="weapon", quantity=1, code="wooden_staff"))

    if char.character_data.position != Point2D(0, 1):
        char.move(Point2D(0, 1))
    def fight_callback(character: Character, _: JSON_TYPE):
        character.fight()
        clear_invertory(character)
        character.rest(callback=fight_callback)
    char.fight(callback=fight_callback)
    await char.run_all()


async def fishing(name: str):
    def level_to_map(level: int) -> Point2D:
        if level >= 40:
            return Point2D(-2, -4)
        elif level >= 30:
            return Point2D(6, 12)
        elif level >= 20:
            return Point2D(7, 12)
        elif level >= 10:
            return Point2D(5, 2)
        else:
            return Point2D(4, 2)
    
    def move_to_level(character: Character) -> None:
        dest = level_to_map(character.character_data.fishing.level)
        if character.character_data.position != dest:
            character.move(dest)

    char = Character(name)
    await char.init()

    move_to_level(char)

    def callback(character: Character, _: JSON_TYPE):
        # Move to a better place (if needed)
        move_to_level(character)

        # Clear inventory if needed
        if is_inventory_full(character):
            clear_invertory(character)
        
        char.gathering(callback=callback)
    char.gathering(callback=callback)
    
    await char.run_all()


async def alchemy(name: str):
    def level_to_map(level: int) -> Point2D:
        if level >= 40:
            return Point2D(1, 10)
        elif level >= 20:
            return Point2D(7, 14)
        else:
            return Point2D(2, 2)
    
    def move_to_level(character: Character) -> None:
        dest = level_to_map(character.character_data.alchemy.level)
        if character.character_data.position != dest:
            character.move(dest)

    char = Character(name)
    await char.init()

    move_to_level(char)

    def callback(character: Character, _: JSON_TYPE):
        # Move to a better place (if needed)
        move_to_level(character)

        # Clear inventory if needed
        if is_inventory_full(character):
            clear_invertory(character)
        
        char.gathering(callback=callback)
    char.gathering(callback=callback)
    
    await char.run_all()


async def woodcutting(name: str):
    def level_to_map(level: int) -> Point2D:
        if level >= 40:
            return Point2D(1, 12)
        elif level >= 30:
            return Point2D(9, 6)
        elif level >= 20:
            return Point2D(3, 5)
        elif level >= 10:
            return Point2D(2, 6)
        else:
            return Point2D(-1, 0)
    
    def move_to_level(character: Character) -> None:
        dest = level_to_map(character.character_data.woodcutting.level)
        if character.character_data.position != dest:
            character.move(dest)

    char = Character(name)
    await char.init()

    move_to_level(char)

    def callback(character: Character, _: JSON_TYPE):
        # Move to a better place (if needed)
        move_to_level(character)

        # Clear inventory if needed
        if is_inventory_full(character):
            clear_invertory(character)
        
        char.gathering(callback=callback)
    char.gathering(callback=callback)
    
    await char.run_all()


async def mining(name: str):
    def level_to_map(level: int) -> Point2D:
        if level >= 40:
            return Point2D(-2, 13)
        elif level >= 30:
            return Point2D(6, -3)
        elif level >= 20:
            return Point2D(1, 6)
        elif level >= 10:
            return Point2D(1, 7)
        else:
            return Point2D(2, 0)
    
    def move_to_level(character: Character) -> None:
        dest = level_to_map(character.character_data.mining.level)
        if character.character_data.position != dest:
            character.move(dest)

    char = Character(name)
    await char.init()


    def callback(character: Character, _: JSON_TYPE):
        # Move to a better place (if needed)
        move_to_level(character)

        # Clear inventory (if needed)
        if is_inventory_full(character):
            safe_full_delete(character, "copper_ore")
            safe_full_delete(character, "iron_ore")
            safe_full_delete(character, "coal")
            safe_full_delete(character, "gold_ore")
            safe_full_delete(character, "mithril_ore")

            if is_inventory_full(character):
                char.move(Point2D(4, 1))
                for item in character.character_data.inventory:
                    char.depost_bank_item(item)
                move_to_level(char)

        char.gathering(callback=callback)
    

    while True:
        try:
            move_to_level(char)
            char.gathering(callback=callback)
            await char.run_all()
        except aiohttp.client_exceptions.ClientResponseError as e:
            print(f"Error: {e}")
            clear_invertory(char)


def run_main():
    asyncio.run(async_main())


async def async_main():
    players = []
    players.extend([fighter(name) for name in getenv("FIGHTER_LIST", "").split(",")])  # type: ignore
    players.extend([fishing(name) for name in getenv("FISHING_LIST", "").split(",")])  # type: ignore
    players.extend([alchemy(name) for name in getenv("ALCHEMY_LIST", "").split(",")])  # type: ignore
    players.extend([woodcutting(name) for name in getenv("WOODCUTTING_LIST", "").split(",")])  # type: ignore
    players.extend([mining(name) for name in getenv("MINING_LIST", "").split(",")])  # type: ignore
    print("Starting players...")
    print(players)  # type: ignore
    await asyncio.gather(*players)  # type: ignore


if __name__ == "__main__":
    run_main()
