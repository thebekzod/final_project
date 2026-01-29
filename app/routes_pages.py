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
        "jobs": "Jobs",
        "freelancers": "Freelancers",
        "profile": "Profile",
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
        "welcome": "Welcome",
        "loading": "Loading...",
        "not_logged_in": "Not logged in.",
        "logout": "Log out",
        "language": "Language",
        "hero_title": "Find talent. Find work. All in one place.",
        "hero_body": "Post a project or showcase your skills to land your next freelance opportunity.",
        "cta_jobs": "Browse jobs",
        "cta_freelancers": "Meet freelancers",
        "cta_create_job": "Post a job",
        "cta_create_profile": "Create profile",
        "jobs_title": "Latest jobs",
        "jobs_empty": "No jobs posted yet.",
        "job_new_title": "Post a new job",
        "job_title_label": "Job title",
        "job_description_label": "Job description",
        "job_create_success": "Job posted successfully.",
        "freelancers_title": "Freelancer profiles",
        "freelancers_empty": "No freelancer profiles yet.",
        "freelancer_new_title": "Create your freelancer profile",
        "freelancer_name_label": "Full name",
        "freelancer_skills_label": "Skills",
        "freelancer_bio_label": "Bio",
        "freelancer_create_success": "Profile created successfully.",
        "profile_title": "Your profile",
        "logged_in_as": "Logged in as",
        "login_required": "Please log in to continue.",
    },
    "ru": {
        "app_name": "NEONHIRE (Clean)",
        "register": "Регистрация",
        "login": "Вход",
        "home": "Главная",
        "jobs": "Вакансии",
        "freelancers": "Фрилансеры",
        "profile": "Профиль",
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
        "welcome": "Добро пожаловать",
        "loading": "Загрузка...",
        "not_logged_in": "Вы не вошли в систему.",
        "logout": "Выйти",
        "language": "Язык",
        "hero_title": "Найдите талант и проект в одном месте.",
        "hero_body": "Разместите проект или покажите навыки, чтобы найти следующую фриланс-возможность.",
        "cta_jobs": "Смотреть вакансии",
        "cta_freelancers": "Найти фрилансеров",
        "cta_create_job": "Разместить проект",
        "cta_create_profile": "Создать профиль",
        "jobs_title": "Новые вакансии",
        "jobs_empty": "Пока нет размещённых вакансий.",
        "job_new_title": "Создать вакансию",
        "job_title_label": "Название вакансии",
        "job_description_label": "Описание вакансии",
        "job_create_success": "Вакансия успешно создана.",
        "freelancers_title": "Профили фрилансеров",
        "freelancers_empty": "Пока нет профилей фрилансеров.",
        "freelancer_new_title": "Создать профиль фрилансера",
        "freelancer_name_label": "ФИО",
        "freelancer_skills_label": "Навыки",
        "freelancer_bio_label": "О себе",
        "freelancer_create_success": "Профиль успешно создан.",
        "profile_title": "Ваш профиль",
        "logged_in_as": "Вы вошли как",
        "login_required": "Пожалуйста, войдите, чтобы продолжить.",
    },
}


def get_lang(request: Request) -> str:
    lang = request.cookies.get("lang", "en")
    return lang if lang in TRANSLATIONS else "en"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_email_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        return auth.decode_access_token(token)
    except Exception:
        return None


@router.get("/")
def home(request: Request):
    lang = get_lang(request)
    current_email = get_current_email_from_cookie(request)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "t": TRANSLATIONS[lang], "lang": lang, "current_email": current_email},
    )


@router.get("/register")
def register_page(request: Request):
    lang = get_lang(request)
    message = request.query_params.get("message")
    error = request.query_params.get("error")
    if error == "login_required":
        error = TRANSLATIONS[lang]["login_required"]
    current_email = get_current_email_from_cookie(request)
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "t": TRANSLATIONS[lang],
            "lang": lang,
            "message": message,
            "error": error,
            "current_email": current_email,
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
    current_email = get_current_email_from_cookie(request)

    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "t": TRANSLATIONS[lang],
                "lang": lang,
                "error": TRANSLATIONS[lang]["email_exists"],
                "current_email": current_email,
            },
            status_code=400,
        )

    user = models.User(email=email, hashed_password=auth.hash_password(password))
    db.add(user)
    db.commit()

    return RedirectResponse(url="/login?registered=1", status_code=303)


