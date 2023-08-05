# -*- coding: utf-8 -*-
from requests_toolbelt import MultipartEncoder

from rapconector.utils import parse_or_raise


class Document:
    '''Representação de um documento no Conector.'''
    def __init__(self, client, json):
        # API client, for future requests.
        self._client = client

        #: Identificador do documento.
        self.document_id = json['documentId']

        #: Tipo do documento. Possivelmente nulo. Ver
        #: :class:`DocumentType <DocumentType>` ou
        #: :class:`ExternalDocumentType <ExternalDocumentType>`, dependendo de
        #: onde a instância foi encontrada.
        self.document_type = json.get('documentType')

        #: Identificador do grupo ao qual o documento pertence. Possivelmente
        #: nulo.
        self.group_id = json.get('groupId')

        #: Identificador do documento no contexto do cliente. Possivelmente
        #: nulo.
        self.your_number = json.get('yourNumber')

        #: Código de estado atual do documento. Possivelmente nulo. Ver
        #: :class:`DocumentStateCode <DocumentStateCode>`.
        self.current_state = json.get('currentState')

        #: Código de segurança do documento. Possivelmente nulo.
        self.security_code = json.get('securityCode')

        #: Recibo do documento. Possivelmente nulo.
        self.receipt = json.get('receipt')

        #: Estado de autorização do documento. Possivelmente nulo. Ver
        #: :class:`DocumentAuthorizationState <DocumentAuthorizationState>`.
        self.authorization = json.get('authorization')

    def __repr__(self):
        return '{}(document_id={}, document_type={}, group_id={}, ' \
            'your_number={}, current_state={}, security_code={}, receipt={}, ' \
            'authorization={})' \
            .format(self.__class__.__name__, self.document_id,
            self.document_type, self.group_id, self.your_number,
            str(self.current_state), self.security_code, self.receipt,
            self.authorization)

    def update(self,
               document_type=None,
               document_data=None,
               document_file=None,
               update_description=None):
        '''
        Atualiza o dados de um documento, quais sejam: tipo, JSON com dados
        e/ou arquivo gerado.

        Após atualização, o documento retorna ao estado inicial reniciando sua
        geração/processamento. Documentos com estado de registro válido não são
        afetados por essa operação.

        Nos casos em que um documento já está em estado válido de registro
        (estado 10) ou suspenso, é necessário revogar todo o seu respectivo
        grupo de documentos e reiniciar o processo de registro fazendo a
        inserção de novos documentos na ordem correta.

        :param document_type: Código do tipo do documento.
        :type document_type: :class:`DocumentType <DocumentType>` ou
            :class:`ExternalDocumentType <ExternalDocumentType>`, optional

        :param document_data: Dados do documento (string JSON).
        :type document_data: str, optional

        :param document_file: Arquivo(s) do documento, onde um arquivo é uma
            tupla ``(name (str), file (IOBase), mime_type (str))``
        :type document_file: tuple or list(tuple), optional

        :param update_description: Mensagem de atualização.
        :type update_description: str, optional

        :return: O identificador do documento atualizado.
        :rtype: int
        '''
        fields = {
            'documentType':
            str(document_type) if document_type is not None else None,
            'documentData': document_data,
            'updateDescription': update_description
        }
        if document_file:
            fields['documentFile'] = document_file

        encoder = MultipartEncoder(fields=fields)

        return parse_or_raise(
            self._client.session.put(
                u'{}/documents/{}'.format(self._client.base_url,
                                          self.document_id),
                data=encoder,
                headers={'Content-Type': encoder.content_type}))['documentId']

    def delete(self, cascade=False):
        '''
        Deleta este documento da base de dados do RAP Conector.

        **ATENÇÃO:** Essa operação apaga os registros apenas no Conector local,
        de forma que não deleta documentos preservados no contexto do Serviço
        RAP. Para remoção do(s) documento(s) no contexto do RAP é necessário
        revogá-lo(s) antes de ter seus dados deletados do Conector local.

        :param cascade: Se deve ocorrer remoção em cascata de documentos
            dependentes.
        :type cascade: bool, optional

        :return: Número de documentos removidos.
        :rtype: int
        '''
        return parse_or_raise(
            self._client.session.delete(u'{}/documents/{}?cascade={}'.format(
                self._client.base_url, self.document_id,
                'true' if cascade else 'false'))).get('deletedDocuments', 0)

    def get_state(self):
        '''
        Exibe o estado atual do documento.

        Em caso de erro, suspensão, re-ativação ou revogação de documento, o
        campo aditionalInfo indicará a razão de entrada em cada estado.

        As informações de suspensão, ativação e revogação podem ser utilizadas
        para mapear o histórico do documento conforme previsão na nota técnica
        referente a diplomas digitais: ver item 7.12 da Nota Técnica No.
        13/2019/DIFES/SESU/SESU.

        :rtype: DocumentState
        '''
        json = parse_or_raise(
            self._client.session.get(u'{}/documents/{}/state'.format(
                self._client.base_url, self.document_id)))

        return DocumentState(json['currentState'], json['description'],
                             json['aditionalInfo'], json.get('signatures'))

    def get_history(self):
        '''
        Retorna o histórico de processamento do documento.

        :rtype: list(DocumentStateChange)
        '''
        json = parse_or_raise(
            self._client.session.get(u'{}/documents/{}/history'.format(
                self._client.base_url, self.document_id)))

        return list(
            map(
                lambda x: DocumentStateChange(x['previousState'], x[
                    'currentState'], x['description'], x['timestamp'], x[
                        'aditionalInfo']), json))

    def get_receipt(self):
        '''
        Retorna o recibo do documento. Por exemplo::

            {
                "raw_signatures": [
                    "string"
                ],
                "doc_type": "string",
                "status": "string",
                "dlt_id": "string",
                "group_id": "string",
                "client_id": "string",
                "mime_type": "string",
                "our_number": "string",
                "your_number": "string",
                "client_signature": "string",
                "data": {},
                "register_path": [],
                "created_at": "string",
                "updated_at": "string",
                "__v": int,
                "doc_hash": "string",
                "register_root": "string",
                "tx_date": "string",
                "tx_receipt": "string",
                "UUID": "string",
                "status_detail": "string",
            }

        :rtype: dict
        '''
        return parse_or_raise(
            self._client.session.get(u'{}/documents/{}/receipt'.format(
                self._client.base_url, self.document_id)))

    def download_file(self, version):
        '''
        Faz download de uma versão específica do arquivo do documento em formato
        XML.

        Caso seja indicado
        :class:`DocumentVersion.SIGNED <DocumentVersion.SIGNED>`, o serviço irá
        retornar o estado atual do documento assinado. Caso a coleta de
        assinaturas ainda não tenha sido finalizada, esse documento pode ainda
        não representar o documento final assinado. Recomenda-se seu download
        quando o documento alcançar o status registrado no serviço (estado
        :class:`DocumentStateCode.VALID <DocumentStateCode.VALID>`).

        A chamada desse método com parâmetro ``version`` contendo
        :class:`DocumentVersion.REGISTERED <DocumentVersion.REGISTERED>` faz o
        Conector realizar o download do arquivo diretamente do Serviço de
        Preservação. Esse arquivo só existe após o registro do documento no
        Serviço (estado :class:`DocumentStateCode.VALID
        <DocumentStateCode.VALID>`). O acesso ao arquivo do Serviço de
        Preservação pode ser útil nos casos em que a cópia local foi corrompida.
        Caso a instituição escolha não enviar os documentos para registro, a
        versão de registro do arquivo não existirá.

        :param version: Versão desejada do documento.
        :type version: DocumentVersion

        :return: Um objeto :class:`requests.Response <requests.Response>`, com
            a propriedade ``stream`` setada para ``True``. Para exemplos de como
            realizar o download do arquivo de forma eficiente, ver
            https://stackoverflow.com/a/39217788 e
            https://2.python-requests.org/en/master/user/quickstart/#raw-response-content.
        :rtype: :class:`requests.Response <requests.Response>`
        '''
        return parse_or_raise(self._client.session.get(
            u'{}/documents/{}/files/{}'.format(self._client.base_url,
                                               self.document_id, version),
            stream=True),
                              dont_parse=True)

    def suspend(self, reason):
        '''
        Suspende o documento.

        :param reason: Motivo da suspensão do documento.
        :type reason: str

        :return: Se o documento foi suspenso.
        :rtype: bool
        '''
        return bool(
            parse_or_raise(
                self._client.session.post(u'{}/documents/{}/suspend'.format(
                    self._client.base_url, self.document_id),
                                          data={'reason': reason}))['message'])

    def activate(self, reason):
        '''
        Ativa o documento.

        :param reason: Motivo da re-ativação do documento.
        :type reason: str

        :return: Se o documento foi re-ativado.
        :rtype: bool
        '''
        return bool(
            parse_or_raise(
                self._client.session.post(u'{}/documents/{}/activate'.format(
                    self._client.base_url, self.document_id),
                                          data={'reason': reason}))['message'])

    def revoke(self, reason):
        '''
        Revoga um documento no contexto do Conector e no contexto do Serviço
        RAP.

        :param reason: Motivo da revogação do documento.
        :type reason: str

        :return: Se o documento foi marcado como "irá ser revogado".
        :rtype: bool
        '''
        return bool(
            parse_or_raise(
                self._client.session.post(u'{}/documents/{}/revoke'.format(
                    self._client.base_url, self.document_id),
                                          data={'reason': reason}))['message'])

    def retry_processing(self, step=None):
        '''
        Caso o documento esteja em um estado de falha, tenta reiniciar a etapa
        desejada do processamento.

        :param step: Qual etapa para re-executar. Caso omitido, a etapa tentará
            ser inferida a partir do ``current_state`` do documento.
        :type step:
            :class:`DocumentProcessingStep <DocumentProcessingStep>`, optional

        :return: ``True`` em caso de sucesso.
        :rtype: bool
        '''
        if not step:
            cur_state = self.current_state if self.current_state is not None \
                else 0

            # If no errors, bail.
            if (DocumentStateCode.UNKNOWN < cur_state <
                    DocumentStateCode.ERROR_DURING_CREATION_PREPARATION):
                return None

            # Figure out latest step we can retry from.
            if cur_state == DocumentStateCode.UNKNOWN:
                step = 'restart-processing'
            elif cur_state < DocumentStateCode.ERROR_DURING_SIGNING_STARTING:
                step = 'retry-generation'
            elif cur_state < DocumentStateCode.ERROR_DURING_REGISTRATION:
                step = 'retry-signature'
            elif cur_state == DocumentStateCode.ERROR_DURING_REVOCATION:
                step = 'retry-revocation'
            elif cur_state >= DocumentStateCode.ERROR_DURING_REGISTRATION:
                step = 'retry-registration'
            else:
                step = 'restart-processing'

        return bool(
            parse_or_raise(
                self._client.session.post(
                    u'{}/documents/{}/{}'.format(self._client.base_url,
                                                 self.document_id,
                                                 step), ))['message'])

    def set_authorization(self, desired_auth_status, description):
        '''
        Atualiza o estado de autorização de um documento para permitir ou
        proibir a assinatura e registro de um documento após a revisão manual
        do arquivo gerado pelo Conector.

        Atenção: documentos com a revisão manual desativada terão seu estado de
        autorização atualizado para authorized automaticamente pelo Conector.

        :param desired_auth_status: Estado de autorização desejado.
        :type desired_auth_status: :class:`DocumentAuthorizationState <DocumentAuthorizationState>`

        :param description: Descrição textual para o novo estado de autorização.
        :type description: str

        :return: ``True`` em caso de sucesso.
        :rtype: bool
        '''
        parse_or_raise(
            self._client.session.patch(
                '{}/documents/{}/authorization'.format(self._client.base_url,
                                                       self.document_id),
                json={
                    "documentAuthorization": desired_auth_status,
                    "authorizationDescription": description
                }))

        return True


