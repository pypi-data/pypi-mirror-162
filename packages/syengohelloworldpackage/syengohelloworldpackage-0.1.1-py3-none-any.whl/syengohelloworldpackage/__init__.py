__version__ = '0.1.0'


def hello_world(name=None) -> None:
    greet = "Hello world"
    if name:
        print(f"{greet}, may name is {name}!")
    else:
        print(f"{greet}!")

    print(
        f"\nThis was message from syengo254helloworldpackage for version {__version__}.")


def main():
    hello_world()


if __name__ == "__main__":
    main()
