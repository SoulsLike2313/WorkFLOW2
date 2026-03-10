from __future__ import annotations

import asyncio
import json
import random
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from playwright.async_api import Browser, Page, async_playwright

from settings import BotSettings

LogFn = Callable[[str], None]


class TikTokAutomationEngine:
    def __init__(self, settings: BotSettings, stop_event: threading.Event, logger: LogFn):
        self.settings = settings.normalized()
        self.stop_event = stop_event
        self.log = logger
        self.stats_path = self.settings.output_dir / "session_stats.jsonl"
        self.events_path = self.settings.output_dir / "session_events.jsonl"

    async def run(self) -> None:
        self.settings.output_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"Подключение к CDP: {self.settings.cdp_url}")

        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(self.settings.cdp_url)
            try:
                page = await self._get_or_create_page(browser)
                await self._ensure_tiktok_open(page)

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
        if "tiktok.com" not in current_url:
            self.log("Открываю TikTok.")
            await page.goto("https://www.tiktok.com", wait_until="domcontentloaded")
            await self._sleep_with_stop(3.0)

    async def watch_feed(self, page: Page) -> None:
        self.log(f"Сценарий: просмотр {self.settings.watch_videos} видео.")
        await page.goto(self.settings.for_you_url, wait_until="domcontentloaded")
        await self._sleep_with_stop(4.0)

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
                self.log(f"[Лента {index + 1}] {stats.get('author', '-')}, лайки: {stats.get('likes', '-')}")
            else:
                self.log(f"[Лента {index + 1}] просмотр.")

            self._append_jsonl(self.events_path, entry)
            await page.keyboard.press("PageDown")
            await self._random_delay()

    async def write_comments(self, page: Page) -> None:
        max_comments = min(self.settings.max_comments, len(self.settings.comments))
        if max_comments <= 0:
            self.log("Комментарии пропущены: нет текста или лимит = 0.")
            return

        self.log(f"Сценарий: комментарии, максимум {max_comments}.")
        if "/video/" not in page.url:
            await self._open_video_from_feed(page)
        await self._sleep_with_stop(2.0)

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
            await page.goto(target, wait_until="domcontentloaded")
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
        await page.goto("https://www.tiktok.com/upload?lang=en", wait_until="domcontentloaded")
        await self._sleep_with_stop(4.0)

        input_selector = "input[type='file']"
        file_input = page.locator(input_selector).first
        if await file_input.count() == 0:
            self.log("Не найден input[type=file]. Проверьте, открыта ли страница загрузки в авторизованном профиле.")
            return

        await file_input.set_input_files(str(upload_file))
        self.log(f"Видео выбрано: {upload_file}")
        await self._sleep_with_stop(6.0)

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
        await page.goto(profile_url, wait_until="domcontentloaded")
        await self._sleep_with_stop(3.0)

        metrics = {
            "event": "profile_metrics",
            "timestamp": self._timestamp(),
            "profile_url": profile_url,
            "followers": await self._text_or_none(page, "[data-e2e='followers-count']"),
            "following": await self._text_or_none(page, "[data-e2e='following-count']"),
            "likes": await self._text_or_none(page, "[data-e2e='likes-count']"),
        }

        posts = await page.evaluate(
            """
            () => {
              const links = Array.from(document.querySelectorAll("a[href*='/video/']")).slice(0, 12);
              return links.map((a) => {
                const views = a.querySelector("strong")?.innerText || null;
                return { url: a.href, views };
              });
            }
            """
        )
        metrics["posts"] = posts

        self._append_jsonl(self.stats_path, metrics)
        self._append_jsonl(self.events_path, metrics)
        self.log(
            f"Метрики профиля: подписчики={metrics.get('followers', '-')}, "
            f"лайки={metrics.get('likes', '-')}, постов={len(posts)}"
        )

    async def _open_video_from_feed(self, page: Page) -> None:
        candidates = [
            "a[href*='/video/']",
            "[data-e2e='recommend-list-item-container'] a",
        ]
        for selector in candidates:
            locator = page.locator(selector).first
            if await locator.count() == 0:
                continue
            try:
                await locator.click(timeout=3000)
                await self._sleep_with_stop(2.0)
                if "/video/" in page.url:
                    return
            except Exception:
                continue

    async def _submit_comment(self, page: Page, comment: str) -> bool:
        input_selectors = [
            "div[data-e2e='comment-input'] [contenteditable='true']",
            "div[data-e2e='comment-input'] div[contenteditable='true']",
            "textarea[placeholder*='comment']",
            "textarea[placeholder*='комментарий']",
        ]

        for selector in input_selectors:
            field = page.locator(selector).first
            if await field.count() == 0:
                continue
            try:
                await field.click()
                await field.fill("")
                await field.type(comment, delay=35)
                posted = await self._click_first(
                    page,
                    [
                        "button[data-e2e='comment-post']",
                        "button:has-text('Post')",
                        "button:has-text('Опубликовать')",
                    ],
                )
                return posted
            except Exception:
                continue

        return False

    async def _fill_caption(self, page: Page, caption: str) -> None:
        selectors = [
            "[data-e2e='video-caption'] [contenteditable='true']",
            "textarea[placeholder*='Describe']",
            "textarea[maxlength]",
        ]
        for selector in selectors:
            field = page.locator(selector).first
            if await field.count() == 0:
                continue
            try:
                await field.click()
                await field.fill("")
                await field.type(caption, delay=25)
                return
            except Exception:
                continue

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
            if await locator.count() == 0:
                return None
            text = await locator.inner_text()
            return text.strip() if text else None
        except Exception:
            return None

    async def _click_first(self, page: Page, selectors: List[str]) -> bool:
        for selector in selectors:
            try:
                button = page.locator(selector).first
                if await button.count() == 0:
                    continue
                await button.click(timeout=3000)
                return True
            except Exception:
                continue
        return False

    def _append_jsonl(self, path: Path, payload: Dict[str, object]) -> None:
        data = dict(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, ensure_ascii=False) + "\n")

    async def _random_delay(self) -> None:
        value = random.uniform(self.settings.min_delay_seconds, self.settings.max_delay_seconds)
        await self._sleep_with_stop(value)

    async def _sleep_with_stop(self, seconds: float) -> None:
        remaining = float(seconds)
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
            self.log("Остановка по запросу пользователя.")
            return True
        return False
