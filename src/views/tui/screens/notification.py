from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical

class NotificationScreen(ModalScreen):
    """Una pantalla modal para mostrar un mensaje al usuario."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.message, id="message"),
            Button("Aceptar", variant="primary", id="accept_button"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()
