"""
Unit tests for Ollama recipe import and automatic elaboration generation.
"""

from decimal import Decimal
import json
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.utils import timezone

from calories_tracker import models
from calories_tracker.management.commands.import_recipe import (
    OllamaClient,
    ProductMatcher,
    RecipeImporter,
    RecipeTextExtractor,
    YouTubeHelper,
)


def test_ollama_client_parse_json(self):
    """
    Test JSON parsing logic of OllamaClient with plain, markdown-fenced, trailing commas, unescaped newlines, and truncated responses.
    """
    client = OllamaClient()

    # Clean JSON
    res = client._parse_json_response('{"name": "Tortilla", "diners": 4}')
    self.assertEqual(res["name"], "Tortilla")
    self.assertEqual(res["diners"], 4)

    # Markdown fenced JSON
    res_fenced = client._parse_json_response('```json\n{"name": "Tortilla", "diners": 4}\n```')
    self.assertEqual(res_fenced["name"], "Tortilla")
    self.assertEqual(res_fenced["diners"], 4)

    # JSON with surrounding text
    res_surrounded = client._parse_json_response('Here is the recipe:\n{"name": "Tortilla", "diners": 4}\nEnjoy!')
    self.assertEqual(res_surrounded["name"], "Tortilla")

    # JSON with trailing commas
    res_trailing = client._parse_json_response('{"name": "Tortilla con cebolla", "diners": 4, "categories": ["Eggs",],}')
    self.assertEqual(res_trailing["name"], "Tortilla con cebolla")

    # JSON with unescaped newlines in steps string
    raw_newlines = '{\n"name": "Tortilla Newline",\n"steps": "Paso 1:\nBatir huevos\nPaso 2:\nFreír patatas",\n"diners": 2\n}'
    res_newlines = client._parse_json_response(raw_newlines)
    self.assertEqual(res_newlines["name"], "Tortilla Newline")
    self.assertEqual(res_newlines["diners"], 2)

    # Truncated JSON recovery
    truncated = '{"name": "Bizcocho Truncado", "diners": 6, "ingredients": [{"name": "Harina", "amount": 250, "unit": "g"}]'
    res_truncated = client._parse_json_response(truncated)
    self.assertEqual(res_truncated["name"], "Bizcocho Truncado")
    self.assertEqual(res_truncated["diners"], 6)

    # Malformed text recovered via fallback extractor
    malformed_text = 'Result of LLM analysis: "name": "Guiso Recuperado", "food_type": "Meat", "diners": 5, "steps": "Cocinar a fuego lento."'
    res_fallback = client._parse_json_response(malformed_text)
    self.assertEqual(res_fallback["name"], "Guiso Recuperado")
    self.assertEqual(res_fallback["diners"], 5)


def test_recipe_text_extractor_html(self):
    """
    Test HTML text and title extraction.
    """
    sample_html = b"""
    <html>
        <head><title>Receta de Pollo al Horno</title></head>
        <body>
            <h1>Pollo al Horno</h1>
            <p>Ingredientes: 500g de pollo, 2 patatas.</p>
            <script>console.log("ignore");</script>
        </body>
    </html>
    """
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = sample_html
        mock_response.headers.get_content_charset.return_value = "utf-8"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        text, title = RecipeTextExtractor.extract_from_url("http://example.com/recipe")
        self.assertEqual(title, "Receta de Pollo al Horno")
        self.assertIn("Pollo al Horno", text)
        self.assertIn("500g de pollo", text)
        self.assertNotIn("console.log", text)


