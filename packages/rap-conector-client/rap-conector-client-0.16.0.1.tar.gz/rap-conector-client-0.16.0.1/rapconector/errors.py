# -*- coding: utf-8 -*-


class AuthenticationError(Exception):
    '''Credenciais de autenticação incorretas fornecidas ao Conector.'''


class NotFoundError(Exception):
    '''Objeto não encontrado no Conector.'''


class ServerError(Exception):
    '''Erro inesperado no servidor do Conector.'''
