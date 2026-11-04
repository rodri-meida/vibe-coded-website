# GitHub Trending Repositories

A production-ready Django web application that discovers and displays trending public repositories from the GitHub Search API. Features language filtering, time-period filtering, search, sorting, pagination, dark mode, and responsive design.

## Live Demo

Visit http://127.0.0.1:8000/ after starting the server.

## Features

| Feature | Description |
|---------|-------------|
| 🔥 Trending repos | Fetches from GitHub Search API (`/search/repositories`) |
| 🔤 Language filter | Dropdown of 15+ popular languages + "All" |
| 📅 Time period | Weekly, monthly, yearly, all time |
| 🔍 Search | Debounced search by repo name/description |
| 📊 Sorting | Stars, forks, recently updated (client-side sort) |
| 📄 Pagination | 30 repos per page with Django Paginator |
| 🌓 Dark mode | Toggle persisted in `localStorage`, respects system preference |
| 📱 Responsive | Mobile-first CSS grid, collapsible filters on small screens |
| ⚠️ Error handling | Graceful error and empty states with retry |
| ⚡ Caching | Django cache layer (10 min TTL) to reduce API calls |
| 📈 Rate limit | Displays remaining GitHub API rate limit |
| 🎨 Modern UI | Clean cards, hover effects, animations, topic tags |

## Improved Prompt (for AI Coding Assistants)

> Build a production-ready Django web application called "GitHub Trending Repositories" that fetches and displays trending public repositories from the GitHub Search API. The app should:
>
> 1. **Home page** showing a grid of repository cards with: owner avatar, name (linked to GitHub), description, language, star count, fork count, open issues, license, last updated date, and topic tags.
> 2. **Filter controls**: language dropdown (All + 15+ popular languages), time period dropdown (weekly/monthly/yearly/all), and a debounced search text input (500ms).
> 3. **Sorting**: buttons to sort by stars, forks, or recently updated (client-side sort to avoid extra API calls).
> 4. **Pagination**: Django Paginator with 30 items per page, preserving all query parameters.
> 5. **Theme**: light/dark mode toggle persisted in `localStorage`, respecting system preference by default, with CSS custom properties.
> 6. **Responsive**: mobile-first CSS grid, single-column filters on small screens, touch-friendly buttons.
> 7. **Error handling**: graceful error and empty states with retry option, distinct messages for rate limits, timeouts, and validation errors.
> 8. **GitHub API**: use the `/search/repositories` endpoint with `q`, `sort`, `order`, and `per_page` params. Support an optional `GITHUB_TOKEN` for higher rate limits. Display remaining rate limit in UI.
> 9. **Caching**: Django cache layer with 10-minute TTL keyed by filter parameters.
> 10. **Django structure**: standard project layout with `manage.py`, `trending_site/` config, and a `repos/` app. Include `settings.py`, `urls.py`, `views.py`, `services.py`, `models.py`, admin, templates, and static files.
> 11. **Setup**: `requirements.txt` with Django and requests. Provide clear install, migration, and run instructions.
> 12. **Code quality**: clean, well-commented, follows Django best practices, separates API logic into a service layer, uses class-based model methods, includes custom exceptions.

## Project Structure

```
vibe-coded-website/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── db.sqlite3
├── trending_site/
│   ├── __init__.py
│   ├── settings.py      # Django config, cache, GitHub settings
│   ├── urls.py          # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
├── repos/
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py         # Repository admin config
│   ├── models.py        # Repository model with from_github_item()
│   ├── services.py      # GitHubService with caching & error handling
│   ├── views.py         # Home view with filtering, sorting, pagination
│   └── urls.py          # App URL routing
├── templates/
│   ├── base.html        # Base template with theme toggle & skip link
│   └── repos/
│       └── home.html    # Main page: filters, results, pagination, states
└── static/
    ├── css/
    │   └── style.css    # CSS variables, dark mode, animations, responsive
    └── js/
        └── app.js       # Theme, debounced search, sorting, a11y, animations
```

## Setup & Installation

### Prerequisites

- Python 3.10+
- `pip`

### 1. Clone or Create the Project

```bash
cd vibe-coded-website
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create a Superuser (Optional, for Admin)

```bash
python manage.py createsuperuser
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.

### 6. Access the Admin

http://127.0.0.1:8000/admin/ (login with your superuser credentials)

## Optional: GitHub Token

The GitHub Search API allows 10 requests per minute for unauthenticated users, and 30 with a token. For higher limits, set a `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

The token is read automatically from `trending_site/settings.py`:

```python
import os
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
```

## Running Tests

```bash
python manage.py test
```

## Deployment

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn trending_site.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "trending_site.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## License

MIT License