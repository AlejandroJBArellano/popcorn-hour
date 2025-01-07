# PopcornHour 🍿

PopcornHour es una plataforma web que permite a los usuarios descubrir, calificar y discutir sobre películas y series. La plataforma ofrece una experiencia interactiva donde los moderadores pueden subir contenido y los usuarios estándar pueden participar en discusiones y calificaciones.

## Características principales ⭐

- Sistema de autenticación con dos tipos de usuarios: moderadores y estándar
- Catálogo de películas y series
- Sistema de calificación y reseñas
- Sección de comentarios y discusiones
- Panel de administración para moderadores
- Sistema de recomendaciones

## Requisitos del sistema 🔧

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- PostgreSQL 13 o superior
- Entorno virtual de Python (recomendado)

## Instalación 🚀

1. Clonar el repositorio:
```bash
git clone https://github.com/your-username/popcornhour.git
cd popcornhour
```

2. Crear y activar el entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar las variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Inicializar la base de datos:
```bash
flask db upgrade
```

6. Ejecutar la aplicación:
```bash
flask run
```

## Estructura del proyecto 📁

```
popcornhour/
├── app/                  # Código principal de la aplicación
│   ├── models/          # Modelos de la base de datos
│   ├── routes/          # Rutas y vistas
│   ├── templates/       # Plantillas HTML
│   └── static/          # Archivos estáticos (CSS, JS, imágenes)
├── tests/               # Pruebas unitarias y de integración
├── config.py            # Configuración de la aplicación
├── requirements.txt     # Dependencias del proyecto
└── README.md           # Este archivo
```

## Uso 📝

### Para usuarios moderadores:
1. Iniciar sesión con credenciales de moderador
2. Acceder al panel de administración
3. Subir nuevas películas o series
4. Gestionar contenido existente

### Para usuarios estándar:
1. Crear una cuenta o iniciar sesión
2. Explorar el catálogo de películas y series
3. Calificar contenido
4. Participar en discusiones

## Pruebas 🧪

Para ejecutar las pruebas:
```bash
pytest tests/
```

Para ver la cobertura de código:
```bash
pytest --cov=app tests/
```

## Contribuir 🤝

1. Fork el proyecto
2. Crear una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Autor ✒️

[Tu nombre]
- GitHub: [@your-username](https://github.com/your-username)

## Licencia 📄

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles

## Agradecimientos 🎁

- A todos los que contribuyen al proyecto
- A la comunidad open source por las herramientas utilizadas

---
⌨️ con ❤️ por [Tu nombre]