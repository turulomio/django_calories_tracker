"""
Management command and helper services to import recipes and generate automatic
elaborations using a local Ollama LLM instance.
"""

from decimal import Decimal
import base64
from glob import glob
import html
import json
import logging
import mimetypes
import os
from os import path
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone, translation
from django.utils.translation import gettext as _

from calories_tracker import models

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for interacting with local Ollama API.
    """

    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize the Ollama client with base URL and model name.

        :param base_url: Ollama server URL (defaults to settings.OLLAMA_BASE_URL)
        :param model: Model identifier (defaults to settings.OLLAMA_MODEL)
        """
        self.base_url = (base_url or getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or getattr(settings, "OLLAMA_MODEL", "gemma4:e2b")

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        format_json: bool = True,
        audio_base64: str = None,
    ) -> dict | str:
        """
        Send a generation request to the Ollama server.

        :param prompt: User prompt to send to the model.
        :param system_prompt: Optional system prompt to guide LLM behavior.
        :param format_json: If True, request JSON response format from Ollama.
        :param audio_base64: Optional base64 encoded audio track to send to Ollama.
        :return: Parsed JSON dict if format_json is True, otherwise response string.
        :raises RuntimeError: On network error or Ollama execution failure.
        """
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if format_json:
            payload["format"] = "json"
        if audio_base64:
            payload["audio"] = [audio_base64]
            payload["images"] = [audio_base64]

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                raw_response = res_json.get("response", "")
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Error connecting to Ollama at {endpoint}. Ensure Ollama is running and model '{self.model}' is available. Error: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error communicating with Ollama: {e}") from e

        if format_json:
            return self._parse_json_response(raw_response)
        return raw_response

    @staticmethod
    def _parse_json_response(raw_text: str) -> dict:
        """
        Clean and parse a JSON response from the LLM, handling markdown codeblocks.

        :param raw_text: Raw string returned by LLM.
        :return: Parsed dictionary.
        """
        cleaned = raw_text.strip()
        # Remove markdown fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Attempt to extract JSON object between first { and last }
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Could not parse JSON from LLM output: {raw_text}")


