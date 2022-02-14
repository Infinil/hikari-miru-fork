# MIT License
#
# Copyright (c) 2022-present HyperGH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import typing as t

import attr
import hikari

from .context import RawContext
from .interaction import ComponentInteraction
from .interaction import ModalInteraction

if t.TYPE_CHECKING:
    from .traits import MiruAware

__all__ = ["Event", "ComponentInteractionCreateEvent", "ModalInteractionCreateEvent"]

# The currently running app instance that will be subscribed to the listener
_app: t.Optional[MiruAware] = None


@attr.define()
class Event(hikari.Event):
    """A base class for every miru event."""

    app: MiruAware = attr.field()
    context: RawContext[t.Any] = attr.field()


@attr.define()
class ComponentInteractionCreateEvent(Event):
    """An event that is dispatched when a new component interaction is received."""

    interaction: ComponentInteraction = attr.field()


@attr.define()
class ModalInteractionCreateEvent(Event):
    """An event that is dispatched when a new modal interaction is received."""

    interaction: ModalInteraction = attr.field()


def start_listeners(app: MiruAware) -> None:
    """Start all custom event listeners, this is called during miru.load()"""
    if _app is not None:
        raise RuntimeError(f"miru is already loaded, cannot start listeners.")
    _app = app
    _app.event_manager.subscribe(hikari.InteractionCreateEvent, _sort_interactions)


def stop_listeners() -> None:
    """Stop all custom event listeners for events, this is called during miru.unload()"""
    if _app is None:
        raise RuntimeError(f"miru was never loaded, cannot stop listeners.")
    _app.event_manager.unsubscribe(hikari.InteractionCreateEvent, _sort_interactions)
    _app = None


async def _sort_interactions(event: hikari.InteractionCreateEvent) -> None:
    """Sort interaction create events and dispatch miru custom events."""

    assert _app is not None

    if not isinstance(event.interaction, (hikari.ComponentInteraction, hikari.ModalInteraction)):
        return

    # God why does mypy hate me so much for naming two variables the same in two if statement arms >_<
    if isinstance(event.interaction, hikari.ComponentInteraction):
        comp_inter = ComponentInteraction.from_hikari(event.interaction)
        comp_ctx = RawContext(comp_inter)
        _app.event_manager.dispatch(ComponentInteractionCreateEvent(_app, comp_ctx, comp_inter))

    elif isinstance(event.interaction, hikari.ModalInteraction):
        modal_inter = ModalInteraction.from_hikari(event.interaction)
        modal_ctx = RawContext(modal_inter)
        _app.event_manager.dispatch(ModalInteractionCreateEvent(_app, modal_ctx, modal_inter))
