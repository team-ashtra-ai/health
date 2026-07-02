#!/usr/bin/env python3
"""Generate Brazilian Portuguese static pages under /pt/.

The default engine is a curated local glossary tuned to the Sofiati site voice.
If Argos Translate is installed and an en->pt package is available, the script
can use it for unknown strings, but the site does not require that dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
PT_DIR = ROOT / "pt"
CACHE_PATH = ROOT / ".translation-cache.json"
DOMAIN = "https://www.sofiati.com"
RULE_VERSION = "pt-br-static-v1"

PUBLIC_PAGES = [
    "index.html",
    "about.html",
    "accessibility.html",
    "blog.html",
    "care.html",
    "consultation.html",
    "contact.html",
    "cookies.html",
    "faq.html",
    "journal.html",
    "laser.html",
    "legal.html",
    "mission.html",
    "privacy.html",
    "results.html",
    "skin.html",
    "testimonials.html",
    "thank-you.html",
    "values.html",
    "404.html",
]

SECTION_COMMENTS = {
    "01": "PAGE HERO",
    "02": "GUIDED PROCESS",
    "03": "RESPONSIBLE CARE STATEMENT",
    "04": "HELPFUL READING PATH",
    "05": "EXPECTATION LEDGER",
    "06": "EDUCATIONAL BRIDGE",
    "07": "CONTACT BRIDGE",
    "08": "TRUST BRIDGE",
    "09": "DECISION BRIDGE",
    "10": "FINAL CTA",
}

EXACT_TRANSLATIONS = {
    "Skip to main content": "Ir para o conteúdo principal",
    "Home": "Início",
    "About": "Sobre",
    "Care": "Cuidado",
    "Laser": "Laser",
    "Skin": "Pele",
    "Results": "Resultados",
    "Contact": "Contato",
    "FAQ": "FAQ",
    "Journal": "Guia",
    "Blog": "Blog",
    "Mission": "Missão",
    "Values": "Valores",
    "Testimonials": "Depoimentos",
    "Privacy": "Privacidade",
    "Cookies": "Cookies",
    "Accessibility": "Acessibilidade",
    "Legal": "Legal",
    "Consultation": "Consulta",
    "Request consultation": "Solicitar consulta",
    "Ask a question": "Fazer uma pergunta",
    "Contact the clinic": "Fale com a clínica",
    "Back to home": "Voltar ao início",
    "Return home": "Voltar ao início",
    "Return": "Voltar",
    "Read FAQ": "Ler o FAQ",
    "Read the FAQ": "Ler o FAQ",
    "Read guidance": "Ler orientações",
    "Explore care approach": "Conheça a abordagem de cuidado",
    "Explore skin guidance": "Conheça as orientações para pele",
    "Explore laser guidance": "Conheça as orientações sobre laser",
    "Learn about care": "Entenda o cuidado",
    "Learn about Franciele": "Conheça Franciele",
    "Explore values": "Conheça os valores",
    "Explore results context": "Entenda o contexto dos resultados",
    "Explore consultation": "Conheça a consulta",
    "Explore journal": "Explorar o guia",
    "Explore care": "Conheça o cuidado",
    "Skin guidance": "Orientação para pele",
    "Laser guidance": "Orientação sobre laser",
    "Results context": "Contexto dos resultados",
    "Care approach": "Abordagem de cuidado",
    "Legal notes": "Notas legais",
    "Privacy policy": "Política de privacidade",
    "Cookie information": "Informações sobre cookies",
    "About Franciele": "Sobre Franciele",
    "Meet Franciele": "Conheça Franciele",
    "Email the clinic": "Enviar e-mail para a clínica",
    "Send a message": "Enviar uma mensagem",
    "Message WhatsApp": "Enviar WhatsApp",
    "WhatsApp": "WhatsApp",
    "Instagram": "Instagram",
    "Email": "E-mail",
    "Questions": "Perguntas",
    "Question": "Pergunta",
    "Trust": "Confiança",
    "Clarity": "Clareza",
    "Comfort": "Conforto",
    "Suitability": "Adequação",
    "Expectations": "Expectativas",
    "Evaluation": "Avaliação",
    "Aftercare": "Cuidados posteriores",
    "Preparation": "Preparo",
    "Timing": "Tempo",
    "Planning": "Planejamento",
    "Assessment": "Avaliação",
    "Responsibility": "Responsabilidade",
    "Listening": "Escuta",
    "Education": "Educação",
    "Closing": "Fechamento",
    "Next step": "Próximo passo",
    "First step": "Primeiro passo",
    "Local care": "Cuidado local",
    "Local service": "Atendimento local",
    "Professional identity": "Identidade profissional",
    "Professional care": "Cuidado profissional",
    "Care style": "Estilo de cuidado",
    "Care perspective": "Perspectiva de cuidado",
    "Responsible care": "Cuidado responsável",
    "Results with context": "Resultados com contexto",
    "Page not found": "Página não encontrada",
    "This page could not be found": "Esta página não foi encontrada",
    "Thank you": "Obrigada",
    "Thank you for reaching out": "Obrigada pelo contato",
    "Start with a simple message": "Comece com uma mensagem simples",
    "Clarity before aesthetic care": "Clareza antes do cuidado estético",
    "Care begins with listening and evaluation": "O cuidado começa com escuta e avaliação",
    "Skin care guided by your context": "Cuidado da pele guiado pelo seu contexto",
    "Laser care with suitability first": "Cuidado com laser começando pela adequação",
    "Results are best understood with context": "Resultados são melhor compreendidos com contexto",
    "Request a consultation before treatment decisions": "Solicite uma consulta antes de decidir sobre tratamentos",
    "Meet Franciele Sofiati Biomédica": "Conheça Franciele Sofiati Biomédica",
    "Aesthetic care guided by consultation in Londrina": "Cuidado estético guiado por consulta em Londrina",
    "A mission built on listening and responsibility": "Uma missão construída com escuta e responsabilidade",
    "Principles that guide every consultation": "Princípios que orientam cada consulta",
    "Trust is built through clarity and care": "Confiança se constrói com clareza e cuidado",
    "Professional legal clarity": "Clareza legal profissional",
    "Privacy information with clarity": "Informações de privacidade com clareza",
    "Cookie choices, explained simply": "Escolhas de cookies explicadas de forma simples",
    "Accessible, comfortable site use": "Uso do site acessível e confortável",
    "Clear notes on skin, laser, and responsible care": "Notas claras sobre pele, laser e cuidado responsável",
    "Thoughtful guidance before aesthetic decisions": "Orientação cuidadosa antes de decisões estéticas",
    "A calm next step": "Um próximo passo com calma",
    "A calm conversation before any procedure is planned.": "Uma conversa tranquila antes de qualquer procedimento ser planejado.",
    "Aesthetic planning guided by context, not pressure.": "Planejamento estético guiado por contexto, não por pressão.",
    "Helpful guidance for decisions that should feel informed.": "Orientação útil para decisões que devem ser bem informadas.",
    "Honest expectation-setting before decisions are made.": "Expectativas honestas antes das decisões.",
    "Personalized skin guidance with realistic expectations.": "Orientação personalizada para a pele com expectativas realistas.",
    "Professional care with a warm, consultation-first rhythm.": "Cuidado profissional com um ritmo acolhedor e centrado na consulta.",
    "Listening, clarity, comfort, and responsible planning.": "Escuta, clareza, conforto e planejamento responsável.",
    "A responsible approach to testimonials and client experience.": "Uma abordagem responsável para depoimentos e experiência do cliente.",
    "Clear information supports trust before contact.": "Informação clara apoia a confiança antes do contato.",
    "Transparent preferences for a calm browsing experience.": "Preferências transparentes para uma navegação tranquila.",
    "Feedback is welcome when something can be clearer.": "Sugestões são bem-vindas quando algo puder ficar mais claro.",
    "Responsible language supports informed decisions.": "Linguagem responsável apoia decisões informadas.",
    "A warm next step after making contact.": "Um próximo passo acolhedor depois do contato.",
    "Easy recovery without losing your place.": "Um caminho simples para voltar sem se perder.",
    "Use this page as orientation, then confirm what applies to you through consultation.": "Use esta página como orientação e confirme, em consulta, o que se aplica ao seu caso.",
    "When a topic feels personal, a consultation can make it specific.": "Quando um assunto parece pessoal, a consulta ajuda a torná-lo específico.",
    "Care is most useful when it is grounded in your real context.": "O cuidado é mais útil quando parte do seu contexto real.",
    "Evaluation comes first.": "A avaliação vem primeiro.",
    "Results vary.": "Os resultados variam.",
    "Results vary from person to person.": "Os resultados variam de pessoa para pessoa.",
    "Context matters.": "O contexto importa.",
    "Questions are welcome.": "Perguntas são bem-vindas.",
    "Questions matter.": "Perguntas importam.",
    "Assessment comes first.": "A avaliação vem primeiro.",
    "Assessment happens personally.": "A avaliação acontece de forma individual.",
    "Individual response varies.": "A resposta individual varia.",
    "Individual response": "Resposta individual",
    "Personal evaluation comes before recommendations.": "A avaliação individual vem antes das recomendações.",
    "Options depend on individual assessment.": "As opções dependem de avaliação individual.",
    "Explanations come before decisions.": "As explicações vêm antes das decisões.",
    "Your questions and boundaries matter.": "Suas perguntas e limites importam.",
    "Ask if you are unsure what to send.": "Pergunte se não tiver certeza do que enviar.",
    "Only share what is needed.": "Compartilhe apenas o necessário.",
    "You can ask before deciding.": "Você pode perguntar antes de decidir.",
    "Your schedule and goals can be discussed.": "Sua rotina e seus objetivos podem ser conversados.",
    "Ask before deciding.": "Pergunte antes de decidir.",
    "Support continues after the appointment.": "O suporte continua após o atendimento.",
    "Decisions do not need to be rushed.": "As decisões não precisam ser apressadas.",
    "Claims stay grounded.": "As afirmações permanecem realistas.",
    "Plans and aftercare matter.": "Plano e cuidados posteriores importam.",
    "Each response is personal.": "Cada resposta é individual.",
    "External contact route.": "Canal externo de contato.",
    "External social profile.": "Perfil social externo.",
    "External communication route.": "Canal externo de comunicação.",
    "Used for contact.": "Usado para contato.",
    "Used for social profile access.": "Usado para acesso ao perfil social.",
    "Used for direct messages.": "Usado para mensagens diretas.",
    "Londrina, Paraná, Brazil": "Londrina, Paraná, Brasil",
    "Franciele Sofiati portrait for consultation guidance": "Retrato de Franciele Sofiati para orientação de consulta",
}

PAGE_COPY = {
    "index.html": {
        "title": "Início | Franciele Sofiati Biomédica",
        "description": "Cuidado estético, de pele e laser em Londrina com Franciele Sofiati Biomédica, orientado por escuta, avaliação, conforto e expectativas realistas.",
        "kicker": "Franciele Sofiati Biomédica",
        "h1": "Cuidado estético guiado por consulta em Londrina",
        "summary": "Pele, laser e estética começam com escuta, avaliação, conforto e expectativas realistas antes de qualquer procedimento ser considerado.",
        "trust": "Planejamento responsável para pele, laser e estética em Londrina, Paraná.",
        "topic": "o cuidado estético",
        "local": "Cuidado estético em Londrina",
        "alt": "Franciele Sofiati em retrato profissional para orientação estética em Londrina",
    },
    "about.html": {
        "title": "Sobre Franciele Sofiati | Biomédica em Londrina",
        "description": "Conheça Franciele Sofiati Biomédica e sua abordagem de cuidado responsável, acolhedora e centrada na consulta em Londrina.",
        "kicker": "Identidade profissional",
        "h1": "Conheça Franciele Sofiati Biomédica",
        "summary": "Uma abordagem profissional, calma e atenta, construída com avaliação cuidadosa, explicações claras e cuidado humano.",
        "trust": "Cuidado profissional com ritmo acolhedor e centrado na consulta.",
        "topic": "a trajetória e a abordagem de Franciele",
        "local": "Atuação profissional em Londrina",
        "alt": "Franciele Sofiati em retrato profissional composto",
    },
    "care.html": {
        "title": "Abordagem de Cuidado | Estética Responsável em Londrina",
        "description": "Entenda a abordagem de Franciele Sofiati para cuidado estético responsável: escuta, avaliação, adequação, conforto, cuidados posteriores e expectativas realistas.",
        "kicker": "Abordagem de cuidado",
        "h1": "O cuidado começa com escuta e avaliação",
        "summary": "Antes de decisões sobre tratamentos, Franciele considera objetivos, contexto da pele, tempo, conforto, adequação e expectativas realistas.",
        "trust": "Planejamento estético guiado por contexto, não por pressão.",
        "topic": "a abordagem de cuidado",
        "local": "Cuidado orientado por consulta em Londrina",
        "alt": "Franciele Sofiati em retrato calmo para abordagem de cuidado",
    },
    "laser.html": {
        "title": "Laser em Londrina | Orientação Responsável",
        "description": "Orientação sobre laser em Londrina com foco em avaliação, adequação, preparo, conforto, cuidados posteriores e expectativas realistas.",
        "kicker": "Orientação sobre laser",
        "h1": "Laser com adequação em primeiro lugar",
        "summary": "A indicação de laser depende do contexto da pele, preparo, timing, sensibilidade, cuidados posteriores e avaliação profissional.",
        "trust": "Laser deve ser discutido com avaliação, preparo e limites claros.",
        "topic": "a orientação sobre laser",
        "local": "Orientação sobre laser em Londrina",
        "alt": "Franciele Sofiati em retrato profissional preciso para orientação sobre laser",
    },
    "skin.html": {
        "title": "Orientação para Pele em Londrina | Franciele Sofiati",
        "description": "Orientação responsável para pele em Londrina, considerando histórico, rotina, consistência, conforto, cuidados posteriores e expectativas realistas.",
        "kicker": "Orientação para pele",
        "h1": "Cuidado da pele guiado pelo seu contexto",
        "summary": "As necessidades da pele são individuais. A melhor rota depende de histórico, rotina, constância, conforto, cuidados posteriores e avaliação.",
        "trust": "Orientação personalizada para pele com expectativas realistas.",
        "topic": "o cuidado da pele",
        "local": "Orientação para pele em Londrina",
        "alt": "Franciele Sofiati em retrato acolhedor para orientação da pele",
    },
    "results.html": {
        "title": "Resultados | Expectativas Estéticas Realistas",
        "description": "Entenda resultados estéticos com contexto: resposta individual, adequação, planejamento, cuidados posteriores, tempo e expectativas realistas.",
        "kicker": "Resultados com contexto",
        "h1": "Resultados são melhor compreendidos com contexto",
        "summary": "Uma conversa responsável considera resposta individual, adequação, planejamento, constância, cuidados posteriores e tempo.",
        "trust": "Expectativas honestas antes das decisões.",
        "topic": "os resultados estéticos",
        "local": "Discussões sobre resultados em Londrina",
        "alt": "Franciele Sofiati em retrato sereno para falar sobre resultados com contexto",
    },
    "consultation.html": {
        "title": "Consulta Estética em Londrina | Franciele Sofiati Biomédica",
        "description": "Solicite uma consulta estética em Londrina com Franciele Sofiati Biomédica para avaliação cuidadosa, explicações claras e planejamento responsável.",
        "kicker": "Primeiro passo",
        "h1": "Solicite uma consulta antes de decidir sobre tratamentos",
        "summary": "A consulta é o momento de conversar sobre objetivos, contexto da pele, conforto, adequação e possíveis próximos passos.",
        "trust": "Uma conversa tranquila antes de qualquer procedimento ser planejado.",
        "topic": "a consulta estética",
        "local": "Consulta estética em Londrina",
        "alt": "Franciele Sofiati em retrato profissional acolhedor para consulta",
    },
    "contact.html": {
        "title": "Contato | Franciele Sofiati Biomédica em Londrina",
        "description": "Fale com Franciele Sofiati Biomédica em Londrina por WhatsApp, e-mail ou Instagram para tirar dúvidas ou solicitar consulta.",
        "kicker": "Contato",
        "h1": "Comece com uma mensagem simples",
        "summary": "Faça uma pergunta, compartilhe o que gostaria de entender ou solicite uma consulta. O próximo passo pode ser orientado a partir disso.",
        "trust": "WhatsApp, e-mail, Instagram e orientação de consulta em Londrina.",
        "topic": "o contato com a clínica",
        "local": "Contato em Londrina",
        "alt": "Franciele Sofiati em retrato sorridente para contato com a clínica",
    },
    "faq.html": {
        "title": "FAQ | Perguntas sobre Pele, Laser e Consulta Estética",
        "description": "Respostas práticas sobre consulta, adequação, pele, laser, preparo, cuidados posteriores, tempo e expectativas realistas.",
        "kicker": "Perguntas respondidas",
        "h1": "Clareza antes do cuidado estético",
        "summary": "Respostas práticas ajudam a reduzir dúvidas antes da consulta, especialmente sobre adequação, tempo, cuidados posteriores e expectativas.",
        "trust": "Orientação útil para decisões que devem ser bem informadas.",
        "topic": "as perguntas frequentes",
        "local": "Dúvidas comuns em Londrina",
        "alt": "Franciele Sofiati em retrato composto para perguntas frequentes",
    },
    "journal.html": {
        "title": "Guia | Orientação sobre Pele, Laser e Estética",
        "description": "Orientações editoriais de Franciele Sofiati sobre pele, laser, consulta, cuidados posteriores e expectativas realistas.",
        "kicker": "Guia editorial",
        "h1": "Orientação cuidadosa antes de decisões estéticas",
        "summary": "O guia reúne conteúdos para ajudar você a entender pele, laser, consulta e expectativas sem pressão ou exageros.",
        "trust": "Leitura responsável para decisões mais calmas.",
        "topic": "o guia editorial",
        "local": "Orientação editorial em Londrina",
        "alt": "Franciele Sofiati em retrato editorial para orientação estética",
    },
    "blog.html": {
        "title": "Blog | Pele, Laser e Cuidado Estético Responsável",
        "description": "Notas educativas sobre pele, laser, consulta, planejamento responsável e expectativas realistas em Londrina.",
        "kicker": "Notas educativas",
        "h1": "Notas claras sobre pele, laser e cuidado responsável",
        "summary": "Os artigos ajudam a entender possibilidades de cuidado sem pressão, promessas exageradas ou conselhos genéricos.",
        "trust": "Um espaço de educação estética centrado na consulta.",
        "topic": "os conteúdos educativos",
        "local": "Conteúdo para leitores de Londrina",
        "alt": "Franciele Sofiati em retrato editorial para conteúdo educativo",
    },
    "mission.html": {
        "title": "Missão | Cuidado Estético Responsável",
        "description": "A missão de Franciele Sofiati é oferecer cuidado estético responsável com escuta, clareza, conforto, avaliação profissional e planejamento realista.",
        "kicker": "Missão",
        "h1": "Uma missão construída com escuta e responsabilidade",
        "summary": "O cuidado Sofiati existe para tornar decisões estéticas mais calmas, claras, pessoais e profissionalmente orientadas.",
        "trust": "Escuta, clareza, conforto e planejamento responsável.",
        "topic": "a missão da marca",
        "local": "Uma missão enraizada em Londrina",
        "alt": "Franciele Sofiati em retrato sereno para falar sobre missão",
    },
    "values.html": {
        "title": "Valores | Escuta, Clareza, Conforto e Responsabilidade",
        "description": "Os valores que guiam o cuidado Sofiati: escuta antes do tratamento, responsabilidade profissional, explicação clara, conforto, planejamento individual e expectativas realistas.",
        "kicker": "Valores",
        "h1": "Princípios que orientam cada consulta",
        "summary": "Escuta, responsabilidade profissional, clareza, conforto, planejamento individual e expectativas realistas moldam a experiência de cuidado.",
        "trust": "Valores que tornam o processo calmo e bem considerado.",
        "topic": "os valores do cuidado",
        "local": "Valores em prática em Londrina",
        "alt": "Franciele Sofiati em retrato confiante para os valores da marca",
    },
    "testimonials.html": {
        "title": "Depoimentos | Confiança e Cuidado Responsável",
        "description": "Página de confiança para Franciele Sofiati Biomédica, com foco em clareza, conforto, escuta e cuidado profissional sem promessas de resultado.",
        "kicker": "Confiança",
        "h1": "Confiança se constrói com clareza e cuidado",
        "summary": "Prova social deve refletir escuta, informação, respeito e orientação profissional, não promessas de resultado.",
        "trust": "Uma abordagem responsável para depoimentos e experiência do cliente.",
        "topic": "a experiência de confiança",
        "local": "Confiança no cuidado em Londrina",
        "alt": "Franciele Sofiati em retrato sorridente para confiança e depoimentos",
    },
    "privacy.html": {
        "title": "Privacidade | Franciele Sofiati Biomédica",
        "description": "Informações de privacidade sobre o site Sofiati, canais de contato, solicitações de consulta e uso responsável de dados pessoais.",
        "kicker": "Privacidade",
        "h1": "Informações de privacidade com clareza",
        "summary": "Esta página explica como canais de contato, solicitações de consulta e informações do site são tratados com profissionalismo.",
        "trust": "Informação clara apoia a confiança antes do contato.",
        "topic": "a privacidade no site",
        "local": "Privacidade e contato em Londrina",
        "alt": "Franciele Sofiati em retrato profissional discreto",
    },
    "cookies.html": {
        "title": "Cookies | Preferências do Site Sofiati",
        "description": "Informações sobre cookies do site Sofiati, incluindo armazenamento essencial, preferências opcionais e escolhas de navegação.",
        "kicker": "Cookies",
        "h1": "Escolhas de cookies explicadas de forma simples",
        "summary": "As informações sobre cookies são mantidas claras para que você entenda o armazenamento essencial do site e preferências opcionais.",
        "trust": "Preferências transparentes para uma navegação tranquila.",
        "topic": "as preferências de cookies",
        "local": "Preferências do site",
        "alt": "Franciele Sofiati em retrato profissional para informações de cookies",
    },
    "accessibility.html": {
        "title": "Acessibilidade | Site Sofiati",
        "description": "Informações de acessibilidade do site Sofiati, incluindo navegação, legibilidade, teclado, feedback e uso inclusivo.",
        "kicker": "Acessibilidade",
        "h1": "Uso do site acessível e confortável",
        "summary": "O site deve ser legível, navegável e prático para visitantes em diferentes dispositivos, preferências e recursos assistivos.",
        "trust": "Sugestões são bem-vindas quando algo puder ficar mais claro.",
        "topic": "a acessibilidade do site",
        "local": "Acessibilidade digital",
        "alt": "Franciele Sofiati em retrato calmo para acessibilidade do site",
    },
    "legal.html": {
        "title": "Notas Legais | Informação Responsável",
        "description": "Notas legais e educativas do site Sofiati sobre consulta, variação individual, expectativas realistas e uso responsável das informações.",
        "kicker": "Notas legais",
        "h1": "Clareza legal profissional",
        "summary": "As informações do site são educativas e gerais. Recomendações pessoais exigem consulta e avaliação profissional.",
        "trust": "Linguagem responsável apoia decisões informadas.",
        "topic": "as notas legais",
        "local": "Informação responsável",
        "alt": "Franciele Sofiati em retrato profissional para notas legais",
    },
    "thank-you.html": {
        "title": "Obrigada | Franciele Sofiati Biomédica",
        "description": "Obrigada por entrar em contato com Franciele Sofiati Biomédica. Veja próximos passos, consulta, FAQ e páginas úteis enquanto aguarda retorno.",
        "kicker": "Obrigada",
        "h1": "Obrigada pelo contato",
        "summary": "Sua mensagem foi recebida. Enquanto aguarda, você pode revisar a abordagem de cuidado ou voltar ao início.",
        "trust": "Um próximo passo acolhedor depois do contato.",
        "topic": "o retorno após o contato",
        "local": "Próximos passos",
        "alt": "Franciele Sofiati em retrato acolhedor para agradecimento",
    },
    "404.html": {
        "title": "Página Não Encontrada | Franciele Sofiati Biomédica",
        "description": "A página não foi encontrada. Volte ao início, solicite uma consulta ou fale com a clínica para encontrar o próximo passo.",
        "kicker": "Página não encontrada",
        "h1": "Esta página não foi encontrada",
        "summary": "A página pode ter mudado, mas você pode voltar ao início ou falar com a clínica para seguir com calma.",
        "trust": "Um caminho simples para voltar sem se perder.",
        "topic": "a recuperação da navegação",
        "local": "Volte ao caminho certo",
        "alt": "Franciele Sofiati em retrato suave para recuperar a navegação",
    },
}

PHRASE_REPLACEMENTS = [
    ("Franciele Sofiati Biomédica", "Franciele Sofiati Biomédica"),
    ("consultation-led", "orientado por consulta"),
    ("consultation-first", "centrado na consulta"),
    ("skin, laser, and aesthetic care", "cuidado de pele, laser e estética"),
    ("skin, laser, and aesthetic guidance", "orientação para pele, laser e estética"),
    ("skin, laser, and aesthetic planning", "planejamento de pele, laser e estética"),
    ("responsible aesthetic care", "cuidado estético responsável"),
    ("realistic expectations", "expectativas realistas"),
    ("individual response", "resposta individual"),
    ("professional evaluation", "avaliação profissional"),
    ("clear explanation", "explicação clara"),
    ("before treatment decisions", "antes de decisões sobre tratamentos"),
    ("before any procedure", "antes de qualquer procedimento"),
    ("before decisions", "antes das decisões"),
    ("without pressure", "sem pressão"),
    ("with care", "com cuidado"),
    ("in Londrina", "em Londrina"),
    ("Londrina, Paraná, Brazil", "Londrina, Paraná, Brasil"),
]

WORD_REPLACEMENTS = {
    "Aesthetic": "Estético",
    "aesthetic": "estético",
    "care": "cuidado",
    "Care": "Cuidado",
    "consultation": "consulta",
    "Consultation": "Consulta",
    "skin": "pele",
    "Skin": "Pele",
    "laser": "laser",
    "Laser": "Laser",
    "guidance": "orientação",
    "Guidance": "Orientação",
    "responsible": "responsável",
    "Responsible": "Responsável",
    "planning": "planejamento",
    "Planning": "Planejamento",
    "evaluation": "avaliação",
    "Evaluation": "Avaliação",
    "comfort": "conforto",
    "Comfort": "Conforto",
    "suitability": "adequação",
    "Suitability": "Adequação",
    "expectations": "expectativas",
    "Expectations": "Expectativas",
    "results": "resultados",
    "Results": "Resultados",
    "context": "contexto",
    "Context": "Contexto",
    "clarity": "clareza",
    "Clarity": "Clareza",
    "trust": "confiança",
    "Trust": "Confiança",
    "questions": "perguntas",
    "Questions": "Perguntas",
    "comfort": "conforto",
    "timing": "tempo",
    "Timing": "Tempo",
    "aftercare": "cuidados posteriores",
    "Aftercare": "Cuidados posteriores",
    "preparation": "preparo",
    "Preparation": "Preparo",
    "professional": "profissional",
    "Professional": "Profissional",
    "personal": "individual",
    "Personal": "Individual",
    "clear": "claro",
    "Clear": "Claro",
    "calm": "calmo",
    "Calm": "Calmo",
    "warm": "acolhedor",
    "Warm": "Acolhedor",
    "local": "local",
    "Local": "Local",
    "contact": "contato",
    "Contact": "Contato",
    "message": "mensagem",
    "Message": "Mensagem",
    "page": "página",
    "Page": "Página",
    "privacy": "privacidade",
    "Privacy": "Privacidade",
    "cookies": "cookies",
    "Cookies": "Cookies",
    "legal": "legal",
    "Legal": "Legal",
    "mission": "missão",
    "Mission": "Missão",
    "values": "valores",
    "Values": "Valores",
    "journal": "guia",
    "Journal": "Guia",
    "blog": "blog",
    "Blog": "Blog",
    "testimonials": "depoimentos",
    "Testimonials": "Depoimentos",
}

ENGLISH_PATTERNS = re.compile(
    r"\b(the|and|with|before|after|through|should|could|would|what|when|where|your|you|care|skin|laser|consultation|results|questions|contact|guidance|page)\b",
    re.I,
)


def en_url(page: str) -> str:
    return f"{DOMAIN}/" if page == "index.html" else f"{DOMAIN}/{page}"


def pt_url(page: str) -> str:
    return f"{DOMAIN}/pt/" if page == "index.html" else f"{DOMAIN}/pt/{page}"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shared_hash() -> str:
    h = hashlib.sha256(RULE_VERSION.encode())
    for rel in [
        "partials/header.html",
        "partials/mobile-menu.html",
        "partials/footer.html",
        "partials/cookie-banner.html",
        "partials/floating-widgets.html",
        "data/navigation.json",
        "data/seo.json",
        "data/faq.json",
        "data/services.json",
    ]:
        path = ROOT / rel
        if path.exists():
            h.update(rel.encode())
            h.update(path.read_bytes())
    return h.hexdigest()


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {"version": RULE_VERSION, "shared_hash": "", "pages": {}}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_argos_engine():
    try:
        from argostranslate import translate  # type: ignore

        installed = translate.get_installed_languages()
        source = next((lang for lang in installed if lang.code == "en"), None)
        target = next((lang for lang in installed if lang.code in {"pt", "pt_br", "pt-BR"}), None)
        if not source or not target:
            return None
        translation = source.get_translation(target)
        return translation.translate
    except Exception:
        return None


def protect_tokens(text: str) -> tuple[str, dict[str, str]]:
    tokens: dict[str, str] = {}
    patterns = [
        r"Franciele Sofiati(?: Biomédica)?",
        r"Sofiati",
        r"sofiatimendonca@gmail\.com",
        r"@sofiati_biomedica",
        r"\(\d{2}\) \d \d{4}-\d{4}",
        r"\+55 \d{2} \d{5}-\d{4}",
        r"https?://[^\s<]+",
    ]
    result = text
    for pattern in patterns:
        for match in re.findall(pattern, result):
            key = f"__TOKEN_{len(tokens)}__"
            tokens[key] = match
            result = result.replace(match, key)
    return result, tokens


def restore_tokens(text: str, tokens: dict[str, str]) -> str:
    for key, value in tokens.items():
        text = text.replace(key, value)
    return text


def fallback_translate(text: str) -> str:
    if not text.strip():
        return text
    if text in EXACT_TRANSLATIONS:
        return EXACT_TRANSLATIONS[text]
    if " | " in text:
        return " | ".join(translate_text(part) for part in text.split(" | "))

    working, tokens = protect_tokens(text)
    for source, target in sorted(PHRASE_REPLACEMENTS, key=lambda item: len(item[0]), reverse=True):
        working = working.replace(source, target)

    # A conservative word-level fallback keeps unknown strings from staying fully
    # English while the review script still reports lines that need human polish.
    for source, target in sorted(WORD_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        working = re.sub(rf"\b{re.escape(source)}\b", target, working)

    working = working.replace(" and ", " e ")
    working = working.replace(" with ", " com ")
    working = working.replace(" before ", " antes de ")
    working = working.replace(" after ", " depois de ")
    working = working.replace(" through ", " por meio de ")
    working = working.replace(" for ", " para ")
    working = working.replace(" in ", " em ")
    working = working.replace(" to ", " para ")
    working = working.replace(" of ", " de ")
    working = working.replace(" or ", " ou ")
    working = restore_tokens(working, tokens)
    return working


ARGOS_ENGINE = None


def translate_text(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return text
    leading = text[: len(text) - len(text.lstrip())]
    trailing = text[len(text.rstrip()) :]
    if stripped in EXACT_TRANSLATIONS:
        translated = EXACT_TRANSLATIONS[stripped]
    elif ARGOS_ENGINE:
        try:
            translated = ARGOS_ENGINE(stripped)
        except Exception:
            translated = fallback_translate(stripped)
    else:
        translated = fallback_translate(stripped)
    return f"{leading}{translated}{trailing}"


def is_external(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "mailto", "tel", "sms", "whatsapp"}


def prefix_asset(value: str) -> str:
    if value.startswith("../") or value.startswith("/") or is_external(value) or value.startswith("#"):
        return value
    if value.startswith(("assets/", "css/", "js/", "partials/", "data/", "docs/")) or value in {"favicon.ico", "site.webmanifest"}:
        return f"../{value}"
    return value


def translate_schema(raw: str, page: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    data["url"] = pt_url(page)
    data["mainEntityOfPage"] = pt_url(page)
    if "description" in data:
        data["description"] = translate_text(data["description"])
    if "areaServed" in data:
        data["areaServed"] = "Londrina, Paraná, Brasil"
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


class PortugueseHTMLParser(HTMLParser):
    def __init__(self, page: str) -> None:
        super().__init__(convert_charrefs=False)
        self.page = page
        self.out: list[str] = []
        self.in_script = False
        self.in_style = False
        self.json_script = False
        self.script_buffer: list[str] = []

    def attrs_to_string(self, attrs: list[tuple[str, str | None]], tag: str) -> str:
        parts = []
        rel_value = ""
        property_value = ""
        name_value = ""
        for key, value in attrs:
            if key == "rel" and value:
                rel_value = value
            if key == "property" and value:
                property_value = value
            if key == "name" and value:
                name_value = value

        for key, value in attrs:
            if value is None:
                parts.append(key)
                continue
            new_value = value

            if tag == "html" and key == "lang":
                new_value = "pt-BR"
            elif tag == "html" and key == "data-default-lang":
                new_value = "pt-BR"
            elif tag == "link" and rel_value == "canonical" and key == "href":
                new_value = pt_url(self.page)
            elif tag == "link" and rel_value == "alternate" and key == "href":
                if any(v == "en" for k, v in attrs if k == "hreflang"):
                    new_value = en_url(self.page)
                elif any(v == "pt-BR" for k, v in attrs if k == "hreflang"):
                    new_value = pt_url(self.page)
                elif any(v == "x-default" for k, v in attrs if k == "hreflang"):
                    new_value = en_url(self.page)
            elif tag == "meta" and key == "content" and name_value == "description":
                new_value = translate_text(value)
            elif tag == "meta" and key == "content" and property_value in {"og:title", "og:description"}:
                new_value = translate_text(value)
            elif tag == "meta" and key == "content" and property_value == "og:url":
                new_value = pt_url(self.page)
            elif tag == "meta" and key == "content" and name_value in {"twitter:title", "twitter:description"}:
                new_value = translate_text(value)
            elif tag == "meta" and key == "content" and value.startswith("assets/"):
                new_value = prefix_asset(value)
            elif key in {"href", "src"}:
                new_value = prefix_asset(value)
            elif key == "srcset":
                new_value = ", ".join(
                    " ".join([prefix_asset(part.split()[0]), *part.split()[1:]])
                    for part in value.split(",")
                    if part.strip()
                )
            elif key in {"alt", "title", "placeholder"}:
                new_value = translate_text(value)
            elif key == "aria-label" and value not in {"Primary navigation", "Primary mobile navigation"}:
                new_value = translate_text(value)

            parts.append(f'{key}="{html.escape(new_value, quote=True)}"')
        return (" " + " ".join(parts)) if parts else ""

    def handle_decl(self, decl: str) -> None:
        self.out.append(f"<!{decl}>")

    def handle_comment(self, data: str) -> None:
        match = re.match(r"\s*Section\s+(\d{2}):", data)
        if match:
            data = f" {SECTION_COMMENTS.get(match.group(1), data.strip())} "
        self.out.append(f"<!--{data}-->")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_text = self.attrs_to_string(attrs, tag)
        self.out.append(f"<{tag}{attr_text}>")
        if tag == "script":
            self.in_script = True
            self.json_script = any(key == "type" and value == "application/ld+json" for key, value in attrs)
            self.script_buffer = []
        elif tag == "style":
            self.in_style = True

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.out.append(f"<{tag}{self.attrs_to_string(attrs, tag)} />")

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            if self.json_script:
                self.out.append(translate_schema("".join(self.script_buffer), self.page))
            self.in_script = False
            self.json_script = False
            self.script_buffer = []
        elif tag == "style":
            self.in_style = False
        self.out.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self.json_script:
            self.script_buffer.append(data)
        elif self.in_script or self.in_style:
            self.out.append(data)
        else:
            self.out.append(translate_text(data))

    def handle_entityref(self, name: str) -> None:
        self.out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.out.append(f"&#{name};")


def pt_utility(page: str) -> str:
    return f'''    <!-- LANGUAGE UTILITY BAR -->
    <nav class="utility-bar" aria-label="Opções de idioma">
      <div class="utility-bar__inner">
        <div class="language-switcher" aria-label="Escolher idioma">
          <a class="language-switcher__link" href="../{page}" hreflang="en" lang="en">EN</a>
          <span class="language-switcher__separator" aria-hidden="true"></span>
          <a class="language-switcher__link language-switcher__link--active" href="{page}" hreflang="pt-BR" lang="pt-BR" aria-current="true">PT</a>
        </div>
      </div>
    </nav>'''


def set_text(node, value: str) -> None:
    if node is None:
        return
    node.clear()
    node.append(value)


def link_label(href: str, fallback: str = "Saiba mais") -> str:
    clean = (href or "").split("#", 1)[0].split("?", 1)[0]
    labels = {
        "index.html": "Início",
        "about.html": "Sobre Franciele",
        "care.html": "Abordagem de cuidado",
        "laser.html": "Orientação sobre laser",
        "skin.html": "Orientação para pele",
        "results.html": "Contexto dos resultados",
        "consultation.html": "Solicitar consulta",
        "contact.html": "Fale com a clínica",
        "faq.html": "Ler o FAQ",
        "journal.html": "Ler orientações",
        "blog.html": "Ler o blog",
        "mission.html": "Missão",
        "values.html": "Valores",
        "testimonials.html": "Depoimentos",
        "privacy.html": "Privacidade",
        "cookies.html": "Cookies",
        "accessibility.html": "Acessibilidade",
        "legal.html": "Notas legais",
        "thank-you.html": "Início",
    }
    if clean.startswith("https://wa.me/"):
        return "Enviar WhatsApp"
    if clean.startswith("mailto:"):
        return "Enviar e-mail"
    return labels.get(clean, fallback)


def apply_links(section, labels: list[str] | None = None) -> None:
    if section is None:
        return
    links = section.select("a")
    for index, link in enumerate(links):
        label = labels[index] if labels and index < len(labels) else link_label(link.get("href", ""))
        set_text(link, label)


def polish_page(html_text: str, page: str) -> str:
    copy = PAGE_COPY[page]
    soup = BeautifulSoup(html_text, "html.parser")

    soup.html["lang"] = "pt-BR"
    soup.html["data-default-lang"] = "pt-BR"
    set_text(soup.title, copy["title"])

    for meta in soup.find_all("meta"):
        name = meta.get("name")
        prop = meta.get("property")
        if name == "description" or prop == "og:description":
            meta["content"] = copy["description"]
        elif prop == "og:title":
            meta["content"] = copy["title"]

    schema = soup.find("script", {"type": "application/ld+json"})
    if schema and schema.string:
        try:
            data = json.loads(schema.string)
            data["description"] = copy["description"]
            data["url"] = pt_url(page)
            data["mainEntityOfPage"] = pt_url(page)
            data["areaServed"] = "Londrina, Paraná, Brasil"
            schema.string.replace_with(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        except json.JSONDecodeError:
            pass

    main = soup.find("main")
    if main:
        main["aria-label"] = "Conteúdo da página"

    hero = soup.select_one('[data-content-section="01"]')
    if hero:
        set_text(hero.select_one(".hero__kicker"), copy["kicker"])
        set_text(hero.select_one("h1"), copy["h1"])
        set_text(hero.select_one(".hero__summary"), copy["summary"])
        set_text(hero.select_one(".hero__trust"), copy["trust"])
        actions = hero.select(".hero__actions a")
        if actions:
            set_text(actions[0], "Solicitar consulta" if page not in {"contact.html", "404.html", "thank-you.html"} else link_label(actions[0].get("href", "")))
        if len(actions) > 1:
            set_text(actions[1], link_label(actions[1].get("href", ""), "Saiba mais"))
        img = hero.find("img")
        if img:
            img["alt"] = copy["alt"]

    section_copy = {
        "02": (
            "Como começa",
            f"Uma conversa clara antes de qualquer decisão sobre {copy['topic']}",
            "A primeira etapa é entender objetivos, histórico, rotina, conforto e tempo disponível. A partir disso, a orientação fica mais segura, pessoal e realista.",
            ["Escutar o que você deseja compreender.", "Avaliar contexto, pele e expectativas.", "Conversar sobre caminhos possíveis sem pressa."],
        ),
        "03": (
            "Avaliação",
            "A indicação depende do que faz sentido para você",
            "Nem toda opção é adequada para toda pessoa ou para todo momento. A avaliação ajuda a separar o que parece interessante do que realmente pode ser responsável.",
            None,
        ),
        "04": (
            "Orientação",
            "Leitura útil antes da decisão",
            "As páginas de orientação ajudam você a chegar à consulta com perguntas melhores e mais clareza sobre pele, laser, resultados e cuidados posteriores.",
            None,
        ),
        "05": (
            "Expectativas",
            "O que precisa ficar claro",
            "Um plano responsável deve explicar limites, preparo, possíveis cuidados posteriores e a variação natural de resposta de cada pessoa.",
            [("Avaliação", "A indicação é discutida antes das decisões."), ("Conforto", "Perguntas e limites fazem parte do plano."), ("Realismo", "Resultados individuais variam e precisam de contexto.")],
        ),
        "06": (
            "Educação",
            "Entenda o raciocínio, não apenas o nome do procedimento",
            "Saber por que uma rota pode ou não ser indicada ajuda a tornar a decisão mais calma, informada e coerente com sua realidade.",
            None,
        ),
        "07": (
            "Próximo passo",
            "Quando vale conversar com a clínica",
            "Se a dúvida envolve sua pele, seu histórico ou suas expectativas, uma conversa profissional pode transformar informação geral em orientação pessoal.",
            None,
        ),
        "08": (
            "Confiança",
            "Cuidado também é ritmo, clareza e contexto",
            "O objetivo não é apressar decisões. É criar espaço para entender o que você busca e o que pode ser planejado com responsabilidade.",
            None,
        ),
        "09": (
            "Londrina",
            copy["local"],
            "Franciele Sofiati Biomédica atende em Londrina, Paraná, com uma abordagem acolhedora, refinada e profissional para decisões estéticas.",
            None,
        ),
        "10": (
            "Fechamento",
            "Comece com clareza",
            "Você não precisa saber o nome do procedimento antes de pedir ajuda. Comece pelo que percebe, pelo que deseja entender e pelas perguntas que gostaria de fazer.",
            None,
        ),
    }

    for number, data in section_copy.items():
        section = soup.select_one(f'[data-content-section="{number}"]')
        if not section:
            continue
        eyebrow, heading, paragraph, extra = data
        set_text(section.select_one(".c01-eyebrow"), eyebrow)
        h2 = section.find("h2")
        set_text(h2, heading)
        first_p = None
        for p in section.find_all("p"):
            if "c01-eyebrow" not in p.get("class", []) and not p.find_parent(".c01-section-note"):
                first_p = p
                break
        set_text(first_p, paragraph)

        if number == "02" and extra:
            for li, text in zip(section.select("ol li"), extra):
                set_text(li, text)
        if number == "05" and extra:
            dts = section.find_all("dt")
            dds = section.find_all("dd")
            for (dt_text, dd_text), dt, dd in zip(extra, dts, dds):
                set_text(dt, dt_text)
                set_text(dd, dd_text)

        note = section.select_one(".c01-section-note span")
        if note:
            set_text(note, "Use esta página como orientação e confirme, em consulta, o que se aplica ao seu caso.")
        apply_links(section)

    for img in soup.select("main section:not(.hero) img"):
        img["alt"] = "Retrato de Franciele Sofiati para orientação de consulta"

    return str(soup)


def normalize_generated(html_text: str, page: str) -> str:
    html_text = re.sub(
        r'    <!-- LANGUAGE UTILITY BAR -->\n    <nav class="utility-bar".*?\n    </nav>',
        pt_utility(page),
        html_text,
        flags=re.S,
    )
    html_text = re.sub(r"<!-- Section (\d{2}): .*? -->", lambda m: f"<!-- {SECTION_COMMENTS[m.group(1)]} -->", html_text)
    return html_text


def generate_page(page: str) -> str:
    parser = PortugueseHTMLParser(page)
    parser.feed((ROOT / page).read_text(encoding="utf-8"))
    return polish_page(normalize_generated("".join(parser.out), page), page)


def main() -> int:
    global ARGOS_ENGINE
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument("--force", action="store_true", help="Regenerate every Portuguese page.")
    arg_parser.add_argument("--use-argos", action="store_true", help="Use Argos Translate for unknown strings when installed.")
    args = arg_parser.parse_args()

    if args.use_argos:
        ARGOS_ENGINE = load_argos_engine()
        if not ARGOS_ENGINE:
            print("Argos Translate is not available with an installed en->pt package; using curated fallback.")

    PT_DIR.mkdir(exist_ok=True)
    cache = load_cache()
    current_shared_hash = shared_hash()
    regenerate_all = args.force or cache.get("version") != RULE_VERSION or cache.get("shared_hash") != current_shared_hash
    page_cache = cache.setdefault("pages", {})
    generated = 0
    skipped = 0

    for page in PUBLIC_PAGES:
        source = ROOT / page
        output = PT_DIR / page
        source_hash = file_hash(source)
        cached = page_cache.get(page, {})
        if not regenerate_all and cached.get("source_hash") == source_hash and output.exists():
            skipped += 1
            continue
        output.write_text(generate_page(page), encoding="utf-8")
        page_cache[page] = {
            "source_file": page,
            "source_hash": source_hash,
            "output_file": f"pt/{page}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rule_version": RULE_VERSION,
        }
        generated += 1

    cache["version"] = RULE_VERSION
    cache["shared_hash"] = current_shared_hash
    save_cache(cache)
    print(f"Portuguese generation complete: {generated} generated, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