class YouTubeHelper:
    """
    Helper for detecting YouTube URLs and fetching video thumbnail images.
    """

    YOUTUBE_REGEX = re.compile(
        r"(?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    )

    @classmethod
    def get_video_id(cls, url: str) -> str | None:
        """
        Extract the 11-character YouTube video ID from a URL if present.

        :param url: URL string to inspect.
        :return: Video ID string or None.
        """
        if not url:
            return None
        match = cls.YOUTUBE_REGEX.search(url)
        return match.group(1) if match else None

    @classmethod
    def fetch_thumbnail(cls, video_id: str) -> tuple[bytes, str] | None:
        """
        Download the highest available resolution thumbnail image for a YouTube video.

        :param video_id: 11-character YouTube video ID.
        :return: Tuple (image_bytes, mime_type) or None if download fails.
        """
        print(f"[YouTube] Descargando snapshot/miniatura para el vídeo '{video_id}'...", flush=True)
        thumbnail_urls = [
            f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/0.jpg",
        ]
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        for thumb_url in thumbnail_urls:
            try:
                req = urllib.request.Request(thumb_url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status == 200:
                        content = resp.read()
                        # Some missing maxresdefault return 1097 byte placeholder; check valid length
                        if len(content) > 1500:
                            print(f"[YouTube] ✓ Snapshot descargado exitosamente ({len(content)} bytes, image/jpeg)", flush=True)
                            return content, "image/jpeg"
            except Exception as e:
                logger.debug("Failed downloading thumbnail from %s: %s", thumb_url, e)
        print(f"[YouTube] ⚠ No se pudo obtener snapshot/miniatura para '{video_id}'", flush=True)
        return None

    @classmethod
    def clean_vtt(cls, vtt_content: str) -> str:
        """
        Strip timing tags and formatting from WebVTT subtitles to get clean plain text.

        :param vtt_content: Raw VTT subtitle content.
        :return: Cleaned subtitle text.
        """
        lines = []
        for line in vtt_content.splitlines():
            line = line.strip()
            if (
                not line
                or line.startswith("WEBVTT")
                or line.startswith("Kind:")
                or line.startswith("Language:")
                or line.startswith("Style:")
                or line.startswith("NOTE")
                or line.startswith("REGION")
                or "-->" in line
                or line.isdigit()
            ):
                continue
            cleaned = re.sub(r"<[^>]+>", "", line).strip()
            if cleaned and (not lines or lines[-1] != cleaned):
                lines.append(cleaned)
        return " ".join(lines)

    @classmethod
    def extract_full_youtube_data(cls, url: str, video_id: str, locale: str = "es") -> dict:
        """
        Extract title, description, spoken subtitles/transcript, and audio track from YouTube using yt-dlp.

        :param url: YouTube video URL.
        :param video_id: 11-character YouTube video ID.
        :param locale: Preferred language code for subtitle extraction (default: "es").
        :return: Dict containing title, description, transcript, combined_text, and base64 audio.
        """
        result = {
            "title": "",
            "description": "",
            "transcript": "",
            "combined_text": "",
            "audio_base64": None,
        }

        ytdlp_bin = shutil.which("yt-dlp")
        tmp_dir = getattr(settings, "TMPDIR", "/tmp")

        if ytdlp_bin:
            # 1. Extract metadata and subtitles/transcripts
            print(f"[YouTube] Extrayendo metadatos y subtítulos con yt-dlp (ID: {video_id})...", flush=True)
            sub_template = f"{tmp_dir}/yt_sub_{video_id}"
            try:
                for f in glob(f"{sub_template}*"):
                    try:
                        os.remove(f)
                    except OSError:
                        pass

                clean_loc = (locale or "es").split("_")[0].lower()
                sub_langs = f"{clean_loc},{clean_loc}-orig,es,en,es-orig,en-orig,es-419"

                proc = subprocess.run(
                    [
                        ytdlp_bin,
                        "--dump-json",
                        "--skip-download",
                        "--write-auto-sub",
                        "--write-sub",
                        "--sub-lang", sub_langs,
                        "--sub-format", "vtt/best",
                        "-o", f"subtitle:{sub_template}",
                        url,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
                if proc.returncode == 0 and proc.stdout:
                    try:
                        meta = json.loads(proc.stdout)
                        result["title"] = meta.get("title", "")
                        result["description"] = meta.get("description", "")
                        print(f"[YouTube] ✓ Título: '{result['title']}'", flush=True)
                    except Exception as e:
                        logger.debug("Failed parsing yt-dlp metadata JSON: %s", e)

                # Check for extracted subtitle files
                sub_files = glob(f"{sub_template}*.vtt")
                if sub_files:
                    try:
                        with open(sub_files[0], "r", encoding="utf-8", errors="replace") as sf:
                            result["transcript"] = cls.clean_vtt(sf.read())
                        print(f"[YouTube] ✓ Subtítulos extraídos ({len(result['transcript'])} caracteres)", flush=True)
                    except Exception as e:
                        logger.debug("Failed reading subtitle file: %s", e)
                    finally:
                        for f in sub_files:
                            try:
                                os.remove(f)
                            except OSError:
                                pass
                else:
                    print("[YouTube] ℹ No se encontraron subtítulos VTT; se usará la descripción", flush=True)
            except Exception as e:
                logger.debug("yt-dlp metadata/subtitle extraction error: %s", e)
                print(f"[YouTube] ⚠ Error extrayendo subtítulos: {e}", flush=True)

            # 2. Extract audio track from video
            print(f"[YouTube] Extrayendo y convirtiendo pista de audio a MP3 con yt-dlp (ID: {video_id})...", flush=True)
            audio_template = f"{tmp_dir}/yt_audio_{video_id}.%(ext)s"
            try:
                for f in glob(f"{tmp_dir}/yt_audio_{video_id}.*"):
                    try:
                        os.remove(f)
                    except OSError:
                        pass

                audio_proc = subprocess.run(
                    [
                        ytdlp_bin,
                        "-x",
                        "--audio-format", "mp3",
                        "--audio-quality", "5",
                        "-o", audio_template,
                        url,
                    ],
                    capture_output=True,
                    timeout=90,
                )
                if audio_proc.returncode == 0:
                    generated_audios = glob(f"{tmp_dir}/yt_audio_{video_id}.*")
                    if generated_audios:
                        with open(generated_audios[0], "rb") as af:
                            audio_bytes = af.read()
                            if audio_bytes:
                                result["audio_base64"] = base64.b64encode(audio_bytes).decode("utf-8")
                                print(f"[YouTube] ✓ Pista de audio convertida y codificada en Base64 ({len(audio_bytes)} bytes)", flush=True)
                        for af_path in generated_audios:
                            try:
                                os.remove(af_path)
                            except OSError:
                                pass
                else:
                    print(f"[YouTube] ⚠ Falló la conversión de audio: {audio_proc.stderr}", flush=True)
            except Exception as e:
                logger.debug("yt-dlp audio extraction error: %s", e)
                print(f"[YouTube] ⚠ Error al extraer pista de audio: {e}", flush=True)

        # Fallback to HTML extraction if title or description are empty
        if not result["title"] or not result["description"]:
            try:
                print("[YouTube] Realizando extracción fallback HTML...", flush=True)
                html_text, html_title = RecipeTextExtractor.extract_from_url(url)
                if not result["title"]:
                    result["title"] = html_title
                if not result["description"]:
                    result["description"] = html_text
            except Exception as e:
                logger.debug("HTML fallback error: %s", e)

        # Combine all gathered information into rich prompt context
        combined = f"Title: {result['title']}\n\nDescription:\n{result['description']}\n"
        if result["transcript"]:
            combined += f"\nVideo Transcript / Spoken Subtitles:\n{result['transcript']}\n"
        result["combined_text"] = combined.strip()

        return result


class RecipeTextExtractor:
    """
    Extracts raw text content from URLs and local documents.
    """

    @staticmethod
    def extract_from_url(url: str) -> tuple[str, str]:
        """
        Fetch HTML from URL and strip tags to get readable plain text.

        :param url: Web page URL to fetch.
        :return: Tuple of (extracted_text, title).
        :raises RuntimeError: If URL cannot be retrieved.
        """
        print(f"[Web] Extrayendo contenido de la URL: {url}...", flush=True)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                html_bytes = response.read()
                html_text = html_bytes.decode(charset, errors="replace")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch content from URL '{url}': {e}") from e

        # Extract title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        # Extract meta description / og:description
        meta_desc = ""
        meta_desc_match = re.search(
            r'<meta\s+(?:name|property)=["\'](?:description|og:description)["\']\s+content=["\'](.*?)["\']',
            html_text,
            re.IGNORECASE | re.DOTALL,
        )
        if not meta_desc_match:
            meta_desc_match = re.search(
                r'<meta\s+content=["\'](.*?)["\']\s+(?:name|property)=["\'](?:description|og:description)["\']',
                html_text,
                re.IGNORECASE | re.DOTALL,
            )
        if meta_desc_match:
            meta_desc = meta_desc_match.group(1).strip()

        # Remove scripts, styles, header, footer, nav
        cleaned = re.sub(r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>", " ", html_text, flags=re.IGNORECASE | re.DOTALL)
        # Strip all HTML tags
        text = re.sub(r"<[^>]+>", " ", cleaned)
        # Unescape HTML entities
        text = html.unescape(text)
        meta_desc = html.unescape(meta_desc)
        title = html.unescape(title)

        if meta_desc:
            text = f"Title: {title}\nDescription: {meta_desc}\n\nContent:\n{text}"

        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        print(f"[Web] ✓ Texto extraído: '{title}' ({len(text)} caracteres)", flush=True)

        return text, title

    @staticmethod
    def extract_from_file(file_path: str) -> tuple[str, bytes, str]:
        """
        Read local document or file content and determine mime type.

        :param file_path: Path to the local file.
        :return: Tuple of (extracted_text, raw_bytes, mime_type).
        :raises FileNotFoundError: If file does not exist.
        :raises RuntimeError: If file cannot be read.
        """
        if not path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        mime_type, _encoding = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        print(f"[Documento] Leyendo archivo local '{file_path}' (MIME: {mime_type})...", flush=True)

        with open(file_path, "rb") as f:
            raw_bytes = f.read()

        text = ""
        # Handle plain text, markdown, html, json
        if mime_type.startswith("text/") or file_path.endswith((".md", ".txt", ".html", ".htm", ".json", ".rst")):
            try:
                text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = raw_bytes.decode("latin-1", errors="replace")
        elif file_path.lower().endswith(".pdf"):
            # Attempt to extract text from PDF if pypdf or PyPDF2 is installed
            try:
                import pypdf
                import io
                reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
            except ImportError:
                # Fallback basic string extraction for ASCII streams
                text = re.sub(r"[^\x20-\x7E\n\r\t]", " ", raw_bytes.decode("latin-1", errors="replace"))
        else:
            # Generic binary fallback string extraction
            text = raw_bytes.decode("utf-8", errors="replace")

        # Collapse whitespace
        text = re.sub(r"[ \t]+", " ", text).strip()
        print(f"[Documento] ✓ Texto extraído ({len(text)} caracteres, {len(raw_bytes)} bytes)", flush=True)
        return text, raw_bytes, mime_type


class RecipeImporter:
    """
    Coordinates LLM parsing, database object creation (Recipes, RecipesLinks,
    RecipesCategories), and automatic elaboration generation.
    """

    MEASURE_MAP = {
        "g": 1,
        "gr": 1,
        "gram": 1,
        "grams": 1,
        "gramo": 1,
        "gramos": 1,
        "kg": 1,  # Will convert amount * 1000
        "kilo": 1,
        "kilos": 1,
        "ml": 2,
        "milliliter": 2,
        "milliliters": 2,
        "mililitro": 2,
        "mililitros": 2,
        "cl": 2,  # Will convert amount * 10
        "l": 2,   # Will convert amount * 1000
        "litro": 2,
        "litros": 2,
        "tbsp": 3,
        "cucharada": 3,
        "cucharadas": 3,
        "cda": 3,
        "table spoon": 3,
        "tablespoon": 3,
        "tsp": 4,
        "cucharadita": 4,
        "cucharaditas": 4,
        "cdita": 4,
        "tea spoon": 4,
        "teaspoon": 4,
        "cup": 5,
        "taza": 5,
        "tazas": 5,
    }

    def __init__(self, ollama_client: OllamaClient = None, locale: str = "es"):
        """
        Initialize the recipe importer.

        :param ollama_client: Optional custom OllamaClient instance.
        :param locale: Default locale/language code for imports and translations (default: "es").
        """
        self.client = ollama_client or OllamaClient()
        self.locale = locale or "es"

    def parse_recipe_with_llm(self, content_text: str, audio_base64: str = None, locale: str = None) -> dict:
        """
        Send recipe text and optional audio to Ollama and obtain structured JSON.

        :param content_text: Plain text extracted from URL, transcript, or document.
        :param audio_base64: Optional base64 encoded audio track.
        :param locale: Optional locale override (defaults to self.locale).
        :return: Parsed dictionary with recipe attributes.
        """
        # Truncate content text if excessively large to stay within context
        truncated_text = content_text[:12000]
        loc = (locale or self.locale or "es").split("_")[0].lower()
        lang_map = {
            "es": "Spanish",
            "en": "English",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
        }
        lang_name = lang_map.get(loc, "Spanish" if loc.startswith("es") else "English")

        print(f"[Ollama] Enviando contenido al LLM (modelo: '{self.client.model}', idioma: {lang_name})...", flush=True)
        if audio_base64:
            print("[Ollama] Adjuntando pista de audio codificada en Base64...", flush=True)

        system_prompt = (
            f"You are a professional culinary assistant. Your task is to analyze the provided text and audio, "
            f"summarize the recipe clearly and concisely in {lang_name}, and extract recipe information into a strict JSON format.\n"
            "Respond ONLY with valid JSON conforming to the requested schema. Do not include markdown formatting outside the JSON."
        )

        existing_categories = list(models.RecipesCategories.objects.values_list("name", flat=True))
        if existing_categories:
            cats_sample = ", ".join(f"'{c}'" for c in existing_categories[:30])
            cats_prompt_line = f"- \"categories\": (array of strings) List of categories chosen ONLY from available ones (e.g. [{cats_sample}]).\n"
        else:
            cats_prompt_line = "- \"categories\": (array of strings) List of suitable recipe categories.\n"

        prompt = (
            f"Analyze the following text, summarize the recipe clearly and concisely in {lang_name}, and extract the recipe information into a single JSON object with these exact keys:\n"
            f"- \"name\": (string) Recipe title in {lang_name}.\n"
            f"- \"comment\": (string) Concise summary or description of the recipe in {lang_name}.\n"
            "- \"food_type\": (string) Main category (e.g., 'Homemade food', 'Meat', 'Fish', 'Vegetables', 'Pasta', 'Bakery', 'Eggs', 'Dessert').\n"
            f"{cats_prompt_line}"
            "- \"diners\": (integer) Number of servings/diners (default 4 if not specified).\n"
            "- \"ingredients\": (array of objects) Each object must have:\n"
            "    - \"name\": (string) Ingredient/Product name.\n"
            "    - \"amount\": (number) Quantity needed.\n"
            "    - \"unit\": (string) Unit of measure ('g', 'ml', 'tbsp', 'tsp', 'cup', 'unit').\n"
            "    - \"comment\": (string) Preparation notes (e.g., 'chopped', 'diced', 'peeled', 'at room temperature').\n"
            f"- \"steps\": (string) Summarized, concise, step-by-step preparation instructions in {lang_name} in Markdown format.\n\n"
            f"Recipe source text:\n{truncated_text}\n"
        )

        result_json = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            format_json=True,
            audio_base64=audio_base64,
        )
        if isinstance(result_json, dict):
            print(f"[Ollama] ✓ Respuesta estructurada recibida: '{result_json.get('name')}' ({len(result_json.get('ingredients', []))} ingredientes)", flush=True)
        return result_json

    @transaction.atomic
    def save_recipe(
        self,
        recipe_data: dict,
        user: User,
        source_url: str = None,
        source_file_info: tuple[str, bytes, str] = None,
        locale: str = None,
    ) -> models.Recipes:
        """
        Persist Recipe, RecipesLinks, and RecipesCategories to database.

        :param recipe_data: Structured recipe data from LLM.
        :param user: Owner user for the recipe.
        :param source_url: Optional source URL for RecipesLinks.
        :param source_file_info: Optional tuple (filename, raw_bytes, mime_type) for RecipesLinks.
        :param locale: Optional locale override for i18n notices.
        :return: Created Recipes model instance.
        """
        loc = locale or self.locale or "es"
        translation.activate(loc)

        # Resolve FoodType
        food_type_name = recipe_data.get("food_type", "Homemade food")
        food_type = (
            models.FoodTypes.objects.filter(name__icontains=food_type_name).first()
            or models.FoodTypes.objects.filter(name__icontains="Homemade food").first()
            or models.FoodTypes.objects.first()
        )

        ai_notice = _("Generated by AI")
        raw_name = recipe_data.get("name", "Receta sin título").strip()
        if f"({ai_notice})" not in raw_name and "(Generated by AI)" not in raw_name and "(Generatated by IA)" not in raw_name and "(Generado por IA)" not in raw_name:
            final_name = f"{raw_name} ({ai_notice})"
        else:
            final_name = raw_name

        print(f"[BD] Guardando receta '{final_name}' (Tipo: {food_type.name})...", flush=True)

        recipe = models.Recipes()
        recipe.name = final_name
        recipe.datetime = timezone.now()
        recipe.food_types = food_type
        recipe.obsolete = False
        recipe.user = user
        recipe.comment = recipe_data.get("comment", "")
        recipe.guests = False
        recipe.soon = False
        recipe.save()
        print(f"[BD] ✓ Receta creada con ID {recipe.id}", flush=True)

        # Handle Categories: only associate existing categories, do not create new ones
        category_names = recipe_data.get("categories", [])
        added_categories = []
        if isinstance(category_names, list):
            for cat_name in category_names:
                if isinstance(cat_name, str) and cat_name.strip():
                    name_clean = cat_name.strip()
                    cat = (
                        models.RecipesCategories.objects.filter(name__iexact=name_clean).first()
                        or models.RecipesCategories.objects.filter(name__icontains=name_clean).first()
                    )
                    if cat:
                        recipe.recipes_categories.add(cat)
                        added_categories.append(cat.name)
                    else:
                        print(f"[BD] ℹ Categoría '{name_clean}' no encontrada en la base de datos (omitida)", flush=True)

        if added_categories:
            print(f"[BD] ✓ Categorías vinculadas: {added_categories}", flush=True)

        # Handle URL Link
        if source_url:
            yt_video_id = YouTubeHelper.get_video_id(source_url)
            if yt_video_id:
                link_type = (
                    models.RecipesLinksTypes.objects.filter(name__icontains="Video link").first()
                    or models.RecipesLinksTypes.objects.get(pk=1)
                )
                rl_desc = f"Vídeo de YouTube: {recipe.name}"
            else:
                link_type = (
                    models.RecipesLinksTypes.objects.filter(name__icontains="Web page link").first()
                    or models.RecipesLinksTypes.objects.get(pk=3)
                )
                rl_desc = f"Fuente web: {recipe.name}"

            rl = models.RecipesLinks()
            rl.datetime = timezone.now()
            rl.description = rl_desc
            rl.type = link_type
            rl.link = source_url
            rl.recipes = recipe
            rl.save()
            print(f"[BD] ✓ Enlace guardado: '{source_url}' ({link_type.name})", flush=True)

            # If origin is YouTube, fetch thumbnail and set as Main Photo
            if yt_video_id:
                thumb_result = YouTubeHelper.fetch_thumbnail(yt_video_id)
                if thumb_result:
                    thumb_bytes, thumb_mime = thumb_result
                    thumb_file = models.Files()
                    thumb_file.content = thumb_bytes
                    thumb_file.size = len(thumb_bytes)
                    thumb_file.mime = thumb_mime
                    thumb_file.user = user
                    thumb_file.save()

                    main_photo_type = (
                        models.RecipesLinksTypes.objects.filter(pk=getattr(models.eRecipeLink, "MainPhoto", 7)).first()
                        or models.RecipesLinksTypes.objects.filter(name__icontains="Main photo").first()
                        or models.RecipesLinksTypes.objects.get(pk=7)
                    )

                    main_rl = models.RecipesLinks()
                    main_rl.datetime = timezone.now()
                    main_rl.description = f"Imagen principal del vídeo: {recipe.name}"
                    main_rl.type = main_photo_type
                    main_rl.files = thumb_file
                    main_rl.recipes = recipe
                    main_rl.save()
                    print(f"[BD] ✓ Snapshot guardado como Main Photo (Files ID: {thumb_file.id})", flush=True)

        # Handle File Link
        if source_file_info:
            file_name, raw_bytes, mime_type = source_file_info
            file_obj = models.Files()
            file_obj.content = raw_bytes
            file_obj.size = len(raw_bytes)
            file_obj.mime = mime_type
            file_obj.user = user
            file_obj.save()

            link_type = (
                models.RecipesLinksTypes.objects.filter(name__icontains="Document file").first()
                or models.RecipesLinksTypes.objects.get(pk=6)
            )
            rl = models.RecipesLinks()
            rl.datetime = timezone.now()
            rl.description = f"Documento: {path.basename(file_name)}"
            rl.type = link_type
            rl.files = file_obj
            rl.recipes = recipe
            rl.save()
            print(f"[BD] ✓ Documento adjunto guardado: '{path.basename(file_name)}' (Files ID: {file_obj.id})", flush=True)

        return recipe

    @transaction.atomic
    def create_automatic_elaboration(
        self,
        recipe: models.Recipes,
        recipe_data: dict,
        user: User,
        locale: str = None,
    ) -> models.Elaborations:
        """
        Create an automatic Elaboration for the recipe with ingredients and text steps.

        :param recipe: The parent Recipes model.
        :param recipe_data: Structured recipe data containing ingredients and steps.
        :param user: User performing the action.
        :param locale: Optional locale override for i18n notices.
        :return: Created Elaborations model instance.
        """
        loc = locale or self.locale or "es"
        translation.activate(loc)

        diners = recipe_data.get("diners", 4)
        try:
            diners = int(diners)
            if diners <= 0:
                diners = 4
        except (ValueError, TypeError):
            diners = 4

        print(f"[Elaboración] Creando elaboración automática ({diners} comensales) para receta ID {recipe.id}...", flush=True)

        elaboration = models.Elaborations()
        elaboration.recipes = recipe
        elaboration.diners = diners
        elaboration.automatic = False
        elaboration.automatic_adaptation_step = ""
        elaboration.save()

        ingredients = recipe_data.get("ingredients", [])
        through_list = []

        print(f"[Elaboración] Procesando {len(ingredients)} ingredientes...", flush=True)

        for ing in ingredients:
            if not isinstance(ing, dict):
                continue

            ing_name = str(ing.get("name", "")).strip()
            if not ing_name or len(ing_name) < 2:
                continue

            # Resolve product - only look up valid, non-empty existing products
            qs_valid = models.Products.objects.filter(obsolete=False).exclude(name__isnull=True).exclude(name__exact="").exclude(name__regex=r"^\s*$")

            # 1. Exact match (case insensitive) for user's own products first, then any non-obsolete product
            product = (
                qs_valid.filter(name__iexact=ing_name, user=user).first()
                or qs_valid.filter(name__iexact=ing_name).first()
            )

            # 2. Substring match fallback: only if ing_name is specific enough (at least 4 chars)
            if not product and len(ing_name) >= 4:
                product = (
                    qs_valid.filter(name__icontains=ing_name, user=user).first()
                    or qs_valid.filter(name__icontains=ing_name).first()
                )

            if not product or not getattr(product, "id", None) or not getattr(product, "name", "").strip():
                # If product is not found in the database, do not add it and do not create placeholder products
                print(f"  - Ingrediente ignorado (no existe producto en BD): '{ing_name}'", flush=True)
                continue

            # Resolve unit & measure type
            unit_str = str(ing.get("unit", "g")).lower().strip()
            measure_id = self.MEASURE_MAP.get(unit_str, 1)

            # Resolve amount
            raw_amount = ing.get("amount", 100)
            try:
                amount_num = float(raw_amount)
                # Handle kg or liter conversions
                if unit_str in ["kg", "kilo", "kilos", "l", "litro", "litros"]:
                    amount_num *= 1000
                elif unit_str in ["cl"]:
                    amount_num *= 10
                amount_dec = Decimal(str(round(amount_num, 3)))
            except (ValueError, TypeError):
                amount_dec = Decimal("100.000")

            comment = str(ing.get("comment", "")).strip()[:100]

            measure_type = models.MeasuresTypes.objects.filter(pk=measure_id).first()
            if not measure_type:
                measure_type = models.MeasuresTypes.objects.get(pk=1)

            pi = models.ElaborationsProductsInThrough()
            pi.elaborations = elaboration
            pi.products = product
            pi.measures_types = measure_type
            pi.amount = amount_dec
            pi.comment = comment if comment else None
            pi.ni = True
            pi.automatic_percentage = 100
            pi.save()
            through_list.append(pi)
            print(f"  + Ingrediente vinculado: '{product.name}' ({amount_dec} {measure_type.name})", flush=True)

        # ElaborationsTexts
        steps_text = recipe_data.get("steps", "")
        if not steps_text:
            steps_text = recipe_data.get("comment", "Preparación según la receta.")

        # Enrich text with ingredient mention spans if ingredient names appear
        for pi in through_list:
            p_name = pi.products.name
            span = models.ElaborationsTexts.span_ingredient(pi.id, pi.fullname())
            # Replace case-insensitively product name with mention span
            pattern = re.compile(re.escape(p_name), re.IGNORECASE)
            steps_text = pattern.sub(span, steps_text, count=1)

        # Append i18n AI notice at the end of the recipe elaboration text
        ai_notice = _("Generated by AI")
        if not steps_text.endswith("\n"):
            steps_text += f"\n\n({ai_notice})"
        else:
            steps_text += f"\n({ai_notice})"

        elaboration_text = models.ElaborationsTexts()
        elaboration_text.elaborations = elaboration
        elaboration_text.text = steps_text
        elaboration_text.save()
        print(f"[Elaboración] ✓ Pasos de elaboración guardados ({len(steps_text)} caracteres)", flush=True)

        return elaboration

    def create_elaboration_from_recipe_links(self, recipe: models.Recipes, user: User, locale: str = None) -> models.Elaborations:
        """
        Generate an automatic elaboration for an existing recipe by reading its associated RecipesLinks.

        :param recipe: The existing Recipe instance.
        :param user: User executing the action.
        :param locale: Optional locale override.
        :return: Created Elaborations model instance.
        """
        loc = locale or self.locale or "es"
        translation.activate(loc)

        combined_text = f"Receta: {recipe.name}\n{recipe.comment or ''}\n"
        audio_base64 = None

        for link in recipe.recipes_links.all():
            if link.link:
                yt_id = YouTubeHelper.get_video_id(link.link)
                if yt_id:
                    try:
                        yt_data = YouTubeHelper.extract_full_youtube_data(link.link, yt_id, locale=loc)
                        combined_text += f"\n--- Contenido de YouTube ({link.link}) ---\n{yt_data['combined_text']}\n"
                        if yt_data.get("audio_base64"):
                            audio_base64 = yt_data["audio_base64"]
                    except Exception as e:
                        logger.warning("Could not extract full YouTube data for %s: %s", link.link, e)
                else:
                    try:
                        url_text, _title = RecipeTextExtractor.extract_from_url(link.link)
                        combined_text += f"\n--- Contenido de enlace {link.link} ---\n{url_text}\n"
                    except Exception as e:
                        logger.warning("Could not extract text from recipe link %s: %s", link.link, e)
            elif link.files and link.files.content:
                try:
                    content_str = bytes(link.files.content).decode("utf-8", errors="replace")
                    combined_text += f"\n--- Contenido de archivo ---\n{content_str}\n"
                except Exception as e:
                    logger.warning("Could not decode file content for recipe %s: %s", recipe.id, e)

        recipe_data = self.parse_recipe_with_llm(combined_text, audio_base64=audio_base64, locale=loc)
        return self.create_automatic_elaboration(recipe, recipe_data, user, locale=loc)

    def import_recipe(
        self,
        url: str = None,
        file_path: str = None,
        user: User = None,
        create_elaboration: bool = True,
        locale: str = None,
    ) -> tuple[models.Recipes, models.Elaborations | None]:
        """
        Full workflow: extracts text from source, queries Ollama LLM,
        creates Recipe, RecipesLinks, RecipesCategories, and automatic Elaboration.

        :param url: URL to scrape recipe from.
        :param file_path: Path to local document file.
        :param user: Owner user for created entities.
        :param create_elaboration: If True, creates automatic Elaboration with ingredients & steps.
        :param locale: Optional locale override (defaults to self.locale).
        :return: Tuple of (created_recipe, created_elaboration).
        :raises ValueError: If neither url nor file_path is provided, or no user available.
        """
        loc = locale or self.locale or "es"
        translation.activate(loc)

        if not url and not file_path:
            raise ValueError("Must provide either a URL or a file path.")

        if not user:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if not user:
                raise ValueError("No user found in database to assign recipe to.")

        source_file_info = None
        audio_base64 = None
        if url:
            yt_id = YouTubeHelper.get_video_id(url)
            if yt_id:
                yt_data = YouTubeHelper.extract_full_youtube_data(url, yt_id, locale=loc)
                extracted_text = yt_data["combined_text"]
                audio_base64 = yt_data.get("audio_base64")
            else:
                extracted_text, _title = RecipeTextExtractor.extract_from_url(url)
        else:
            extracted_text, raw_bytes, mime_type = RecipeTextExtractor.extract_from_file(file_path)
            source_file_info = (file_path, raw_bytes, mime_type)

        # Parse with LLM (passing text and audio when available)
        recipe_data = self.parse_recipe_with_llm(extracted_text, audio_base64=audio_base64, locale=loc)

        # Save Recipe, Categories, Links
        recipe = self.save_recipe(
            recipe_data=recipe_data,
            user=user,
            source_url=url,
            source_file_info=source_file_info,
            locale=loc,
        )

        # Create Elaboration
        elaboration = None
        if create_elaboration:
            elaboration = self.create_automatic_elaboration(recipe, recipe_data, user, locale=loc)

        return recipe, elaboration


class Command(BaseCommand):
    """
    Django management command for recipe importation and automatic elaboration generation.
    """

    help = (
        "Imports a recipe from a URL or local document using local Ollama LLM, "
        "populates Recipes, RecipesLinks, RecipesCategories, and creates an automatic Elaboration."
    )

    def add_arguments(self, parser):
        """
        Register CLI arguments.
        """
        parser.add_argument(
            "--url",
            type=str,
            help="Web page URL containing the recipe to import.",
            default=None,
        )
        parser.add_argument(
            "--document",
            "--file",
            type=str,
            dest="document",
            help="Local document/file path containing the recipe.",
            default=None,
        )
        parser.add_argument(
            "--locale",
            type=str,
            help="Locale/language code for recipe import and translation (e.g., 'es', 'en'). Default is 'es'.",
            default="es",
        )
        parser.add_argument(
            "--user_id",
            type=int,
            help="ID of the User who will own the imported recipe.",
            default=None,
        )
        parser.add_argument(
            "--username",
            type=str,
            help="Username of the User who will own the imported recipe.",
            default=None,
        )
        parser.add_argument(
            "--from-recipe-id",
            type=int,
            dest="from_recipe_id",
            help="ID of an existing recipe to generate an automatic elaboration for, using its recipes_links.",
            default=None,
        )
        parser.add_argument(
            "--no-elaboration",
            action="store_true",
            help="If set, only creates the Recipe and RecipesLinks without creating an automatic Elaboration.",
            default=False,
        )

    def handle(self, *args, **options):
        """
        Execute command logic.
        """
        locale = options.get("locale", "es") or "es"
        current_language = translation.get_language()
        translation.activate(locale)

        try:
            importer = RecipeImporter(locale=locale)

            # Resolve User
            user = None
            if options.get("user_id"):
                try:
                    user = User.objects.get(pk=options["user_id"])
                except User.DoesNotExist:
                    raise CommandError(f"User with ID {options['user_id']} does not exist.")
            elif options.get("username"):
                try:
                    user = User.objects.get(username=options["username"])
                except User.DoesNotExist:
                    raise CommandError(f"User with username '{options['username']}' does not exist.")
            else:
                user = User.objects.filter(is_superuser=True).first() or User.objects.first()
                if not user:
                    raise CommandError("No users exist in the database. Please create a user first.")

            # Mode 1: Create automatic elaboration from existing recipe's recipes_links
            if options.get("from_recipe_id"):
                recipe_id = options["from_recipe_id"]
                try:
                    recipe = models.Recipes.objects.get(pk=recipe_id)
                except models.Recipes.DoesNotExist:
                    raise CommandError(f"Recipe with ID {recipe_id} not found.")

                self.stdout.write(self.style.NOTICE(f"Processing recipe '{recipe.name}' (ID: {recipe.id}) from its recipes_links..."))
                try:
                    elaboration = importer.create_elaboration_from_recipe_links(recipe, user=user, locale=locale)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully created automatic elaboration (ID: {elaboration.id}) for recipe '{recipe.name}' with {elaboration.diners} diners."
                        )
                    )
                except Exception as e:
                    raise CommandError(f"Failed to generate elaboration from recipe links: {e}") from e
                return

            # Mode 2: Import new recipe from URL or document
            url = options.get("url")
            document = options.get("document")

            if not url and not document:
                raise CommandError("You must provide either --url, --document (or --file), or --from-recipe-id.")

            source_desc = f"URL '{url}'" if url else f"file '{document}'"
            self.stdout.write(self.style.NOTICE(f"Importing recipe from {source_desc} using Ollama LLM (locale: {locale})..."))

            try:
                recipe, elaboration = importer.import_recipe(
                    url=url,
                    file_path=document,
                    user=user,
                    create_elaboration=not options.get("no_elaboration"),
                    locale=locale,
                )
            except Exception as e:
                raise CommandError(f"Error importing recipe: {e}") from e

            self.stdout.write(self.style.SUCCESS(f"Successfully created Recipe '{recipe.name}' (ID: {recipe.id})"))
            self.stdout.write(f"  - Food Type: {recipe.food_types.name}")
            self.stdout.write(f"  - Categories: {', '.join([c.name for c in recipe.recipes_categories.all()]) or 'None'}")
            self.stdout.write(f"  - Associated Links: {recipe.recipes_links.count()}")

            if elaboration:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created automatic Elaboration (ID: {elaboration.id}, {elaboration.diners} diners)"
                    )
                )
                pi_count = models.ElaborationsProductsInThrough.objects.filter(elaborations=elaboration).count()
                self.stdout.write(f"  - Ingredients added: {pi_count}")
        finally:
            if current_language:
                translation.activate(current_language)