class DocumentAuthenticityResult:
    '''
    Resultado da autenticação de um documento.

    Observação: o único campo que tem garantia de estar preenchido é o campo
    ``valid`` os outros campos podem ou não estar preenchidos, de acordo com a
    validade do documento.
    '''
    def __init__(self, json):
        #: Identificador da blockchain em que o documento está registrado.
        self.dlt_id = json.get('dlt_id')

        #: Código do recibo da transação de registro do documento na blockchain
        #: escolhida.
        self.tx_receipt = json.get('tx_receipt')

        #: Hash do documento registrado na blockchain.
        self.doc_hash = json.get('doc_hash')

        #: Booleano que indica se o status do documento é válido no serviço RAP.
        self.valid = json.get('valid')

        #: Raiz da estrutura de dados utilizada para registro do documento na
        #: blockchain.
        self.register_root = json.get('register_root')

        #: Identificador da instituição no serviço RAP.
        self.client_id = json.get('client_id')

        #: Identificador único do documento no serviço RAP.
        self.your_number = json.get('your_number')

        #: Data e hora de registro do documento na blockchain (timestamp Unix).
        self.register_date = json.get('register_date')

        #: Número de confirmações da transação de registro do documento na
        #: blockchain.
        self.confirmations = json.get('confirmations')

        #: Data e hora da revogação do documento na blockchain (timestamp Unix).
        self.revocation_date = json.get('revocation_date')

    def __repr__(self):
        return '{}(dlt_id={}, tx_receipt={}, doc_hash={}, valid={}, ' \
                'register_root={}, client_id={}, your_number={}, ' \
                    'register_date={}, confirmations={}, ' \
                        'revocation_date={})'.format(
            self.__class__.__name__,
            self.dlt_id,
            self.tx_receipt,
            self.doc_hash,
            self.valid,
            self.register_root,
            self.client_id,
            self.your_number,
            self.register_date,
            self.confirmations,
            self.revocation_date
        )


