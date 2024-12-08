from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from anticaptchaofficial.recaptchav2proxyless import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
import os
import time
from termcolor import colored


# Carregar variáveis do arquivo .env
load_dotenv()
api_key = os.getenv("API_KEY_anticaptcha_1")

# Configurar o driver do Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
url = "https://google.com/recaptcha/api2/demo"

try:
    # Acessar a URL
    driver.get(url)

    # Aguardar até o CAPTCHA carregar
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "recaptcha-demo"))
    )

    # Obter a sitekey do CAPTCHA
    captcha_element = driver.find_element(By.ID, "recaptcha-demo")
    captcha_key = captcha_element.get_attribute("data-sitekey")
    if not captcha_key:        
        print(colored(f"Falha ao obter a sitekey do CAPTCHA.", 'red'))
        driver.quit()
        exit()

    print(colored( f"Sitekey obtida: {captcha_key}", "green"))

    # Resolver o CAPTCHA com a API do AntiCaptcha
    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key(api_key)
    solver.set_website_url(url)
    solver.set_website_key(captcha_key)
    
    print(colored(f"Enviando CAPTCHA para resolução...", "yellow"))
    response = solver.solve_and_return_solution()

    if response == 0:        
        print(colored(f"Erro ao resolver o CAPTCHA: {solver.error_code}", "red"))
        driver.quit()
        exit()
    
    print(colored(f"CAPTCHA resolvido com sucesso!", "green"))    
    print(colored(f"Resposta do CAPTCHA: {response}", "light_green"))

    # Injetar a resposta no campo invisível do CAPTCHA
    driver.execute_script(
        "document.getElementById('g-recaptcha-response').style.display = 'block';"
    )
    driver.execute_script(
        f"document.getElementById('g-recaptcha-response').innerHTML = '{response}'"
    )

    # Simular clique no botão de envio
    submit_button = driver.find_element(By.ID, "recaptcha-demo-submit")
    submit_button.click()
    
    print(colored("CAPTCHA enviado com sucesso!", "green"))

    # Aguardar para verificar se a ação foi concluída
    time.sleep(5)

except Exception as e:    
    print(colored(f"Ocorreu um erro: {str(e)}", "red"))

finally:
    # Encerrar o driver
    driver.quit()
