from flask import Flask, request, jsonify
from database import SessionLocal, Base, engine
from models import Lead, Etapa

app = Flask(__name__)

Base.metadata.create_all(bind=engine)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    telefone = data.get("telefone")
    mensagem = data.get("mensagem")

    db = SessionLocal()

    etapa_user = db.query(Etapa).filter_by(telefone=telefone).first()

    if not etapa_user:
        nova_etapa = Etapa(telefone=telefone, etapa="nome")
        db.add(nova_etapa)
        db.commit()
        return jsonify({"resposta": "Olá! Qual é o seu nome?"})
    
    if etapa_user.etapa == "nome":
        lead = Lead(telefone=telefone, nome=mensagem)
        db.add(lead)

        etapa_user.etapa = "interesse"
        db.commit()

        return jsonify({"resposta": "Qual seu interesse?"})
    
    elif etapa_user.etapa == "interesse":
        lead = db.query(Lead).filter_by(telefone=telefone).first()
        lead.interesse = mensagem

        etapa_user.etapa = "finalizado"
        db.commit()

        return jsonify({"resposta": "Cadastro finalizado! Obrigado! 🙌"})
    
    return jsonify({"resposta": "Fluxo Finalizado."})

if __name__ == "__main__":
    app.run(debug=True)
