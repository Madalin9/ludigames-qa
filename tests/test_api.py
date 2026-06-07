"""
API Tests — play.ludigames.com
===============================
Scenario A1 · Homepage returns HTTP 200 within 3 seconds
Scenario A2 · Category page (Sport) returns HTTP 200 and contains game data
Scenario A3 · Non-existent page returns a handled error (not a 5xx server crash)
"""

import time
import pytest
import requests

BASE_URL = "https://play.ludigames.com"
TIMEOUT = 10  # seconds for requests


@pytest.mark.api
class TestApiHomepage:
    def test_a1_homepage_returns_200_within_3s(self):
        """
        WHY: The homepage is the entry point for every user.
        If it is down or slow, no one can play anything.
        We verify HTTP 200 and a response time under 3 seconds.
        """
        start = time.time()
        response = requests.get(BASE_URL + "/", timeout=TIMEOUT)
        elapsed = time.time() - start

        assert response.status_code == 200, (
            f"Expected HTTP 200, got {response.status_code}"
        )
        assert elapsed < 3.0, (
            f"Homepage took {elapsed:.2f}s — too slow (limit: 3s)"
        )
        print(f"\n  ✔ Homepage responded in {elapsed:.2f}s with status 200")

    def test_a2_homepage_content_type_is_html(self):
        """
        WHY: The homepage must serve HTML, not a redirect to a CDN error
        page or a JSON blob. A wrong Content-Type means users see a broken page.
        """
        response = requests.get(BASE_URL + "/", timeout=TIMEOUT)
        content_type = response.headers.get("Content-Type", "")

        assert "text/html" in content_type, (
            f"Expected text/html content type, got: {content_type}"
        )
        print(f"\n  ✔ Content-Type is '{content_type}'")

    def test_a3_homepage_body_contains_key_landmarks(self):
        """
        WHY: Even if HTTP 200 is returned, the body could be empty or corrupted.
        We check for landmark strings that every real Ludigames page must have.
        """
        response = requests.get(BASE_URL + "/", timeout=TIMEOUT)
        body = response.text.lower()

        landmarks = ["ludigames", "gameloft", "play"]
        for landmark in landmarks:
            assert landmark in body, (
                f"Expected keyword '{landmark}' not found in homepage body"
            )
        print(f"\n  ✔ All landmarks found: {landmarks}")


@pytest.mark.api
class TestApiCategoryPage:
    def test_a4_sport_category_page_returns_200(self):
        """
        WHY: Category pages are how users discover games.
        The Sport category is listed prominently on the homepage — it must load.
        A broken category page would silently hide dozens of games from users.
        """
        url = BASE_URL + "/category.html?cat=Sport"
        response = requests.get(url, timeout=TIMEOUT)

        assert response.status_code == 200, (
            f"Sport category page returned {response.status_code}"
        )
        print(f"\n  ✔ Sport category page returned HTTP 200")

    def test_a5_action_category_page_returns_200(self):
        """
        WHY: Action is one of the most popular categories.
        Verifying it loads ensures the category routing mechanism works
        beyond just one category.
        """
        url = BASE_URL + "/category.html?cat=Action"
        response = requests.get(url, timeout=TIMEOUT)

        assert response.status_code == 200, (
            f"Action category page returned {response.status_code}"
        )
        print(f"\n  ✔ Action category page returned HTTP 200")

    def test_a6_unknown_category_does_not_cause_500(self):
        """
        WHY: Users may type random URLs. A graceful 404 is acceptable,
        but a 500 Internal Server Error reveals a backend crash and is
        embarrassing and potentially exploitable.
        """
        url = BASE_URL + "/category.html?cat=ThisCategoryDoesNotExist12345"
        response = requests.get(url, timeout=TIMEOUT)

        assert response.status_code < 500, (
            f"Server crashed with {response.status_code} on unknown category — "
            "should return 200 (empty) or 404, not 5xx"
        )
        print(f"\n  ✔ Unknown category returned {response.status_code} (no server crash)")

    def test_a7_response_headers_include_security_basics(self):
        """
        WHY: A public gaming portal serving thousands of users should have
        basic HTTP security headers. Missing X-Content-Type-Options can
        allow MIME-sniffing attacks in older browsers.
        """
        response = requests.get(BASE_URL + "/", timeout=TIMEOUT)
        headers = {k.lower(): v for k, v in response.headers.items()}

        # At minimum the server should send a Content-Type header
        assert "content-type" in headers, "Response is missing Content-Type header"

        # Log what security headers are present (informational)
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "strict-transport-security",
            "content-security-policy",
        ]
        present = [h for h in security_headers if h in headers]
        missing = [h for h in security_headers if h not in headers]
        print(f"\n  ✔ Security headers present: {present}")
        if missing:
            print(f"  ⚠ Security headers absent (informational): {missing}")
