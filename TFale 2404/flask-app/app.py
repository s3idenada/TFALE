from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
from flasgger import Swagger, swag_from

app = Flask(__name__)

# Configuração do Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger_template = {
    "info": {
        "title": "API de Gerenciamento Escolar",
        "description": "API para gerenciamento de alunos e recursos escolares",
        "contact": {
            "name": "Equipe de Desenvolvimento",
            "email": "dev@escola.com"
        },
        "version": "1.0.0"
    },
    "schemes": ["http", "https"],
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="aula2003",  # Nome do container Docker PostgreSQL
            database="escola",
            user="postgres",
            password="postgres"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

@app.route('/alunos', methods=['GET'])
@swag_from({
    'tags': ['Alunos'],
    'summary': 'Retorna a lista de todos os alunos',
    'description': 'Endpoint para obter todos os alunos cadastrados no sistema',
    'responses': {
        200: {
            'description': 'Lista de alunos recuperada com sucesso',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id_aluno': {'type': 'integer', 'description': 'ID único do aluno'},
                        'nome_completo': {'type': 'string', 'description': 'Nome completo do aluno'},
                        'data_nascimento': {'type': 'string', 'format': 'date', 'description': 'Data de nascimento do aluno'},
                        'id_turma': {'type': 'integer', 'description': 'ID da turma do aluno'},
                        'nome_responsavel': {'type': 'string', 'description': 'Nome do responsável pelo aluno'},
                        'telefone_responsavel': {'type': 'string', 'description': 'Telefone do responsável'},
                        'email_responsavel': {'type': 'string', 'description': 'Email do responsável'},
                        'informacoes_adicionais': {'type': 'string', 'description': 'Informações adicionais sobre o aluno'}
                    }
                }
            },
            'examples': {
                'application/json': [
                    {
                        'id_aluno': 1,
                        'nome_completo': 'João da Silva',
                        'data_nascimento': '2010-05-15',
                        'id_turma': 3,
                        'nome_responsavel': 'Maria da Silva',
                        'telefone_responsavel': '(11) 98765-4321',
                        'email_responsavel': 'maria@exemplo.com',
                        'informacoes_adicionais': 'Alergia a amendoim'
                    }
                ]
            }
        },
        500: {
            'description': 'Erro ao conectar ao banco de dados',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            },
            'examples': {
                'application/json': {'error': 'Falha ao conectar ao banco de dados'}
            }
        }
    }
})
def listar_alunos():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Falha ao conectar ao banco de dados'}), 500
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute('SELECT * FROM Aluno;')
        alunos = cur.fetchall()
        result = [dict(aluno) for aluno in alunos]  # Converte os dados para dict
    except psycopg2.Error as e:
        return jsonify({'error': f'Erro ao consultar dados: {e}'}), 500
    finally:
        cur.close()
        conn.close()
    
    return jsonify(result), 200