def test_recipe_importer_save_and_automatic_elaboration(self):
    """
    Test saving parsed recipe and creating automatic elaboration with products and text.
    """
    importer = RecipeImporter()

    recipe_data = {
        "name": "Pollo con Patatas Test",
        "comment": "Receta deliciosa para toda la familia",
        "food_type": "Meat",
        "categories": ["Chicken", "NonExistentCategoryTest"],
        "diners": 4,
        "ingredients": [
            {
                "name": "Pechuga de pollo test",
                "amount": 500,
                "unit": "g",
                "comment": "cortada en tiras",
            },
            {
                "name": "Aceite de oliva test",
                "amount": 2,
                "unit": "tbsp",
                "comment": "virgen extra",
            },
        ],
        "steps": "1. Cortar Pechuga de pollo test.\n2. Añadir Aceite de oliva test y hornear a 180C durante 30 minutos.",
    }

    # Create one existing product in DB, leave the second one non-existent
    existing_product = models.Products.objects.create(
        name="Pechuga de pollo test",
        amount=Decimal("100.000"),
        calories=Decimal("110.000"),
        food_types=models.FoodTypes.objects.first(),
        glutenfree=False,
        obsolete=False,
        user=self.user_authorized_1,
    )

    # 1. Save recipe with URL link
    recipe = importer.save_recipe(
        recipe_data=recipe_data,
        user=self.user_authorized_1,
        source_url="https://recetas.test/pollo-patatas",
    )

    self.assertIsNotNone(recipe.id)
    self.assertIn("Pollo con Patatas Test", recipe.name)
    self.assertTrue("Generado por IA" in recipe.name or "Generated by AI" in recipe.name)
    self.assertEqual(recipe.recipes_links.count(), 1)
    link = recipe.recipes_links.first()
    self.assertEqual(link.link, "https://recetas.test/pollo-patatas")
    self.assertTrue(recipe.recipes_categories.filter(name="Chicken").exists())
    self.assertFalse(recipe.recipes_categories.filter(name="NonExistentCategoryTest").exists())
    self.assertFalse(models.RecipesCategories.objects.filter(name="NonExistentCategoryTest").exists())

    # 2. Create automatic elaboration
    elaboration = importer.create_automatic_elaboration(
        recipe=recipe,
        recipe_data=recipe_data,
        user=self.user_authorized_1,
    )

    self.assertIsNotNone(elaboration.id)
    self.assertEqual(elaboration.diners, 4)
    self.assertFalse(elaboration.automatic)

    # Check products in through: only existing product was added (count == 1)
    through_items = models.ElaborationsProductsInThrough.objects.filter(elaborations=elaboration)
    self.assertEqual(through_items.count(), 1)
    self.assertEqual(through_items.first().products, existing_product)

    # Verify placeholder product for non-existing ingredient was NOT created in DB
    self.assertFalse(models.Products.objects.filter(name="Aceite de oliva test").exists())

    # Check elaboration text
    self.assertTrue(hasattr(elaboration, "elaborations_texts"))
    elaboration_text = elaboration.elaborations_texts.text
    self.assertIn("mention_ingredients", elaboration_text)
    self.assertTrue("Generado por IA" in elaboration_text or "Generated by AI" in elaboration_text)


def test_management_command_import_recipe(self):
    """
    Test import_recipe management command with mocked Ollama and URL extraction.
    """
    mock_recipe_json = {
        "name": "Sopa de Verduras Command Test",
        "comment": "Sopa casera saludable",
        "food_type": "Vegetables",
        "categories": ["Vegetables", "Soups and creams"],
        "diners": 2,
        "ingredients": [
            {
                "name": "Zanahoria test command",
                "amount": 200,
                "unit": "g",
                "comment": "picada",
            }
        ],
        "steps": "Hervir Zanahoria test command durante 20 minutos.",
    }

    with patch.object(RecipeTextExtractor, "extract_from_url", return_value=("Texto de prueba", "Título")):
        with patch.object(OllamaClient, "generate", return_value=mock_recipe_json):
            call_command(
                "import_recipe",
                url="https://example.com/sopa",
                username="authorized_1",
            )

    recipe = models.Recipes.objects.filter(name__icontains="Sopa de Verduras Command Test").first()
    self.assertIsNotNone(recipe)
    self.assertTrue("Generado por IA" in recipe.name or "Generated by AI" in recipe.name)
    self.assertEqual(recipe.recipes_links.count(), 1)
    self.assertEqual(recipe.elaborations.count(), 1)
    elaboration = recipe.elaborations.first()
    self.assertEqual(elaboration.diners, 2)


