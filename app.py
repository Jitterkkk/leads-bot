# importação do Flask para criar a API, request para receber os dados e jsonify para enviar respostas em formato JSON
from flask import Flask, request, jsonify 
# importação do banco de dados e dos modelos (tabelas) para interagir com eles
from database import SessionLocal, Base, engine
from models import Lead, Etapa

# criação da aplicação Flask
app = Flask(__name__)

# criação das tabelas no banco de dados (se ainda não existirem)
Base.metadata.create_all(bind=engine)

def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))  # Remove caracteres não numéricos

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    for i in range(9, 11):
        valor = sum((int(cpf[num]) * ((i+1) - num) for num in range(0, i)))
        digito = ((valor * 10) % 11) % 10

        if int(cpf[i]) != digito:
            return False
        
    return True

# rota para receber as mensagens do WhatsApp (webhook)
@app.route("/webhook", methods=["POST"])
def webhook():
    # recebe os dados da requisição (telefone e mensagem)
    data = request.json
    telefone = data.get("telefone")
    mensagem = data.get("mensagem")

    # cria uma sessão para interagir com o banco de dados
    db = SessionLocal()

    # resetar a conversa se o usuário enviar a mensagem "resetar"
    if mensagem.lower() == "resetar":
        # deleta o lead e a etapa do usuário com base no telefone
        db.query(Etapa).filter_by(telefone=telefone).delete()
        db.query(Lead).filter_by(telefone=telefone).delete()
        db.commit()
        return jsonify({"resposta": "Conversa reiniciada! Vamos começar de novo 😄\nQual seu nome?"})
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

        etapa_user.etapa = "cpf"
        db.commit()
        return jsonify({"resposta": "Perfeito! Agora me informe seu CPF 👇"})
    
    elif etapa_user.etapa == "cpf":

        if not validar_cpf(mensagem):
            return jsonify({"resposta": "CPF inválido. Por favor, insira um CPF válido."})
        
        lead = db.query(Lead).filter_by(telefone=telefone).first()
        lead.cpf = mensagem

        etapa_user.etapa = "cidade"
        db.commit()
        return jsonify({"resposta": "Boa! Em qual cidade você mora?"})
    
    elif etapa_user.etapa == "cidade":
        lead = db.query(Lead).filter_by(telefone=telefone).first()
        lead.cidade = mensagem
        
        etapa_user.etapa = "interesse"
        db.commit()
        return jsonify({"resposta": "Show! Qual serviço você está procurando?"})
    
    
    elif etapa_user.etapa == "interesse":
        lead = db.query(Lead).filter_by(telefone=telefone).first()
        lead.interesse = mensagem

        # atualiza a etapa do usuário para "finalizado" e salva no banco
        etapa_user.etapa = "finalizado"
        db.commit()

        return jsonify({"resposta": "Cadastro concluído com sucesso! Em breve entraremos em contato 🚀"})
    
    return jsonify({"resposta": "Fluxo Finalizado."})

@app.route("/leads", methods=["GET"])
def listar_leads():
    db = SessionLocal()
    leads = db.query(Lead).all()

    resultado = []

    for lead in leads:
        resultado.append({
            "nome": lead.nome,
            "telefone": lead.telefone,
            "cpf": lead.cpf,
            "cidade": lead.cidade,
            "interesse": lead.interesse
        })
    return jsonify(resultado)

# roda a aplicação Flask em modo de desenvolvimento
if __name__ == "__main__":
    app.run(debug=True)
