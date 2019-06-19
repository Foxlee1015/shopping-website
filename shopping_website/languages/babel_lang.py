from shopping_website import babel


@babel.localeselector
def get_locale():
    """
    1. 세션에 저장되어 있는 언어 2.Ip 주소로 한국이면 한국어 그외 영어로 설정 
    """
    try:
        language = session['language']
        return language
    except:
        a, b, c = Get_ip_loca()
        if a == "South Korea":
            return 'ko'
        else: 
            return 'en'
        #return app.config['BABEL_DEFAULT_LOCALE']
        #return request.accept_languages.best(['en', 'ko'])  # 사용자의 위치에 따라 언어 바뀜(best, 가능한 옵션중(나의 경우. 영어, 한국어)

@babel.localeselector
def get_locale_ko():
    return 'ko'


@babel.localeselector
def get_locale_en():
    return 'en'


