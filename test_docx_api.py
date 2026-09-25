import httpx

test_md = """# AI Content Generation Chatbot
## Features
This application uses **Generative AI** and *Prompt Engineering*.
### Main Features
- Email Generation
- Report Generation
- Technical Explanation
### Technologies
| Technology | Purpose |
|------------|---------|
| FastAPI    | Backend |
| Groq       | AI Generation |
| SQLite     | Database |
### Example Code
```python
print('Hello World')
```
Visit [Google](https://www.google.com/)"""

try:
    res = httpx.post('http://127.0.0.1:8000/api/download/docx', json={'text': test_md})
    print(res.status_code)
    if res.status_code == 200:
        with open("test.docx", "wb") as f:
            f.write(res.content)
        print("Created test.docx")
    else:
        print(res.text)
except Exception as e:
    print(e)