def test_management_command_from_recipe_id(self):
    """
    Test generating automatic elaboration from an existing recipe's recipes_links using --from-recipe-id.
    """
    recipe = models.Recipes.objects.create(
        name="Lentejas con Verduras Test",
        food_types=models.FoodTypes.objects.first(),
        obsolete=False,
        user=self.user_authorized_1,
        guests=False,
        soon=False,
    )

    models.RecipesLinks.objects.create(
        datetime=timezone.now(),
        description="Enlace de receta",
        type=models.RecipesLinksTypes.objects.get(pk=3),
        link="https://example.com/lentejas",
        recipes=recipe,
    )

    mock_recipe_json = {
        "name": "Lentejas con Verduras Test",
        "comment": "Guiso tradicional",
        "food_type": "Legumes",
        "categories": ["Legumes"],
        "diners": 4,
        "ingredients": [
            {
                "name": "Lentejas pardinas test",
                "amount": 300,
                "unit": "g",
                "comment": "lavadas",
            }
        ],
        "steps": "Cocer las Lentejas pardinas test a fuego lento.",
    }

    with patch.object(RecipeTextExtractor, "extract_from_url", return_value=("Texto lentejas", "Lentejas")):
        with patch.object(OllamaClient, "generate", return_value=mock_recipe_json):
            call_command(
                "import_recipe",
                from_recipe_id=recipe.id,
                username="authorized_1",
            )

    recipe.refresh_from_db()
    self.assertEqual(recipe.elaborations.count(), 1)
    elaboration = recipe.elaborations.first()
    self.assertEqual(elaboration.diners, 4)


def test_youtube_helper_and_main_photo(self):
    """
    Test YouTube URL parsing and automatic thumbnail extraction as Main Photo.
    """
    # Test ID extraction
    yt_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    video_id = YouTubeHelper.get_video_id(yt_url)
    self.assertEqual(video_id, "dQw4w9WgXcQ")

    short_url = "https://youtu.be/dQw4w9WgXcQ"
    self.assertEqual(YouTubeHelper.get_video_id(short_url), "dQw4w9WgXcQ")

    importer = RecipeImporter()
    mock_recipe_data = {
        "name": "Paella Valenciana Video Test",
        "comment": "Receta en video",
        "food_type": "Homemade food",
        "categories": ["Rice"],
        "diners": 4,
        "ingredients": [],
        "steps": "Seguir pasos del video",
    }

    mock_image_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 2000

    with patch.object(YouTubeHelper, "fetch_thumbnail", return_value=(mock_image_bytes, "image/jpeg")):
        recipe = importer.save_recipe(
            recipe_data=mock_recipe_data,
            user=self.user_authorized_1,
            source_url=yt_url,
        )

    # Should have 2 links: Video link (pk=1) and Main photo (pk=7)
    self.assertEqual(recipe.recipes_links.count(), 2)

    video_link = recipe.recipes_links.filter(link=yt_url).first()
    self.assertIsNotNone(video_link)
    self.assertEqual(video_link.type.id, 1)

    photo_link = recipe.recipes_links.filter(type__id=models.eRecipeLink.MainPhoto).first()
    self.assertIsNotNone(photo_link)
    self.assertIsNotNone(photo_link.files)
    self.assertEqual(bytes(photo_link.files.content), mock_image_bytes)


