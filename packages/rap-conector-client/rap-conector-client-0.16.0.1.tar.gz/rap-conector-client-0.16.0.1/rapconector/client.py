# -*- coding: utf-8 -*-
import platform

import requests
from requests_toolbelt import MultipartEncoder

from rapconector.document import (Document, DocumentAuthenticityResult,
                                  DocumentGroup, ExternalDocumentType)
from rapconector.utils import parse_or_raise, rewrite_docstring_for_external_client
from rapconector.session import Session
from rapconector.version import VERSION_STR


class Client():
    '''Cliente da API.'''
    def __init__(self, base_url, *args, **kwargs):
        '''
        Observação: qualquer parâmetro não listado abaixo será repassado
        diretamente para o construtor do :class:`requests.Session
        <requests.Session>`.

        :param base_url: URL do conector.
        :type base_url: str

        :param email: E-mail para autenticação.
        :type email: str, optional

        :param password: Senha para autenticação.
        :type password: str, optional

        :param default_timeout: Timeout padrão para ser utilizado em todas as
            requisições.
        :type default_timeout: number, optional

        :return: Instância da classe.
        '''

        # ":rtype: Client" was removed from docstring for now - don't want to
        # copy-paste this entire thing just so ExternalClient looks correct on
        # the autodocs

        # Save credentials.
        email, password = None, None
        if 'email' in kwargs:
            email = kwargs['email']
            del kwargs['email']

        if 'password' in kwargs:
            password = kwargs['password']
            del kwargs['password']

        use_auth = bool(email and password)
        self.email = email
        self.password = password

        # Create either a wrapped or a regular requests session, depending on if
        # we need to intercept requests to authenticate them beforehand.
        self.session = Session(_rapconector_client=self, *args, **
                               kwargs) if use_auth else requests.session(
                                   *args, **kwargs)
        self.base_url = base_url[:-1] if base_url[-1] == '/' else base_url

        # For information gathering.
        self.session.headers.update({
            'User-Agent':
            'RAPConector Python{} Client (v{})'.format(
                platform.python_version(), VERSION_STR)
        })

    def with_document_id(self, document_id):
        '''
        Retorna uma instância de :class:`Document
        <rapconector.document.Document>` com somente o campo ``document_id``
        preenchido. Útil para evitar requisições adicionais. Por exemplo::

            # 2 requisições: uma para get_document() e outra para get_receipt()
            receipt = conector.get_document(372).get_receipt()

            # 1 única requisição, pois `with_document_id` cria um objeto vazio
            receipt = conector.with_document_id(372).get_receipt()

        :param document_id: Identificador do documento.
        :type document_id: int

        :rtype: Document
        '''
        return Document(self, {'documentId': document_id})

    def get_group(self, group_id):
        '''
        Exibe as informações básicas de um grupo de documentos, incluindo os
        slots ocupados e disponíveis para a inserção de novos documentos.

        **IMPORTANTE:**: Novos documentos só devem ser inseridos em grupos
        parcialmente ocupados caso o documento seja do tipo do slot disponível e
        que contenha dados complementares aos demais documentos.

        :param group_id: Identificador do grupo de documentos.
        :type group_id: str

        :return: O documento especificado, caso exista. ``None`` caso contrário.
        :rtype: Document
        '''
        json = parse_or_raise(self.session.get(self.base_url +
                                               '/groups/{}'.format(group_id)),
                              raise_for_404=False)

        if not json:
            return None

        return DocumentGroup(json)

    def list_groups(self, page=None, limit=None):
        '''
        Lista todos os grupos de documentos, incluindo seus slots ocupados e
        disponíveis para a inserção de novos documentos.

        **IMPORTANTE:**: Novos documentos só devem ser inseridos em grupos
        parcialmente ocupados caso o documento seja do tipo do slot disponível e
        que contenha dados complementares aos demais documentos.

        :param page: Número da página utilizada na paginação dos resultados.
        :type page: int, optional

        :param limit: Quantos items retornar por página.
        :type limit: int, optional

        :return: Lista de grupos de documentos.
        :rtype: list(DocumentGroup)
        '''
        json = parse_or_raise(
            self.session.get(self.base_url + '/groups',
                             params={
                                 'page': page,
                                 'limit': limit
                             }))

        return list(map(DocumentGroup, json))

    def delete_group(self, group_id):
        '''
        Deleta um grupo de documentos da base de dados do Conector, incluindo
        todos os documentos nele contidos.

        **IMPORTANTE:** Essa operação apaga apenas os documentos do registro
        local, de forma que não deleta os documentos preservados no registro do
        Serviço RAP. Para a remoção dos documentos do registro do RAP é
        necessário revogá-los antes deletar os dados no Conector.

        :param group_id: Identificador do grupo de documentos a ser removido.
        :type group_id: str

        :return: Número de documentos removidos.
        :rtype: int
        '''
        # NOTE: for consistency with the rest of the lib design, this should be
        # a "delete()" method in the DocumentGroup class. consider refactoring
        return parse_or_raise(
            self.session.delete(u'{}/groups/{}'.format(
                self.base_url, group_id))).get('deletedDocuments', 0)

    def get_document(self, id_or_security_code):
        '''
        Exibe as informações básicas de um documento, incluindo o código de
        segurança que se torna disponível após o documento ser gerado e o
        recibo após o documento ser registrado.

        Cada documento possui um código de segurança baseado no seu contexto. No
        caso do Diploma Digital esse código de segurança é o Código de Validação
        do Diploma.

        :param id_or_security_code: Identificador ou código de segurança do
            documento.
        :type id_or_security_code: int or str

        :return: O documento especificado.
        :rtype: Document
        '''
        json = parse_or_raise(self.session.get(self.base_url + u'/documents/' +
                                               str(id_or_security_code)),
                              raise_for_404=False)

        if not json:
            return None

        return Document(self, json)

    # Private method: Regular client needs to filter out external doc_type, but
    # external client must filter _only_by external doc_type, so shouldn't have
    # the method at all. Both of them end up calling this method internally.
    def _list_documents(self,
                        state=None,
                        document_type=None,
                        cpf=None,
                        page=None,
                        limit=None):
        json = parse_or_raise(
            self.session.get(self.base_url + u'/documents',
                             params={
                                 'state': state,
                                 'type': document_type,
                                 'cpf': cpf,
                                 'page': page,
                                 'limit': limit
                             }))

        return list(map(lambda doc: Document(self, doc), json))

    def list_documents(self,
                       state=None,
                       document_type=None,
                       cpf=None,
                       page=None,
                       limit=None):
        '''
        Lista todos os documentos processados pelo RAP Conector, indicando para
        cada documento o seu estado atual.

        :param state: Código de estado para utilizar como filtro. O retorno
            incluirá todos os documentos que já passaram pelo estado
            especificado. Nesse contexto, ``currentState`` representa o estado
            corrente da consulta e não o estado atual do documento.
        :type state: DocumentStateCode, optional

        :param document_type: Tipo de documento, para utilizar como filtro.
        :type document_type: DocumentType, optional

        :param cpf: CPF do diplomado, para utilizar como filtro.
        :type cpf: str, optional

        :param page: Número da página utilizada na paginação dos resultados.
        :type page: int, optional

        :param limit: Quantos items retornar por página.
        :type limit: int, optional

        :return: Lista de documentos.
        :rtype: list(Document)
        '''
        docs = self._list_documents(state=state,
                                    document_type=document_type,
                                    cpf=cpf,
                                    page=page,
                                    limit=limit)

        return list(
            filter(
                lambda doc: doc.document_type not in [
                    ExternalDocumentType.EXTERNAL_ACADEMIC_DOC,
                    ExternalDocumentType.EXTERNAL_DEGREE
                ], docs))

    def insert_document(self,
                        document_type,
                        document_data,
                        document_file=None):
        '''
        Insere um novo documento ou um lote de documentos.

        **IMPORTANTE:** As etapas de processamento dos documentos possuem uma
        ordem lógica bem definida que deve ser respeitada. Inicialmente deve ser
        gerada, assinada e registrada a Documentação Acadêmica. Após isso, deve
        ser gerado, assinado e registrado o Diploma Digital associado. Por
        último (opcionalmente) pode ser processada a Representação Visual do
        Diploma.

        **IMPORTANTE:** Os arquivos PDF anexados em base64 no JSON da
        Documentação Acadêmica ou inseridos no campo ``document_file`` para a
        Representação Visual, devem estar preferencialmente no formato de
        preservação PDF/A (www.pdfa.org). Caso algum arquivo esteja no formato
        PDF comum, o Conector tentará a conversão automática que se for
        malsucedida, fará com que o documento entre no estado de erro de
        geração.

        :param document_type: Código do tipo do documento.
        :type document_type:
            :class:`DocumentType <rapconector.document.DocumentType>`

        :param document_data: Dados e metadados do documento, em formato JSON.
            No caso da inserção em lote, o JSON esperado é um array onde cada
            item representa (e obedece o schema) da inserção de um único
            documento. Caso o lote seja do tipo
            :class:`DocumentType.VISUAL_REP_DEGREE
            <rapconector.document.DocumentType.VISUAL_REP_DEGREE>`, deve ser
            adicionado nos metadados de cada documento o atributo ``attachment``
            contendo o nome e a extensão do arquivo utilizado no parâmetro
            ``document_file`` para que a representação visual do diploma seja
            associada ao documento correspondente.
        :type document_data: str

        :param document_file: Arquivo(s) do documento, onde um arquivo é uma
            tupla ``name (str), file (IOBase), mime_type (str)``.
        :type document_file: tuple or list(tuple), optional

        :return: O identificador do documento inserido, ou uma lista de
            identificadores no caso da inserção em lote.
        :rtype: int or list(int)
        '''
        fields = {
            'documentData': document_data,
            'documentType': str(document_type)
        }
        if document_file:
            fields['documentFile'] = document_file

        encoder = MultipartEncoder(fields=fields)

        parsed_res = parse_or_raise(
            self.session.post(u'{}/documents'.format(self.base_url),
                              data=encoder,
                              headers={'Content-Type': encoder.content_type}))

        if isinstance(parsed_res, list):
            return [x['documentId'] for x in parsed_res]
        return parsed_res['documentId']

    def retrieve_file(self, document_type, client_id, your_number):
        '''
        Recupera o arquivo de um documento diretamente do Serviço de Preservação
        usando os metadados do documento preservado.

        :param document_type: Código do tipo do documento.
        :type document_type:
            :class:`DocumentType <rapconector.document.DocumentType>`

        :param client_id: Identificador da instituição cliente.
        :type client_id: string

        :param your_number: Identificador do documento no contexto do cliente.
        :type your_number: string

        :return: Um objeto :class:`requests.Response <requests.Response>`, com
            a propriedade ``stream`` setada para ``True``. Para exemplos de como
            realizar o download do arquivo de forma eficiente, ver
            https://stackoverflow.com/a/39217788 e
            https://2.python-requests.org/en/master/user/quickstart/#raw-response-content.
        :rtype: :class:`requests.Response <requests.Response>`
        '''
        return parse_or_raise(self.session.get(
            self.base_url + u'/documents/retrieve',
            params={
                'documentType': document_type,
                'clientId': client_id,
                'yourNumber': your_number
            },
            stream=True),
                              dont_parse=True)

    def authenticate_document(self, document_type, document_file):
        '''
        Verifica a autenticidade de um documento no contexto do registro do
        Serviço RAP.

        :param document_type: Código do tipo do documento.
        :type document_type:
            :class:`DocumentType <rapconector.document.DocumentType>`

        :param document_file: Arquivo para verificar, onde um arquivo é uma
            tupla ``(name (str), file (IOBase), mime_type (str))``.
        :type document_file: tuple or list(tuple), optional

        :rtype: DocumentAuthenticityResult
        '''
        json = parse_or_raise(
            self.session.post(self.base_url + u'/documents/authenticate',
                              data={'documentType': document_type},
                              files={'documentFile': document_file}))

        return DocumentAuthenticityResult(json)

    def healthcheck(self):
        '''
        Retorna dados sobre a saúde do serviço. Por exemplo::

            {
                "status": "pass",
                "version": "1",
                "releaseId": "0.7.8",
                "checks": {
                    "conector": [
                        {
                            "status": "pass",
                            "version": "0.7.8"
                        }
                    ],
                    "RAP": [
                        {
                            "status": "pass",
                            "version": "1.0.0"
                        }
                    ],
                    "database": [
                        {
                            "status": "pass"
                        }
                    ]
                }
            }

        :return: Objeto JSON contendo informações sobre o estado do serviço.
        :rtype: dict
        '''
        return parse_or_raise(self.session.get(self.base_url + u'/health'))


