# 🎮 Ludigames QA Automation Suite

**Candidate:** Pușcașu Marius-Cătălin  
**Position:** QA Automation Internship — Gameloft Bucharest  
**Target site:** [play.ludigames.com](https://play.ludigames.com)

---

## 📦 Stack

| Tool | Role |
|---|---|
| Python 3.10+ | Language |
| pytest | Test runner & assertions |
| Playwright (pytest-playwright) | UI / browser automation |
| Requests | API / HTTP checks |
| pytest-html | HTML test report |

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ludigames-qa.git
cd ludigames-qa
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

---

## ▶️ Run the tests

### All tests
```bash
pytest
```

### Only API tests
```bash
pytest -m api
```

### Only UI tests
```bash
pytest -m ui
```

### With an HTML report
```bash
pytest --html=report.html --self-contained-html
```

---

## 🧪 Test Scenarios

### API Tests (`tests/test_api.py`)

| ID | Scenario | Why I chose it |
|---|---|---|
| A1 | Homepage returns HTTP 200 within 3 seconds | The homepage is the entry point for every user. Slowness or downtime here blocks everyone. |
| A2 | Homepage Content-Type is `text/html` | HTTP 200 alone is not enough — a CDN error page also returns 200. The body must be real HTML. |
| A3 | Homepage body contains key brand landmarks | Even a valid HTML file could be empty. We verify that core strings (`ludigames`, `gameloft`) are present. |
| A4 | Sport category page returns HTTP 200 | Categories are the main discovery mechanism. A broken category silently hides dozens of games. |
| A5 | Action category page returns HTTP 200 | Verifies that category routing works for more than one category — not just a lucky first hit. |
| A6 | Unknown category does not cause a 500 error | Users mistype URLs. A 5xx server crash is embarrassing and potentially exploitable. A 200 or 404 is acceptable. |
| A7 | Response headers include `Content-Type` | Basic HTTP hygiene check. Also logs which security headers are present vs. absent (informational). |

### UI Tests (`tests/test_ui.py`)

| ID | Scenario | Why I chose it |
|---|---|---|
| U1 | Homepage title is recognisable | The page title is the first thing a browser tab shows. A wrong title means the wrong page loaded entirely. |
| U2 | Homepage shows ≥ 5 game links | Categories and game cards are the portal's core content. If they don't render, the site has no purpose. |
| U3 | Search input accepts typed text | Search is how power users navigate. A frozen or read-only input is a silent critical bug. |
| U4 | Clicking a game card navigates to a detail page | This is the most common user action. If clicks don't work, nothing works. |
| U5 | Homepage renders on a 375 × 667 mobile viewport | Ludigames targets casual/mobile users. A desktop-only site loses the majority of its audience. |
| U6 | No `<img>` tags have an empty `src` | Broken images make the site look unprofessional and signal CDN or asset pipeline failures. |

---

## 💡 Design Decisions

- **Why Python + pytest?** Widely used in QA, easy to read, excellent plugin ecosystem. The code is approachable even for someone who has never seen the project.
- **Why Playwright over Selenium?** Playwright has built-in auto-wait, is faster, and handles modern JS-heavy SPAs better. `pytest-playwright` integrates cleanly with the pytest fixture model.
- **Why mix UI and API?** API tests are fast and stable — they catch infrastructure issues in milliseconds. UI tests are slower but verify that the full rendering pipeline works for a real user. Both layers are necessary.
- **Headless by default.** Tests run headless so they work in any CI environment without a display server.

---

## 📸 Test Output

```
tests/test_api.py::TestApiHomepage::test_a1_homepage_returns_200_within_3s PASSED
tests/test_api.py::TestApiHomepage::test_a2_homepage_content_type_is_html PASSED
tests/test_api.py::TestApiHomepage::test_a3_homepage_body_contains_key_landmarks PASSED
tests/test_api.py::TestApiCategoryPage::test_a4_sport_category_page_returns_200 PASSED
tests/test_api.py::TestApiCategoryPage::test_a5_action_category_page_returns_200 PASSED
tests/test_api.py::TestApiCategoryPage::test_a6_unknown_category_does_not_cause_500 PASSED
tests/test_api.py::TestApiCategoryPage::test_a7_response_headers_include_security_basics PASSED
tests/test_ui.py::TestUiHomepage::test_u1_homepage_title_and_header_visible PASSED
tests/test_ui.py::TestUiHomepage::test_u2_category_sections_visible_with_game_cards PASSED
tests/test_ui.py::TestUiHomepage::test_u3_search_input_accepts_text PASSED
tests/test_ui.py::TestUiHomepage::test_u4_game_card_click_navigates_to_detail_page PASSED
tests/test_ui.py::TestUiHomepage::test_u5_mobile_viewport_homepage_renders PASSED
tests/test_ui.py::TestUiHomepage::test_u6_page_has_no_broken_images_in_hero_section PASSED

13 passed in 18.42s
```

---

## 📁 Project Structure

```
ludigames-qa/
├── tests/
│   ├── conftest.py      # Shared fixtures (browser context, base_url)
│   ├── test_api.py      # API / HTTP tests (7 scenarios)
│   └── test_ui.py       # UI / browser tests (6 scenarios)
├── pytest.ini           # pytest config and markers
├── requirements.txt     # Python dependencies
└── README.md
```
