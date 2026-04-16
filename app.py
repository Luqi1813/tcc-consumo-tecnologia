import csv
import random
import uuid
from datetime import datetime
from html import escape
from pathlib import Path

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


# ============================================================
# APP STREAMLIT - EXPERIMENTO TCC
# Execute com: streamlit run app.py
# ============================================================

st.set_page_config(
    page_title="Pesquisa Acadêmica sobre Consumo de Tecnologia",
    page_icon="🎧",
    layout="wide",
)

CSV_PATH = Path(__file__).with_name("dados_tcc_final.csv")
GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# ============================================================
# DADOS DOS PRODUTOS
# As imagens usam URLs publicas. Se quiser trocar depois, basta
# substituir os campos "imagem_url" por outras URLs.
# ============================================================

PRODUTOS = {
    "soundmax": {
        "nome": "Fone SoundMax X1",
        "destaque_1": "Graves potentes",
        "destaque_2": "Bateria de 30h",
        "preco": "R$ 250,00",
        "imagem_url": (
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
    "audiopro": {
        "nome": "Fone AudioPro Z",
        "destaque_1": "Som equilibrado",
        "destaque_2": "Cancelamento de ruído",
        "preco": "R$ 250,00",
        "imagem_url": (
            "https://images.unsplash.com/photo-1484704849700-f032a568e944"
            "?auto=format&fit=crop&w=900&q=80"
        ),
    },
}


AVALIACOES = {
    "Grupo A": {
        "tipo": "Expert",
        "texto": (
            "Depois de uma semana de testes com músicas, podcasts e chamadas, "
            "o desempenho surpreende pela consistência. Os graves são fortes, "
            "mas não embolam os vocais; o palco sonoro entrega boa separação "
            "entre instrumentos, e o isolamento acústico reduz bem os ruídos "
            "externos em ambientes como transporte público e escritórios. "
            "A bateria também se manteve estável durante longos períodos de uso. "
            "Para quem procura um fone equilibrado dentro desta faixa de preço, "
            "é uma escolha tecnicamente muito segura. Recomendo."
        ),
    },
    "Grupo B": {
        "tipo": "Microinfluenciador Publi",
        "texto": (
            "Gente, eu testei esse fone na academia, no ônibus e até trabalhando "
            "em casa, e sério: virou meu queridinho da semana! Ele é confortável, "
            "não fica caindo da orelha, o som é bem gostoso de ouvir e a bateria "
            "durou vários dias sem eu precisar carregar. Também achei lindo para "
            "usar no dia a dia porque combina com tudo. Confiem, vale cada centavo! "
            "😍🎧 #Publi #Patrocinado"
        ),
    },
}


COLUNAS_CSV = [
    "Nome",
    "Idade",
    "Gênero",
    "Grupo Experimental",
    "Tipo de Avaliador",
    "Decisão Após Avaliação",
    "Ação no Clique Simulado",
    "Likert 1 - Avaliação Ajudou na Decisão",
    "Likert 2 - Credibilidade da Avaliação",
    "Likert 3 - Compraria por Recomendação",
    "Data e Hora da Resposta",
]


# ============================================================
# CSS GLOBAL
# Todo o visual dos cards, mockups e botão simulado fica aqui.
# ============================================================

def aplicar_css_global() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #f5f7fb;
                --ink: #172033;
                --muted: #667085;
                --line: #d9e0ec;
                --blue: #2563eb;
                --green: #16a34a;
                --green-dark: #11803a;
                --card: #ffffff;
            }

            .main .block-container {
                max-width: 1180px;
                padding-top: 2rem;
                padding-bottom: 4rem;
            }

            .hero-copy {
                background: linear-gradient(135deg, #eef4ff 0%, #f7fafc 100%);
                border: 1px solid var(--line);
                border-radius: 8px;
                padding: 22px 24px;
                color: var(--ink);
                margin-bottom: 22px;
            }

            .hero-copy h1,
            .store-card h2,
            .final-box h1 {
                color: var(--ink) !important;
            }

            .hero-copy p {
                margin: 8px 0 0 0;
                color: var(--muted);
                font-size: 1.02rem;
                line-height: 1.55;
            }

            div[data-testid="stRadio"] {
                max-width: 760px;
                margin: 28px auto 14px auto;
            }

            div[data-testid="stRadio"] > label {
                display: block;
                text-align: center;
                color: #ffffff !important;
                font-size: 1.12rem !important;
                font-weight: 900 !important;
                margin-bottom: 14px;
            }

            div[data-testid="stRadio"] div[role="radiogroup"] {
                gap: 14px;
            }

            div[data-testid="stRadio"] label[data-baseweb="radio"] {
                width: 100%;
                min-height: 66px;
                display: flex;
                align-items: center;
                background: #ffffff;
                border: 2px solid #d7dde7;
                border-radius: 8px;
                padding: 16px 18px;
                margin: 10px 0;
                box-shadow: 0 8px 20px rgba(15, 23, 42, 0.10);
                cursor: pointer;
                transition: transform 0.12s ease, border-color 0.12s ease, box-shadow 0.12s ease;
            }

            div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
                transform: translateY(-1px);
                border-color: #ff4b4b;
                box-shadow: 0 12px 26px rgba(255, 75, 75, 0.18);
            }

            div[data-testid="stRadio"] label[data-baseweb="radio"] p,
            div[data-testid="stRadio"] label[data-baseweb="radio"] span {
                color: var(--ink) !important;
                font-size: 1.05rem !important;
                font-weight: 800 !important;
                line-height: 1.35 !important;
            }

            div[data-testid="stButton"] {
                max-width: 360px;
                margin: 22px auto 0 auto;
            }

            div[data-testid="stButton"] > button {
                width: 100%;
                min-height: 60px;
                border-radius: 8px;
                font-size: 1.12rem;
                font-weight: 900;
                box-shadow: 0 10px 24px rgba(255, 75, 75, 0.22);
            }

            div[data-testid="stButton"] > button[kind="primary"] {
                background: #16a34a;
                border-color: #11803a;
                color: #ffffff;
                box-shadow: 0 10px 24px rgba(22, 163, 74, 0.22);
            }

            .product-card {
                background: var(--card);
                border: 1px solid var(--line);
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 10px 24px rgba(21, 32, 56, 0.08);
                min-height: 500px;
            }

            .product-card img {
                width: 100%;
                height: 270px;
                object-fit: cover;
                display: block;
            }

            .product-card-body {
                padding: 20px;
            }

            .product-card h3 {
                margin: 0 0 12px 0;
                color: var(--ink);
                font-size: 1.35rem;
            }

            .product-tag {
                display: inline-block;
                background: #eef4ff;
                color: #1d4ed8;
                border: 1px solid #c7d7fe;
                border-radius: 8px;
                padding: 7px 10px;
                margin: 0 6px 8px 0;
                font-weight: 700;
                font-size: 0.92rem;
            }

            .price {
                margin-top: 14px;
                font-size: 1.55rem;
                color: #111827;
                font-weight: 800;
            }

            .helper-note {
                color: var(--muted);
                font-size: 0.95rem;
                margin-top: 8px;
            }

            .shop-header {
                background: #ffffff;
                border: 1px solid var(--line);
                border-radius: 8px;
                padding: 16px 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 16px;
                margin-bottom: 18px;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
            }

            .shop-logo {
                color: #111827;
                font-size: 1.25rem;
                font-weight: 950;
            }

            .shop-trust {
                color: #166534;
                font-weight: 800;
                font-size: 0.95rem;
                text-align: right;
            }

            .shop-section-title {
                text-align: center;
                margin: 12px auto 24px auto;
                max-width: 820px;
            }

            .shop-section-title h2 {
                color: #ffffff !important;
                font-size: 1.55rem;
                margin: 0 0 8px 0;
            }

            .shop-section-title p {
                color: #cbd5e1 !important;
                font-size: 1rem;
                margin: 0;
            }

            .product-image-wrap {
                position: relative;
                overflow: hidden;
            }

            .product-choice-overlay {
                display: none;
                position: static;
                background: #ff4b4b;
                color: #ffffff !important;
                text-decoration: none !important;
                text-align: center;
                border-radius: 8px;
                padding: 16px 18px;
                font-size: 1.08rem;
                font-weight: 950;
                box-shadow: 0 12px 28px rgba(255, 75, 75, 0.34);
                transition: transform 0.12s ease, background 0.12s ease;
            }

            .product-choice-overlay:hover {
                transform: translateY(-2px);
                background: #e83a3a;
            }

            .rating-line {
                color: #f59e0b;
                font-size: 1.03rem;
                font-weight: 900;
                margin-bottom: 12px;
            }

            .store-benefits {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
                margin-top: 16px;
            }

            .store-benefits div {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px;
                color: #334155;
                font-weight: 750;
                font-size: 0.9rem;
            }

            .review-target-alert {
                max-width: 900px;
                margin: 10px auto 22px auto;
                background: #f8fafc;
                border: 1px solid #d9e0ec;
                border-radius: 8px;
                padding: 16px 18px;
                color: #334155 !important;
                font-size: 1rem;
                line-height: 1.5;
                font-weight: 650;
            }

            .cart-line {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                max-width: 900px;
                margin: 10px auto 12px auto;
                background: #ffffff;
                border: 1px solid #d9e0ec;
                border-radius: 8px;
                padding: 14px 16px;
                color: #172033 !important;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
            }

            .cart-product {
                display: flex;
                align-items: center;
                gap: 14px;
            }

            .cart-thumb {
                width: 74px;
                height: 58px;
                border-radius: 8px;
                object-fit: cover;
                border: 1px solid #e5e7eb;
                flex: 0 0 auto;
            }

            .cart-copy {
                display: flex;
                flex-direction: column;
                gap: 4px;
            }

            .cart-copy span {
                color: #64748b !important;
                font-size: 0.9rem;
                font-weight: 700;
            }

            .cart-line strong {
                color: #111827 !important;
            }

            .cart-pill {
                white-space: nowrap;
                background: #dcfce7;
                color: #166534;
                border: 1px solid #86efac;
                border-radius: 8px;
                padding: 8px 10px;
                font-weight: 900;
                font-size: 0.9rem;
            }

            .review-product-strip {
                display: flex;
                align-items: center;
                gap: 14px;
                max-width: 900px;
                margin: 0 auto 22px auto;
                background: #ffffff;
                border: 1px solid #d9e0ec;
                border-radius: 8px;
                padding: 14px 16px;
                color: #172033 !important;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
            }

            .review-product-strip img {
                width: 112px;
                height: 78px;
                border-radius: 8px;
                object-fit: cover;
                border: 1px solid #e5e7eb;
            }

            .review-product-strip span {
                color: #64748b !important;
                font-size: 0.9rem;
                font-weight: 800;
            }

            .review-product-strip strong {
                display: block;
                color: #111827 !important;
                font-size: 1.05rem;
                margin-top: 2px;
            }

            .blog-product-hero {
                display: grid;
                grid-template-columns: 220px 1fr;
                gap: 18px;
                align-items: center;
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 14px;
                margin: 16px 0;
            }

            .blog-product-hero img {
                width: 100%;
                height: 140px;
                border-radius: 8px;
                object-fit: cover;
                border: 1px solid #d9e0ec;
            }

            .blog-product-hero span {
                display: block;
                color: #2563eb !important;
                font-weight: 900;
                font-size: 0.85rem;
                text-transform: uppercase;
                margin-bottom: 6px;
            }

            .blog-product-hero strong {
                display: block;
                color: #111827 !important;
                font-size: 1.25rem;
                margin-bottom: 8px;
            }

            .blog-product-hero p {
                color: #475569 !important;
                margin: 0;
                line-height: 1.45;
            }

            .switch-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 16px;
                max-width: 980px;
                margin: 24px auto 10px auto;
            }

            .switch-card {
                background: #ffffff;
                border: 1px solid var(--line);
                border-radius: 8px;
                padding: 18px;
                color: var(--ink) !important;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.10);
            }

            .switch-card h3 {
                color: var(--ink) !important;
                margin: 0 0 8px 0;
            }

            .switch-card p {
                color: var(--muted) !important;
                min-height: 42px;
            }

            .switch-card a {
                display: none;
                width: 100%;
                margin-top: 14px;
                background: #ff4b4b;
                color: #ffffff !important;
                text-align: center;
                text-decoration: none !important;
                border-radius: 8px;
                padding: 16px 14px;
                font-weight: 950;
            }

            .switch-card a.secondary {
                background: #2563eb;
            }

            .checkout-shell {
                background: #ffffff;
                border: 1px solid var(--line);
                border-radius: 8px;
                padding: 22px;
                color: var(--ink) !important;
                box-shadow: 0 14px 32px rgba(15, 23, 42, 0.10);
                margin-bottom: 22px;
            }

            .checkout-grid {
                display: grid;
                grid-template-columns: minmax(280px, 0.95fr) minmax(320px, 1.05fr);
                gap: 26px;
                align-items: start;
            }

            .checkout-image {
                width: 100%;
                height: 380px;
                object-fit: cover;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
            }

            .checkout-title {
                color: #111827 !important;
                margin: 0 0 10px 0;
                font-size: 2rem;
            }

            .checkout-price {
                color: #111827 !important;
                font-size: 2.2rem;
                font-weight: 950;
                margin: 14px 0;
            }

            .checkout-badge {
                display: inline-block;
                background: #dcfce7;
                color: #166534;
                border: 1px solid #86efac;
                border-radius: 8px;
                padding: 8px 10px;
                font-weight: 900;
                margin: 8px 8px 8px 0;
            }

            .purchase-intent-box {
                max-width: 860px;
                margin: 24px auto 8px auto;
                background: #101828;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 20px;
            }

            .purchase-intent-box h3 {
                color: #ffffff !important;
                margin: 0 0 10px 0;
                text-align: center;
            }

            .purchase-action-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 12px;
                max-width: 820px;
                margin: 14px auto 0 auto;
            }

            .purchase-action {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 54px;
                border-radius: 8px;
                border: 1px solid #334155;
                background: #ffffff;
                color: #172033 !important;
                text-decoration: none !important;
                font-size: 0.98rem;
                font-weight: 950;
                text-align: center;
                box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
                transition: transform 0.12s ease, box-shadow 0.12s ease;
            }

            .purchase-action:hover {
                transform: translateY(-1px);
                box-shadow: 0 12px 24px rgba(15, 23, 42, 0.16);
            }

            .purchase-action.buy {
                background: #16a34a;
                border-color: #11803a;
                color: #ffffff !important;
            }

            .purchase-action.close {
                background: #f8fafc;
            }

            .purchase-actions-native {
                max-width: 820px;
                margin: 14px auto 0 auto;
            }

            .purchase-actions-native div[data-testid="stButton"] {
                max-width: none;
                margin: 0;
            }

            .purchase-actions-native div[data-testid="stButton"] > button {
                min-height: 54px;
                width: 100%;
                border-radius: 8px;
                font-size: 0.98rem;
                font-weight: 950;
                box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
            }

            .blog-card {
                background: #ffffff;
                border: 1px solid #d7dde7;
                border-radius: 8px;
                box-shadow: 0 14px 32px rgba(15, 23, 42, 0.10);
                max-width: 900px;
                margin: 18px auto 30px auto;
                overflow: hidden;
            }

            .blog-topbar {
                background: #101828;
                color: #ffffff;
                padding: 16px 22px;
                letter-spacing: 0.02em;
                font-weight: 800;
            }

            .blog-body {
                padding: 30px;
                color: var(--ink) !important;
            }

            .blog-eyebrow {
                color: #2563eb;
                font-size: 0.85rem;
                font-weight: 800;
                text-transform: uppercase;
                margin-bottom: 6px;
            }

            .blog-title {
                color: var(--ink) !important;
                font-size: 2rem;
                line-height: 1.16;
                font-weight: 900;
                margin: 0 0 14px 0;
            }

            .blog-author {
                display: flex;
                align-items: center;
                gap: 12px;
                border-top: 1px solid #eef1f6;
                border-bottom: 1px solid #eef1f6;
                padding: 14px 0;
                margin: 16px 0 18px 0;
            }

            .blog-author img {
                width: 72px;
                height: 72px;
                border-radius: 50%;
                object-fit: cover;
                border: 3px solid #ffffff;
                box-shadow: 0 0 0 2px #2563eb, 0 8px 18px rgba(15, 23, 42, 0.16);
            }

            .blog-author strong {
                color: var(--ink) !important;
            }

            .blog-author span {
                color: var(--muted);
                font-size: 0.9rem;
            }

            .blog-quote {
                border-left: 5px solid #2563eb;
                padding: 18px 20px;
                background: #f8fbff;
                color: #243044 !important;
                font-size: 1.05rem;
                line-height: 1.65;
                margin-top: 12px;
            }

            .blog-verdict {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
                margin-top: 18px;
            }

            .blog-verdict div {
                background: #f3f7ff;
                border: 1px solid #d8e5ff;
                border-radius: 8px;
                padding: 12px;
                color: var(--ink) !important;
                font-weight: 800;
                text-align: center;
            }

            .instagram-post {
                background: #ffffff;
                border: 1px solid #dbdbdb;
                border-radius: 8px;
                max-width: 520px;
                margin: 18px auto 30px auto;
                overflow: hidden;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
                color: #262626;
                font-family: Arial, Helvetica, sans-serif;
            }

            .ig-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 12px 14px;
                border-bottom: 1px solid #efefef;
            }

            .ig-profile {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .ig-profile img {
                width: 52px;
                height: 52px;
                border-radius: 50%;
                border: 2px solid #e1306c;
                object-fit: cover;
            }

            .ig-name {
                font-weight: 800;
                font-size: 0.98rem;
            }

            .ig-sponsored {
                font-size: 0.78rem;
                color: #8e8e8e;
            }

            .ig-menu {
                font-weight: 900;
                color: #262626;
                font-size: 1.25rem;
            }

            .ig-photo {
                width: 100%;
                aspect-ratio: 1 / 1;
                object-fit: cover;
                display: block;
            }

            .ig-actions {
                display: flex;
                gap: 14px;
                padding: 12px 14px 4px 14px;
                font-size: 1.55rem;
            }

            .ig-likes {
                font-size: 0.92rem;
                font-weight: 800;
                padding: 0 14px 6px 14px;
            }

            .ig-caption {
                padding: 0 14px 16px 14px;
                font-size: 1rem;
                line-height: 1.52;
                color: #262626 !important;
            }

            .ig-caption strong {
                margin-right: 5px;
            }

            .store-card {
                background: #ffffff;
                border: 1px solid var(--line);
                border-radius: 8px;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.10);
                padding: 24px;
                margin: 14px 0 24px 0;
            }

            .buy-button-simulated {
                width: 100%;
                text-align: center;
                background: linear-gradient(180deg, #22c55e 0%, var(--green) 100%);
                border: 1px solid var(--green-dark);
                border-radius: 8px;
                box-shadow: 0 10px 0 #0b6b2d, 0 18px 32px rgba(22, 163, 74, 0.26);
                color: #ffffff;
                font-size: clamp(1.35rem, 3vw, 2.2rem);
                font-weight: 950;
                letter-spacing: 0;
                padding: 24px 20px;
                margin: 20px 0 28px 0;
                text-transform: uppercase;
            }

            .final-box {
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 8px;
                padding: 26px;
                color: #14532d;
                margin-top: 18px;
            }

            /* Ajustes finais para caber melhor em uma tela */
            .main .block-container {
                max-width: 1080px;
                padding-top: 0.85rem;
                padding-bottom: 2rem;
            }

            .hero-copy {
                padding: 14px 18px;
                margin-bottom: 12px;
            }

            .hero-copy h1 {
                font-size: 1.65rem;
                margin-bottom: 4px;
            }

            .hero-copy p,
            .shop-section-title p {
                font-size: 0.92rem;
                line-height: 1.35;
            }

            .shop-header {
                padding: 10px 14px;
                margin-bottom: 10px;
            }

            .shop-section-title {
                margin: 6px auto 12px auto;
            }

            .shop-section-title h2 {
                font-size: 1.28rem;
                margin-bottom: 4px;
            }

            .product-card {
                min-height: auto;
            }

            .product-card img {
                height: 190px;
            }

            .product-card-body {
                padding: 14px;
            }

            .product-card h3 {
                font-size: 1.12rem;
                margin-bottom: 8px;
            }

            .price {
                font-size: 1.3rem;
                margin-top: 8px;
            }

            .store-benefits {
                margin-top: 10px;
            }

            .store-benefits div {
                padding: 8px;
                font-size: 0.82rem;
            }

            .review-target-alert,
            .review-product-strip {
                max-width: 820px;
                margin-bottom: 10px;
                padding: 10px 12px;
            }

            .review-product-strip img {
                width: 92px;
                height: 60px;
            }

            .blog-card {
                max-width: 820px;
                margin: 10px auto 14px auto;
            }

            .blog-topbar {
                padding: 10px 16px;
            }

            .blog-body {
                padding: 16px 18px;
            }

            .blog-title {
                font-size: 1.45rem;
                margin-bottom: 10px;
            }

            .blog-product-hero {
                grid-template-columns: 150px 1fr;
                gap: 12px;
                padding: 10px;
                margin: 10px 0;
            }

            .blog-product-hero img {
                height: 92px;
            }

            .blog-author {
                padding: 10px 0;
                margin: 10px 0;
            }

            .blog-author img {
                width: 52px;
                height: 52px;
            }

            .blog-quote {
                padding: 12px 14px;
                font-size: 0.95rem;
                line-height: 1.45;
            }

            .blog-verdict {
                display: none;
            }

            .instagram-post {
                max-width: 390px;
                margin: 8px auto 12px auto;
            }

            .ig-photo {
                aspect-ratio: auto;
                height: 250px;
            }

            .ig-caption {
                font-size: 0.9rem;
                line-height: 1.35;
                padding-bottom: 12px;
            }

            .floating-cart {
                position: fixed;
                left: 18px;
                bottom: 18px;
                z-index: 9999;
                width: 255px;
                background: #ffffff;
                border: 1px solid #d9e0ec;
                border-radius: 8px;
                box-shadow: 0 18px 38px rgba(0, 0, 0, 0.25);
                padding: 10px;
                color: #172033 !important;
            }

            .floating-cart-title {
                color: #64748b !important;
                font-size: 0.76rem;
                font-weight: 900;
                text-transform: uppercase;
                margin-bottom: 8px;
            }

            .floating-cart-row {
                display: flex;
                gap: 10px;
                align-items: center;
            }

            .floating-cart img {
                width: 64px;
                height: 52px;
                border-radius: 8px;
                object-fit: cover;
                border: 1px solid #e5e7eb;
                flex: 0 0 auto;
            }

            .floating-cart strong {
                display: block;
                color: #111827 !important;
                font-size: 0.92rem;
                line-height: 1.2;
            }

            .floating-cart-pill {
                display: inline-block;
                margin-top: 6px;
                background: #dcfce7;
                color: #166534;
                border: 1px solid #86efac;
                border-radius: 8px;
                padding: 4px 7px;
                font-size: 0.75rem;
                font-weight: 900;
            }

            .decision-actions {
                max-width: 820px;
                margin: 12px auto 0 auto;
            }

            .checkout-shell {
                padding: 16px;
                margin-bottom: 14px;
            }

            .checkout-grid {
                grid-template-columns: minmax(260px, 0.85fr) minmax(320px, 1.15fr);
                gap: 18px;
            }

            .checkout-image {
                height: 250px;
            }

            .checkout-title {
                font-size: 1.55rem;
            }

            .checkout-price {
                font-size: 1.7rem;
                margin: 10px 0;
            }

            .buy-button-simulated {
                padding: 16px 20px;
                margin: 12px 0 16px 0;
                font-size: 1.45rem;
                box-shadow: 0 7px 0 #0b6b2d, 0 14px 24px rgba(22, 163, 74, 0.22);
            }

            .purchase-intent-box {
                max-width: 820px;
                padding: 10px;
                margin: 10px auto 0 auto;
            }

            div[data-testid="stRadio"] {
                max-width: 760px;
                margin: 12px auto 8px auto;
            }

            div[data-testid="stRadio"] label[data-baseweb="radio"] {
                min-height: 48px;
                padding: 10px 14px;
                margin: 7px 0;
            }

            div[data-testid="stButton"] {
                margin-top: 10px;
            }

            div[data-testid="stButton"] > button {
                min-height: 50px;
                font-size: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FUNCOES DE ESTADO E PERSISTENCIA
# ============================================================

def inicializar_estado() -> None:
    defaults = {
        "tela": 0,
        "id_usuario": str(uuid.uuid4()),
        "nome_participante": "",
        "idade": None,
        "genero": "",
        "grupo_ab": None,
        "fone_inicial_key": None,
        "fone_rejeitado_key": None,
        "fone_final_key": None,
        "houve_troca": None,
        "acao_clique_simulado": None,
        "likert_avaliacao_ajudou": 3,
        "likert_credibilidade": 3,
        "likert_compraria_recomendados": 3,
        "dados_salvos": False,
    }

    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def produto_nome(produto_key: str) -> str:
    return PRODUTOS[produto_key]["nome"]


def produto_rejeitado(produto_escolhido_key: str) -> str:
    return next(chave for chave in PRODUTOS if chave != produto_escolhido_key)


def limpar_query_params() -> None:
    try:
        st.query_params.clear()
    except Exception:
        pass


def avancar_para(tela: int) -> None:
    st.session_state.tela = tela
    st.rerun()


def garantir_fluxo_valido() -> None:
    """Evita erro caso o usuario recarregue ou acesse uma etapa sem dados anteriores."""
    if st.session_state.tela >= 1 and not st.session_state.nome_participante:
        st.session_state.tela = 0
    if st.session_state.tela >= 2 and st.session_state.fone_inicial_key is None:
        st.session_state.tela = 1
    if st.session_state.tela >= 3 and st.session_state.fone_final_key is None:
        st.session_state.tela = 2
    if st.session_state.tela >= 4 and st.session_state.acao_clique_simulado is None:
        st.session_state.tela = 3


def montar_linha_resposta() -> dict:
    manteve_ou_trocou = "Trocou" if st.session_state.houve_troca == "Sim" else "Manteve"

    return {
        "Nome": st.session_state.nome_participante,
        "Idade": st.session_state.idade,
        "Gênero": st.session_state.genero,
        "Grupo Experimental": st.session_state.grupo_ab,
        "Tipo de Avaliador": AVALIACOES[st.session_state.grupo_ab]["tipo"],
        "Decisão Após Avaliação": manteve_ou_trocou,
        "Ação no Clique Simulado": st.session_state.acao_clique_simulado,
        "Likert 1 - Avaliação Ajudou na Decisão": st.session_state.likert_avaliacao_ajudou,
        "Likert 2 - Credibilidade da Avaliação": st.session_state.likert_credibilidade,
        "Likert 3 - Compraria por Recomendação": st.session_state.likert_compraria_recomendados,
        "Data e Hora da Resposta": datetime.now().isoformat(timespec="seconds"),
    }


def salvar_resposta_google_sheets(linha: dict) -> bool:
    """Salva online no Google Sheets quando os secrets estiverem configurados."""
    try:
        sheets_config = st.secrets["google_sheets"]
        service_account_info = dict(st.secrets["gcp_service_account"])
    except Exception:
        return False

    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=GOOGLE_SHEETS_SCOPES,
    )
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(sheets_config["spreadsheet_id"])
    worksheet_name = sheets_config.get("worksheet_name", "respostas")

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=1000,
            cols=len(COLUNAS_CSV),
        )

    valores = worksheet.get_all_values()
    if not valores:
        worksheet.append_row(COLUNAS_CSV, value_input_option="USER_ENTERED")
    elif valores[0] != COLUNAS_CSV:
        worksheet.insert_row(COLUNAS_CSV, index=1, value_input_option="USER_ENTERED")

    worksheet.append_row(
        [linha.get(coluna, "") for coluna in COLUNAS_CSV],
        value_input_option="USER_ENTERED",
    )
    return True