@app.route('/alunos', methods=['POST'])
@swag_from({
    'tags': ['Alunos'],
    'summary': 'Cadastra um novo aluno',
    'description': 'Endpoint para cadastrar um novo aluno no sistema',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'Dados do aluno a ser cadastrado',
            'schema': {
                'type': 'object',
                'required': ['nome_completo'],
                'properties': {
                    'nome_completo': {'type': 'string', 'description': 'Nome completo do aluno'},
                    'data_nascimento': {'type': 'string', 'format': 'date', 'description': 'Data de nascimento do aluno'},
                    'id_turma': {'type': 'integer', 'description': 'ID da turma do aluno'},
                    'nome_responsavel': {'type': 'string', 'description': 'Nome do responsável pelo aluno'},
                    'telefone_responsavel': {'type': 'string', 'description': 'Telefone do responsável'},
                    'email_responsavel': {'type': 'string', 'description': 'Email do responsável'},
                    'informacoes_adicionais': {'type': 'string', 'description': 'Informações adicionais sobre o aluno'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Aluno cadastrado com sucesso',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'id_aluno': {'type': 'integer'}
                }
            },
            'examples': {
                'application/json': {'message': 'Aluno cadastrado com sucesso!', 'id_aluno': 1}
            }
        },
        400: {
            'description': 'Dados inválidos',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            },
            'examples': {
                'application/json': {'error': 'O campo "nome_completo" é obrigatório'}
            }
        },
        500: {
            'description': 'Erro ao conectar ao banco de dados ou inserir dados',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def cadastrar_aluno():
    novo_aluno = request.json
    
    # Validação básica
    if not novo_aluno or not novo_aluno.get('nome_completo'):
        return jsonify({'error': 'O campo "nome_completo" é obrigatório'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Falha ao conectar ao banco de dados'}), 500

    cur = conn.cursor()
    try:
        cur.execute(
            '''INSERT INTO Aluno (nome_completo, data_nascimento, id_turma, nome_responsavel, telefone_responsavel, email_responsavel, informacoes_adicionais)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_aluno''',
            (novo_aluno.get('nome_completo'),
             novo_aluno.get('data_nascimento'),
             novo_aluno.get('id_turma'),
             novo_aluno.get('nome_responsavel'),
             novo_aluno.get('telefone_responsavel'),
             novo_aluno.get('email_responsavel'),
             novo_aluno.get('informacoes_adicionais'))
        )
        aluno_id = cur.fetchone()[0]
        conn.commit()
    except psycopg2.Error as e:
        return jsonify({'error': f'Erro ao inserir dados: {e}'}), 500
    finally:
        cur.close()
        conn.close()
    
    return jsonify({'message': 'Aluno cadastrado com sucesso!', 'id_aluno': aluno_id}), 201

@app.route('/alunos/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['Alunos'],
    'summary': 'Atualiza os dados de um aluno',
    'description': 'Endpoint para atualizar os dados de um aluno existente',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do aluno a ser atualizado'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'Novos dados do aluno',
            'schema': {
                'type': 'object',
                'properties': {
                    'nome_completo': {'type': 'string', 'description': 'Nome completo do aluno'},
                    'data_nascimento': {'type': 'string', 'format': 'date', 'description': 'Data de nascimento do aluno'},
                    'id_turma': {'type': 'integer', 'description': 'ID da turma do aluno'},
                    'nome_responsavel': {'type': 'string', 'description': 'Nome do responsável pelo aluno'},
                    'telefone_responsavel': {'type': 'string', 'description': 'Telefone do responsável'},
                    'email_responsavel': {'type': 'string', 'description': 'Email do responsável'},
                    'informacoes_adicionais': {'type': 'string', 'description': 'Informações adicionais sobre o aluno'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Aluno atualizado com sucesso',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'id_aluno': {'type': 'integer'}
                }
            },
            'examples': {
                'application/json': {'message': 'Aluno atualizado com sucesso!', 'id_aluno': 1}
            }
        },
        404: {
            'description': 'Aluno não encontrado',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            },
            'examples': {
                'application/json': {'error': 'Aluno não encontrado'}
            }
        },
        500: {
            'description': 'Erro ao conectar ao banco de dados ou atualizar dados',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def atualizar_aluno(id):
    dados_atualizados = request.json

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Falha ao conectar ao banco de dados'}), 500

    cur = conn.cursor()
    try:
        cur.execute(
            '''UPDATE Aluno
               SET nome_completo = %s, data_nascimento = %s, id_turma = %s, nome_responsavel = %s, telefone_responsavel = %s, email_responsavel = %s, informacoes_adicionais = %s
               WHERE id_aluno = %s RETURNING id_aluno''',
            (dados_atualizados.get('nome_completo'),
             dados_atualizados.get('data_nascimento'),
             dados_atualizados.get('id_turma'),
             dados_atualizados.get('nome_responsavel'),
             dados_atualizados.get('telefone_responsavel'),
             dados_atualizados.get('email_responsavel'),
             dados_atualizados.get('informacoes_adicionais'),
             id)
        )
        conn.commit()
        aluno_id = cur.fetchone()
        if not aluno_id:
            return jsonify({'error': 'Aluno não encontrado'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': f'Erro ao atualizar dados: {e}'}), 500
    finally:
        cur.close()
        conn.close()
    
    return jsonify({'message': 'Aluno atualizado com sucesso!', 'id_aluno': id}), 200

@app.route('/alunos/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['Alunos'],
    'summary': 'Remove um aluno',
    'description': 'Endpoint para excluir um aluno do sistema',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do aluno a ser excluído'
        }
    ],
    'responses': {
        200: {
            'description': 'Aluno excluído com sucesso',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'id_aluno': {'type': 'integer'}
                }
            },
            'examples': {
                'application/json': {'message': 'Aluno excluído com sucesso!', 'id_aluno': 1}
            }
        },
        404: {
            'description': 'Aluno não encontrado',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            },
            'examples': {
                'application/json': {'error': 'Aluno não encontrado'}
            }
        },
        500: {
            'description': 'Erro ao conectar ao banco de dados ou excluir dados',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def excluir_aluno(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Falha ao conectar ao banco de dados'}), 500

    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM Aluno WHERE id_aluno = %s RETURNING id_aluno', (id,))
        conn.commit()
        aluno_id = cur.fetchone()
        if not aluno_id:
            return jsonify({'error': 'Aluno não encontrado'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': f'Erro ao excluir dados: {e}'}), 500
    finally:
        cur.close()
        conn.close()
    
    return jsonify({'message': 'Aluno excluído com sucesso!', 'id_aluno': id}), 200

# Rota para obter um aluno específico por ID
@app.route('/alunos/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Alunos'],
    'summary': 'Retorna um aluno específico',
    'description': 'Endpoint para obter os detalhes de um aluno específico pelo ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do aluno a ser consultado'
        }
    ],
    'responses': {
        200: {
            'description': 'Aluno encontrado com sucesso',
            'schema': {
                'type': 'object',
                'properties': {
                    'id_aluno': {'type': 'integer', 'description': 'ID único do aluno'},
                    'nome_completo': {'type': 'string', 'description': 'Nome completo do aluno'},
                    'data_nascimento': {'type': 'string', 'format': 'date', 'description': 'Data de nascimento do aluno'},
                    'id_turma': {'type': 'integer', 'description': 'ID da turma do aluno'},
                    'nome_responsavel': {'type': 'string', 'description': 'Nome do responsável pelo aluno'},
                    'telefone_responsavel': {'type': 'string', 'description': 'Telefone do responsável'},
                    'email_responsavel': {'type': 'string', 'description': 'Email do responsável'},
                    'informacoes_adicionais': {'type': 'string', 'description': 'Informações adicionais sobre o aluno'}
                }
            },
            'examples': {
                'application/json': {
                    'id_aluno': 1,
                    'nome_completo': 'João da Silva',
                    'data_nascimento': '2010-05-15',
                    'id_turma': 3,
                    'nome_responsavel': 'Maria da Silva',
                    'telefone_responsavel': '(11) 98765-4321',
                    'email_responsavel': 'maria@exemplo.com',
                    'informacoes_adicionais': 'Alergia a amendoim'
                }
            }
        },
        404: {
            'description': 'Aluno não encontrado',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            },
            'examples': {
                'application/json': {'error': 'Aluno não encontrado'}
            }
        },
        500: {
            'description': 'Erro ao conectar ao banco de dados',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def obter_aluno(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Falha ao conectar ao banco de dados'}), 500
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute('SELECT * FROM Aluno WHERE id_aluno = %s;', (id,))
        aluno = cur.fetchone()
        if not aluno:
            return jsonify({'error': 'Aluno não encontrado'}), 404
        result = dict(aluno)
    except psycopg2.Error as e:
        return jsonify({'error': f'Erro ao consultar dados: {e}'}), 500
    finally:
        cur.close()
        conn.close()
    
    return jsonify(result), 200

# Rota principal para verificar se a API está funcionando
@app.route('/')
@swag_from({
    'tags': ['Status'],
    'summary': 'Verifica o status da API',
    'description': 'Endpoint para verificar se a API está em funcionamento',
    'responses': {
        200: {
            'description': 'API está funcionando corretamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'}
                }
            },
            'examples': {
                'application/json': {
                    'status': 'online',
                    'message': 'API de Gerenciamento Escolar está funcionando corretamente'
                }
            }
        }
    }
})
def index():
    return jsonify({
        'status': 'online',
        'message': 'API de Gerenciamento Escolar está funcionando corretamente'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
