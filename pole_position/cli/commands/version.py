from importlib.metadata import PackageNotFoundError, version


def run(args: list[str]) -> None:
    try:
        print(version("poleposition"))
    except PackageNotFoundError:
        print("0.0.8") # Fallback version if package metadata is not found