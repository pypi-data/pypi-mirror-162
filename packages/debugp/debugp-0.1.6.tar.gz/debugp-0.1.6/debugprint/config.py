class __Config:
    ins = None
    __slots__ = ["arg", "const", "esc_char", "f_str_brace", "op", "punc", "str",
                 "var", "enabled", "print_file", "print_hook"]

    def __new__(cls, **kwargs):
        if cls.ins is not None:
            return cls.ins
        return super().__new__(cls)

    def __init__(self, *, arg, const, esc_char, f_str_brace, op, punc, _str,
                 var, enabled, print_file, print_hook):
        self.arg = arg
        self.const = const
        self.esc_char = esc_char
        self.f_str_brace = f_str_brace
        self.op = op
        self.punc = punc
        self.str = _str
        self.var = var
        self.enabled = enabled
        self.print_file = print_file
        self.print_hook = print_hook


dp_conf = __Config(
    arg="dark_orange italic",
    const="green",
    esc_char="bright_cyan",
    f_str_brace="bright cyan bold",
    op="red",
    punc="grey58",
    _str="yellow",
    var="white",
    enabled=True,
    print_file=False,
    print_hook=repr
)

__all__ = dp_conf
