from multiprocessing import Process, Queue, Semaphore
import time
import random
from datetime import datetime

class PrintJob:
    """Representa um trabalho de impressão"""
    def __init__(self, client_id, document, job_id):
        self.client_id = client_id
        self.document = document
        self.job_id = job_id
        self.timestamp = time.time()
    
    def __str__(self):
        time_str = datetime.fromtimestamp(self.timestamp).strftime('%H:%M:%S')
        return f"Job #{self.job_id} [Cliente {self.client_id}] {self.document} às {time_str}"


def client_process(client_id, print_queue, jobs_available, spaces_available):
    """
    Processo cliente que envia trabalhos para impressão
    
    Args:
        client_id: Identificador do cliente
        print_queue: Queue compartilhada
        jobs_available: Semaphore (conta jobs na fila)
        spaces_available: Semaphore (conta espaços livres)
    """
    jobs_number = 0

    print(f"[Cliente {client_id}] Iniciado")

    while True: 
        # Simula criação de documento
        time.sleep(random.uniform(1, 4))
        
        documents_list = ["relatorio_pibict.pdf", "contrato_acc.docx", 
                         "foto_dos_gatos.jpg", "contagem_daniel.xlsx"]
        doc = random.choice(documents_list)

        # Cria o job
        job = PrintJob(client_id, doc, jobs_number)
        print(f"[Cliente {client_id}] Criou: {job}")

        # Protocolo Produtor (Buffer Finito)
        spaces_available.acquire()  # Down(Spaces) - espera espaço
        print(f"[Cliente {client_id}] Adquiriu espaço na fila")

        print_queue.put(job)
        print(f"[Cliente {client_id}] Inseriu {job} na fila")

        jobs_available.release()  # Up(Jobs) - sinaliza job disponível
        print(f"[Cliente {client_id}] Sinalizou job disponível")

        jobs_number += 1


def print_server_process(print_queue, jobs_available, spaces_available):
    """
    Processo servidor que processa a fila de impressão
    
    Args:
        print_queue: Queue compartilhada
        jobs_available: Semaphore (conta jobs disponíveis)
        spaces_available: Semaphore (conta espaços livres)
    """
    print("[SERVIDOR] Iniciado e aguardando jobs...")
    
    while True:

        jobs_available.acquire()

        print("[SERVIDOR] Job disponível detectado!")

        job = print_queue.get()

        print(f"[SERVIDOR] Removeu da fila: {job}") 

        spaces_available.release()

        print("[SERVIDOR] Sinalizou espaço disponível")
        
        print(f"[SERVIDOR] Imprimindo: {job}")
        time.sleep(random.uniform(3, 7))
        print(f"[SERVIDOR] Concluído: {job}")


def main():
    """Função principal que inicializa e coordena o sistema"""
    
    # Configurações
    QUEUE_SIZE = 10
    NUM_CLIENTS = 3
    
    # Estruturas compartilhadas
    print_queue = Queue()
    
    # Semáforos
    jobs_available = Semaphore(0)           
    spaces_available = Semaphore(QUEUE_SIZE)  

    clients = [Process(target=client_process, args=(i, print_queue, jobs_available, spaces_available)) for i in range(NUM_CLIENTS)]
    
    server = Process(target=print_server_process, args=(print_queue, jobs_available, spaces_available))


    server.start()

    for c in clients:
        c.start()
        
    
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Encerrando programa...")

        for c in clients:
            c.terminate()
            c.join()

        server.terminate()
        server.join()

if __name__ == "__main__":
    main()