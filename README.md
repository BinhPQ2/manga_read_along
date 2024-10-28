# Manga Read Along

## Introduction
Welcome to the **Manga Read Along** project! This project provides a flexible solution for extracting information from various websites and delivering answers in a chatbot format. Leveraging the power of LangChain and large language models, the chatbot can interact with and process information from multiple online sources, assisting users in efficiently searching for and answering their queries.

## Features
- **Information Extraction**: Crawl information from major news websites such as VnExpress.
- **Integration of Large Language Models**: Utilize advanced language models to understand and answer user questions based on extracted information, ensuring accurate and natural responses.
- **User-Friendly Interface**: The user interface is developed using Streamlit, providing an intuitive and easy-to-use experience suitable for users of all technical levels.
- **Python Language**: The project is entirely developed in Python, making it easy to customize and extend.
- **Docker**: Docker file is included.

## System Requirements
- Python 3.7 or higher
- GPU with CUDA support is needed

## Installation Guide
### A. With local machine
#### 1. Clone the Repository
Clone this repository to your local machine:

```bash
git clone https://github.com/BinhPQ2/manga_read_along.git
cd manga_read_along
```
#### 2. Install Required Libraries

```bash
pip install -r requirements.txt
```

#### 3. How to Use
- If you have GPU, you can run both FE and BE with command:
``` bash
python main.py
```
- Recommended to use Kaggle import the `demo.ipynb` to run.


### B. With Docker
A simple way to start with only command:
```bash
docker compose up --build
```
Explore at:
```bash
http://localhost:8501
```
