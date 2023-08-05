import gdsfactory as gf

if __name__ == "__main__":
    c = gf.Component()
    c1 = gf.components.straight()
    c2 = c1.copy()

    c << c1
    c << c2
    c.show(show_ports=True)
