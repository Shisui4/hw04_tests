from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_title'] = 'Информация о создателе'
        context['title'] = 'Страница с информацией об Авторе'
        context['obout_info'] = ('Добрый день. Меня зовут Сергей,'
                                 'я изучаю курсы программирования Python.')
        context['another_info'] = 'Страница с информацией об Авторе'
        context['git'] = 'https://github.com/Shisui4'
        context['vk'] = 'https://vk.com/shisui4'
        context['inst'] = 'https://www.instagram.com/dash_s4s'
        return context


class AboutTech(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_title'] = 'Информация о Технологиях'
        context['how_i_can'] = 'Вот что я умею (ничего))'
        context['tech'] = 'Python'
        context['tech_two'] = 'Django'
        context['obout_tech'] = 'Прошу прощения, это тестовая(мемная) страница'
        return context
