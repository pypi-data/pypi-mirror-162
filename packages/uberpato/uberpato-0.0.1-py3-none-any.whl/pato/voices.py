DEFAULTS = {
    "polly": ["Emma"],
    "uberduck": ["trebek", "zwf"],
    "lovo": ["Charlie Carter HD"],
}
DEFAULTS_INVERSE = {}
for k, vs in DEFAULTS.items():
    for v in vs:
        DEFAULTS_INVERSE[v] = k
