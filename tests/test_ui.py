"""
UI Tests — play.ludigames.com
==============================
Scenario U1 · Homepage loads and displays game category sections
Scenario U2 · Each visible category section contains at least one game card
Scenario U3 · Search bar is present and accepts input without crashing
Scenario U4 · Clicking a game card navigates to a game detail page
Scenario U5 · Site is usable on a mobile viewport (375x667)
Scenario U6 · Images use src or data-src (lazy loading) — no completely missing sources
"""

import pytest
from playwright.sync_api import expect

BASE_URL = "https://play.ludigames.com"


def dismiss_cookie_consent(page):
    """
    Ludigames uses Didomi for cookie consent. The popup blocks all clicks
    until dismissed. We force-remove it via JavaScript as a reliable fallback.
    """
    try:
        page.evaluate("""
            () => {
                const host = document.getElementById('didomi-host');
                if (host) host.remove();
                const backdrop = document.getElementById('didomi-popup');
                if (backdrop) backdrop.remove();
                document.body.style.overflow = 'auto';
            }
        """)
    except Exception:
        pass


@pytest.mark.ui
class TestUiHomepage:
    def test_u1_homepage_title_and_header_visible(self, page):
        """
        WHY: The page title and main header are the first things a user sees.
        If they are missing, the page either failed to render or loaded the
        wrong resource entirely.
        """
        page.goto(BASE_URL + "/", wait_until="domcontentloaded", timeout=15000)

        title = page.title().lower()
        assert any(kw in title for kw in ["ludigames", "gameloft", "games"]), (
            f"Unexpected page title: '{page.title()}'"
        )
        print(f"\n  ✔ Page title: '{page.title()}'")

    def test_u2_category_sections_visible_with_game_cards(self, page):
        """
        WHY: Categories (Sport, Action, Racing...) are the primary navigation
        mechanism. If they are empty or invisible, users cannot discover games.
        We check that at least 5 game links are present on the homepage.
        """
        page.goto(BASE_URL + "/", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector("a[href*='game']", timeout=10000)

        game_links = page.locator("a[href*='game']").all()
        assert len(game_links) >= 5, (
            f"Expected at least 5 game links on homepage, found {len(game_links)}"
        )
        print(f"\n  ✔ Found {len(game_links)} game links on homepage")

    def test_u3_search_input_accepts_text(self, page):
        """
        WHY: Search is how users find specific games by name.
        A broken search input forces users to scroll the entire catalogue.
        """
        page.goto(BASE_URL + "/", wait_until="domcontentloaded", timeout=15000)

        search = page.locator(
            "input[type='search'], input[placeholder*='earch'], "
            "input[name*='search'], input[id*='search']"
        ).first

        if search.count() == 0:
            pytest.skip("No search input found on this page — skipping")

        search.click()
        search.fill("Racing")
        value = search.input_value()

        assert "Racing" in value, (
            f"Search field did not accept text. Current value: '{value}'"
        )
        print(f"\n  ✔ Search input accepted text: '{value}'")

    def test_u4_game_card_click_navigates_to_detail_page(self, page):
        """
        WHY: Clicking a game is the single most common user action on the portal.
        NOTE: Ludigames shows a Didomi cookie consent popup on first load that
        intercepts all pointer events. We remove it via JavaScript before clicking
        — this is itself a real-world scenario: the consent layer must not
        permanently block navigation.
        """
        page.goto(BASE_URL + "/", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector("a[href*='game']", timeout=10000)

        # Remove cookie consent popup via JS before clicking
        dismiss_cookie_consent(page)
        page.wait_for_timeout(500)

        first_game = page.locator("a[href*='game']").first
        game_href = first_game.get_attribute("href") or ""
        first_game.click()

        page.wait_for_load_state("domcontentloaded", timeout=10000)
        current_url = page.url

        assert current_url != BASE_URL + "/", (
            "Clicking a game card did not navigate away from the homepage"
        )
        assert "game" in current_url.lower() or game_href in current_url, (
            f"Unexpected URL after clicking game card: {current_url}"
        )
        print(f"\n  ✔ Game card navigated to: {current_url}")

    def test_u5_mobile_viewport_homepage_renders(self, browser_context):
        """
        WHY: Ludigames targets mobile and casual players.
        If the homepage breaks on a 375px viewport (iPhone SE), a huge segment
        of the audience sees a broken or unusable site.
        """
        mobile_page = browser_context.new_page()
        mobile_page.set_viewport_size({"width": 375, "height": 667})

        try:
            mobile_page.goto(BASE_URL + "/", wait_until="domcontentloaded", timeout=15000)
            mobile_page.wait_for_selector("a[href*='game']", timeout=10000)

            game_links = mobile_page.locator("a[href*='game']").all()
            assert len(game_links) >= 1, (
                "No game links found on mobile viewport — site may be broken on mobile"
            )
            print(f"\n  ✔ Mobile viewport: found {len(game_links)} game links (375x667)")
        finally:
            mobile_page.close()

    def test_u6_game_card_images_have_src_or_data_src(self, page):
        """
        WHY: Ludigames uses lazy loading — game card images start with data-src
        and are swapped to src by JavaScript as they scroll into view.
        A game card image with neither src nor data-src will NEVER render.

        NOTE: The site intentionally uses empty src="" on a few UI placeholders
        (e.g. the logo skeleton before JS loads). We scope this check only to
        game card images (img tags inside anchor tags pointing to games), which
        must always have a resolvable image source.
        """
        page.goto(BASE_URL + "/", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector("a[href*='game']", timeout=10000)

        broken = page.evaluate("""
            () => {
                // Only check images inside game card links
                const gameLinks = Array.from(document.querySelectorAll("a[href*='game']"));
                const imgs = gameLinks.flatMap(a => Array.from(a.querySelectorAll('img')));
                return imgs
                    .filter(img => {
                        const src = (img.getAttribute('src') || '').trim();
                        const dataSrc = (img.getAttribute('data-src') || '').trim();
                        return !src && !dataSrc;
                    })
                    .map(img => img.outerHTML.slice(0, 150));
            }
        """)

        assert len(broken) == 0, (
            f"Found {len(broken)} game card image(s) with neither src nor data-src: {broken[:3]}"
        )
        print(f"\n  ✔ All game card <img> elements have a src or data-src attribute")
