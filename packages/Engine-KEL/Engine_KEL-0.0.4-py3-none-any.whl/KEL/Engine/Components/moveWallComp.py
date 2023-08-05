import KEL 


class MoveWallComp:
    def start(self, comps):
        self.hold = False

    def update(self, comps) -> list:
        input = KEL.Input('K_SPACE')

        if input == "Down":
            self.hold = True

        elif input == "Up":
            self.hold = False


        if self.hold:
            comps['TransformRectComp'].yLT += 1

        return comps
