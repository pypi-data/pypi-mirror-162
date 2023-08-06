class Time(float):
    def __new__(cls, time):
        if isinstance(time, str):
            total = 0
            for i, amount in enumerate(time.split(":")[::-1]):
                amount = amount.lstrip("0")
                if amount:
                    total += 60 ** i * float(amount)
            time = total
        return super().__new__(cls, time)

    def __str__(self):
        secs = self
        string = ""
        while secs > 60:
            string = f":{int(secs % 60):02}{string}"
            secs //= 60
        secs = float(secs)
        if secs.is_integer():
            secs = int(secs)
        return str(secs) + string

    def __repr__(self):
        return f"{self.__class__.__qualname__}('{self}')"
