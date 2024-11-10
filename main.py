import multiprocessing
import subprocess

# def run_fastapi():
#     subprocess.run(["uvicorn", "src.backend.api:app", "--host", "0.0.0.0", "--port", "8000"])

def run_streamlit():
    subprocess.run(["streamlit", "run", "./src/frontend/new_gui.py"])

if __name__ == "__main__":
    #fastapi_process = multiprocessing.Process(target=run_fastapi)
    streamlit_process = multiprocessing.Process(target=run_streamlit)

    #fastapi_process.start()
    streamlit_process.start()

    try:
        #fastapi_process.join()
        streamlit_process.join()
    except KeyboardInterrupt:
        #fastapi_process.terminate()
        streamlit_process.terminate()

    #fastapi_process.join()
    streamlit_process.join()
