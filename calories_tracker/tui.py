import os
import django

# Configure Django environment before any Django-related imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_calories_tracker.settings')
django.setup()

from asgiref.sync import sync_to_async
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Label, ListView, ListItem
from textual.containers import Vertical
from django.db import transaction
from django.contrib.auth.models import User
from calories_tracker.models import Meals, Products
from datetime import datetime

# --- Textual Application for adding Meals ---
class MealInputApp(App):
    """A Textual app to add a new Meal entry."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    #product_suggestions_list {
        display: none; /* Hidden by default */
        height: auto;
        max-height: 10; /* Limit height to 10 items */
        border: solid grey;
        margin-top: 0;
        margin-bottom: 0;
    }
    #selected_product_display {
        margin-top: 0;
        margin-bottom: 1;
        color: grey;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_product_id: int | None = None
        self.product_suggestions: list[Products] = []
        self.current_product_search_term: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Vertical(id="main_container"):
            yield Label("Enter Meal Details:")
            yield Input(placeholder="Search Product Name", id="product_search_input")
            yield Label("Selected Product: None", id="selected_product_display")
            yield ListView(id="product_suggestions_list")
            yield Input(placeholder="Amount (grams, e.g., 150.5)", id="amount_input", type="number")
            yield Input(placeholder="Datetime (YYYY-MM-DD HH:MM:SS, e.g., 2023-10-27 14:30:00)", id="datetime_input", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            yield Button("Save Meal", id="save_button", variant="primary")
            yield Label("", id="status_message")

    async def on_input_changed(self, event: Input.Changed) -> None: # Already async, good.
        if event.input.id == "product_search_input":
            self.current_product_search_term = event.value
            self.selected_product_id = None # Clear selected product when typing
            self.query_one("#selected_product_display", Label).update("Selected Product: None") # Textual UI update, no sync_to_async

            if event.value:
                # Wrap the entire synchronous ORM operation (filter, slice, list conversion) in sync_to_async
                self.product_suggestions = await sync_to_async(lambda: list(Products.objects.filter(name__icontains=event.value)[:10]))()
                
                list_view = self.query_one("#product_suggestions_list", ListView)
                list_view.clear()
                for product in self.product_suggestions:
                    list_view.append(ListItem(Label(product.fullname()), value=product.id))
                
                if self.product_suggestions:
                    list_view.display = True
                    list_view.focus() # Textual UI update, no sync_to_async
                else:
                    list_view.display = False
            else:
                self.query_one("#product_suggestions_list", ListView).display = False # Textual UI update, no sync_to_async
                self.query_one("#product_suggestions_list", ListView).clear() # Textual UI update, no sync_to_async
                self.query_one("#product_search_input", Input).focus() # Textual UI update, no sync_to_async

    async def on_list_view_selected(self, event: ListView.Selected) -> None: # Already async, good.
        selected_id = event.item.value
        try:
            selected_product = await sync_to_async(Products.objects.get)(id=selected_id) # ORM call wrapped, good.
            self.selected_product_id = selected_product.id
            self.query_one("#product_search_input", Input).value = selected_product.fullname() # Textual UI update, no sync_to_async
            self.query_one("#selected_product_display", Label).update(f"Selected Product: [b]{selected_product.fullname()}[/b] (ID: {selected_product.id})") # Textual UI update, no sync_to_async
            self.query_one("#product_suggestions_list", ListView).display = False # Textual UI update, no sync_to_async
            self.query_one("#amount_input", Input).focus() # Textual UI update, no sync_to_async
        except Products.DoesNotExist:
            self.query_one("#status_message", Label).update(f"[red]Error: Selected product with ID {selected_id} not found.[/red]") # Textual UI update, no sync_to_async
        event.stop() # Prevent further propagation

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_button":
            self.action_save_meal()

    async def action_save_meal(self) -> None: # Already async, good.
        # product_id_str is no longer used, we rely on self.selected_product_id
        amount_str = self.query_one("#amount_input", Input).value
        datetime_str = self.query_one("#datetime_input", Input).value
        status_label = self.query_one("#status_message", Label)

        if self.selected_product_id is None:
            status_label.update("[red]Please select a product using the search field.[/red]") # Textual UI update, no sync_to_async
            return
        if not amount_str or not datetime_str:
            status_label.update("[red]Amount and Datetime fields are required.[/red]") # Textual UI update, no sync_to_async
            return

        try:
            product_id = self.selected_product_id
            amount = float(amount_str)
            meal_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            status_label.update(f"[red]Invalid input: {e}. Check Product ID (integer), Amount (number), and Datetime format (YYYY-MM-DD HH:MM:SS).[/red]")
            return

        try:
            user = await sync_to_async(User.objects.first)()
            if not user:
                status_label.update("[red]No users found in the database. Please create a user first.[/red]")
                return
            product = await sync_to_async(Products.objects.get)(id=product_id)

            async with sync_to_async(transaction.atomic)():
                meal = await sync_to_async(Meals.objects.create)(
                    user=user,
                    amount=amount,
                    products=product,
                    datetime=meal_datetime
                )
                status_label.update(f"[green]Meal saved successfully: {meal.products.name} ({meal.amount}g) for {meal.user.username} at {meal.datetime}.[/green]")
                
                # Clear fields after successful save
                self.query_one("#product_search_input", Input).value = "" # Textual UI update, no sync_to_async
                self.query_one("#selected_product_display", Label).update("Selected Product: None") # Textual UI update, no sync_to_async
                self.selected_product_id = None
                self.query_one("#amount_input", Input).value = "" # Textual UI update, no sync_to_async
                self.query_one("#datetime_input", Input).value = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Textual UI update, no sync_to_async
                self.query_one("#product_search_input", Input).focus() # Textual UI update, no sync_to_async
        except Products.DoesNotExist:
            status_label.update(f"[red]Product with ID {product_id} not found.[/red]")
        except Exception as e:
            status_label.update(f"[red]Error saving meal: {e}[/red]")

    def action_quit(self) -> None:
        self.exit()

def tui_meals():
    """
    Launches a Textual TUI application to add a new Meal entry.
    Assumes the Django environment is already set up by the calling script.
    """
    MealInputApp().run()
