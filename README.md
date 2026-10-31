# AI Developer Tools Zoomcamp 2026

This repository contains my work for the **AI Developer Tools Zoomcamp 2026**. It is a hands-on learning portfolio for exploring AI-assisted software development and applying those workflows to practical projects.

The repository is organized by course module. Each module can include its own project, implementation notes, planning documents, and setup instructions. The first module is a Django web application for coordinating chores across a household.

## Course roadmap

| Module | Topic | Work in this repository |
| --- | --- | --- |
| 01 | AI-native workflow | Plan and build a shared household chores application. [Module README](./01-ai-native-workflow/README.md) |
| 02+ | To be added | Project materials will be added as the course progresses. |

## Module 01: AI-native workflow

The first project is a household chores app designed to help members coordinate recurring work. Its current scope includes household membership, chore schedules and rotation, completion tracking, points, streaks, and a leaderboard. The application is built with Django and includes installable PWA assets.

The module's planning and implementation documents live in [`01-ai-native-workflow/_docs/`](./01-ai-native-workflow/_docs/). Start with the [module README](./01-ai-native-workflow/README.md) for project details and development commands.

## Repository layout

```text
.
├── README.md
└── 01-ai-native-workflow/
    ├── README.md                 # Module overview and project notes
    ├── manage.py                 # Django management entry point
    ├── pyproject.toml            # Python project metadata and dependencies
    ├── household_chores/         # Django project settings and URL configuration
    ├── chores/                   # App models, views, templates, and PWA assets
    └── _docs/                    # Plans, design notes, and workflow documents
```

## Getting started

### Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) for Python environment and dependency management

### Run Module 01 locally

```bash
git clone https://github.com/pranabsarma18/ai-dev-tools-zoomcamp-2026.git
cd ai-dev-tools-zoomcamp-2026/01-ai-native-workflow
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. Django's development server is intended for local development.

To create an administrator account for the Django admin interface, run:

```bash
uv run python manage.py createsuperuser
```

See the [Module 01 README](./01-ai-native-workflow/README.md) for additional project context and commands.

## Development notes

- Python dependencies for Module 01 are declared in [`pyproject.toml`](./01-ai-native-workflow/pyproject.toml) and locked in [`uv.lock`](./01-ai-native-workflow/uv.lock).
- Planning, task breakdowns, and design references are maintained in the module's `_docs` directory.
- Course notes and project scope may evolve as each module is completed.

## License

MIT
