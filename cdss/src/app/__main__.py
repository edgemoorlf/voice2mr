import argparse
import uvicorn
from app import app

def main():
    parser = argparse.ArgumentParser(description='Medical AI Assistant API.')
    parser.add_argument('--domain', 
                        type=str, 
                        help='The expertise domain of RAG', 
                        default='oncology')
    parser.add_argument('--collection', 
                        type=str, 
                        help='The collection of RAG', 
                        default='med_refv3')
    parser.add_argument('--port', 
                        type=int, 
                        help='The listening port', 
                        default=8000)
    args = parser.parse_args()

    uvicorn.run("app:app", 
                host="0.0.0.0", 
                port=args.port,
                reload=True)

if __name__ == "__main__":
    main() 