class DocumentGroup:
    '''Representação de um grupo de documentos.'''
    def __init__(self, json):
        #: String de identificação do grupo.
        self.group_id = json.get('groupId')

        #: Documentos pertencentes ao grupo, representados por uma lista de
        #: dicionários contendo as chaves ``document_id`` e ``document_type``.
        self.document_stubs = [{
            'document_id': x.get('documentId'),
            'document_type': x.get('documentType')
        } for x in json.get('documents')]

    def __repr__(self):
        return '{}(group_id={}, document_stubs={})'.format(
            self.__class__.__name__, self.group_id, self.document_stubs)


class DocumentProcessingStep:
    '''Enumeração das possíveis etapas de processamento para re-executar.'''
    #: Para re-executar o processamento de um documento.
    PROCESSING = 'restart-processing'

    #: Para re-executar o processo de geração de um documento.
    GENERATION = 'retry-generation'

    #: Para re-executar o processo de assinatura de um documento.
    SIGNATURE = 'retry-signature'

    #: Para re-executar o processo de revogação de um documento.
    REVOCATION = 'retry-revocation'

    #: Para re-executar o processo de registro de um documento.
    REGISTRATION = 'retry-registration'


class DocumentSignature:
    '''Representação de uma assinatura em um documento.'''
    def __init__(self, json):
        #: Nome do assinante.
        self.signer = json.get('signer')

        #: Identificador do assinante.
        self.signer_id = json.get('signerId')

        #: Tag da assinatura.
        self.tag = json.get('tag')

        #: Estado da assinatura. Ver
        #: :class:`DocumentSignatureState <DocumentSignatureState>`.
        self.state = json.get('signatureState')

        #: Se a assinatura é uma assinatura de arquivamento.
        self.archiving_signature = bool(json.get('archivingSignature'))

        #: Nome do assinante substituto, caso exista.
        self.substitute_signer = json.get('substituteSigner').get('name') if \
            json.get('substituteSigner') else None

        #: Estado da assinatura substituta, caso exista. Ver
        #: :class:`DocumentSignatureState <DocumentSignatureState>`.
        self.substitute_signature_state = json \
            .get('substituteSigner').get('signatureState') if \
            json.get('substituteSigner') else None

    def __repr__(self):
        return '{}(signer={}, signer_id={}, tag={}, state={}, archiving_signature={}, ' \
            'substitute_signer={}, substitute_signature_state={})'.format(
                self.__class__.__name__, self.signer, self.signer_id, self.tag,
                str(self.state), str(self.archiving_signature),
                self.substitute_signer, str(self.substitute_signature_state))


