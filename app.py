# importação do Flask para criar a API, request para receber os dados e jsonify para enviar respostas em formato JSON
from flask import Flask, request, jsonify 
# importação do banco de dados e dos modelos (tabelas) para interagir com eles
from database import SessionLocal, Base, engine
from models import Lead, Etapa

# criação da aplicação Flask
app = Flask(__name__)

# criação das tabelas no banco de dados (se ainda não existirem)
Base.metadata.create_all(bind=engine)

# rota para receber as mensagens do WhatsApp (webhook)
@app.route("/webhook", methods=["POST"])
def webhook():
    # recebe os dados da requisição (telefone e mensagem)
    data = request.json
    telefone = data.get("telefone")
    mensagem = data.get("mensagem")

    # cria uma sessão para interagir com o banco de dados
    db = SessionLocal()
    # verifica a etapa atual do usuário (telefone) no fluxo de cadastro
    etapa_user = db.query(Etapa).filter_by(telefone=telefone).first()

    # se o usuário ainda não tiver uma etapa, inicia o fluxo perguntando o nome
    if not etapa_user:
        nova_etapa = Etapa(telefone=telefone, etapa="nome")
        db.add(nova_etapa)
        db.commit()
        return jsonify({"resposta": "Olá! Qual é o seu nome?"})
    # se o usuário já tiver uma etapa, continua o fluxo de acordo com a etapa atual
    if etapa_user.etapa == "nome":
        lead = Lead(telefone=telefone, nome=mensagem)
        db.add(lead)
        # atualiza a etapa do usuário para "interesse" e salva no banco
        etapa_user.etapa = "interesse"
        db.commit()
        # pergunta o interesse do usuário
        return jsonify({"resposta": "Qual seu interesse?"})
    
    # se o usuário já tiver respondido o nome, salva o interesse e finaliza o cadastro
    elif etapa_user.etapa == "interesse":
        lead = db.query(Lead).filter_by(telefone=telefone).first()
        lead.interesse = mensagem

        # atualiza a etapa do usuário para "finalizado" e salva no banco
        etapa_user.etapa = "finalizado"
        db.commit()

        return jsonify({"resposta": "Cadastro finalizado! Obrigado! 🙌"})
    
    return jsonify({"resposta": "Fluxo Finalizado."})

# roda a aplicação Flask em modo de desenvolvimento
if __name__ == "__main__":
    app.run(debug=True)