def test_youtube_full_data_and_audio_extraction(self):
    """
    Test extraction of full YouTube context (metadata, transcripts, audio) and passing to Ollama.
    """
    # Test clean_vtt helper
    vtt_sample = (
        "WEBVTT\n"
        "Kind: captions\n"
        "Language: es\n\n"
        "00:00:01.000 --> 00:00:04.000\n"
        "<c>Bienvenidos</c> a la receta de paella\n\n"
        "00:00:04.000 --> 00:00:07.000\n"
        "Añadimos 400 gramos de arroz\n"
    )
    cleaned = YouTubeHelper.clean_vtt(vtt_sample)
    self.assertEqual(cleaned, "Bienvenidos a la receta de paella Añadimos 400 gramos de arroz")

    # Test import_recipe workflow with YouTube data and audio
    importer = RecipeImporter()
    mock_yt_data = {
        "title": "Receta Paella Marinera",
        "description": "Ingredientes y pasos de la paella marinera",
        "transcript": "Bienvenidos a la receta de paella. Añadimos 400 gramos de arroz y marisco.",
        "combined_text": "Title: Receta Paella Marinera\n\nDescription:\nIngredientes...\n\nTranscript:\nBienvenidos...",
        "audio_base64": "bW9ja19hdWRpb19kYXRh",
    }
    mock_recipe_json = {
        "name": "Paella Marinera YouTube",
        "comment": "Paella marinera tradicional con marisco",
        "food_type": "Fish",
        "categories": ["Rice", "Fish"],
        "diners": 4,
        "ingredients": [
            {
                "name": "Arroz bomba test",
                "amount": 400,
                "unit": "g",
                "comment": "para paella",
            }
        ],
        "steps": "1. Sofreír marisco.\n2. Añadir arroz y caldo.",
    }

    with patch.object(YouTubeHelper, "extract_full_youtube_data", return_value=mock_yt_data):
        with patch.object(YouTubeHelper, "fetch_thumbnail", return_value=(b"thumbnail_bytes", "image/jpeg")):
            with patch.object(importer.client, "generate", return_value=mock_recipe_json) as mock_generate:
                recipe, elaboration = importer.import_recipe(
                    url="https://www.youtube.com/watch?v=mockvideoid",
                    user=self.user_authorized_1,
                )

                # Verify audio_base64 was forwarded to OllamaClient
                mock_generate.assert_called_once()
                call_kwargs = mock_generate.call_args[1]
                self.assertEqual(call_kwargs.get("audio_base64"), "bW9ja19hdWRpb19kYXRh")

    self.assertIsNotNone(recipe)
    self.assertIn("Paella Marinera YouTube", recipe.name)
    self.assertTrue("Generado por IA" in recipe.name or "Generated by AI" in recipe.name)
    self.assertIsNotNone(elaboration)
    self.assertFalse(elaboration.automatic)


def test_recipe_import_with_custom_locale(self):
    """
    Test recipe importing and management command with custom locale options ('en' and 'es').
    """
    mock_recipe_json = {
        "name": "Apple Pie Test",
        "comment": "Classic homemade dessert",
        "food_type": "Dessert",
        "categories": ["Dessert"],
        "diners": 6,
        "ingredients": [],
        "steps": "1. Bake apple pie.",
    }

    with patch.object(RecipeTextExtractor, "extract_from_url", return_value=("Apple pie recipe text", "Apple Pie")):
        with patch.object(OllamaClient, "generate", return_value=mock_recipe_json):
            call_command(
                "import_recipe",
                url="https://example.com/apple-pie",
                username="authorized_1",
                locale="en",
            )

    recipe = models.Recipes.objects.filter(name__icontains="Apple Pie Test").first()
    self.assertIsNotNone(recipe)
    self.assertIn("Generated by AI", recipe.name)


def test_recipe_importer_only_matches_target_user_products(self):
    """
    Test that recipe ingredient product resolution strictly checks the target user's products,
    and never links products belonging to another user.
    """
    importer = RecipeImporter()

    # Product owned by user_authorized_1
    prod_user1 = models.Products.objects.create(
        name="Harina de trigo user1",
        amount=Decimal("100.000"),
        calories=Decimal("350.000"),
        food_types=models.FoodTypes.objects.first(),
        glutenfree=False,
        obsolete=False,
        user=self.user_authorized_1,
    )

    # Product owned by user_authorized_2 with same/similar ingredient name
    prod_user2 = models.Products.objects.create(
        name="Leche entera user2",
        amount=Decimal("100.000"),
        calories=Decimal("60.000"),
        food_types=models.FoodTypes.objects.first(),
        glutenfree=False,
        obsolete=False,
        user=self.user_authorized_2,
    )

    recipe = models.Recipes.objects.create(
        name="Bizcocho Test",
        food_types=models.FoodTypes.objects.first(),
        obsolete=False,
        user=self.user_authorized_1,
        guests=False,
        soon=False,
    )

    recipe_data = {
        "name": "Bizcocho Test",
        "diners": 4,
        "ingredients": [
            {
                "name": "Harina de trigo user1",
                "amount": 250,
                "unit": "g",
            },
            {
                "name": "Leche entera user2",
                "amount": 200,
                "unit": "ml",
            },
            {
                "name": "Azúcar no existente",
                "amount": 100,
                "unit": "g",
            },
        ],
        "steps": "Mezclar ingredientes y hornear.",
    }

    # When user_authorized_1 creates elaboration:
    # 1. "Harina de trigo user1" should be added (exists for user1)
    # 2. "Leche entera user2" should NOT be added (exists only for user2, not user1)
    # 3. "Azúcar no existente" should NOT be added (does not exist for anyone)
    elaboration = importer.create_automatic_elaboration(
        recipe=recipe,
        recipe_data=recipe_data,
        user=self.user_authorized_1,
    )

    through_items = models.ElaborationsProductsInThrough.objects.filter(elaborations=elaboration)
    self.assertEqual(through_items.count(), 1)
    self.assertEqual(through_items.first().products, prod_user1)
    self.assertFalse(through_items.filter(products=prod_user2).exists())