class ExternalClient(Client):
    '''Cliente da API, para diplomas digitais externos.'''
    def list_documents(self,
                       state=None,
                       document_type=None,
                       cpf=None,
                       page=None,
                       limit=None):
        '''
        Lista todos os documentos processados pelo RAP Conector, indicando para
        cada documento o seu estado atual.

        :param state: Código de estado para utilizar como filtro. O retorno
            incluirá todos os documentos que já passaram pelo estado
            especificado. Nesse contexto, ``currentState`` representa o estado
            corrente da consulta e não o estado atual do documento.
        :type state: DocumentStateCode, optional

        :param document_type: Tipo de documento, para utilizar como filtro.
        :type document_type: ExternalDocumentType, optional

        :param cpf: CPF do diplomado, para utilizar como filtro.
        :type cpf: str, optional

        :param page: Número da página utilizada na paginação dos resultados.
        :type page: int, optional

        :param limit: Quantos items retornar por página.
        :type limit: int, optional

        :return: Lista de documentos.
        :rtype: list(Document)
        '''
        docs = self._list_documents(state=state,
                                    document_type=document_type,
                                    cpf=cpf,
                                    page=page,
                                    limit=limit)

        return list(
            filter(
                lambda doc: doc.document_type in [
                    ExternalDocumentType.EXTERNAL_ACADEMIC_DOC,
                    ExternalDocumentType.EXTERNAL_DEGREE
                ], docs))

    def insert_document(self,
                        document_type,
                        document_data,
                        document_file=None):
        '''
        Insere um novo documento ou um lote de documentos.

        **IMPORTANTE:** As etapas de processamento dos documentos possuem uma
        ordem lógica bem definida que deve ser respeitada. Inicialmente deve ser
        gerada, assinada e registrada a Documentação Acadêmica Externa. Em
        seguida, deve ser gerado, assinado e registrado o Diploma Digital
        Externo associado.

        :param document_type: Código do tipo do documento.
        :type document_type:
            :class:`ExternalDocumentType <rapconector.document.ExternalDocumentType>`

        :param document_data: Dados e metadados do documento, em formato JSON.
            No caso da inserção em lote, o JSON esperado é um array onde cada
            item representa (e obedece o schema) da inserção de um único
            documento. Caso o documento seja do tipo
            :class:`ExternalDocumentType.EXTERNAL_ACADEMIC_DOC
            <rapconector.document.ExternalDocumentType.EXTERNAL_ACADEMIC_DOC>`,
            deve ser passado no parâmetro ``document_file`` o arquivo XML
            assinado da Documentação Acadêmica.
        :type document_data: str

        :param document_file: Arquivo(s) do documento, onde um arquivo é uma
            tupla ``name (str), file (IOBase), mime_type (str)``.
        :type document_file: tuple or list(tuple), optional

        :return: O identificador do documento inserido, ou uma lista de
            identificadores no caso da inserção em lote.
        :rtype: int or list(int)
        '''
        return super().insert_document(document_type,
                                       document_data,
                                       document_file=document_file)


# Some docstrings in the Client refer to DocumentType, but for the
# ExternalClient we need them to refer to ExternalDocumentType instead. We
# programatically rewrite these references here. Does not work for Py2.
if int(platform.python_version_tuple()[0]) > 2:
    methods = [
        ExternalClient.authenticate_document, ExternalClient.retrieve_file
    ]
    for method in methods:
        method.__doc__ = rewrite_docstring_for_external_client(method.__doc__)
