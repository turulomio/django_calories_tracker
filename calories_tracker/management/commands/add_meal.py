from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone, translation
from calories_tracker.models import Meals, Products
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from decimal import Decimal
import os
from django.conf import settings

class Command(BaseCommand):
    """
    A Django management command to interactively add new Meal entries.

    This command guides the user through selecting a user, a product (filtered by the selected user),
    entering an amount, and optionally a specific date and time for the meal.
    It supports searching for users and products by name and handles multiple results.
    All user-facing strings are marked for translation using Django's i18n system.
    """
    help = _('Adds a new Meal entry interactively. (e.g., "manage.py tui.add_meal")')

    def _select_object(self, model, prompt_name, user_filter=None):
        """
        Interactively prompts the user to search for and select an object from a given model.

        Args:
            model (django.db.models.Model): The Django model to search within (e.g., User, Products).
            prompt_name (str): The name of the object type to display in prompts (e.g., "User", "Product").
            user_filter (User, optional): A User object to filter Products by. Required for Products model.

        Returns:
            django.db.models.Model instance or None: The selected object, or None if selection fails or is aborted.
        """
        while True:
            search_term = input(_(f"Enter {prompt_name} (or part of it) to search: ")).strip()
            if not search_term:
                self.stdout.write(self.style.WARNING(_(f"Search term cannot be empty. Please try again.")))
                continue

            if model == User:
                queryset = model.objects.filter(username__icontains=search_term)
            elif model == Products:
                if user_filter:
                    queryset = model.objects.filter(user=user_filter, name__icontains=search_term)
                else: # This case should ideally not be reached if called correctly
                    self.stdout.write(self.style.ERROR(_("User filter is required for product selection.")))
                    return None
            else:
                self.stdout.write(self.style.ERROR(_("Unsupported model for selection.")))
                return None

            results = list(queryset)

            if not results:
                self.stdout.write(self.style.WARNING(_(f"No {prompt_name} found matching '{search_term}'.")))
                continue
            elif len(results) == 1:
                selected_obj = results[0]
                if model == User:
                    display_name = selected_obj.fullname() if hasattr(selected_obj, 'fullname') else selected_obj.username
                elif model == Products:
                    display_name = selected_obj.fullname() if hasattr(selected_obj, 'fullname') else selected_obj.name
                else:
                    display_name = str(selected_obj) # Generic fallback
                self.stdout.write(self.style.SUCCESS(_(f"Selected {prompt_name}: {display_name} (ID: {selected_obj.id})")))
                return selected_obj
            else:
                self.stdout.write(_(f"Multiple {prompt_name} found:"))
                for i, obj in enumerate(results):
                    if model == User:
                        display_name = obj.fullname() if hasattr(obj, 'fullname') else obj.username
                    elif model == Products:
                        display_name = obj.fullname() if hasattr(obj, 'fullname') else obj.name
                    else:
                        display_name = str(obj) # Generic fallback
                    self.stdout.write(_(f"  {i+1}. {display_name} (ID: {obj.id})"))
                
                while True:
                    choice = input(_(f"Enter the number of the {prompt_name} to select (or 's' to search again): ")).strip().lower()
                    if choice == 's':
                        break # Break inner loop to search again
                    
                    try:
                        choice_index = int(choice) - 1
                        if 0 <= choice_index < len(results):
                            selected_obj = results[choice_index]
                            if model == User:
                                display_name = selected_obj.fullname() if hasattr(selected_obj, 'fullname') else selected_obj.username
                            elif model == Products:
                                display_name = selected_obj.fullname() if hasattr(selected_obj, 'fullname') else selected_obj.name
                            else:
                                display_name = str(selected_obj) # Generic fallback
                            self.stdout.write(self.style.SUCCESS(_(f"Selected {prompt_name}: {display_name} (ID: {selected_obj.id})")))
                            return selected_obj
                        else:
                            self.stdout.write(self.style.WARNING(_("Invalid choice. Please enter a valid number or 's'.")))
                    except ValueError:
                        self.stdout.write(self.style.WARNING(_("Invalid input. Please enter a number or 's'.")))

    def handle(self, *args, **options):
        """
        The main entry point for the command.
        It orchestrates the interactive process of adding a new meal.
        """
        # Store the current language to restore it later
        current_language = translation.get_language()
        try:
            # Attempt to activate language based on the console's LANG environment variable
            # Fallback to settings.LANGUAGE_CODE if LANG is not set or not supported
            env_lang = os.environ.get('LANG')
            if env_lang:
                lang_code = env_lang.split('_')[0] # e.g., 'es' from 'es_ES.UTF-8'
                supported_languages = [code for code, _ in settings.LANGUAGES]
                if lang_code in supported_languages:
                    translation.activate(lang_code)
                else:
                    self.stdout.write(self.style.WARNING(_(f"Console language '{lang_code}' not supported. Using default from settings.")))
                    translation.activate(settings.LANGUAGE_CODE)
            else:
                translation.activate(settings.LANGUAGE_CODE)

            self.stdout.write(self.style.HTTP_INFO(_("--- Add New Meal Entry ---")))

            # 1. Select User
            self.stdout.write(self.style.NOTICE(_("Step 1: Select a User")))
            selected_user = self._select_object(User, _("User"))
            if not selected_user:
                self.stdout.write(self.style.ERROR(_("User selection failed. Aborting.")))
                return

            # 2. Select Product for the selected user
            self.stdout.write(self.style.NOTICE(_("Step 2: Select a Product")))
            selected_product = self._select_object(Products, _("Product"), user_filter=selected_user)
            if not selected_product:
                self.stdout.write(self.style.ERROR(_("Product selection failed. Aborting.")))
                return

            # 3. Get Amount
            self.stdout.write(self.style.NOTICE(_("Step 3: Enter Amount")))
            amount_str = ""
            while not amount_str:
                amount_str = input(_("Enter amount in grams (e.g., 150.5): ")).strip()
                try:
                    amount = Decimal(amount_str)
                    if amount <= 0:
                        self.stdout.write(self.style.WARNING(_("Amount must be a positive number.")))
                        amount_str = "" # Reset to re-prompt
                except ValueError:
                    self.stdout.write(self.style.WARNING(_("Invalid amount. Please enter a number.")))
                    amount_str = "" # Reset to re-prompt

            # 4. Get Datetime
            self.stdout.write(self.style.NOTICE(_("Step 4: Enter Datetime (optional)")))
            default_datetime_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            datetime_input = input(_(f"Enter datetime (YYYY-MM-DD HH:MM:SS) [default: {default_datetime_str}]: ")).strip()
            meal_datetime = timezone.now() # Default to now if input is empty or invalid
            if datetime_input:
                while True:
                    try:
                        meal_datetime = datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S")
                        # Make it timezone aware if Django's USE_TZ is True
                        if timezone.is_aware(timezone.now()):
                            meal_datetime = timezone.make_aware(meal_datetime)
                        break
                    except ValueError:
                        self.stdout.write(self.style.WARNING(_("Invalid datetime format. Please use YYYY-MM-DD HH:MM:SS.")))
                        datetime_input = input(_(f"Enter datetime (YYYY-MM-DD HH:MM:SS) [default: {default_datetime_str}]: ")).strip()
                        if not datetime_input: # If user enters empty string again, use default
                            break

            # 5. Create Meal
            self.stdout.write(self.style.NOTICE(_("Step 5: Creating Meal...")))
            try:
                meal = Meals.objects.create(
                    user=selected_user,
                    products=selected_product,
                    amount=amount,
                    datetime=meal_datetime
                )
                self.stdout.write(self.style.SUCCESS(_(f"Successfully created Meal: {meal}")))
                self.stdout.write(self.style.SUCCESS(_(f"Meal ID: {meal.id}")))
            except Exception as e:
                self.stdout.write(self.style.ERROR(_(f"Error creating meal: {e}")))

        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR(_("\nOperation cancelled by user.")))
            return # Exit immediately after KeyboardInterrupt
        finally:
            # Always restore the original language after the command finishes
            translation.activate(current_language)