def test_recipe_import_atomic_rollback_on_failure(self):
    """
    Test that import_recipe is atomic: if an exception occurs during elaboration creation,
    all previously inserted objects (Recipe, RecipesLinks, Files) are rolled back.
    """
    importer = RecipeImporter()
    mock_recipe_json = {
        "name": "Receta Fallida Rollback Test",
        "comment": "Prueba de atomicidad",
        "food_type": "Dessert",
        "categories": ["Dessert"],
        "diners": 4,
        "ingredients": [],
        "steps": "Paso 1.",
    }

    initial_recipes_count = models.Recipes.objects.count()
    initial_links_count = models.RecipesLinks.objects.count()

    with patch.object(RecipeTextExtractor, "extract_from_url", return_value=("Texto receta", "Receta")):
        with patch.object(importer.client, "generate", return_value=mock_recipe_json):
            # Mock create_automatic_elaboration to simulate unexpected error after recipe and links were created
            with patch.object(
                importer,
                "create_automatic_elaboration",
                side_effect=RuntimeError("Simulated database failure during elaboration"),
            ):
                with self.assertRaises(RuntimeError):
                    importer.import_recipe(
                        url="https://example.com/rollback-test",
                        user=self.user_authorized_1,
                    )

    # Verify atomic rollback: no Recipe or RecipesLinks remain in the database
    self.assertEqual(models.Recipes.objects.count(), initial_recipes_count)
    self.assertEqual(models.RecipesLinks.objects.count(), initial_links_count)
    self.assertFalse(models.Recipes.objects.filter(name__icontains="Receta Fallida Rollback Test").exists())


def test_product_matcher_heuristics(self):
    """
    Test ProductMatcher confidence calculations, modifier conflict detection, and false positive prevention.
    """
    # 1. Exact and normalized matches
    score_exact = ProductMatcher.calculate_confidence("Pechuga de pollo", "Pechuga de pollo")
    self.assertEqual(score_exact, 1.0)

    score_norm = ProductMatcher.calculate_confidence("Aceite de oliva virgen extra", "aceite de oliva vírgen extra")
    self.assertGreaterEqual(score_norm, 0.98)

    score_plural = ProductMatcher.calculate_confidence("Huevos frescos", "Huevo")
    self.assertGreaterEqual(score_plural, 0.90)

    # 2. Conflicting modifiers must produce score 0.0
    score_conflict_oil = ProductMatcher.calculate_confidence("Aceite de oliva", "Aceite de girasol")
    self.assertEqual(score_conflict_oil, 0.0)

    score_conflict_wine = ProductMatcher.calculate_confidence("Vino blanco", "Vino tinto")
    self.assertEqual(score_conflict_wine, 0.0)

    score_conflict_milk = ProductMatcher.calculate_confidence("Leche desnatada", "Leche entera")
    self.assertEqual(score_conflict_milk, 0.0)

    score_conflict_flour = ProductMatcher.calculate_confidence("Harina de trigo", "Harina de avena")
    self.assertEqual(score_conflict_flour, 0.0)

    # 3. Substrings with low similarity must be rejected (score < get_confidence_threshold())
    threshold = ProductMatcher.get_confidence_threshold()
    self.assertEqual(threshold, 0.75)

    score_sal = ProductMatcher.calculate_confidence("Sal", "Salmón")
    self.assertLess(score_sal, threshold)

    score_ajo = ProductMatcher.calculate_confidence("Ajo", "Majo")
    self.assertLess(score_ajo, threshold)

    # 4. find_best_product with setting threshold
    mock_prod = MagicMock()
    mock_prod.name = "Pechuga de pollo"
    found_prod, conf = ProductMatcher.find_best_product("Pechuga de pollo", [mock_prod])
    self.assertEqual(found_prod, mock_prod)
    self.assertGreaterEqual(conf, 0.75)