def salvar_resposta_csv_local(linha: dict) -> None:
    """Salva os dados em modo append e cria o cabecalho na primeira resposta."""
    if CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:
        primeira_linha = CSV_PATH.read_text(encoding="utf-8-sig").splitlines()[0]
        cabecalho_atual = [coluna.strip() for coluna in primeira_linha.split(",")]

        if cabecalho_atual != COLUNAS_CSV:
            backup_path = CSV_PATH.with_name(
                f"{CSV_PATH.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{CSV_PATH.suffix}"
            )
            CSV_PATH.replace(backup_path)

    arquivo_existe = CSV_PATH.exists() and CSV_PATH.stat().st_size > 0

    with CSV_PATH.open("a", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=COLUNAS_CSV)

        if not arquivo_existe:
            writer.writeheader()

        writer.writerow(linha)


def salvar_resposta() -> None:
    if st.session_state.dados_salvos:
        return

    linha = montar_linha_resposta()

    try:
        salvou_online = salvar_resposta_google_sheets(linha)
    except Exception as erro:
        st.warning(
            "Não foi possível salvar no Google Sheets agora. "
            f"A resposta será salva no CSV local. Detalhe técnico: {erro}"
        )
        salvou_online = False

    if not salvou_online:
        salvar_resposta_csv_local(linha)

    st.session_state.dados_salvos = True


