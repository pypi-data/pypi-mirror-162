import shutil


class Title:
    def __init__(self, text, template="=", sep=None, color="white"):
        if sep is None:
            sep = ["(", ")"]
        self.text = text
        self.s_template = template
        if len(sep) > 1:
            self.lsep = sep[0]
            self.rsep = sep[1]
        else:
            self.lsep = self.rsep = sep
        self.size = shutil.get_terminal_size().columns
        self.color = color

    def __str__(self):
        lt = len(self.text) // 2
        half = self.size // 2 - lt - 2 - (len(self.text) - len(self.text) // 2)
        h = half // len(self.s_template)
        left = f"{self.s_template * h + self.s_template[:(half - h)]}{self.lsep} "
        right = f" {self.rsep}{self.s_template * h + self.s_template[:(half - h)]}"

        return f"[{self.color}]{left}[/{self.color}]{self.text}[{self.color}]{right}[/{self.color}]"
