# rap-conector-client

## Instalação

O cliente é distribuído como um pacote pip tradicional. Para instalar:

```s
$ pip install rap-conector-client
```

### Tabela de compatibilidade

A versão do cliente que deve ser utilizada depende da versão do RAP Conector a ser acessado. O esquema de versionamento segue o formato **vX.Y.Z.A**, onde:
- **X.Y.Z** é referente à versão do RAP Conector. Por exemplo, caso esteja utilizando o RAP Conector v0.11.3, **X.Y.Z** na versão do cliente deve ser 0.11.3.
    - **Obs.:** Caso essa versão não exista no cliente, deve-se utilizar a versão anterior mais próxima.
- **A** é referente à versão do cliente em si. Idealmente deve ser sempre a mais recente.

Por exemplo:

| Versão do RAP Conector | Versão do cliente que deve ser utilizada |
|------------------------|------------------------------------------|
| v0.16.0                | v0.16.0.1                                |
| v0.15.0                | v0.15.0.2                                |
| v0.14.0                | v0.14.0.1                                |
| v0.13.3                | v0.11.3.1                                |
| v0.13.2                | v0.11.3.1                                |
| v0.13.1                | v0.11.3.1                                |
| v0.13.0                | v0.11.3.1                                |
| v0.12.0                | v0.11.3.1                                |
| v0.11.4                | v0.11.3.1                                |
| v0.11.3                | v0.11.3.1                                |
| v0.11.2                | v0.9.0.1                                 |
| v0.11.1                | v0.9.0.1                                 |
| v0.11.0                | v0.9.0.1                                 |
| v0.10.1                | v0.9.0.1                                 |
| v0.10.0                | v0.9.0.1                                 |
| v0.9.0                 | v0.9.0.1                                 |

## Exemplos de uso

### Uso básico do cliente

O ponto de partida para o uso da API é a classe `Client`. A partir dela, é possível por exemplo receber instâncias da classe `Document`:

```python
>>> import rapconector
>>> conector = rapconector.Client('{{ URL_DO_CONECTOR }}/api')
>>> doc = conector.get_document(25)
>>> doc.current_state
503
```

A partir dessa instância, é possível interagir com o documento no Conector:

```python
>>> receipt = doc.get_receipt()
>>> receipt['status']
'preserved'
>>> receipt['group_id']
'350'
```

Caso deseje interagir com um documento sem precisar antes fazer uma requisição
para pegar o objeto do documento, é possível utilizar a função
`with_document_id()` da
classe principal:

```python
>>> conector.with_document_id(39).suspend('Suspendendo o documento com id 39.')
True
```

Além disso, também são disponibilizadas algumas classes de enumeração para melhorar a legibilidade do
código:

```python
>>> from rapconector.document import DocumentStateCode
>>> doc.current_state == DocumentStateCode.ERROR_DURING_SIGNING
True
```

### Download e validação de um arquivo

Por questões de performance, os métodos que interagem com arquivos do Conector
não fornecem suporte a parâmetros do tipo string. Sendo assim, é
necessário passar *file handles* abertos para os métodos que fazem upload, e os
métodos que fazem download de arquivos retornam um objeto
`requests.Response` com a propriedade ``stream=True``, para que a
aplicação tenha controle total sobre o processo de download:

```python
>>> from rapconector.document import DocumentType, DocumentVersion
>>>
>>> res = conector.with_document_id(17).download_file(DocumentVersion.SIGNED)
>>> with open('diploma.xml', 'wb') as f:
>>>     for chunk in res.iter_content(chunk_size=4096):
>>>         f.write(chunk)
>>>
>>> with open('diploma.xml', 'r') as f:
>>>     authenticity = conector.authenticate_document(
>>>         DocumentType.ACADEMIC_DOC_MEC_DEGREE,
>>>             ('diploma.xml', f, 'application/xml'))
>>>
>>> authenticity.valid
True
```

## Documentação

A documentação completa de todas as versões disponíveis do pacote podem ser encontradas [neste link](https://ledgertec.com.br/Jz3JAEOKSLOnaopk/).
