from contextlib import asynccontextmanager

from fastapi.responses import HTMLResponse, RedirectResponse
from wtforms.fields import TextAreaField
from core.database import Database
from fastapi import FastAPI, Response
from core.logging import exception_handler, log_response_time
from core.opentelemetry import handle_tracing
from src.user.infrastructure.http.router import router as user_router
from src.flashcard.infrastructure.http.router import router as flashcard_router
from src.study.infrastructure.http.router import router as study_router
import uvicorn
from starlette.requests import Request
from core.open_api import custom_openapi
from core.logging import queue_listener
from config import settings
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import core.database as database
from sqladmin import Admin, BaseView, ModelView, action, expose
from core.models import Users
from sqlalchemy import create_engine

_already_instrumented = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _already_instrumented

    database.db = Database(settings.database_url)

    if not _already_instrumented:
        FastAPIInstrumentor.instrument_app(app, server_request_hook=server_request_naming_hook)
        SQLAlchemyInstrumentor().instrument(engine=database.db.engine.sync_engine)
        _already_instrumented = True

    yield

    if database.db:
        await database.db.close()

    queue_listener.stop()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    return await handle_tracing(request, call_next)


def server_request_naming_hook(span, scope):
    """Rename spans automatically to reflect route names like GET /users/{id}"""
    if span and scope:
        method = scope.get("method", "GET")
        route = scope.get("path", "<unknown>")
        span.update_name(f"{method} {route}")
        span.set_attribute("http.route", route)
        span.set_attribute("http.method", method)


@app.middleware("http")
async def logging(request: Request, call_next) -> Response:
    return await log_response_time(request, call_next)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await exception_handler(request, exc)


app.openapi = lambda: custom_openapi(app)
app.include_router(user_router)
app.include_router(flashcard_router)
app.include_router(study_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")


admin = Admin(app, Database(settings.database_url).engine)

from wtforms.widgets import TextArea
from markupsafe import Markup


class HugeRTEWidget(TextArea):
    def __call__(self, field, **kwargs):
        html = super().__call__(field, **kwargs)
        # Dodajemy JS inicjalizujący edytor
        js = f"""
        <script>
        document.addEventListener("DOMContentLoaded", function () {{
            let options = {{
                selector: '#{field.id}',
                height: 300,
                menubar: false,
                plugins: [
                    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview', 'anchor',
                    'searchreplace', 'visualblocks', 'code', 'fullscreen',
                    'insertdatetime', 'media', 'table', 'code', 'help', 'wordcount'
                ],
                toolbar: 'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat',
            }};
            hugeRTE.init(options);
        }});
        </script>
        """
        return Markup(html + js)


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.name, Users.email, Users.created_at, Users.updated_at]
    column_details_list = [Users.id, Users.name, Users.email, Users.created_at, Users.updated_at]
    can_create = True
    can_edit = False
    can_delete = False
    can_view_details = True
    category = "Management"

    form_overrides = {"email": TextAreaField}

    form_widget_args = {"email": {"widget": HugeRTEWidget()}}

    @action(
        name="send_email",  # internal action name
        confirmation_message="Are you sure you want to send emails?",  # optional confirmation
    )
    async def send_email(self, request: Request) -> RedirectResponse:
        pks = request.query_params.get("pks", "").split(",")
        if pks:
            for pk in pks:
                print(pks)

        referer = request.headers.get("Referer")

        if referer:
            return RedirectResponse(referer)
        else:
            return RedirectResponse(request.url_for("admin:list", identity=self.identity))


class ReportView(BaseView):
    name = "Report Page"
    icon = "fa-solid fa-chart-line"
    category = "Management"

    @expose("/report", methods=["GET"])
    async def report_page(self, request):
        users_count = 15

        return await self.templates.TemplateResponse(
            request,
            "report.html",
            context={"users_count": users_count},
        )


class HugeRTEAdmin(BaseView):
    name = "Huge RTE"
    icon = "fa-solid fa-pencil"
    category = "Tools"

    @expose("/hugerte", methods=["GET", "POST"])
    async def hugerte_page(self, request: Request) -> HTMLResponse:
        # Render your template here
        return await self.templates.TemplateResponse(
            request,
            "hugerte.html",
        )


admin.add_view(UserAdmin)
admin.add_view(HugeRTEAdmin)
