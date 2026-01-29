from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import auth, models
from .db import SessionLocal

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

TRANSLATIONS = {
    "en": {
        "app_name": "NEONHIRE (Clean)",
        "register": "Register",
        "login": "Login",
        "home": "Home",
        "email": "Email",
        "password": "Password",
        "register_title": "Create your account",
        "login_title": "Sign in",
        "submit": "Submit",
        "already_have": "Already have an account?",
        "need_account": "Need an account?",
        "registration_success": "Registration successful. Please log in.",
        "invalid_credentials": "Invalid email or password.",
        "email_exists": "Email already registered.",
        "password_too_long": "Password must be at most 72 bytes.",
        "welcome": "Welcome",
        "loading": "Loading...",
        "not_logged_in": "Not logged in.",
        "logout": "Log out",
        "language": "Language",
    },
    "ru": {
        "app_name": "NEONHIRE (Clean)",
        "register": "Регистрация",
        "login": "Вход",
        "home": "Главная",
        "email": "Email",
        "password": "Пароль",
        "register_title": "Создать аккаунт",
        "login_title": "Войти",
        "submit": "Отправить",
        "already_have": "Уже есть аккаунт?",
        "need_account": "Нужен аккаунт?",
        "registration_success": "Регистрация прошла успешно. Войдите в систему.",
        "invalid_credentials": "Неверный email или пароль.",
        "email_exists": "Email уже зарегистрирован.",
        "password_too_long": "Пароль должен быть не длиннее 72 байт.",
        "welcome": "Добро пожаловать",
        "loading": "Загрузка...",
        "not_logged_in": "Вы не вошли в систему.",
        "logout": "Выйти",
        "language": "Язык",
    },
}


def get_lang(request: Request) -> str:
    lang = request.cookies.get("lang", "en")
    if lang not in TRANSLATIONS:
        return "en"
    return lang


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def home(request: Request):
    lang = get_lang(request)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "t": TRANSLATIONS[lang],
            "lang": lang,
        },
    )


@router.get("/register")
def register_page(request: Request):
    lang = get_lang(request)
    message = request.query_params.get("message")
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "t": TRANSLATIONS[lang],
            "lang": lang,
            "message": message,
            "error": error,
        },
    )


@router.post("/register")
def register_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    lang = get_lang(request)
    if auth.is_password_too_long(password):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "t": TRANSLATIONS[lang],
                "lang": lang,
                "error": TRANSLATIONS[lang]["password_too_long"],
            },
            status_code=400,
        )
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "t": TRANSLATIONS[lang],
                "lang": lang,
                "error": TRANSLATIONS[lang]["email_exists"],
            },
            status_code=400,
        )
    user = models.User(email=email, hashed_password=auth.hash_password(password))
    db.add(user)
    db.commit()
    response = RedirectResponse(url="/login?registered=1", status_code=303)
    return response


@router.get("/login")
def login_page(request: Request):
    lang = get_lang(request)
    registered = request.query_params.get("registered")
    message = TRANSLATIONS[lang]["registration_success"] if registered else None
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "t": TRANSLATIONS[lang],
            "lang": lang,
            "message": message,
        },
    )


@router.post("/login")
def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    lang = get_lang(request)
    if auth.is_password_too_long(password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "t": TRANSLATIONS[lang],
                "lang": lang,
                "error": TRANSLATIONS[lang]["password_too_long"],
            },
            status_code=400,
        )
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "t": TRANSLATIONS[lang],
                "lang": lang,
                "error": TRANSLATIONS[lang]["invalid_credentials"],
            },
            status_code=401,
        )
    token = auth.create_access_token(subject=user.email)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie("access_token", token, httponly=False, samesite="lax")
    return response


@router.get("/lang/{lang}")
def set_language(request: Request, lang: str):
    lang = lang if lang in TRANSLATIONS else "en"
    redirect_to = request.headers.get("referer") or "/"
    response = RedirectResponse(url=redirect_to, status_code=303)
    response.set_cookie("lang", lang, samesite="lax")
    return response