class DocumentSignatureState:
    '''
    Enumeração dos possíveis estados de uma
    :class:`DocumentSignature <DocumentSignature>`.
    '''
    #: Não assinado.
    NOT_SIGNED = 0

    #: Assinatura em processamento, no caso da assinatura principal.
    PROCESSING = 1

    #: Assinatura substituta concluída.
    SUBSTITUTE_PROCESSING = 1

    #: Assinatura concluída.
    SIGNED = 2


class DocumentState:
    '''Representação do estado atual do processamento de um documento.'''
    def __init__(self, current_state, description, additional_info,
                 signatures):
        #: Código de estado atual do documento. Ver
        #: :class:`DocumentStateCode <DocumentStateCode>`.
        self.current_state = current_state

        #: Descrição textual do estado atual do documento.
        self.description = description

        #: Informações adicionais sobre o estado atual do documento.
        self.additional_info = additional_info

        #: Assinaturas do documento. Ver
        #: :class:`DocumentSignature <DocumentSignature>`.
        self.signatures = [DocumentSignature(s) for s in signatures] \
            if signatures else None

    def __repr__(self):
        return '{}(current_state={}, description={}, additional_info={}, ' \
            'signatures={})'.format(
            self.__class__.__name__, str(self.current_state), self.description,
            self.additional_info, str(self.signatures))


