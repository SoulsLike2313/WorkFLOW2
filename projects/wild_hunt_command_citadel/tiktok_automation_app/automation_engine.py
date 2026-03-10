from __future__ import annotations

import asyncio
import json
import random
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

from playwright.async_api import Browser, Locator, Page, async_playwright

from settings import BotSettings

LogFn = Callable[[str], None]


class TikTokAutomationEngine:
    def __init__(self, settings: BotSettings, stop_event: threading.Event, logger: LogFn):
        self.settings = settings.normalized()
        self.stop_event = stop_event
        self.log = logger
        self.stats_path = self.settings.output_dir / "session_stats.jsonl"
        self.events_path = self.settings.output_dir / "session_events.jsonl"
        self.diagnostics_path = self.settings.output_dir / "selector_diagnostics.jsonl"
        self._stop_logged = False

    @property
    def action_timeout_ms(self) -> int:
        return int(self.settings.action_timeout_seconds * 1000)

    async def run(self) -> None:
        self.settings.output_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"Подключение к CDP: {self.settings.cdp_url}")

        async with async_playwright() as playwright:
            browser = await self._connect_browser(playwright)
            try:
                page = await self._get_or_create_page(browser)
                await self._ensure_tiktok_open(page)

                if self.settings.health_check_enabled:
                    health_ok = await self._run_health_check(page)
                    if not health_ok and self.settings.strict_health_check:
                        self.log("Контракт остановлен: health-check профиля не пройден.")
                        return

                if self.settings.watch_enabled:
                    await self.watch_feed(page)

                if self.settings.comment_enabled:
                    await self.write_comments(page)

                if self.settings.visit_profiles_enabled:
                    await self.visit_profiles(page)

                if self.settings.upload_enabled:
                    await self.upload_video(page)

                if self.settings.monitor_enabled:
                    await self.monitor_profile(page)
            finally:
                await browser.close()
                self.log("CDP-сессия закрыта.")

    async def _connect_browser(self, playwright) -> Browser:
        last_error: Exception | None = None
        for attempt in range(1, self.settings.retry_attempts + 1):
            if self._should_stop():
                raise RuntimeError("Остановка по запросу пользователя.")
            try:
                return await playwright.chromium.connect_over_cdp(
                    self.settings.cdp_url,
                    timeout=self.action_timeout_ms,
                )
            except Exception as error:
                last_error = error
                self.log(f"Ошибка подключения к CDP (попытка {attempt}/{self.settings.retry_attempts}): {error}")
                if attempt < self.settings.retry_attempts:
                    await self._sleep_with_stop(1.3 * attempt)
        raise RuntimeError(f"Не удалось подключиться к CDP: {last_error}")

    async def _get_or_create_page(self, browser: Browser) -> Page:
        if browser.contexts:
            context = browser.contexts[0]
        else:
            context = await browser.new_context()

        if context.pages:
            page = context.pages[0]
            self.log("Использую уже открытую вкладку профиля.")
            return page

        self.log("Открытой вкладки не было, создаю новую.")
        return await context.new_page()

    async def _ensure_tiktok_open(self, page: Page) -> None:
        current_url = page.url or ""
        if "tiktok.com" in current_url:
            return
        self.log("Открываю TikTok.")
        await self._goto_with_retry(page, "https://www.tiktok.com", context="open_tiktok")
        await self._sleep_with_stop(2.0)

    async def _run_health_check(self, page: Page) -> bool:
        self.log("Health-check профиля...")
        checks: Dict[str, object] = {
            "timestamp": self._timestamp(),
            "event": "health_check",
            "url": page.url,
        }

        try:
            title = await page.title()
        except Exception:
            title = ""
        checks["title"] = title

        checks["is_tiktok"] = "tiktok.com" in (page.url or "")
        checks["title_ok"] = bool(title.strip())

        auth_markers = [
            "[data-e2e='profile-icon']",
            "[data-e2e='nav-profile']",
            "a[href*='@'] img",
        ]
        auth_detected = False
        for selector in auth_markers:
            try:
                if await page.locator(selector).count() > 0:
                    auth_detected = True
                    break
            except Exception:
                continue
        checks["auth_marker"] = auth_detected

        passed = bool(checks["is_tiktok"] and checks["title_ok"])
        checks["passed"] = passed
        self._append_jsonl(self.events_path, checks)
        if passed:
            self.log("Health-check пройден.")
        else:
            self.log("Health-check выявил проблемы. Смотри session_events.jsonl.")
        return passed

    async def watch_feed(self, page: Page) -> None:
        self.log(f"Сценарий: просмотр {self.settings.watch_videos} видео.")
        await self._goto_with_retry(page, self.settings.for_you_url, context="watch_feed_open")
        await self._sleep_with_stop(3.0)

        for index in range(self.settings.watch_videos):
            if self._should_stop():
                return

            entry = {
                "event": "watch_feed",
                "index": index + 1,
                "timestamp": self._timestamp(),
                "url": page.url,
            }

            if self.settings.collect_stats_enabled:
                stats = await self._extract_video_stats(page)
                entry["video_stats"] = stats
                self._append_jsonl(self.stats_path, stats)
                self.log(
                    f"[Лента {index + 1}] {stats.get('author', '-')}, "
                    f"лайки: {stats.get('likes', '-')}, комменты: {stats.get('comments', '-')}"
                )
            else:
                self.log(f"[Лента {index + 1}] просмотр.")

            self._append_jsonl(self.events_path, entry)
            try:
                await page.keyboard.press("PageDown")
            except Exception as error:
                await self._record_selector_diagnostic(
                    context="watch_feed_scroll",
                    selectors=["keyboard:PageDown"],
                    page=page,
                    error=error,
                )
            await self._random_delay()

    async def write_comments(self, page: Page) -> None:
        max_comments = min(self.settings.max_comments, len(self.settings.comments))
        if max_comments <= 0:
            self.log("Комментарии пропущены: нет текста или лимит = 0.")
            return

        self.log(f"Сценарий: комментарии, максимум {max_comments}.")
        if "/video/" not in page.url:
            await self._open_video_from_feed(page)
        await self._sleep_with_stop(1.8)

        for index, comment in enumerate(self.settings.comments[:max_comments]):
            if self._should_stop():
                return

            success = await self._submit_comment(page, comment)
            self._append_jsonl(
                self.events_path,
                {
                    "event": "comment",
                    "timestamp": self._timestamp(),
                    "index": index + 1,
                    "comment": comment,
                    "success": success,
                    "url": page.url,
                },
            )
            if success:
                self.log(f"[Комментарий {index + 1}] отправлен.")
            else:
                self.log(f"[Комментарий {index + 1}] не удалось отправить (селекторы/доступ).")
            await self._random_delay()

    async def visit_profiles(self, page: Page) -> None:
        limit = min(self.settings.max_profiles_to_visit, len(self.settings.profiles))
        if limit <= 0:
            self.log("Переходы по профилям пропущены: список пуст.")
            return

        self.log(f"Сценарий: переход по {limit} профилям.")
        for index, raw_url in enumerate(self.settings.profiles[:limit]):
            if self._should_stop():
                return

            target = self._normalize_profile_url(raw_url)
            await self._goto_with_retry(page, target, context="visit_profile")
            self._append_jsonl(
                self.events_path,
                {
                    "event": "visit_profile",
                    "timestamp": self._timestamp(),
                    "index": index + 1,
                    "profile_url": target,
                },
            )
            self.log(f"[Профиль {index + 1}] {target}")
            await self._random_delay()

    async def upload_video(self, page: Page) -> None:
        upload_file = Path(self.settings.upload_file)
        if not upload_file.exists():
            self.log(f"Загрузка пропущена: файл не найден {upload_file}")
            return

        self.log("Сценарий: загрузка видео.")
        await self._goto_with_retry(page, "https://www.tiktok.com/upload?lang=en", context="upload_open")
        await self._sleep_with_stop(3.0)

        selectors = ["input[type='file']", "input[accept*='video']"]
        file_input, selected = await self._find_first_selector(page, selectors, context="upload_file_input")
        if file_input is None:
            self.log("Не найден input[type=file]. Проверь страницу загрузки в авторизованном профиле.")
            return

        try:
            await file_input.set_input_files(str(upload_file), timeout=self.action_timeout_ms)
        except Exception as error:
            await self._record_selector_diagnostic("upload_set_file", [selected], page, error)
            self.log("Не удалось указать файл для загрузки.")
            return

        self.log(f"Видео выбрано: {upload_file}")
        await self._sleep_with_stop(5.0)

        if self.settings.upload_caption:
            await self._fill_caption(page, self.settings.upload_caption)
            self.log("Описание для видео заполнено.")

        if self.settings.publish_upload:
            success = await self._click_first(
                page,
                [
                    "button[data-e2e='post-video-button']",
                    "button:has-text('Post')",
                    "button:has-text('Опубликовать')",
                ],
                context="upload_publish",
            )
            self.log("Видео отправлено на публикацию." if success else "Кнопка публикации не найдена.")
        else:
            self.log("Видео подготовлено. Автопубликация выключена.")

        self._append_jsonl(
            self.events_path,
            {
                "event": "upload",
                "timestamp": self._timestamp(),
                "file": str(upload_file),
                "caption": self.settings.upload_caption,
                "publish": self.settings.publish_upload,
            },
        )

    async def monitor_profile(self, page: Page) -> None:
        profile_url = self._normalize_profile_url(self.settings.profile_url)
        if not profile_url:
            self.log("Мониторинг профиля пропущен: не указан profile_url.")
            return

        self.log(f"Сценарий: мониторинг профиля {profile_url}")
        await self._goto_with_retry(page, profile_url, context="monitor_profile_open")
        await self._sleep_with_stop(2.0)

        metrics = {
            "event": "profile_metrics",
            "timestamp": self._timestamp(),
            "profile_url": profile_url,
            "followers": await self._text_or_none(page, "[data-e2e='followers-count']"),
            "following": await self._text_or_none(page, "[data-e2e='following-count']"),
            "likes": await self._text_or_none(page, "[data-e2e='likes-count']"),
        }

        posts = await self._safe_eval(
            page,
            """
            () => {
              const links = Array.from(document.querySelectorAll("a[href*='/video/']")).slice(0, 12);
              return links.map((a) => {
                const views = a.querySelector("strong")?.innerText || null;
                return { url: a.href, views };
              });
            }
            """,
            fallback=[],
            context="monitor_profile_posts",
        )
        metrics["posts"] = posts

        self._append_jsonl(self.stats_path, metrics)
        self._append_jsonl(self.events_path, metrics)
        self.log(
            f"Метрики профиля: подписчики={metrics.get('followers', '-')}, "
            f"лайки={metrics.get('likes', '-')}, постов={len(posts)}"
        )

    async def _goto_with_retry(self, page: Page, url: str, context: str) -> None:
        last_error: Exception | None = None
        for attempt in range(1, self.settings.retry_attempts + 1):
            if self._should_stop():
                return
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=self.action_timeout_ms)
                return
            except Exception as error:
                last_error = error
                self.log(
                    f"Навигация не удалась ({context}) "
                    f"попытка {attempt}/{self.settings.retry_attempts}: {error}"
                )
                await self._record_selector_diagnostic(context, [url], page, error)
                if attempt < self.settings.retry_attempts:
                    await self._sleep_with_stop(1.0 * attempt)
        raise RuntimeError(f"Навигация не удалась ({context}): {last_error}")

    async def _open_video_from_feed(self, page: Page) -> None:
        candidates = [
            "a[href*='/video/']",
            "[data-e2e='recommend-list-item-container'] a",
        ]
        for _attempt in range(self.settings.retry_attempts):
            locator, _ = await self._find_first_selector(page, candidates, context="open_video_from_feed")
            if locator is None:
                await self._sleep_with_stop(1.0)
                continue
            try:
                await locator.click(timeout=self.action_timeout_ms)
                await self._sleep_with_stop(1.4)
                if "/video/" in page.url:
                    return
            except Exception as error:
                await self._record_selector_diagnostic("open_video_from_feed_click", candidates, page, error)
        self.log("Не удалось открыть видео из ленты.")

    async def _submit_comment(self, page: Page, comment: str) -> bool:
        input_selectors = [
            "div[data-e2e='comment-input'] [contenteditable='true']",
            "div[data-e2e='comment-input'] div[contenteditable='true']",
            "textarea[placeholder*='comment']",
            "textarea[placeholder*='комментарий']",
        ]
        field, selected = await self._find_first_selector(page, input_selectors, context="comment_input")
        if field is None:
            return False

        try:
            await field.click(timeout=self.action_timeout_ms)
            await field.press("Control+A")
            await field.press("Backspace")
            await field.type(comment, delay=35, timeout=self.action_timeout_ms)
        except Exception as error:
            await self._record_selector_diagnostic("comment_type", [selected], page, error)
            return False

        return await self._click_first(
            page,
            [
                "button[data-e2e='comment-post']",
                "button:has-text('Post')",
                "button:has-text('Опубликовать')",
            ],
            context="comment_submit",
        )

    async def _fill_caption(self, page: Page, caption: str) -> None:
        selectors = [
            "[data-e2e='video-caption'] [contenteditable='true']",
            "textarea[placeholder*='Describe']",
            "textarea[maxlength]",
        ]
        field, selected = await self._find_first_selector(page, selectors, context="upload_caption")
        if field is None:
            self.log("Поле описания не найдено.")
            return

        try:
            await field.click(timeout=self.action_timeout_ms)
            await field.press("Control+A")
            await field.press("Backspace")
            await field.type(caption, delay=25, timeout=self.action_timeout_ms)
        except Exception as error:
            await self._record_selector_diagnostic("upload_caption_type", [selected], page, error)

    async def _extract_video_stats(self, page: Page) -> Dict[str, Optional[str]]:
        return {
            "timestamp": self._timestamp(),
            "url": page.url,
            "author": await self._text_or_none(page, "[data-e2e='video-author-uniqueid']"),
            "description": await self._text_or_none(page, "[data-e2e='browse-video-desc']"),
            "likes": await self._text_or_none(page, "[data-e2e='like-count']"),
            "comments": await self._text_or_none(page, "[data-e2e='comment-count']"),
            "shares": await self._text_or_none(page, "[data-e2e='share-count']"),
            "saves": await self._text_or_none(page, "[data-e2e='undefined-count']"),
        }

    async def _text_or_none(self, page: Page, selector: str) -> Optional[str]:
        try:
            locator = page.locator(selector).first
            await locator.wait_for(state="visible", timeout=self.settings.selector_timeout_ms)
            text = await locator.inner_text(timeout=self.action_timeout_ms)
            return text.strip() if text else None
        except Exception:
            return None

    async def _click_first(self, page: Page, selectors: Sequence[str], context: str) -> bool:
        for _attempt in range(self.settings.retry_attempts):
            locator, selected = await self._find_first_selector(page, selectors, context=context)
            if locator is None:
                await self._sleep_with_stop(0.8)
                continue
            try:
                await locator.click(timeout=self.action_timeout_ms)
                return True
            except Exception as error:
                await self._record_selector_diagnostic(f"{context}_click", [selected], page, error)
                await self._sleep_with_stop(0.8)
        return False

    async def _find_first_selector(
        self,
        page: Page,
        selectors: Sequence[str],
        context: str,
    ) -> tuple[Locator | None, str]:
        for selector in selectors:
            locator = page.locator(selector).first
            try:
                await locator.wait_for(state="visible", timeout=self.settings.selector_timeout_ms)
                return locator, selector
            except Exception:
                continue
        await self._record_selector_diagnostic(context, selectors, page, None)
        return None, ""

    async def _safe_eval(self, page: Page, script: str, fallback, context: str):
        try:
            return await page.evaluate(script)
        except Exception as error:
            await self._record_selector_diagnostic(context, ["page.evaluate(...)"], page, error)
            return fallback

    async def _record_selector_diagnostic(
        self,
        context: str,
        selectors: Sequence[str],
        page: Page | None,
        error: Exception | None,
    ) -> None:
        payload: Dict[str, object] = {
            "timestamp": self._timestamp(),
            "context": context,
            "selectors": list(selectors),
            "url": page.url if page else None,
        }
        if error:
            payload["error"] = str(error)
        self._append_jsonl(self.diagnostics_path, payload)

    def _append_jsonl(self, path: Path, payload: Dict[str, object]) -> None:
        data = dict(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, ensure_ascii=False) + "\n")

    async def _random_delay(self) -> None:
        value = random.uniform(self.settings.min_delay_seconds, self.settings.max_delay_seconds)
        await self._sleep_with_stop(value)

    async def _sleep_with_stop(self, seconds: float) -> None:
        remaining = float(max(0.0, seconds))
        while remaining > 0:
            if self._should_stop():
                return
            step = min(0.5, remaining)
            await asyncio.sleep(step)
            remaining -= step

    def _normalize_profile_url(self, url: str) -> str:
        text = (url or "").strip()
        if not text:
            return ""
        if text.startswith("@"):
            return f"https://www.tiktok.com/{text}"
        if "tiktok.com" in text:
            if text.startswith("http://") or text.startswith("https://"):
                return text
            return f"https://{text.lstrip('/')}"
        return f"https://www.tiktok.com/@{text.lstrip('@')}"

    def _timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _should_stop(self) -> bool:
        if self.stop_event.is_set():
            if not self._stop_logged:
                self.log("Остановка по запросу пользователя.")
                self._stop_logged = True
            return True
        return False
