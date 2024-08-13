from celery import Celery, Task
from core.settings import settings
from .smtp_email import smtp_email
from logs.get_logger import logger

celery_app = Celery("TaskTracker", broker=settings.smtp.broker_url)

celery_app.conf.broker_connection_retry_on_startup = True


class EmailNotification(Task):
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Email notification sent success, task_id={task_id}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.warning(f"Email notification failed, task_id={task_id}")


@celery_app.task(base=EmailNotification)
def send_new_task_comment_notify(
    to_user_email: str,
    comment_author_full_name: str,
    comment_text: str,
    task_title: str,
):
    title = f"Пользователь {comment_author_full_name} оставил(а) комментарий к вашей задаче."
    template = (
        "<header>"
        '<h1 style="text-align: center; font-family: Arial, Helvetica, sans-serif;color:#000000;"><span style="color: #e4921a;">T</span>ask <span style="color: #e4921a;">T</span>racker</h1>'
        "</header>"
        '<hr style="width: 800px;"/>'
        "<main>"
        '<div style="text-align: center; font-family: Arial, Helvetica, sans-serif; margin-top: 50px;">'
        f'<h2 style="color:#000000;">У вас новый комментарий к задаче {task_title!r}</h2>'
        "</div>"
        '<div style="width: 700px; height: 300px; border: 1px solid #5e5d5d; border-radius: 10px; box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.3); margin: auto; margin-top: 40px;">'
        "<article>"
        f'<h4 style="text-align: center;color:#000000;">Пользователь {comment_author_full_name} оставил(а) комментарий к вашей задаче</h4>'
        '<hr style="width: 99%;"/>'
        '<div style="width: 500px; height: 100%; border-radius: 8px; margin: auto; margin-top: 50px;">'
        f'<p style="text-align: left; margin-left: 40px;"><b style="color:#000000;">{comment_author_full_name}</b></p>'
        "<hr/>"
        '<div class="comment-text" style="width: 450px; height: 100%; text-align: left; margin-left: 40px;">'
        f'<p style="display: inline-block;color:#000000;">{comment_text[:200]}...</p>'
        "</div>"
        "</div>"
        "</article>"
        "</div>"
        "</main>"
    )

    email = smtp_email.get_email_template(
        user_email=to_user_email, title=title, content=template
    )
    return smtp_email.send_email(email)


@celery_app.task(base=EmailNotification)
def send_added_to_the_marked_users_notify(
    to_user_email: str,
    task_author_full_name: str,
    task_title: str,
    task_description: str,
):
    title = f"Пользователь {task_author_full_name} отметил(а) вас в таске {task_title[:150]!r}"
    template = (
        "<header>"
        '<h1 style="text-align: center; font-family: Arial, Helvetica, sans-serif;color:#000000;"><span style="color: #e4921a;">T</span>ask <span style="color: #e4921a;">T</span>racker</h1>'
        "</header>"
        '<hr style="width: 800px;"/>'
        "<main>"
        '<div style="text-align: center; font-family: Arial, Helvetica, sans-serif; margin-top: 50px;">'
        f'<h2 style="color:#000000;">Вас отметили в таске</h2>'
        "</div>"
        '<div style="width: 700px; height: 300px; border: 1px solid #5e5d5d; border-radius: 10px; box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.3); margin: auto; margin-top: 40px;">'
        "<article>"
        f'<h4 style="text-align: center;color:#000000;">Пользователь {task_author_full_name} отметил(а) вас в таске {task_title[:150]!r}</h4>'
        '<hr style="width: 99%;"/>'
        '<div style="width: 500px; height: 100%; border-radius: 8px; margin: auto; margin-top: 50px;">'
        f'<p style="text-align: left; margin-left: 40px;"><b style="color:#000000;">{task_title[:150]}</b></p>'
        "<hr/>"
        '<div class="comment-text" style="width: 450px; height: 100%; text-align: left; margin-left: 40px;">'
        f'<p style="display: inline-block;color:#000000;">{task_description[:200]}...</p>'
        "</div>"
        "</div>"
        "</article>"
        "</div>"
        "</main>"
    )
    email = smtp_email.get_email_template(
        user_email=to_user_email, title=title, content=template
    )
    return smtp_email.send_email(email)