@router.get("/login")
def login_page(request: Request):
    lang = get_lang(request)
    registered = request.query_params.get("registered")
    message = TRANSLATIONS[lang]["registration_success"] if registered else None
    error = request.query_params.get("error")
    if error == "login_required":
        error = TRANSLATIONS[lang]["login_required"]
    current_email = get_current_email_from_cookie(request)
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "t": TRANSLATIONS[lang],
            "lang": lang,
            "message": message,
            "error": error,
            "current_email": current_email,
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
    current_email = get_current_email_from_cookie(request)

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "t": TRANSLATIONS[lang],
                "lang": lang,
                "error": TRANSLATIONS[lang]["invalid_credentials"],
                "current_email": current_email,
            },
            status_code=401,
        )

    if not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "t": TRANSLATIONS[lang],
                "lang": lang,
                "error": TRANSLATIONS[lang]["invalid_credentials"],
                "current_email": current_email,
            },
            status_code=401,
        )

    token = auth.create_access_token(subject=user.email)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie("access_token", token, httponly=False, samesite="lax")
    return response


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response


def require_login(request: Request):
    email = get_current_email_from_cookie(request)
    if not email:
        return None
    return email


@router.get("/profile")
def profile(request: Request):
    lang = get_lang(request)
    email = require_login(request)
    if not email:
        return RedirectResponse(url="/login?error=login_required", status_code=303)
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "t": TRANSLATIONS[lang],
            "lang": lang,
            "current_email": email,
        },
    )


@router.get("/jobs")
def jobs_list(request: Request, db: Session = Depends(get_db)):
    lang = get_lang(request)
    current_email = get_current_email_from_cookie(request)
    message = request.query_params.get("message")
    if message == "job_created":
        message = TRANSLATIONS[lang]["job_create_success"]
    jobs = db.query(models.Job).order_by(models.Job.created_at.desc()).all()
    return templates.TemplateResponse(
        "jobs.html",
        {
            "request": request,
            "t": TRANSLATIONS[lang],
            "lang": lang,
            "jobs": jobs,
            "message": message,
            "current_email": current_email,
        },
    )


@router.get("/jobs/new")
def jobs_new_page(request: Request):
    lang = get_lang(request)
    email = require_login(request)
    if not email:
        return RedirectResponse(url="/login?error=login_required", status_code=303)
    return templates.TemplateResponse(
        "job_new.html",
        {"request": request, "t": TRANSLATIONS[lang], "lang": lang, "current_email": email},
    )


@router.post("/jobs/new")
def jobs_new_action(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    lang = get_lang(request)
    email = require_login(request)
    if not email:
        return RedirectResponse(url="/login?error=login_required", status_code=303)
    job = models.Job(title=title, description=description, owner_email=email)
    db.add(job)
    db.commit()
    response = RedirectResponse(url="/jobs?message=job_created", status_code=303)
    return response


@router.get("/freelancers")
def freelancers_list(request: Request, db: Session = Depends(get_db)):
    lang = get_lang(request)
    current_email = get_current_email_from_cookie(request)
    message = request.query_params.get("message")
    if message == "freelancer_created":
        message = TRANSLATIONS[lang]["freelancer_create_success"]
    profiles = db.query(models.FreelancerProfile).order_by(models.FreelancerProfile.created_at.desc()).all()
    return templates.TemplateResponse(
        "freelancers.html",
        {
            "request": request,
            "t": TRANSLATIONS[lang],
            "lang": lang,
            "profiles": profiles,
            "message": message,
            "current_email": current_email,
        },
    )


@router.get("/freelancers/new")
def freelancers_new_page(request: Request):
    lang = get_lang(request)
    email = require_login(request)
    if not email:
        return RedirectResponse(url="/login?error=login_required", status_code=303)
    return templates.TemplateResponse(
        "freelancer_new.html",
        {"request": request, "t": TRANSLATIONS[lang], "lang": lang, "current_email": email},
    )


@router.post("/freelancers/new")
def freelancers_new_action(
    request: Request,
    full_name: str = Form(...),
    skills: str = Form(...),
    bio: str = Form(...),
    db: Session = Depends(get_db),
):
    lang = get_lang(request)
    email = require_login(request)
    if not email:
        return RedirectResponse(url="/login?error=login_required", status_code=303)
    profile = models.FreelancerProfile(
        full_name=full_name,
        skills=skills,
        bio=bio,
        owner_email=email,
    )
    db.add(profile)
    db.commit()
    response = RedirectResponse(url="/freelancers?message=freelancer_created", status_code=303)
    return response


@router.get("/lang/{lang}")
def set_language(request: Request, lang: str):
    lang = lang if lang in TRANSLATIONS else "en"
    redirect_to = request.headers.get("referer") or "/"
    response = RedirectResponse(url=redirect_to, status_code=303)
    response.set_cookie("lang", lang, samesite="lax")
    return response
