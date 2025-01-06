# Mostly for the reference right now so I commented that out. Yeeeah, it's kinda broken :3 And type checker is going crazy here.
"""from asyncio import sleep
import asyncio


async def task(name: str):
    def print_log(data):
        print(f"[{name}] {data}")

    while True:
        fight_data = await make_request(f"/my/{name}/action/fight", "POST")
        print_log("Fight ended!")
        print_log("You " + ("won!" if fight_data['fight']['result'] == "win" else "lost!"))
        print_log(f"You have {fight_data['character']['hp']}/{fight_data['character']['max_hp']} health.")
        print_log("Drops:")
        for index, drop in enumerate(fight_data['fight']['drops'], start=1):
            print_log(f"{index}. {drop['code']} x {drop['quantity']}")
        print_log(f"Sleeping for {fight_data['cooldown']['remaining_seconds']} seconds")
        await sleep(fight_data['cooldown']['remaining_seconds'])

        rest_data = await make_request(f"/my/{name}/action/rest", "POST")
        print_log("Rested!")
        print_log(f"Restored {rest_data["hp_restored"]} health points")
        print_log(f"Sleeping for {rest_data['cooldown']['remaining_seconds']} seconds")
        await sleep(rest_data['cooldown']['remaining_seconds'])


def main():
    asyncio.run(async_main())


async def async_main():
    await asyncio.gather(
        task("zlo_mira"),
        task("Reborn"),
        task("mori"),
        task("grach"),
        task("wulkan"),
    )


if __name__ == "__main__":
    main()
"""