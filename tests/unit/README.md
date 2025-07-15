# 🔬 Teste Unitare

Această secțiune conține teste unitare specifice pentru diverse componente ale sistemului.

## 📁 **Conținut Teste Unitare**

### **🧠 Testare Componente AI**
- **`test_action_handler_budget.py`** - Testare recomandări buget
- **`test_action_handler_fix.py`** - Testare corectări action handler
- **`test_conversational_tone.py`** - Testare tonul conversațional
- **`test_message_flow.py`** - Testare flux procesare mesaje
- **`test_message_processing_flow.py`** - Testare flux procesare mesaje complet
- **`simple_flow_test.py`** - Testare simplă flux procesare mesaje

### **🔍 Testare Căutare și Produse**
- **`test_product_search.py`** - Testare căutare produse
- **`test_product_search_fix.py`** - Testare corectări căutare produse
- **`test_diverse_searches.py`** - Testare căutări diverse
- **`test_budget_recommendations.py`** - Testare recomandări buget

### **🤖 Testare Bot și Funcționalitate**
- **`test_bot_functionality.py`** - Testare funcționalitate bot
- **`test_telegram_bot.py`** - Testare bot Telegram
- **`test_various_scenarios.py`** - Testare scenarii diverse
- **`test_director_scenario.py`** - Testare scenariu director

### **🔧 Testare Sistem**
- **`test_basic.py`** - Testare de bază
- **`test_imports.py`** - Testare import-uri
- **`test_agent.py`** - Testare agent
- **`test_enhanced_agent.py`** - Testare agent îmbunătățit
- **`test_tasks.py`** - Testare sarcini

## 🚀 **Cum să Rulezi**

### **Teste Individuale**
```bash
# Test specific
python tests/unit/test_basic.py

# Test căutare produse
python tests/unit/test_product_search.py

# Test bot functionality
python tests/unit/test_bot_functionality.py
```

### **Toate Testele Unitare**
```bash
# Cu pytest (recomandat)
pytest tests/unit/ -v

# Manual, toate testele
python -m pytest tests/unit/
```

## 🎯 **Cerințe**

- Python 3.8+
- Toate dependențele din `requirements.txt`
- Configurare corectă a `.env` cu API keys
- Baza de date ChromaDB populată (pentru unele teste)

## 📊 **Categorii de Teste**

### **🧠 AI și Inteligență**
- Clasificarea intențiilor
- Generarea răspunsurilor
- Contextul conversațional
- Recomandările personalizate

### **🔍 Căutare și Produse**
- Căutarea în baza de date
- Filtrarea rezultatelor
- Recomandările bugetare
- Eliminarea duplicatelor

### **🤖 Funcționalități Bot**
- Procesarea mesajelor
- Gestionarea comenzilor
- Răspunsurile automate
- Integrarea platformelor

## 📝 **Note**

- Testele unitare sunt rapide și izolate
- Pot fi rulate independent
- Ideal pentru dezvoltare și debugging
- Acoperă funcționalități specifice

## 🔧 **Configurare și Cerințe**

### **Variabile de Mediu Necesare**
Asigurați-vă că aveți următoarele variabile configurate în `.env`:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here

# Database
DATABASE_URL=your_database_url_here

# XOFlowers Configuration
XOFLOWERS_WEBHOOK_SECRET=your_webhook_secret_here
DEBUG_MODE=true
```

### **Dependențe Necesare**
```bash
pip install -r requirements.txt
```

Principalele dependențe includ:
- `openai` - Pentru integrarea OpenAI
- `google-generativeai` - Pentru integrarea Gemini
- `chromadb` - Pentru baza de date vectorială
- `sentence-transformers` - Pentru embedding-uri
- `python-telegram-bot` - Pentru bot Telegram
- `flask` - Pentru API web
- `requests` - Pentru HTTP requests
- `beautifulsoup4` - Pentru web scraping
- `pytest` - Pentru rularea testelor
- `python-dotenv` - Pentru gestionarea variabilelor de mediu
- `cryptography` - Pentru securitate
- `black` și `flake8` - Pentru formatarea și linting

## 🗂️ **Gestionarea Datelor de Test**

### **Directorul `tests/unit/data/`**
Conține date de test și fixture-uri pentru testele unitare:
- Mock responses pentru API calls
- Date de test pentru produse și comenzi
- Configurări de test pentru diverse scenarii

### **Utilizarea Fixture-urilor**
```python
# Exemplu de fixture pentru date de test
@pytest.fixture
def sample_product_data():
    return {
        "id": "test_product_1",
        "name": "Buchet Trandafiri",
        "price": 150.0,
        "category": "buchet",
        "description": "Buchet elegant cu 12 trandafiri roșii"
    }

