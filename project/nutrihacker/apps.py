from django.apps import AppConfig


class NutrihackerConfig(AppConfig):
    name = 'nutrihacker'
    
    # app initialization
    def ready(self):
        import nutrihacker.signals