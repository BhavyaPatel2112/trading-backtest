from strategies.ma_crossover import generate_signals as ma_crossover_signals

# acts as a dictionary for all available strategies 
# format is function + parameters (sliders) + validation (if slider values are not logical)
STRATEGIES = {
    "MA Crossover": {
        "func": ma_crossover_signals,
        "params": [
            {"name": "fast_window", "label": "Fast MA (days)", "min": 5, "max": 100, "default": 20, "step": 1},
            {"name": "slow_window", "label": "Slow MA (days)", "min": 10, "max": 300, "default": 50, "step": 1},
        ],
        "validate": lambda p: "Fast MA must be smaller than Slow MA." if p["fast_window"] >= p["slow_window"] else None,
    },
}