def test_product_search(sample_product_data):
    # Testul folosește datele din fixture
    assert sample_product_data["price"] == 150.0
```

### **Mock Data Management**
```python
# Exemplu de mockare pentru API calls
from unittest.mock import Mock, patch

@patch('src.intelligence.action_handler.openai_client')
def test_ai_response_mock(mock_openai):
    mock_openai.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response"))]
    )
    # Test logic aici
```

## 🧪 **Descrierea Detaliată a Testelor**

### **Core System Tests**
- **`test_basic.py`** - Testează funcționalitățile de bază ale sistemului
- **`test_imports.py`** - Verifică că toate import-urile funcționează corect
- **`test_agent.py`** - Testează funcționalitatea principală a agentului
- **`test_enhanced_agent.py`** - Testează funcționalitățile avansate ale agentului

### **AI Intelligence Tests**
- **`test_action_handler_budget.py`** - Testează recomandările bazate pe buget
- **`test_action_handler_fix.py`** - Testează corectările în action handler
- **`test_conversational_tone.py`** - Verifică tonul conversațional al agentului
- **`test_message_flow.py`** - Testează fluxul complet de procesare a mesajelor
- **`test_message_processing_flow.py`** - Testează pipelineul de procesare a mesajelor

### **Product Search Tests**
- **`test_product_search.py`** - Testează căutarea de produse în baza de date
- **`test_product_search_fix.py`** - Testează corectările în căutarea de produse
- **`test_diverse_searches.py`** - Testează diverse scenarii de căutare
- **`test_budget_recommendations.py`** - Testează recomandările în funcție de buget

### **Bot Platform Tests**
- **`test_bot_functionality.py`** - Testează funcționalitatea generală a bot-ului
- **`test_telegram_bot.py`** - Testează integrarea cu Telegram
- **`test_various_scenarios.py`** - Testează diverse scenarii de utilizare
- **`test_director_scenario.py`** - Testează scenariul specific pentru directoare

### **Flow Tests**
- **`simple_flow_test.py`** - Test simplu pentru fluxul de bază
- **`test_message_flow.py`** - Test pentru fluxul de procesare mesaje
- **`test_message_processing_flow.py`** - Test complet pentru fluxul de procesare mesaje

**Notă**: Testele `fixed_flow_test.py` și `final_flow_test.py` se află în directorul `tests/integration/` pentru testarea integrată.

## 🚀 **Ghid de Rulare Detailiat**

### **Rularea Individuală**
```bash
# Schimbă directorul
cd tests/unit

# Rulează un test specific
python test_basic.py
python test_product_search.py
python test_bot_functionality.py

# Sau cu pytest pentru output mai detaliat
pytest test_basic.py -v
pytest test_product_search.py -v --tb=short
```

### **Rularea pe Categorii**
```bash
# Toate testele AI
pytest test_*action_handler*.py test_conversational_tone.py -v

# Toate testele de căutare
pytest test_product_search*.py test_diverse_searches.py -v

# Toate testele bot
pytest test_bot_functionality.py test_telegram_bot.py -v

# Toate testele de flux
pytest *flow_test.py -v
```

### **Rularea cu Opțiuni Avansate**
```bash
# Rulează cu output detaliat și raportare
pytest tests/unit/ -v --tb=short --maxfail=5

# Rulează doar testele care nu au eșuat
pytest tests/unit/ --lf

# Rulează cu marcaje specifice (dacă sunt configurate)
pytest tests/unit/ -m "not slow"

