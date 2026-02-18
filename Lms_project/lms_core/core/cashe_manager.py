from django.core.cache import cache


class CacheManager:

    @staticmethod
    def get(key):
        return cache.get(key)

    @staticmethod
    def set(key, value, timeout=300):
        cache.set(key, value, timeout)

    @staticmethod
    def delete(key):
        cache.delete(key)

    @staticmethod
    def get_or_set(key, queryset, timeout=300):
        data = cache.get(key)

        if data is None:
            data = list(queryset)
            cache.set(key, data, timeout)

        return data