# ============================================================
# COMPONENTES VISUAIS EM HTML/CSS
# ============================================================

def render_intro() -> None:
    st.markdown(
        """
        <div class="hero-copy">
            <h1>Pesquisa Acadêmica sobre Consumo de Tecnologia</h1>
            <p>
                Este experimento simula uma jornada de compra online. As suas respostas
                serão usadas apenas para fins acadêmicos e analisadas de forma agregada.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_loja_header() -> None:
    st.markdown(
        """
        <div class="shop-header">
            <div class="shop-logo">TechStore Acadêmica</div>
            <div class="shop-trust">Compra simulada | Frete grátis | Ambiente de pesquisa</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tela_0_identificacao() -> None:
    st.markdown(
        """
        <div class="hero-copy">
            <h1>Pesquisa Acadêmica sobre Consumo de Tecnologia</h1>
            <p>
                Antes de iniciar a simulação de compra, preencha os dados abaixo.
                As respostas serão usadas apenas para fins acadêmicos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_identificacao", clear_on_submit=False):
        nome = st.text_input(
            "Nome",
            value=st.session_state.nome_participante,
            placeholder="Digite seu nome",
        )
        idade = st.number_input(
            "Idade",
            min_value=10,
            max_value=100,
            value=st.session_state.idade or 18,
            step=1,
        )
        genero = st.selectbox(
            "Gênero",
            options=[
                "Selecione",
                "Feminino",
                "Masculino",
                "Não binário",
                "Prefiro não informar",
                "Outro",
            ],
            index=0 if not st.session_state.genero else [
                "Selecione",
                "Feminino",
                "Masculino",
                "Não binário",
                "Prefiro não informar",
                "Outro",
            ].index(st.session_state.genero),
        )

        enviar = st.form_submit_button("Iniciar pesquisa", type="primary")

    if enviar:
        if not nome.strip():
            st.warning("Digite seu nome para iniciar a pesquisa.")
            return

        if genero == "Selecione":
            st.warning("Selecione uma opção de gênero para iniciar a pesquisa.")
            return

        st.session_state.nome_participante = nome.strip()
        st.session_state.idade = int(idade)
        st.session_state.genero = genero
        avancar_para(1)


def render_produto_card(produto_key: str) -> None:
    produto = PRODUTOS[produto_key]
    st.markdown(
        f"""
        <div class="product-card">
            <div class="product-image-wrap">
                <img src="{escape(produto['imagem_url'])}" alt="{escape(produto['nome'])}">
            </div>
            <div class="product-card-body">
                <h3>{escape(produto['nome'])}</h3>
                <span class="product-tag">{escape(produto['destaque_1'])}</span>
                <span class="product-tag">{escape(produto['destaque_2'])}</span>
                <div class="price">{escape(produto['preco'])}</div>
                <div class="helper-note">
                    Produto fictício vendido por TechStore Acadêmica.
                </div>
                <div class="store-benefits">
                    <div>Frete grátis</div>
                    <div>Entrega rápida</div>
                    <div>Garantia 12 meses</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_carrinho_fixo(produto_key: str) -> None:
    produto = PRODUTOS[produto_key]
    st.markdown(
        f"""
        <div class="floating-cart">
            <div class="floating-cart-title">No carrinho</div>
            <div class="floating-cart-row">
                <img src="{escape(produto['imagem_url'])}" alt="{escape(produto['nome'])}">
                <div>
                    <strong>{escape(produto['nome'])}</strong>
                    <span class="floating-cart-pill">Escolha inicial</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_blog_expert(fone_rejeitado_key: str) -> None:
    fone = PRODUTOS[fone_rejeitado_key]
    texto = AVALIACOES["Grupo A"]["texto"]
    avatar_url = (
        "https://images.unsplash.com/photo-1560250097-0b93528c311a"
        "?auto=format&fit=crop&w=300&h=300&q=80"
    )

    st.markdown(
        f"""
        <div class="blog-card">
            <div class="blog-topbar">Guia do Áudio | Review de Ricardo Almeida</div>
            <div class="blog-body">
                <div class="blog-eyebrow">Review profissional</div>
                <h2 class="blog-title">Análise Técnica do modelo avaliado: {escape(fone['nome'])}</h2>
                <div class="blog-product-hero">
                    <img src="{escape(fone['imagem_url'])}" alt="{escape(fone['nome'])}">
                    <div>
                        <span>Modelo em análise</span>
                        <strong>{escape(fone['nome'])}</strong>
                        <p>
                            Este é o fone avaliado nesta publicação, diferente do produto
                            que ficou no carrinho na etapa anterior.
                        </p>
                    </div>
                </div>
                <div class="blog-author">
                    <img src="{avatar_url}" alt="Foto de perfil do Guia do Áudio">
                    <div>
                        <strong>Ricardo Almeida</strong><br>
                        <span>Editor técnico do Guia do Áudio, especialista em acústica e equipamentos premium</span>
                    </div>
                </div>
                <div class="blog-quote">
                    “{escape(texto)}”
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_instagram_microinfluenciador(fone_rejeitado_key: str) -> None:
    fone = PRODUTOS[fone_rejeitado_key]
    texto = AVALIACOES["Grupo B"]["texto"]
    avatar_url = (
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e"
        "?auto=format&fit=crop&w=300&h=300&q=80"
    )

    st.markdown(
        f"""
        <div class="instagram-post">
            <div class="ig-header">
                <div class="ig-profile">
                    <img src="{avatar_url}" alt="Foto de perfil de Lucas Lifestyle">
                    <div>
                        <div class="ig-name">@Lucas_Lifestyle</div>
                        <div class="ig-sponsored">Parceria paga</div>
                    </div>
                </div>
                <div class="ig-menu">...</div>
            </div>
            <img class="ig-photo" src="{escape(fone['imagem_url'])}" alt="{escape(fone['nome'])}">
            <div class="ig-actions">♡ 💬 ↗</div>
            <div class="ig-likes">2.847 curtidas</div>
            <div class="ig-caption">
                <strong>@Lucas_Lifestyle</strong>Testei o {escape(fone['nome'])}: {escape(texto)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_botao_compra_simulado() -> None:
    st.markdown(
        """
        <div class="buy-button-simulated">🛒 IR E COMPRAR</div>
        """,
        unsafe_allow_html=True,
    )


def render_pagina_compra(fone_final_key: str) -> None:
    produto = PRODUTOS[fone_final_key]
    st.markdown(
        f"""
        <div class="checkout-shell">
            <div class="checkout-grid">
                <div>
                    <img class="checkout-image" src="{escape(produto['imagem_url'])}" alt="{escape(produto['nome'])}">
                </div>
                <div>
                    <h2 class="checkout-title">{escape(produto['nome'])}</h2>
                    <span class="checkout-badge">{escape(produto['destaque_1'])}</span>
                    <span class="checkout-badge">{escape(produto['destaque_2'])}</span>
                    <div class="checkout-price">{escape(produto['preco'])}</div>
                    <p class="helper-note">
                        Você está na página da loja do <strong>{escape(produto['nome'])}</strong>.
                        Esta é uma simulação de compra para fins acadêmicos.
                    </p>
                    <div class="store-benefits">
                        <div>Entrega rápida</div>
                        <div>Compra segura</div>
                        <div>Garantia 12 meses</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TELAS DO EXPERIMENTO
# ============================================================

def tela_1_introducao_e_escolha() -> None:
    render_intro()
    render_loja_header()

    st.markdown(
        """
        <div class="shop-section-title">
            <h2>Escolha seu fone de ouvido</h2>
            <p>
                Compare os dois modelos e clique no botão ao final do bloco do produto que você compraria.
                Nesta etapa, considere apenas as informações desta vitrine.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_produto_card("soundmax")
        if st.button("Escolher Fone SoundMax X1", type="primary", use_container_width=True):
            st.session_state.fone_inicial_key = "soundmax"
            st.session_state.fone_rejeitado_key = produto_rejeitado("soundmax")
            if st.session_state.grupo_ab is None:
                st.session_state.grupo_ab = random.choice(["Grupo A", "Grupo B"])
            avancar_para(2)

    with col2:
        render_produto_card("audiopro")
        if st.button("Escolher Fone AudioPro Z", type="primary", use_container_width=True):
            st.session_state.fone_inicial_key = "audiopro"
            st.session_state.fone_rejeitado_key = produto_rejeitado("audiopro")
            if st.session_state.grupo_ab is None:
                st.session_state.grupo_ab = random.choice(["Grupo A", "Grupo B"])
            avancar_para(2)


def tela_2_intervencao() -> None:
    fone_inicial = produto_nome(st.session_state.fone_inicial_key)
    fone_rejeitado = produto_nome(st.session_state.fone_rejeitado_key)
    grupo = st.session_state.grupo_ab

    render_carrinho_fixo(st.session_state.fone_inicial_key)

    st.title("Avaliação encontrada")

    if grupo == "Grupo A":
        render_blog_expert(st.session_state.fone_rejeitado_key)
    else:
        render_instagram_microinfluenciador(st.session_state.fone_rejeitado_key)

    st.markdown(
        f"""
        <div class="shop-section-title">
            <h2>Após ler esta avaliação sobre o {escape(fone_rejeitado)}, você deseja:</h2>
            <p>Escolha apenas uma ação para continuar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button(f"Manter no carrinho: {fone_inicial}", type="secondary", use_container_width=True):
            st.session_state.fone_final_key = st.session_state.fone_inicial_key
            st.session_state.houve_troca = "Não"
            avancar_para(3)
    with col2:
        if st.button(f"Trocar para avaliado: {fone_rejeitado}", type="primary", use_container_width=True):
            st.session_state.fone_final_key = st.session_state.fone_rejeitado_key
            st.session_state.houve_troca = "Sim"
            avancar_para(3)


def tela_3_clique_e_escalas() -> None:
    fone_final = produto_nome(st.session_state.fone_final_key)

    render_loja_header()
    st.markdown(
        f"""
        <div class="shop-section-title">
            <h2>Página da loja do {escape(fone_final)}</h2>
            <p>Confira o produto final da sua jornada e informe sua intenção real de compra.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_pagina_compra(st.session_state.fone_final_key)

    st.markdown(
        """
        <div class="purchase-intent-box">
            <h3>O que você faria agora?</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="purchase-actions-native">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="small")

    with col1:
        if st.button("🛒 Ir e Comprar", type="primary", use_container_width=True):
            st.session_state.acao_clique_simulado = 'Clicar em "Ir e Comprar" agora mesmo'
            avancar_para(4)

    with col2:
        if st.button("Adicionar à lista de desejos", use_container_width=True):
            st.session_state.acao_clique_simulado = "Adicionar à lista de desejos"
            avancar_para(4)

    with col3:
        if st.button("Fechar a página", use_container_width=True):
            st.session_state.acao_clique_simulado = "Fechar a página"
            avancar_para(4)

    st.markdown("</div>", unsafe_allow_html=True)


def tela_4_escalas() -> None:
    st.subheader("Escalas de avaliação")
    st.caption("1 = Discordo totalmente | 5 = Concordo totalmente")

    likert_1 = st.slider(
        "A avaliação lida na tela anterior me ajudou a decidir.",
        min_value=1,
        max_value=5,
        value=st.session_state.likert_avaliacao_ajudou,
        key="slider_likert_avaliacao_ajudou",
    )

    likert_2 = st.slider(
        "A avaliação lida possui alta credibilidade.",
        min_value=1,
        max_value=5,
        value=st.session_state.likert_credibilidade,
        key="slider_likert_credibilidade",
    )

    likert_3 = st.slider(
        "No futuro, eu consideraria comprar produtos recomendados por aquele avaliador.",
        min_value=1,
        max_value=5,
        value=st.session_state.likert_compraria_recomendados,
        key="slider_likert_compraria_recomendados",
    )

    if st.button("Finalizar pesquisa", type="primary"):
        st.session_state.likert_avaliacao_ajudou = likert_1
        st.session_state.likert_credibilidade = likert_2
        st.session_state.likert_compraria_recomendados = likert_3

        salvar_resposta()
        avancar_para(5)


def tela_5_agradecimento() -> None:
    st.markdown(
        """
        <div class="final-box">
            <h1>Muito obrigado por participar!</h1>
            <p>Suas respostas foram registradas com sucesso para a pesquisa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Resumo registrado"):
        st.write(f"ID do usuário: {st.session_state.id_usuario}")
        st.write(f"Nome: {st.session_state.nome_participante}")
        st.write(f"Idade: {st.session_state.idade}")
        st.write(f"Gênero: {st.session_state.genero}")
        st.write(f"Grupo: {st.session_state.grupo_ab}")
        st.write(f"Fone inicial: {produto_nome(st.session_state.fone_inicial_key)}")
        st.write(f"Fone final: {produto_nome(st.session_state.fone_final_key)}")
        st.write(f"Houve troca: {st.session_state.houve_troca}")
        st.write(f"Arquivo CSV: {CSV_PATH.name}")


def main() -> None:
    aplicar_css_global()
    inicializar_estado()
    garantir_fluxo_valido()

    if st.session_state.tela == 0:
        tela_0_identificacao()
    elif st.session_state.tela == 1:
        tela_1_introducao_e_escolha()
    elif st.session_state.tela == 2:
        tela_2_intervencao()
    elif st.session_state.tela == 3:
        tela_3_clique_e_escalas()
    elif st.session_state.tela == 4:
        tela_4_escalas()
    elif st.session_state.tela == 5:
        tela_5_agradecimento()
    else:
        st.session_state.tela = 0
        st.rerun()


if __name__ == "__main__":
    main()
