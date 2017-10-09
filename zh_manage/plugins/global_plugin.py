# -*- coding: utf-8 -*-


class global_plugin():
    def apply(self, func, config):
        def wrapper(*a, **ka):
            return func(*a, **ka)

        return wrapper
