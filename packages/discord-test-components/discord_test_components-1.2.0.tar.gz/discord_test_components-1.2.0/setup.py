from setuptools import setup

if __name__ == "__main__":
    setup(
        name="discord_test_components",
        version="1.2.0",
        author="None",
        include_package_data=True,
        install_requires=["aiohttp", "discord.py"],
        packages=["discord_components", "discord_components.ext"],
        python_requires=">=3.6"
    )