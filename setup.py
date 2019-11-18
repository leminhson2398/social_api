def func() -> dict:
    x = 12

    def getX() -> None:
        print(x)

    def setX(amount: int) -> None:
        # nonlocal x
        x += amount

    return {
        "getX": getX,
        "setX": setX,
    }


f = func()
f["getX"]()
f["setX"](3)
f["getX"]()
f["setX"](3)
f["getX"]()
