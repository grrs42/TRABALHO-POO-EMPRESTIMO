from src.views.first_view import introduction_page

def introduction_process(sessao: dict):
    command = introduction_page(sessao)
    return command
