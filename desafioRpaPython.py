from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# scraping das informações
link_vagas = "https://gruposeb.gupy.io/"
requisicao_vagas = requests.get(link_vagas)
site_vagas = BeautifulSoup(requisicao_vagas.text, "html.parser")

if requisicao_vagas.status_code == 200:
    lista_vagas = site_vagas.find('ul', {'aria-label': 'Lista de Vagas'})
    linhas = lista_vagas.find_all('li', class_='sc-f5007364-2 cskvFe')

    if lista_vagas:
        # lista para armazenar os dados das vagas
        dados_vaga = []

        #loop para adicionar os dados extraídos na lista dados_vaga
        for linha in linhas:
            cargo = linha.find('div', class_='sc-f5007364-4 gPLESq').text.strip()
            localidade = linha.find('div', class_='sc-f5007364-5 dejhbi').text.strip()
            efetividade = linha.find('div', class_='sc-f5007364-6 iWKdVs').text.strip()

            dados_vaga.append({
                "cargo": cargo,
                "localidade": localidade,
                "efetividade": efetividade
            })

    else:
        print("Não foi possível encontrar a lista de vagas.")
else:
    print(f"Erro ao acessar o site de vagas. Código de status: {requisicao_vagas.status_code}")

#print(dados_vaga)

# instala o chrome driver manager mais recente
servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico)

# link do formulário
link_formulario = 'https://forms.office.com/r/zfipx2RFsY'

# abre o navegador e acessa o link do formulário
driver.get(link_formulario)

# loop para preencher o formulário de acordo com as informações de cada vaga
for dado_vaga in dados_vaga:
    try:
        # Preenche o campo Cargo com o valor desejado
        campo_cargo = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f'[aria-labelledby="QuestionId_r28823796bb8b461195112faa4376895e QuestionInfo_r28823796bb8b461195112faa4376895e"]')))
        campo_cargo.send_keys(dado_vaga["cargo"])

        # Preenche o campo Cidade com o valor desejado. Caso o campo esteja vazio, o processo preenche o campo com a frase "não informado"
        if dado_vaga["localidade"] != "":
            campo_cidade = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, f'[aria-labelledby="QuestionId_r62327b3de37b4158b46eb9bf1ff8b45d QuestionInfo_r62327b3de37b4158b46eb9bf1ff8b45d"]')))
            campo_cidade.send_keys(dado_vaga["localidade"])
        else:
            campo_cidade = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, f'[aria-labelledby="QuestionId_r62327b3de37b4158b46eb9bf1ff8b45d QuestionInfo_r62327b3de37b4158b46eb9bf1ff8b45d"]')))
            campo_cidade.send_keys("Não informado")

        # verifica se qual a efetividade da vaga. Se for igual efetivo, clica na opção sim. Caso contrário, clica em não
        if dado_vaga["efetividade"].lower() == "efetivo":
            opcao_efetivo = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-automation-value="Sim"]')))
            opcao_efetivo.click()
        else:
            opcao_efetivo = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-automation-value="Não"]')))
            opcao_efetivo.click()

        # Clica no botão de enviar
        botao_enviar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-automation-id="submitButton"]')))
        botao_enviar.click()

    except Exception as e:
        # exibe a mensagem de erro
        print(f'Erro ao preencher o formulário para a vaga {dado_vaga}. Descrição do erro: {e}')

    # Caso aconteça um erro, os campos preenchidos serão limpos
        campo_cargo.clear()
        campo_cidade.clear()

    # Aguarda até encontrar a mensagem de sucesso 
    element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-automation-id="thankYouMessage"]')))

    # clica na opção de enviar outra resposta
    enviar_outra_resposta = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-automation-id="submitAnother"]')))
    enviar_outra_resposta.click()
        #aguarda um período de tempo para que a página seja carregada novamente
    time.sleep(2)

# exibe mensagem de sucesso
print(f'Processo concluído com sucesso.')
# fecha o navegador
driver.quit()

