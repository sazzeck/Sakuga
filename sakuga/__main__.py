import os

from sakuga.core.bot import Bot


def main() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot = Bot()
    bot.run(asyncio_debug=True)


if __name__ == "__main__":
    main()
