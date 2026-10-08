# NextGenDev

> The next generation of tech. Share, learn and connect with other creators.

Modern blogging platform built with **Django**, **WebSockets** and **AJAX**.
Designed for developers who want to share knowledge, connect with
other creators and discover relevant content in real time.

![NextGenDev](screenshots/banner.png)

---

## Screenshots

### Home
![Home](screenshots/inicio.png)

### Post Detail
![Post Detail](screenshots/detalle.png)

### Public Profile
![Profile](screenshots/perfil.png)

### Dark Mode
![Dark Mode](screenshots/dark-mode.png)

### Mobile
![Mobile](screenshots/movil.png)

---

## Features

### Authentication
- User registration and login
- Password change
- Editable public profile (avatar, bio, location, website)

### Posts
- Create, edit and delete posts
- Image uploads
- Categories
- Search by title with debounce

### Interactions
- Real-time likes (AJAX)
- Real-time comments (WebSocket)
- Save posts (bookmarks)
- Follow users

### Personalized Feed
- Posts only from users you follow
- Infinite scroll with cursor (no duplicates)
- Empty feed with suggestions

### Real-time Notifications
- Likes, comments and follows
- Dynamic badge with counter
- Toast notifications
- Full history
- Mark as read on click

### Design
- Dark/light mode with persistence
- Responsive (mobile, tablet, desktop)
- Facebook-style sidebar
- Smooth animations
- Modular and maintainable CSS

### Search
- Search with debounce (300ms)
- Real-time results
- Dropdown with suggestions

---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Django 6.1** | Web framework |
| **Django Channels** | WebSockets |
| **PostgreSQL** | Database |
| **Redis** | Channel layer |
| **Pillow** | Image processing |
| **Daphne** | ASGI server |
| **WhiteNoise** | Static files |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5 / CSS3** | Structure and styles |
| **Vanilla JavaScript** | Interactivity |
| **Bootstrap 5** | CSS framework |
| **Font Awesome** | Icons |

### Real-time
- **WebSockets** - Comments and notifications
- **AJAX (fetch)** - Likes, saves, follows
- **Intersection Observer** - Infinite scroll
- **Signals** - Auto-generated notifications

---

## Project Structure

```
nextgendev/
├── posts/
│   ├── migrations/
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   ├── base/
│   │   │   ├── layout/
│   │   │   ├── components/
│   │   │   ├── themes/
│   │   │   └── responsive.css
│   │   └── js/
│   │       ├── like.js
│   │       ├── guardado.js
│   │       ├── seguir.js
│   │       ├── scroll.js
│   │       ├── search.js
│   │       ├── notificaciones.js
│   │       ├── ws.js
│   │       └── theme.js
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── models.py
│   ├── routing.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── mi_blog/
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
├── screenshots/
├── manage.py
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

---

## Installation

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 14+**
- **Redis 7+**
- **Git**

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/j-paezalbarracin/nextgendev.git
cd nextgendev
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your values
```

5. **Create PostgreSQL database**
```bash
createdb nextgendev
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Start Redis**
```bash
redis-server
```

9. **Run the server**
```bash
daphne -b 0.0.0.0 -p 8000 mi_blog.asgi:application
```

10. **Open in browser**
```
http://localhost:8000
```

---

## Environment Variables

Create a `.env` file at the root:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/nextgendev

# Redis
REDIS_URL=redis://localhost:6379
```

---

## Tests

```bash
python manage.py test posts
```

---

## Roadmap

- [x] Full authentication
- [x] Public profiles
- [x] Likes system
- [x] Real-time comments
- [x] WebSocket notifications
- [x] Personalized feed
- [x] Save posts
- [x] Follow users
- [x] Search
- [x] Infinite scroll
- [x] Dark mode
- [ ] Complete tests
- [ ] Docker
- [ ] Production deploy
- [ ] REST API with DRF
- [ ] React + Vite frontend

---

## Contributing

1. Fork the project
2. Create your branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

##  Author

**Ingeniero Julian A. Paez A.**

- GitHub: [@j-paezalbarracin](https://github.com/j-paezalbarracin)

---

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Django Channels](https://channels.readthedocs.io/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [Redis](https://redis.io/)

---

 **If you liked this project, give it a star on GitHub!**