class DocumentStateChange:
    '''Representação do histórico de processamento de um documento.'''
    def __init__(self, previous_state, current_state, description, timestamp,
                 additional_info):
        #: Código de estado anterior do documento. Ver
        #: :class:`DocumentStateCode <DocumentStateCode>`.
        self.previous_state = previous_state

        #: Código de estado atual do documento. Ver
        #: :class:`DocumentStateCode <DocumentStateCode>`.
        self.current_state = current_state

        #: Timestamp (str) referente à mudança de estado do documento.
        self.timestamp = timestamp

        #: Descrição textual do estado do documento.
        self.description = description

        #: Informações adicionais sobre o estado do documento.
        self.additional_info = additional_info

    def __repr__(self):
        return '{}(previous_state={}, current_state={}, description={}, ' \
                'timestamp={}, additional_info={})'.format(
                self.__class__.__name__, str(self.previous_state),
                str(self.current_state), self.description, self.timestamp,
                self.additional_info)


class DocumentStateCode:
    '''Enumeração dos possíveis estados de um :class:`Document <Document>`.'''
    # yapf: disable
    # Empty state
    UNKNOWN = 0 #: Desconhecido

    # Success states
    READY_TO_CREATE = 1 #: Pronto para gerar
    CREATED = 2 #: Gerado

    SIGNING_STARTING = 3 #: Iniciando assinatura
    SIGNING_STARTED = 4 #: Assinatura iniciada
    SIGNING_IN_PROGRESS = 5 #: Assinando documento
    SIGNED = 6 #: Documento assinado

    READY_FOR_REGISTRATION = 7 #: Pronto para registrar
    REGISTRATION_STARTED = 8 #: Registro iniciado
    REGISTRATION_FINISHED = 9 #: Processo finalizado

    VALID = 10 #: Documento válido
    SUSPENDED = 11 #: Documento suspenso

    REVOCATION_STARTED = 12 #: Iniciando revogação
    REVOCATION_IN_PROGRESS = 13 #: Revogando
    REVOKED = 14 #: Documento revogado

    # Error states
    ERROR_DURING_CREATION_PREPARATION = 500 #: Erro ao preparar a geração
    ERROR_DURING_CREATION = 501 #: Erro na geração

    ERROR_DURING_SIGNING_STARTING = 502 #: Erro ao iniciar a assinatura
    ERROR_DURING_SIGNING = 503 #: Erro ao assinar o documento

    ERROR_DURING_REGISTRATION = 504 #: Erro ao iniciar o registro
    ERROR_FINISHING_REGISTRATION = 505 #: Erro ao finalizar o registro

    ERROR_DURING_REVOCATION = 506 #: Erro na revogação
    # yapf: enable


class DocumentType:
    '''Enumeração dos possíveis tipos de um :class:`Document <Document>`.'''
    #: Diploma digital. Equivalente a ``digital_degree``.
    DIGITAL_DEGREE = 2

    #: Histórico escolar final. Equivalente a ``final_academic_transcript``.
    FINAL_ACADEMIC_TRANSCRIPT = 3

    #: Documentação acadêmica. Equivalente a ``academic_doc_mec_degree``.
    ACADEMIC_DOC_MEC_DEGREE = 4

    #: Representação visual. Equivalente a ``visual_rep_degree``.
    VISUAL_REP_DEGREE = 5


class ExternalDocumentType:
    '''Enumeração dos possíveis tipos de um :class:`Document <Document>`.'''
    #: Diploma externo. Equivalente a ``external_degree``.
    EXTERNAL_DEGREE = 6

    #: Documentação acadêmica externa. Equivalente a ``external_academic_doc``.
    EXTERNAL_ACADEMIC_DOC = 7


class DocumentVersion:
    '''Enumeração das possíveis versões de um arquivo.'''
    # yapf: disable
    GENERATED = 'generatedDocument' #: Versão gerada do documento.
    SIGNED = 'signedDocument' #: Versão assinada do documento.
    REGISTERED = 'registeredDocument' #: Versão registrada do documento.
    # yapf: enable


class DocumentAuthorizationState:
    '''Enumeração dos possíveis estados de autorização de um documento.'''
    # yapf: disable
    AUTHORIZED = 'authorized' #: Autorizado.
    UNAUTHORIZED = 'unauthorized' #: Não-autorizado.
    AWAITING = 'awaiting' #: Aguardando.
    # yapf: enable
