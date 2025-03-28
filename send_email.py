def report(estacao,  emails, alerta = None,altura = None):
    from smtplib import SMTP
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    email_mine = "floodcastingxai@gmail.com"
    password_mine = "evvm blsh qyou foaw"
    estacao = str(estacao)
    alerta = str(alerta)

    # Criando a conexão com o servidor SMTP
    smtp_port = SMTP("smtp.gmail.com", 587)
    smtp_port.ehlo()
    smtp_port.starttls()
    smtp_port.login(email_mine, password_mine)

    # # Atualizando o corpo da mensagem conforme solicitado
    # subject = f"[AIFOOD ALERT 🌊🚨] alerta de Enchente em {estacao}"
    # body = f"""
    # ATENÇÃO

    # A floodcastingxai registra previsão de {alerta} na região da estação {estacao}.

    # Por favor, acesse nosso site para mais detalhes: www.floodcastingxai.com

    # Esta ferramenta é apoiada pela iniciativa AI4GOOD - Brazil Conference (https://www.brazilconference.org), e está em fase de testes operacionais.
    # """
    
    # emails recorrentes
    
    
    # Atualizando o corpo da mensagem conforme solicitado
    subject = f"[AIFOOD REPORT 🌊🚨] Reporte de Nível da {estacao}"
    body = f"""
    Prezado(a) usuário(a),

    A floodcastingxai gostaria de informar que o volume atual na região da estação {estacao} é de aproximadamente {altura} metros.

    Por favor, acesse nosso site para mais detalhes: www.floodcastingxai.com

    Esta ferramenta é apoiada pela iniciativa AI4GOOD - Brazil Conference (https://www.brazilconference.org), e está em fase de testes operacionais.
    """
    
    # Usando MIMEMultipart para incluir cabeçalhos e corpo com codificação UTF-8
    message = MIMEMultipart()
    message['From'] = email_mine
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    # Enviando o email para cada destinatário na lista de emails
    for email1 in emails:
        message['To'] = email1
        smtp_port.sendmail(email_mine, [email1], message.as_string())
        print(f"Email enviado para {email1} com sucesso!")

    smtp_port.quit()