# Rulează cu coverage
pytest tests/unit/ --cov=src --cov-report=html

# Rulează cu timeouts pentru teste lente
pytest tests/unit/ --timeout=60
```

## 📊 **Structura Testelor**

### **Format Standard**
Fiecare test urmează următoarea structură:
```python
import unittest
import sys
import os

# Adaugă calea către src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestClassName(unittest.TestCase):
    def setUp(self):
        """Configurare înainte de fiecare test"""
        pass
    
    def test_functionality(self):
        """Testează funcționalitatea specifică"""
        pass
    
    def tearDown(self):
        """Curățenie după fiecare test"""
        pass

if __name__ == '__main__':
    unittest.main()
```

## 🔍 **Debugging și Troubleshooting**

### **Probleme Comune**
1. **Import Errors**: Verificați că `sys.path` este configurat corect
2. **API Keys**: Asigurați-vă că toate API key-urile sunt configurate
3. **Database**: Verificați că ChromaDB este populată cu date
4. **Dependencies**: Instalați toate dependențele necesare
5. **Permission Errors**: Asigurați-vă că aveți permisiuni de scriere în directorul de teste
6. **Network Issues**: Verificați conectivitatea pentru API calls externe

### **Soluții Rapide**
```bash
# Reinstalați dependențele
pip install -r requirements.txt --upgrade

# Curățați cache-ul Python
python -c "import sys; print(sys.path)"
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} +

# Verificați configurarea mediului
python -c "import os; print(os.environ.get('OPENAI_API_KEY', 'NOT_SET'))"

# Testați connectivitatea
python -c "import requests; print(requests.get('https://api.openai.com/v1/models', timeout=5).status_code)"
```

### **Rularea cu Debug**
```bash
# Activează debug mode
export DEBUG_MODE=true

# Rulează cu output verbose
pytest tests/unit/ -v -s --tb=long

# Rulează cu pdb pentru debugging
pytest tests/unit/ --pdb
```

## 🎯 **Best Practices**

### **Scrierea Testelor**
- Fiecare test să fie independent
- Utilizați `setUp()` și `tearDown()` pentru configurare
- Testele să fie rapide și deterministe
- Utilizați nume descriptive pentru teste

### **Organizarea Testelor**
- Grupați testele pe funcționalități
- Separați testele unitare de cele de integrare
- Utilizați comentarii pentru claritate
- Mențineți testele actualizate cu codul

## 📈 **Monitorizare și Raportare**

### **Generarea Rapoartelor**
```bash
# Raport HTML cu coverage
pytest tests/unit/ --cov=src --cov-report=html

# Raport XML pentru CI/CD
pytest tests/unit/ --cov=src --cov-report=xml --junitxml=test-results.xml

# Raport în terminal
pytest tests/unit/ --cov=src --cov-report=term-missing
```

### **Metrici Importante**
- **Coverage**: Procent de cod acoperit de teste
- **Pass Rate**: Procentul de teste care trec
- **Execution Time**: Timpul de execuție al testelor
- **Failure Rate**: Procentul de teste care eșuează

## 🔄 **Integrare Continuă**

### **GitHub Actions Setup**
Pentru a configura rularea automată a testelor, creați fișierul `.github/workflows/tests.yml`:

```yaml
name: Unit Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --tb=short
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          DEBUG_MODE: true
```

### **Local CI Simulation**
```bash
# Simulați rularea CI local
python -m pytest tests/unit/ -v --tb=short --maxfail=1

# Testați pe Python versiuni multiple (cu pyenv)
pyenv local 3.8.10 3.9.16 3.10.11
tox -e py38,py39,py310
```

## 🆘 **Suport și Documentație**

### **Resurse Utile**
- [Documentația pytest](https://docs.pytest.org/)
- [Unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

### **Contact**
Pentru întrebări sau probleme cu testele:
- Creați un issue în repository
- Contactați echipa de dezvoltare
- Consultați documentația proiectului

---

**Ultima actualizare**: 15 Iulie 2025  
**Versiune**: 1.0.0  
**Status**: ✅ Toate testele funcționează corect
