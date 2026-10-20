"""Prevent shadowing Tkinter internals (especially Tk._options)."""
import tkinter as tk
from photoguard.gui import App


def test_app_does_not_override_tk_methods_except_init():
    collisions = {name for name, value in App.__dict__.items() if callable(value) and name != '__init__' and hasattr(tk.Tk, name)}
    assert not collisions, f'Unexpected tkinter method overrides: {sorted(collisions)}'


def test_processing_options_method_present():
    assert callable(App.__dict__.get('_build_processing_options'))
